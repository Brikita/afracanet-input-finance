"""Generate a reproducible fictional world in an isolated relational database.

No network calls, application imports, model scoring, private source records,
or genuine payment evidence. All amounts use integer minor units.
"""

import json
import random
import sqlite3
import time
from datetime import date, timedelta
from functools import partial
from pathlib import Path

from .exports import checksum, export_files
from .validation import validate_database
from .writer import Writer

PROFILES = {
    "walkthrough": (100, 24),
    "development": (10_000, 24),
    "stress": (100_000, 36),
}
SCENARIOS = (
    "regular_history",
    "thin_file",
    "late_installments",
    "new_member",
    "sparse_network",
    "seasonal_income",
    "partial_repayment",
    "missing_context",
)
STATUSES = (
    "REQUESTED",
    "APPROVED",
    "INVOICING",
    "AWAITING_PAYMENT",
    "PAYMENT_REVIEW",
    "READY_FOR_COLLECTION",
    "COLLECTED",
    "CANCELLED",
)
REGIONS = (
    "Meru",
    "Machakos",
    "Nakuru",
    "Uasin Gishu",
    "Bungoma",
    "Kakamega",
    "Nyeri",
    "Kirinyaga",
    "Embu",
    "Kitui",
    "Makueni",
    "Trans Nzoia",
)
SOURCE = "synthetic_replay"


def month_start(as_of, offset):
    absolute = as_of.year * 12 + as_of.month - 1 - offset
    return date(absolute // 12, absolute % 12 + 1, 1)


def organization_for(farmer_number, counts, kind, salt=0):
    """Choose a reproducible counterparty inside the farmer's lender partition."""
    tenant_index = farmer_number % 4
    choices = (counts[kind] - 1 - tenant_index) // 4 + 1
    index = tenant_index + 4 * ((farmer_number // 4 + salt) % choices)
    return f"SYN-{kind.upper()}-{index:03d}"


def build_database(
    path, farmers=100, months=24, seed=20261026, as_of=date(2026, 10, 26)
):
    if farmers < 8 or farmers > 1_000_000 or months < 12 or months > 120:
        raise ValueError("Use 8–1,000,000 farmers and 12–120 months.")
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    rng = random.Random(seed)
    with sqlite3.connect(path) as conn:
        conn.executescript(
            Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        )
        conn.execute("PRAGMA cache_size = -32768")
        w = Writer(conn)
        organization_counts = {
            "Lender": 4,
            "Officer": 12,
            "Cooperative": max(4, farmers // 125),
            "SavingsGroup": max(8, farmers // 40),
            "Dealer": max(4, farmers // 500),
        }
        for kind, count in organization_counts.items():
            for n in range(count):
                tenant = f"SYN-LENDER-{n % 4:03d}"
                w.node(
                    f"SYN-{kind.upper()}-{n:03d}",
                    kind,
                    tenant,
                    display_name=f"Synthetic {kind} {n + 1}",
                )
        for n, region in enumerate(REGIONS):
            w.node(
                f"SYN-REGION-{n:02d}",
                "ReferenceRegion",
                "context",
                name=region,
                assignment="fictional_reference_region",
                weather_state="not_joined",
            )
        for crop in ("maize", "beans", "sorghum", "coffee"):
            w.node(f"SYN-CROP-{crop}", "Crop", "context", name=crop)
        for dealer in range(organization_counts["Dealer"]):
            for product, amount, unit in (
                ("dap", 4500, "50 kg bag"),
                ("seed", 1800, "2 kg pack"),
                ("can", 3200, "50 kg bag"),
            ):
                product_id = f"SYN-PRODUCT-{dealer:03d}-{product}"
                w.node(
                    product_id,
                    "Product",
                    f"SYN-LENDER-{dealer % 4:03d}",
                    name=product,
                    unit=unit,
                    price_minor=amount,
                    currency="USD",
                    price_basis="illustrative_not_market_quote",
                )
                w.edge(f"SYN-DEALER-{dealer:03d}", product_id, "OFFERS", as_of)
        w.flush()
        conn.commit()
        for n in range(farmers):
            tenant_index = n % 4
            tenant = f"SYN-LENDER-{tenant_index:03d}"
            farmer = f"farmer-synth-{n + 1:06d}"
            scenario = SCENARIOS[(n // 4) % len(SCENARIOS)]

            # Tenant-local counterparties keep graph permission fixtures coherent.
            organization = partial(organization_for, n, organization_counts)
            cooperative = organization("Cooperative")
            group = organization("SavingsGroup")
            dealer = organization("Dealer")
            officer = organization("Officer")
            region_index = (n // 4) % len(REGIONS)
            created = month_start(as_of, 1 if scenario == "new_member" else months - 1)
            w.node(
                farmer,
                "Farmer",
                tenant,
                display_name=f"Synthetic Farmer {n + 1:06d}",
                reference_region=REGIONS[region_index],
                scenario=scenario,
                joined_on=str(created),
                evidence_state="missing"
                if scenario == "missing_context"
                else "synthetic",
                simulated_outcome_use="scenario_testing_only",
            )
            farm = f"SYN-FARM-{n + 1:06d}"
            household = f"SYN-HOUSEHOLD-{n + 1:06d}"
            w.node(
                farm,
                "Farm",
                tenant,
                area_hectares_tenths=rng.randint(5, 65),
                location_verified=False,
            )
            w.node(household, "Household", tenant, member_count=rng.randint(1, 8))
            w.edge(farmer, farm, "OPERATES_FARM", created)
            w.edge(farmer, household, "IN_HOUSEHOLD", created)
            w.edge(
                farm,
                f"SYN-REGION-{region_index:02d}",
                "ASSIGNED_REFERENCE_REGION",
                created,
            )
            w.edge(farmer, tenant, "SERVED_BY", created)
            if scenario != "sparse_network":
                w.edge(farmer, cooperative, "MEMBER_OF", created)
                w.edge(farmer, group, "MEMBER_OF", created)
                if n % 5 == 0:
                    w.edge(
                        farmer, organization("SavingsGroup", 1), "MEMBER_OF", created
                    )
            crop = ("maize", "beans", "sorghum", "coffee")[(n // 4) % 4]
            w.edge(farm, f"SYN-CROP-{crop}", "GROWS", created)
            w.flush()  # parent rows must exist before dependent relational rows

            # No score is used to choose fictional repayments; scenarios are authoring
            # inputs, never empirically observed risk labels or model validation.
            if scenario not in {"thin_file", "new_member", "sparse_network"}:
                for vintage in range(0, months - 7, 12):
                    originated = month_start(as_of, months - 1 - vintage) + timedelta(
                        days=3
                    )
                    loan = f"SYN-LOAN-{n + 1:06d}-{vintage:03d}"
                    principal = rng.choice((24000, 36000, 48000, 60000)) * 100
                    installments = []
                    for sequence in range(1, 7):
                        due = month_start(
                            as_of, months - 1 - vintage - sequence
                        ) + timedelta(days=14)
                        paid_on = due
                        paid = principal // 6
                        if scenario == "late_installments":
                            paid_on += timedelta(days=14 + sequence % 3 * 7)
                        if scenario == "partial_repayment" and sequence >= 5:
                            paid = paid // 2 if sequence == 5 else 0
                        if paid_on > as_of:
                            paid = 0
                        installments.append(
                            (
                                loan,
                                sequence,
                                str(due),
                                str(paid_on) if paid else None,
                                principal // 6,
                                paid,
                            )
                        )
                    repaid = sum(row[5] for row in installments)
                    w.node(
                        loan,
                        "Loan",
                        tenant,
                        currency="KES",
                        outcome_basis="authored_scenario",
                        originated_on=str(originated),
                    )
                    w.edge(farmer, loan, "HAS_LOAN", originated)
                    w.flush()
                    conn.execute(
                        "INSERT INTO loans VALUES (?,?,?,?,?,?,?,?)",
                        (
                            loan,
                            farmer,
                            principal,
                            repaid,
                            principal - repaid,
                            "KES",
                            str(originated),
                            installments[-1][2],
                        ),
                    )
                    conn.executemany(
                        "INSERT INTO installments VALUES (?,?,?,?,?,?)", installments
                    )
                    w.entry(
                        f"{loan}-DISBURSE",
                        farmer,
                        tenant,
                        loan,
                        "loan_disbursement",
                        principal,
                        originated,
                        tenant,
                    )
                    for row in installments:
                        if row[5]:
                            w.entry(
                                f"{loan}-REPAY-{row[1]}",
                                farmer,
                                tenant,
                                loan,
                                "loan_repayment",
                                row[5],
                                row[3],
                                tenant,
                            )

            history = (
                0
                if scenario == "new_member"
                else 2
                if scenario == "thin_file"
                else months
            )
            for offset in range(history):
                first = month_start(as_of, offset)
                when = first + timedelta(days=9)
                if when < created or when > as_of:
                    continue
                season_id = (
                    f"SYN-SEASON-{n + 1:06d}-{first.year}-{1 if first.month < 7 else 2}"
                )
                # Emit each season once, at its first encountered (latest) month.
                if offset == 0 or first.month in (6, 12):
                    w.node(
                        season_id,
                        "CropSeason",
                        tenant,
                        crop=crop,
                        year=first.year,
                        half=1 if first.month < 7 else 2,
                    )
                    w.edge(farm, season_id, "HAS_SEASON", when)
                # Synthetic income varies by season, never from presumed real yields.
                seasonal = 3 if first.month in (3, 4, 9, 10) else 1
                for event_kind, counterparty, amount in (
                    (
                        "cooperative_delivery",
                        cooperative,
                        rng.randint(80, 250) * 1000 * seasonal,
                    ),
                    ("group_contribution", group, rng.choice((500, 1000, 1500)) * 100),
                    ("dealer_purchase", dealer, rng.randint(12, 65) * 1000),
                    (
                        "farm_sale_receipt",
                        cooperative,
                        rng.randint(40, 180) * 1000 * seasonal,
                    ),
                ):
                    if (
                        scenario == "sparse_network"
                        and event_kind == "group_contribution"
                    ):
                        continue
                    ident = f"SYN-EVENT-{n + 1:06d}-{first:%Y%m}-{event_kind}"
                    w.entry(
                        ident,
                        farmer,
                        counterparty,
                        None,
                        event_kind,
                        amount,
                        when,
                        tenant,
                    )
                if len(w.nodes) >= 2000:
                    w.flush()

            application = f"SYN-APPLICATION-{n + 1:06d}"
            decision = f"SYN-DECISION-{n + 1:06d}"
            allocation = f"SYN-ALLOCATION-{n + 1:06d}"
            order = f"SYN-ORDER-{n + 1:06d}"
            status = STATUSES[(n // 32 + (n % 4) * 2) % len(STATUSES)]
            order_date = as_of - timedelta(days=10)
            quantity = rng.randint(1, 3)
            amount = 4500 * quantity
            limit = rng.choice((15000, 20000, 30000))
            reserved = amount if status in STATUSES[:5] else 0
            spent = amount if status in {"READY_FOR_COLLECTION", "COLLECTED"} else 0
            paid = spent if spent else amount // 2 if status == "PAYMENT_REVIEW" else 0
            application_date = max(created, order_date - timedelta(days=10))
            w.node(
                application,
                "Application",
                tenant,
                submitted_on=str(application_date),
                requested_currency="USD",
                purpose="illustrative_input_allocation",
            )
            w.node(
                decision,
                "LenderDecision",
                tenant,
                decision="approved",
                authority="synthetic_officer",
                approved_on=str(order_date - timedelta(days=1)),
            )
            w.node(
                allocation,
                "Allocation",
                tenant,
                currency="USD",
                basis="separately_assigned_demo_not_KES_conversion",
            )
            w.node(
                order,
                "InputOrder",
                tenant,
                status=status,
                currency="USD",
                amount_minor=amount,
                quantity=quantity,
            )
            w.edge(farmer, application, "SUBMITTED", application_date)
            w.edge(
                application, decision, "HAS_DECISION", order_date - timedelta(days=1)
            )
            w.edge(officer, decision, "AUTHORIZED", order_date - timedelta(days=1))
            w.edge(
                decision,
                allocation,
                "CREATED_ALLOCATION",
                order_date - timedelta(days=1),
            )
            w.edge(farmer, allocation, "HAS_ALLOCATION", order_date - timedelta(days=1))
            w.edge(order, allocation, "USES_ALLOCATION", order_date)
            w.edge(farmer, order, "REQUESTED_INPUTS", order_date)
            w.edge(order, dealer, "SUPPLIED_BY", order_date)
            w.edge(
                order,
                dealer.replace("SYN-DEALER-", "SYN-PRODUCT-") + "-dap",
                "CONTAINS_PRODUCT",
                order_date,
                quantity=quantity,
            )
            if status not in {"REQUESTED", "APPROVED", "INVOICING", "CANCELLED"}:
                invoice = f"REPLAY-INVOICE-{n + 1:06d}"
                w.node(
                    invoice,
                    "Invoice",
                    tenant,
                    amount_minor=amount,
                    currency="USD",
                    provider="synthetic_replay",
                )
                w.edge(order, invoice, "HAS_INVOICE", order_date + timedelta(days=2))
                if paid:
                    payment = f"REPLAY-PAYMENT-{n + 1:06d}"
                    w.node(
                        payment,
                        "ReplayPayment",
                        tenant,
                        amount_minor=paid,
                        currency="USD",
                        payment_evidence_kind=SOURCE,
                    )
                    w.edge(
                        invoice,
                        payment,
                        "HAS_REPLAY_PAYMENT",
                        order_date + timedelta(days=3),
                    )
            if status == "COLLECTED":
                collection = f"SYN-COLLECTION-{n + 1:06d}"
                w.node(
                    collection,
                    "Collection",
                    tenant,
                    collected_on=str(as_of - timedelta(days=2)),
                    basis=SOURCE,
                )
                w.edge(order, collection, "HAS_COLLECTION", as_of - timedelta(days=2))
            if status == "PAYMENT_REVIEW" or n % 19 == 0:
                issue = f"SYN-ISSUE-{n + 1:06d}"
                w.node(
                    issue,
                    "Issue",
                    tenant,
                    category="payment" if paid else "stock",
                    resolved=False,
                )
                w.edge(order, issue, "HAS_ISSUE", as_of - timedelta(days=1))
            w.flush()
            conn.execute(
                "INSERT INTO allocations VALUES (?,?,?,?,?,?,?)",
                (
                    allocation,
                    farmer,
                    limit,
                    reserved,
                    spent,
                    "USD",
                    str(as_of + timedelta(days=60)),
                ),
            )
            conn.execute(
                "INSERT INTO input_orders VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    order,
                    farmer,
                    allocation,
                    dealer,
                    status,
                    amount,
                    "USD",
                    SOURCE,
                    paid,
                    str(order_date),
                    str(as_of - timedelta(days=2)) if status == "COLLECTED" else None,
                ),
            )
            if (n + 1) % 100 == 0:
                conn.commit()
        w.flush()
        conn.commit()
        conn.executescript("""
            CREATE INDEX entities_kind ON entities(kind);
            CREATE INDEX entities_tenant ON entities(tenant_id,kind);
            CREATE INDEX relationships_source ON relationships(source_id,kind);
            CREATE INDEX relationships_target ON relationships(target_id,kind);
            CREATE INDEX ledger_farmer_time ON ledger(farmer_id,occurred_on);
            CREATE INDEX ledger_loan_kind ON ledger(loan_id,kind);
            CREATE INDEX loans_farmer ON loans(farmer_id);
            CREATE INDEX orders_status ON input_orders(status,farmer_id);
            CREATE INDEX orders_allocation ON input_orders(allocation_id,status);
        """)
        return {
            "nodes_by_kind": dict(sorted(w.node_counts.items())),
            "relationships_by_kind": dict(sorted(w.edge_counts.items())),
        }


def generate(
    output,
    profile="walkthrough",
    farmers=None,
    months=None,
    seed=20261026,
    as_of=date(2026, 10, 26),
):
    defaults = PROFILES[profile]
    farmers = defaults[0] if farmers is None else farmers
    months = defaults[1] if months is None else months
    if output.exists():
        raise FileExistsError(
            "Choose a new output directory; existing datasets are never overwritten."
        )
    output.mkdir(parents=True)
    started = time.perf_counter()
    path = output / "scenario.sqlite"
    counts = build_database(path, farmers, months, seed, as_of)
    return finish_pack(output, profile, farmers, months, seed, as_of, counts, started)


def finish_pack(output, profile, farmers, months, seed, as_of, counts, started):
    """Validate and export an owned generated database; never imports into the app."""
    path = output / "scenario.sqlite"
    validated = validate_database(path, as_of)
    export_files(path, output)
    manifest = {
        "schema_version": 1,
        "source_kind": SOURCE,
        "profile": profile,
        "seed": seed,
        "as_of": str(as_of),
        "farmers": farmers,
        "months": months,
        "contains_real_people": False,
        "contains_real_financial_records": False,
        "statistically_calibrated": False,
        "loan_model_training_allowed": False,
        "payment_evidence_kind": SOURCE,
        "provider_calls": 0,
        "currency_boundary": "Fictional KES histories; separate illustrative USD allocations and orders. No exchange rate or relabelling.",
        "weather_boundary": "Synthetic reference-region assignments only. Public weather is not embedded or invented.",
        "use": "Workflow, graph exploration, query/load testing. Not predictive or real-world financial validation.",
        "counts": validated,
        **counts,
        "files": [
            {"file": p.name, "bytes": p.stat().st_size, "sha256": checksum(p)}
            for p in sorted(output.iterdir())
            if p.is_file() and p.name != "manifest.json"
        ],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "output": str(output),
        "seconds": round(time.perf_counter() - started, 2),
        "farmers": farmers,
        **validated,
    }
