import { useState } from "react";
import { Network, ExternalLink, RefreshCw } from "lucide-react";
import {
  api,
  type Application,
  type Context,
  type Decision,
  type Delivery,
  type Officer,
  type Advice,
} from "./api";

import { GraphEvidence } from "./GraphEvidence";

type Props = {
  application: Application;
  officer: Officer;
  decision?: Decision;
  deliveries: Delivery[];
  inputUrl: string;
  refresh: () => Promise<void>;
};
export function CaseReview({
  application,
  officer,
  decision,
  deliveries,
  inputUrl,
  refresh,
}: Props) {
  const [context, setContext] = useState<Context | null>(null);
  const [advice, setAdvice] = useState<Advice | null>(null);
  const [connection, setConnection] = useState("");
  const [revocationReason, setRevocationReason] = useState("");
  const [reason, setReason] = useState("");
  const [limit, setLimit] = useState("");
  const [expiry, setExpiry] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  async function act(task: () => Promise<void>) {
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await task();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function decide(kind: "APPROVED" | "REJECTED") {
    await act(async () => {
      const cents = Number(limit);
      if (kind === "APPROVED" && (!Number.isSafeInteger(cents) || cents < 1 || !expiry))
        throw new Error("Enter a whole-cent USD allocation and an expiry date.");
      await api(`/applications/${application.id}/decisions`, officer, {
        decision: kind,
        reason,
        confirm_lender_authorization: confirmed,
        ...(kind === "APPROVED"
          ? { limit_cents: cents, expires_at: new Date(expiry + "T23:59:59Z").toISOString() }
          : {}),
      });
      setNotice(
        kind === "APPROVED"
          ? "Lender decision recorded. Delivery to input finance is queued; no payment or collection has occurred."
          : "Rejection recorded. No allocation or payment was created.",
      );
      await refresh();
    });
  }
  const terms = decision ? JSON.parse(decision.terms) : null;
  const executionLink = new URL(inputUrl);
  if (decision) executionLink.searchParams.set("approval", decision.id);
  return (
    <section className="credit-case" aria-labelledby="case-heading">
      <header>
        <div>
          <h2 id="case-heading">{application.farmer_id}</h2>
          <p>
            {application.status.replaceAll("_", " ")} · {application.provenance} data
          </p>
        </div>
        <span className="credit-status">Lender review</span>
      </header>
      <dl className="credit-facts">
        <div>
          <dt>Application</dt>
          <dd>{application.id}</dd>
        </div>
        <div>
          <dt>Input-finance profile</dt>
          <dd>{application.input_farmer_id}</dd>
        </div>
      </dl>
      <div className="credit-evidence">
        <h3>Evidence for this decision</h3>
        <p>Graph evidence supports review. It does not authorize credit or establish payment.</p>
        <div className="credit-actions">
          <button
            disabled={busy}
            onClick={() =>
              void act(async () =>
                setContext(await api<Context>(`/applications/${application.id}/context`, officer)),
              )
            }
          >
            <Network size={16} /> Load graph context
          </button>
          <button
            disabled={busy}
            onClick={() =>
              void act(async () => {
                const result = await api<Advice>(
                  `/applications/${application.id}/recommendation`,
                  officer,
                  {},
                );
                setAdvice(result);
              })
            }
          >
            Request AI summary
          </button>
        </div>
        {context && (
          <GraphEvidence
            context={context}
            applicationId={application.id}
            officer={officer}
            busy={busy}
            filter={connection}
            onFilter={(value) => {
              setConnection(value);
              void act(async () =>
                setContext(
                  await api<Context>(
                    `/applications/${application.id}/context${value ? "?relationship=" + encodeURIComponent(value) : ""}`,
                    officer,
                  ),
                ),
              );
            }}
          />
        )}
        {advice && (
          <section className="credit-advice" aria-label="AI evidence summary">
            <h4>AI summary · advisory only</h4>
            <p>
              <strong>{advice.headline}</strong>
            </p>
            <ul>
              {advice.observations.map((row, i) => (
                <li key={i}>
                  {row.text}
                  <small>
                    Evidence:{" "}
                    {row.evidence_ids
                      .map((id) => advice.sources.find((source) => source.id === id)?.label || id)
                      .join("; ")}
                  </small>
                </li>
              ))}
            </ul>
            <h4>Evidence still missing</h4>
            <ul>
              {advice.missing_evidence.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p>
              {advice.provider} · {advice.model}. The lender records the decision separately.
            </p>
            <details>
              <summary>Inspect the facts supplied to AI</summary>
              {advice.sources.map((source) => (
                <div key={source.id}>
                  <h4>{source.label}</h4>
                  <pre>{JSON.stringify(source.value, null, 2)}</pre>
                </div>
              ))}
            </details>
          </section>
        )}
      </div>
      {error && (
        <p className="credit-error" role="alert">
          {error}
        </p>
      )}
      {notice && (
        <p className="credit-notice" role="status">
          {notice}
        </p>
      )}
      {!decision && application.status === "PENDING" && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void decide("APPROVED");
          }}
        >
          <h3>Record the lender’s decision</h3>
          <p>
            USD examples are illustrative. The receiving lender must have confirmed this farmer’s
            mapping.
          </p>
          <div className="credit-form-grid">
            <label>
              Allocation in USD cents
              <input
                type="number"
                min="1"
                max="100000000"
                step="1"
                value={limit}
                onChange={(e) => setLimit(e.target.value)}
                placeholder="e.g. 18000 = $180.00"
              />
            </label>
            <label>
              Expiry date (UTC)
              <input type="date" value={expiry} onChange={(e) => setExpiry(e.target.value)} />
            </label>
          </div>
          <label>
            Decision reason
            <textarea
              required
              minLength={5}
              maxLength={500}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </label>
          <label className="credit-confirm">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              required
            />{" "}
            I am authorized to record this decision for {officer.lender_id}.
          </label>
          <div className="credit-actions">
            <button className="credit-primary" disabled={busy || !confirmed}>
              {busy ? "Recording…" : "Approve and queue handoff"}
            </button>
            <button
              type="button"
              disabled={busy || !confirmed || reason.trim().length < 5}
              onClick={() => void decide("REJECTED")}
            >
              Record rejection
            </button>
          </div>
        </form>
      )}
      {decision && (
        <div className="credit-decision">
          <h3>
            {decision.revoked_at
              ? "Decision revoked"
              : decision.decision === "REPLAY_APPROVED"
                ? "Historical replay decision"
                : "Recorded lender decision"}
          </h3>
          <p>{decision.reason}</p>
          <dl className="credit-facts">
            <div>
              <dt>Reference</dt>
              <dd>{decision.id}</dd>
            </div>
            <div>
              <dt>Officer</dt>
              <dd>{decision.officer_id}</dd>
            </div>
            {terms?.limit_cents && (
              <div>
                <dt>Illustrative allocation</dt>
                <dd>
                  {new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(
                    terms.limit_cents / 100,
                  )}
                </dd>
              </div>
            )}
          </dl>
          {decision.decision === "APPROVED" && (
            <>
              <a className="credit-link" href={executionLink.href}>
                Continue to input finance <ExternalLink size={15} />
              </a>
              <p>
                Sign in separately to the receiving lender workspace. No session is transferred.
              </p>
              {!decision.revoked_at && (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    void act(async () => {
                      await api(`/decisions/${decision.id}/revoke`, officer, {
                        reason: revocationReason,
                      });
                      setNotice(
                        "Revocation recorded and queued. Existing payments still require reconciliation.",
                      );
                      await refresh();
                    });
                  }}
                >
                  <label>
                    Revocation reason
                    <textarea
                      required
                      minLength={5}
                      maxLength={500}
                      value={revocationReason}
                      onChange={(e) => setRevocationReason(e.target.value)}
                    />
                  </label>
                  <button disabled={busy}>Revoke this approval</button>
                </form>
              )}
            </>
          )}
        </div>
      )}
      {deliveries.length > 0 && (
        <section className="credit-deliveries">
          <h3>Delivery to input finance</h3>
          {deliveries.map((event) => (
            <div className="credit-delivery" key={event.id}>
              <div>
                <strong>
                  {event.kind === "approval" ? "Approval" : "Revocation"} ·{" "}
                  {event.status.toLowerCase()}
                </strong>
                <p>
                  {event.attempts} delivery attempts
                  {event.last_error ? ` · ${event.last_error}` : ""}
                </p>
                <p>
                  {event.status === "DELIVERED"
                    ? "Receiver acknowledgment recorded."
                    : `Next attempt: ${new Date(event.next_attempt).toLocaleString()}`}
                </p>
              </div>
              {!["DELIVERED", "SUPERSEDED"].includes(event.status) && (
                <button
                  disabled={busy}
                  onClick={() =>
                    void act(async () => {
                      await api(`/deliveries/${event.id}/retry`, officer, {});
                      await refresh();
                    })
                  }
                >
                  <RefreshCw size={15} /> Check delivery
                </button>
              )}
            </div>
          ))}
        </section>
      )}
    </section>
  );
}
