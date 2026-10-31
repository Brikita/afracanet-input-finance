import { useCallback, useEffect, useRef, useState } from "react";
import { RefreshCw, LogOut } from "lucide-react";
import { api, type Officer, type Workspace } from "./api";
import { CaseReview } from "./CaseReview";
import { ReplayRegistry } from "./ReplayRegistry";
import "./credit.css";

export function CreditWorkspace({ history = false }: { history?: boolean }) {
  const [ready, setReady] = useState(false);
  const [mobileCase, setMobileCase] = useState(false);
  const requestVersion = useRef(0);
  const [officer, setOfficer] = useState<Officer | null>(null);
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [state, setState] = useState<Workspace | null>(null);
  const [selected, setSelected] = useState("");
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState(history ? "" : "PENDING");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [farmer, setFarmer] = useState("");
  const [inputFarmer, setInputFarmer] = useState("");
  const [provenance, setProvenance] = useState("synthetic");
  const [requestId, setRequestId] = useState("");
  useEffect(() => {
    setReady(true);
    try {
      const raw = sessionStorage.getItem("credit-officer");
      if (raw) setOfficer(JSON.parse(raw));
    } catch {
      sessionStorage.removeItem("credit-officer");
    }
    setRequestId(crypto.randomUUID());
  }, []);
  const refresh = useCallback(async () => {
    if (!officer) return;
    const version = ++requestVersion.current;
    const result = await api<Workspace>(
      `/workspace?q=${encodeURIComponent(query)}&status=${encodeURIComponent(filter)}&selected=${encodeURIComponent(selected)}`,
      officer,
    );
    if (version === requestVersion.current) setState(result);
  }, [officer, query, filter, selected]);
  useEffect(() => {
    let active = true;
    async function load() {
      try {
        await refresh();
        if (active) setError("");
      } catch (err) {
        if (active) setError((err as Error).message);
      }
    }
    void load();
    const timer = setInterval(() => void load(), 10000);
    return () => {
      active = false;
      requestVersion.current++;
      clearInterval(timer);
    };
  }, [refresh]);
  async function signIn(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await api<Officer>("/session", null, { officer_id: account, password });
      sessionStorage.setItem("credit-officer", JSON.stringify(result));
      setOfficer(result);
      setPassword("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function signOut() {
    try {
      await api("/session", officer, undefined, "DELETE");
    } finally {
      sessionStorage.removeItem("credit-officer");
      setOfficer(null);
      setState(null);
      setSelected("");
    }
  }
  const application =
    state?.applications.find((a) => a.id === selected) ||
    (state?.selected_application?.id === selected ? state.selected_application : null);
  const decision = state?.decisions.find((d) => d.application_id === selected);
  return (
    <main className="credit-workspace">
      <header className="credit-heading">
        <div>
          <h1>{history ? "Decision history" : "Lender review"}</h1>
          <p>Evidence, lender decisions, and input finance.</p>
        </div>
        {officer && (
          <button onClick={() => void signOut()}>
            <LogOut size={16} /> Sign out
          </button>
        )}
      </header>
      {!officer ? (
        <section className="credit-signin">
          <h2>Sign in as a lender officer</h2>
          <p>
            Your account identifies who records each decision. Local accounts are provisioned by the
            project operator.
          </p>
          <form onSubmit={(e) => void signIn(e)}>
            <label>
              Officer account
              <input
                autoComplete="username"
                disabled={!ready}
                required
                value={account}
                onChange={(e) => setAccount(e.target.value)}
              />
            </label>
            <label>
              Password
              <input
                type="password"
                autoComplete="current-password"
                disabled={!ready}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
            {error && (
              <p role="alert" className="credit-error">
                {error}
              </p>
            )}
            <button className="credit-primary" disabled={busy || !ready}>
              {!ready ? "Loading sign-in…" : busy ? "Signing in…" : "Sign in"}
            </button>
          </form>
        </section>
      ) : (
        <>
          <div className="credit-scope">
            <strong>{officer.lender_id}</strong>
            <span>Officer {officer.officer_id}</span>
            <button
              disabled={busy}
              onClick={() => void refresh().catch((err) => setError(err.message))}
            >
              <RefreshCw size={15} /> Refresh
            </button>
          </div>
          {error && (
            <p className="credit-error" role="alert">
              {error} Reconnect and refresh, or sign in again if your session expired.
            </p>
          )}
          <p className="credit-boundary">
            Review evidence before authorizing credit. Supplier payment is verified before
            collection.
          </p>
          <div className="credit-counts" aria-label="Applications in this lender workspace">
            {state ? (
              Object.entries(state.counts).map(([status, count]) => (
                <span key={status}>
                  <strong>{count.toLocaleString()}</strong>{" "}
                  {status.toLowerCase().replaceAll("_", " ")}
                </span>
              ))
            ) : (
              <span>Loading applications…</span>
            )}
          </div>
          <div className="credit-tools">
            <details className="credit-new">
              <summary>Create an application</summary>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  setBusy(true);
                  setError("");
                  void api<{ id: string }>("/applications", officer, {
                    farmer_id: farmer,
                    input_farmer_id: inputFarmer,
                    provenance,
                    request_id: requestId,
                  })
                    .then(async (result) => {
                      setSelected(result.id);
                      setFilter("PENDING");
                      setQuery("");
                      setFarmer("");
                      setInputFarmer("");
                      setRequestId(crypto.randomUUID());
                      await refresh();
                    })
                    .catch((err) => setError(err.message))
                    .finally(() => setBusy(false));
                }}
              >
                <div className="credit-form-grid">
                  <label>
                    Credit-module farmer ID
                    <input required value={farmer} onChange={(e) => setFarmer(e.target.value)} />
                  </label>
                  <label>
                    Input-finance farmer ID
                    <input
                      required
                      value={inputFarmer}
                      onChange={(e) => setInputFarmer(e.target.value)}
                    />
                  </label>
                  <label>
                    Evidence provenance
                    <select value={provenance} onChange={(e) => setProvenance(e.target.value)}>
                      <option value="synthetic">Synthetic</option>
                      <option value="real">Real</option>
                      <option value="mixed">Mixed</option>
                      <option value="unavailable">Unavailable</option>
                    </select>
                  </label>
                </div>
                <p>Confirm both IDs against the receiving lender’s mapping before approving.</p>
                <button disabled={busy}>{busy ? "Creating…" : "Create application"}</button>
              </form>
            </details>
            <ReplayRegistry key={officer.officer_id} officer={officer} />
          </div>
          <div className="credit-layout" data-mobile-case={mobileCase}>
            <section className="credit-queue" aria-labelledby="queue-heading">
              <h2 id="queue-heading">Applications</h2>
              <label>
                Find a farmer
                <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} />
              </label>
              <label>
                Decision status
                <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                  <option value="">All statuses</option>
                  {["PENDING", "APPROVED", "REJECTED", "REVOKED", "REPLAY_APPROVED"].map((s) => (
                    <option key={s} value={s}>
                      {s.toLowerCase().replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </label>
              <p>Showing up to 100 matching applications.</p>
              <div className="credit-queue-list">
                {state?.applications.map((a) => (
                  <button
                    key={a.id}
                    aria-pressed={a.id === selected}
                    onClick={() => {
                      setSelected(a.id);
                      setMobileCase(true);
                    }}
                  >
                    <strong>{a.farmer_id}</strong>
                    <span>
                      {a.status.toLowerCase().replaceAll("_", " ")} · {a.provenance}
                    </span>
                    <small>{new Date(a.created_at).toLocaleDateString()}</small>
                  </button>
                ))}
              </div>
              {state?.applications.length === 0 && (
                <p>No matching applications. Change the search or create an application.</p>
              )}
            </section>
            <div className="credit-selection">
              <button className="credit-back" onClick={() => setMobileCase(false)}>
                Back to applications
              </button>
              {application ? (
                <CaseReview
                  key={application.id}
                  application={application}
                  officer={officer}
                  decision={decision}
                  deliveries={state?.deliveries.filter((d) => d.decision_id === decision?.id) || []}
                  inputUrl={state?.input_finance_url || "http://127.0.0.1:5173/"}
                  refresh={refresh}
                />
              ) : (
                <section className="credit-case credit-empty">
                  <h2>Select an application to review</h2>
                  <p>
                    Open a farmer’s case to inspect graph evidence, record a lender decision, and
                    follow its delivery to input finance.
                  </p>
                </section>
              )}
            </div>
          </div>
        </>
      )}
    </main>
  );
}
