"""A preserved hosted import gains analytics metadata without replacing data."""

import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "seed_hosted_graph",
    Path(__file__).resolve().parents[2] / "scripts/seed_hosted_graph.py",
)
seed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed)


class Result(list):
    def single(self):
        return self[0]

    def consume(self):
        pass


class PreservedGraph:
    def __init__(self, fingerprint="a" * 64, metadata=()):
        self.fingerprint = fingerprint
        self.metadata = metadata
        self.queries = []

    def run(self, query, **parameters):
        self.queries.append((query, parameters))
        if "RETURN m.fingerprint" in query:
            return Result([{"fingerprint": self.fingerprint}])
        if "MATCH (d:JudgeDataset)" in query:
            return Result(self.metadata)
        if "Entity" in query:
            raise AssertionError("A retry must not reload existing entities.")
        return Result()


def test_preserved_import_adds_missing_analytics_provenance_only():
    tx = PreservedGraph()
    result = seed.import_transaction(tx, "a" * 64, {}, {}, "2026-10-26")
    assert result["preserved"] is True
    creations = [(q, p) for q, p in tx.queries if "CREATE" in q]
    assert len(creations) == 1
    assert creations[0][1] == {"fingerprint": "a" * 64, "as_of": "2026-10-26"}


def test_retry_preserves_matching_analytics_provenance():
    tx = PreservedGraph(
        metadata=[
            {
                "fingerprint": "a" * 64,
                "as_of": "2026-10-26",
                "source_kind": "synthetic_replay",
            }
        ]
    )
    assert seed.import_transaction(tx, "a" * 64, {}, {}, "2026-10-26")["preserved"]
    assert not any("CREATE" in q for q, _ in tx.queries)


def test_conflicting_import_is_not_given_new_provenance():
    tx = PreservedGraph(fingerprint="b" * 64)
    with pytest.raises(ValueError, match="another fixture"):
        seed.import_transaction(tx, "a" * 64, {}, {}, "2026-10-26")
    assert not any("JudgeDataset" in q for q, _ in tx.queries)


@pytest.mark.parametrize(
    "metadata",
    [
        [
            {
                "fingerprint": "b" * 64,
                "as_of": "2026-10-26",
                "source_kind": "synthetic_replay",
            }
        ],
        [
            {
                "fingerprint": "a" * 64,
                "as_of": "2026-10-25",
                "source_kind": "synthetic_replay",
            }
        ],
        [{"fingerprint": "a" * 64, "as_of": "2026-10-26", "source_kind": "real"}],
    ],
)
def test_conflicting_analytics_metadata_is_never_overwritten(metadata):
    tx = PreservedGraph(metadata=metadata)
    with pytest.raises(ValueError, match="provenance differs"):
        seed.import_transaction(tx, "a" * 64, {}, {}, "2026-10-26")
    assert not any("CREATE" in q for q, _ in tx.queries)
