"""Build a deterministic, openly synthetic integration replay. No customer data."""
import argparse
import csv
from datetime import date, timedelta
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]


def build(seed=20261026, as_of=date(2026, 10, 26)):
    rng = random.Random(seed)
    profiles = ["regular_history", "thin_file", "late_installments", "new_member", "sparse_network"]
    farmers, ledger, loans, memberships, approvals = [], [], [], [], []
    products = [
        {"id": "replay-dap-50", "supplier_id": "supplier-demo", "name": "Replay DAP fertilizer", "category": "Fertilizer", "unit": "50 kg bag", "price_cents": 4500, "stock": 100, "currency": "USD"},
        {"id": "replay-seed-2", "supplier_id": "supplier-demo", "name": "Replay maize seed", "category": "Seed", "unit": "2 kg pack", "price_cents": 1800, "stock": 100, "currency": "USD"},
    ]
    def tx(farmer_id, kind, cents, when, counterparty):
        ledger.append({"id": f"REPLAY-TX-{len(ledger)+1:06d}", "farmer_id": farmer_id,
                       "kind": kind, "amount_minor": cents, "currency": "KES", "date": when,
                       "counterparty_id": counterparty, "source_kind": "synthetic_replay"})
    for number in range(1, 31):
        farmer_id = f"farmer-replay-{number:03d}"
        profile = profiles[(number-1) % len(profiles)]
        region = "meru-reference" if number % 2 else "machakos-reference"
        farmers.append({"farmer_id": farmer_id, "source_farmer_id": f"REPLAY-F-{number:03d}",
                        "display_name": f"Replay Farmer {number:03d}", "reference_region": region,
                        "location_assignment": "synthetic_reference_point_assignment", "scenario": profile,
                        "source_kind": "synthetic_replay"})
        cooperative = f"REPLAY-COOP-{1 + number % 2}"
        memberships.append({"farmer_id": farmer_id, "organization_id": cooperative, "relationship": "MEMBER_OF", "source_kind": "synthetic_replay"})
        if profile != "sparse_network":
            memberships.append({"farmer_id": farmer_id, "organization_id": f"REPLAY-CHAMA-{1 + number % 3}", "relationship": "MEMBER_OF", "source_kind": "synthetic_replay"})
        months = [] if profile == "new_member" else [9] if profile == "thin_file" else list(range(1, 10))
        for month in months:
            tx(farmer_id, "cooperative_delivery_receipt", rng.randrange(15000, 60001, 1000) * 100,
               f"2026-{month:02d}-10", cooperative)
            if profile != "sparse_network":
                tx(farmer_id, "group_contribution", rng.choice([500, 1000, 1500]) * 100,
                   f"2026-{month:02d}-12", f"REPLAY-CHAMA-{1 + number % 3}")
            tx(farmer_id, "dealer_purchase", rng.choice([2400, 4500, 6300]) * 100,
               f"2026-{month:02d}-20", f"REPLAY-DEALER-{1 + number % 2}")
        if profile in {"regular_history", "late_installments"}:
            principal = rng.choice([24000, 36000, 48000]) * 100
            loan_id = f"REPLAY-LOAN-{number:03d}"
            tx(farmer_id, "loan_disbursement", principal, "2026-02-15", "REPLAY-LENDER-1")
            repayments = []
            for month in range(3, 9):
                if profile == "late_installments" and month in {6, 7}:
                    continue
                tx(farmer_id, "loan_repayment", principal // 6, f"2026-{month:02d}-15", "REPLAY-LENDER-1")
                repayments.append(ledger[-1]["id"])
            paid = (principal // 6) * len(repayments)
            loans.append({"id": loan_id, "farmer_id": farmer_id, "currency": "KES", "principal_minor": principal,
                          "repaid_minor": paid, "outstanding_minor": principal-paid,
                          "final_due_date": "2026-08-15", "repayment_transaction_ids": repayments,
                          "source_kind": "synthetic_replay", "use": "Workflow scenario only; not observed loan outcomes or a training label."})
        approvals.append({"farmer_id": farmer_id, "name": f"Replay Farmer {number:03d}", "location": region,
                          "limit_cents": rng.choice([7500, 15000, 20000]),
                          "expires_at": (as_of + timedelta(days=90)).isoformat() + "T23:59:59+00:00",
                          "approval_reference": f"REPLAY-USD-APP-{number:03d}"})
    ledger.sort(key=lambda item: (item["date"], item["id"]))
    return {"manifest": {"source_kind": "synthetic_replay", "seed": seed, "as_of": as_of.isoformat(),
                         "contains_real_people": False, "contains_real_financial_records": False,
                         "statistically_calibrated": False, "loan_model_training_allowed": False,
                         "currency_boundary": "KES histories are fictional. USD allocations/catalogue are separately assigned sandbox fixtures, not currency conversions.",
                         "weather_boundary": "Public weather may be joined at reference-region level; farmer location associations remain fictional.",
                         "use": "Anonymous non-live scenarios for integration tests and labelled demos. No evidence of predictive accuracy, lending performance, or demand."},
            "organizations": {"lenders": ["REPLAY-LENDER-1"], "cooperatives": ["REPLAY-COOP-1", "REPLAY-COOP-2"],
                              "chamas": ["REPLAY-CHAMA-1", "REPLAY-CHAMA-2", "REPLAY-CHAMA-3"], "dealers": ["REPLAY-DEALER-1", "REPLAY-DEALER-2"]},
            "farmers": farmers, "memberships": memberships, "ledger": ledger, "loans": loans,
            "sandbox_catalogue": products, "sandbox_approvals": approvals}


def validate(pack):
    manifest = pack["manifest"]
    if manifest["source_kind"] != "synthetic_replay" or manifest["contains_real_people"] or manifest["contains_real_financial_records"] or manifest["statistically_calibrated"] or manifest["loan_model_training_allowed"]:
        raise ValueError("Replay data must retain its synthetic, uncalibrated status.")
    farmer_ids = {row["farmer_id"] for row in pack["farmers"]}
    if len(farmer_ids) != len(pack["farmers"]):
        raise ValueError("Duplicate farmer identifiers.")
    ids = {row["id"] for row in pack["ledger"]}
    if len(ids) != len(pack["ledger"]):
        raise ValueError("Duplicate ledger identifiers.")
    organizations = {value for values in pack["organizations"].values() for value in values}
    by_id = {row["id"]: row for row in pack["ledger"]}
    for row in pack["ledger"]:
        if row["farmer_id"] not in farmer_ids or row["counterparty_id"] not in organizations or row["source_kind"] != "synthetic_replay" or row["currency"] != "KES" or type(row["amount_minor"]) is not int or row["amount_minor"] <= 0 or row["date"] > manifest["as_of"]:
            raise ValueError("Invalid ledger link, provenance, amount, or event date.")
    for link in pack["memberships"]:
        if link["farmer_id"] not in farmer_ids or link["organization_id"] not in organizations or link["source_kind"] != "synthetic_replay":
            raise ValueError("Invalid graph membership.")
    for loan in pack["loans"]:
        repayments = [by_id[tx_id] for tx_id in loan["repayment_transaction_ids"]]
        if any(row["kind"] != "loan_repayment" or row["farmer_id"] != loan["farmer_id"] for row in repayments):
            raise ValueError("Repayment linked to the wrong loan or farmer.")
        if loan["repaid_minor"] != sum(row["amount_minor"] for row in repayments) or loan["principal_minor"] != loan["repaid_minor"] + loan["outstanding_minor"] or loan["outstanding_minor"] < 0:
            raise ValueError("Loan totals do not reconcile.")
    return {"farmers": len(farmer_ids), "ledger_events": len(ids), "loans": len(pack["loans"]), "memberships": len(pack["memberships"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "datasets/replay")
    args = parser.parse_args()
    pack = build()
    counts = validate(pack)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "scenario.json").write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
    with (args.output / "input-finance-usd-demo.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["farmer_id", "name", "location", "limit_cents", "expires_at", "approval_reference"])
        writer.writeheader()
        writer.writerows(pack["sandbox_approvals"])
    print(json.dumps({"source_kind": "synthetic_replay", **counts}))


if __name__ == "__main__":
    main()
