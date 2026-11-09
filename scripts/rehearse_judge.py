"""Rehearse one linked synthetic scenario. Sandbox buyer payment stays manual."""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone

import httpx
from prepare_judge import profile_paths


def request(client, base, method, path, token=None, body=None, expected=(200,)):
    response = client.request(
        method,
        base + "/api" + path,
        headers={"Authorization": "Bearer " + token} if token else {},
        json=body,
    )
    if response.status_code not in expected:
        raise RuntimeError(
            f"{method} {path.split('?')[0]} returned HTTP {response.status_code}; no provider body was logged."
        )
    return response.json()


def run(name, action):
    public, private = profile_paths(name)
    report_path = public / "rehearsal.json"
    report = (
        json.loads(report_path.read_text(encoding="utf-8"))
        if report_path.exists()
        else {
            "profile": name,
            "source_kind": "synthetic_replay",
            "physical_delivery_observed": False,
        }
    )
    access = json.loads((public / "input-access.json").read_text(encoding="utf-8"))[
        "access_code"
    ]
    officer = json.loads(
        (private / "local-officer-accounts.json").read_text(encoding="utf-8")
    )[0]
    credit, inputs = "http://127.0.0.1:28001", "http://127.0.0.1:28000"

    def save():
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    with httpx.Client(timeout=65) as client:
        health = request(client, inputs, "GET", "/health")
        if action != "inspect" and health["payment_mode"] != "sandbox":
            raise RuntimeError(
                "This provider rehearsal requires sandbox mode; simulated payments are not accepted."
            )
        if action == "create-invoice" and (
            health["payment_mode"] != "sandbox" or health["ai_mode"] != "gemini"
        ):
            raise RuntimeError(
                "Start this profile with --providers. Mock payment/demo parsing is not provider verification."
            )
        credit_token = request(
            client,
            credit,
            "POST",
            "/session",
            body={"officer_id": officer["officer_id"], "password": officer["password"]},
        )["token"]
        workspace = request(
            client, credit, "GET", "/workspace?status=PENDING", credit_token
        )
        if "application_id" not in report:
            if not workspace["applications"]:
                raise RuntimeError(
                    "No pending case in the judge officer's lender scope."
                )
            application = workspace["applications"][0]
            report.update(
                application_id=application["id"],
                farmer_id=application["farmer_id"],
                lender_id=officer["lender_id"],
            )
            save()
        application_id = report["application_id"]
        context = request(
            client,
            credit,
            "GET",
            f"/applications/{application_id}/context",
            credit_token,
        )
        graph = request(
            client,
            credit,
            "GET",
            f"/applications/{application_id}/analytics",
            credit_token,
        )
        report.update(
            graph_context_retrieved=True,
            repayment_history_available=context["repayment_history"]["available"],
            analytics_run_id=graph.get("id"),
            gds_version=graph.get("gds_version"),
        )
        if not graph["available"]:
            save()
            raise RuntimeError(
                "Run actual GDS for this lender before recording the connected rehearsal."
            )
        if action == "inspect":
            save()
            print(json.dumps(report))
            return
        if "decision_id" not in report:
            advice = request(
                client,
                credit,
                "POST",
                f"/applications/{application_id}/recommendation",
                credit_token,
                {},
            )
            decision = request(
                client,
                credit,
                "POST",
                f"/applications/{application_id}/decisions",
                credit_token,
                {
                    "decision": "APPROVED",
                    "reason": "Authorized synthetic sandbox rehearsal; no real loan or predictive credit claim.",
                    "confirm_lender_authorization": True,
                    "limit_cents": 18000,
                    "expires_at": (
                        datetime.now(timezone.utc) + timedelta(days=7)
                    ).isoformat(),
                    "analytics_run_id": graph["id"],
                    "evaluation_id": advice["evaluation_id"],
                },
            )
            report.update(
                decision_id=decision["id"],
                evaluation_id=advice["evaluation_id"],
                ai_provider=advice["provider"],
                ai_model=advice["model"],
            )
            save()
        deadline = time.monotonic() + 35
        while True:
            workspace = request(
                client,
                credit,
                "GET",
                f"/workspace?selected={application_id}",
                credit_token,
            )
            delivery = next(
                (
                    row
                    for row in workspace["deliveries"]
                    if row["decision_id"] == report["decision_id"]
                    and row["kind"] == "approval"
                ),
                None,
            )
            if delivery and delivery["status"] == "DELIVERED":
                report["signed_delivery_id"] = delivery["id"]
                save()
                break
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Signed delivery is pending; inspect the outbox. Do not manually substitute authority."
                )
            time.sleep(1)

        def login(persona):
            return request(
                client,
                inputs,
                "POST",
                "/session",
                body={"persona": persona, "access_code": access},
            )["token"]

        farmer_token, lender_token = (
            login(report["farmer_id"]),
            login(report["lender_id"]),
        )
        state = request(client, inputs, "GET", "/state", farmer_token)
        if "order_id" not in report:
            product = next(
                row
                for row in state["products"]
                if row["id"].startswith("SYN-PRODUCT-000-")
                and row["category"] == "Seed"
            )
            interpretation = request(
                client,
                inputs,
                "POST",
                "/assistant",
                farmer_token,
                {
                    "text": f"I need exactly 1 pack of {product['name']} ({product['unit']}), product ID {product['id']}.",
                    "supplier_id": product["supplier_id"],
                },
            )
            if interpretation.get("clarification") or interpretation.get("items") != [
                {"product_id": product["id"], "quantity": 1}
            ]:
                raise RuntimeError(
                    "AI request needs clarification; review it in the farmer UI before recording an order."
                )
            order = request(
                client,
                inputs,
                "POST",
                "/orders",
                farmer_token,
                {
                    "client_request_id": "judge-" + name,
                    "supplier_id": product["supplier_id"],
                    "items": interpretation["items"],
                },
                expected=(200, 201),
            )
            report.update(
                order_id=order["id"],
                supplier_id=product["supplier_id"],
                request_ai_mode=health["ai_mode"],
            )
            save()
        order_id = report["order_id"]
        dealer_token = login(report["supplier_id"])

        def current_order():
            return next(
                row
                for row in request(client, inputs, "GET", "/state", farmer_token)[
                    "orders"
                ]
                if row["id"] == order_id
            )

        order = current_order()
        if order["status"] == "REQUESTED":
            request(client, inputs, "POST", f"/orders/{order_id}/approve", lender_token)
        order = current_order()
        if order["status"] == "APPROVED" and action == "create-invoice":
            request(client, inputs, "POST", f"/orders/{order_id}/invoice", dealer_token)
        elif order["status"] == "APPROVED":
            raise RuntimeError(
                "No invoice exists; run the explicit create-invoice stage first."
            )
        if action in {"reconcile", "collect"}:
            request(
                client, inputs, "POST", f"/orders/{order_id}/reconcile", lender_token
            )
            request(
                client, inputs, "POST", f"/orders/{order_id}/reconcile", lender_token
            )
        order = current_order()
        if order["status"] not in {"READY_FOR_COLLECTION", "COLLECTED"}:
            response = client.post(
                inputs + f"/api/orders/{order_id}/collect",
                headers={"Authorization": "Bearer " + dealer_token},
                json={"code": "000000"},
            )
            if response.status_code != 409:
                raise AssertionError("Unpaid collection was not blocked")
            report["unpaid_collection_blocked"] = True
        if action == "collect":
            if order["status"] not in {"READY_FOR_COLLECTION", "COLLECTED"}:
                raise RuntimeError(
                    "Actual sandbox payment is not confirmed; handover was not recorded."
                )
            if order["status"] != "COLLECTED":
                request(
                    client,
                    inputs,
                    "POST",
                    f"/orders/{order_id}/collect",
                    dealer_token,
                    {"code": order["pickup_code"]},
                )
                request(
                    client,
                    inputs,
                    "POST",
                    f"/orders/{order_id}/collect",
                    dealer_token,
                    {"code": order["pickup_code"]},
                )
        order = current_order()
        timeline = request(
            client, inputs, "GET", f"/orders/{order_id}/timeline", lender_token
        )
        lender_order = next(
            row
            for row in request(client, inputs, "GET", "/state", lender_token)["orders"]
            if row["id"] == order_id
        )
        report.update(
            order_status=order["status"],
            payment_mode=order["payment_mode"],
            amount_cents=order["amount_cents"],
            invoice_id=order.get("invoice_id"),
            payment_url=lender_order.get("payment_url"),
            payment_confirmed_events=sum(
                row["action"] == "PAYMENT_CONFIRMED" for row in timeline
            ),
            collection_events=sum(row["action"] == "COLLECTED" for row in timeline),
            handover_kind="recorded_synthetic_demonstration_only",
        )
        if (
            order["status"] in {"READY_FOR_COLLECTION", "COLLECTED"}
            and report["payment_confirmed_events"] != 1
        ):
            raise AssertionError(
                "Payment reconciliation did not preserve exactly one effect"
            )
        if order["status"] == "COLLECTED" and report["collection_events"] != 1:
            raise AssertionError("Collection did not preserve exactly one effect")
        save()
        print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["inspect", "create-invoice", "reconcile", "collect"]
    )
    parser.add_argument("--name", default="compact")
    args = parser.parse_args()
    run(args.name, args.action)
