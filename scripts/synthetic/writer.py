"""Bounded graph and ledger writes to the offline relational registry."""

import json
from collections import Counter

SOURCE = "synthetic_replay"


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class Writer:
    """Bounded batches preserve insertion order and foreign-key validation."""

    def __init__(self, connection):
        self.connection = connection
        self.nodes, self.edges, self.entries = [], [], []
        self.node_counts, self.edge_counts = Counter(), Counter()

    def node(self, identifier, kind, tenant, **properties):
        self.nodes.append((identifier, kind, tenant, encode(properties), SOURCE))
        self.node_counts[kind] += 1

    def edge(self, source, target, kind, when, **properties):
        self.edges.append((source, target, kind, str(when), encode(properties)))
        self.edge_counts[kind] += 1

    def entry(self, identifier, farmer, counterparty, loan, kind, amount, when, tenant):
        self.node(
            identifier,
            "LedgerEvent",
            tenant,
            event_kind=kind,
            amount_minor=amount,
            currency="KES",
            occurred_on=str(when),
        )
        self.entries.append(
            (identifier, farmer, counterparty, loan, kind, amount, "KES", str(when))
        )
        self.edge(farmer, identifier, "HAS_LEDGER_EVENT", when)
        self.edge(identifier, counterparty, "WITH_COUNTERPARTY", when)
        if loan:
            self.edge(identifier, loan, "FOR_LOAN", when)

    def flush(self):
        self.connection.executemany(
            "INSERT INTO entities VALUES (?,?,?,?,?)", self.nodes
        )
        self.connection.executemany(
            "INSERT INTO ledger VALUES (?,?,?,?,?,?,?,?)", self.entries
        )
        self.connection.executemany(
            "INSERT INTO relationships(source_id,target_id,kind,occurred_on,properties) VALUES (?,?,?,?,?)",
            self.edges,
        )
        self.nodes.clear()
        self.edges.clear()
        self.entries.clear()
