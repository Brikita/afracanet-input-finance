import { useState } from "react";
import { api, type Officer } from "./api";

type Registry = {
  source_kind: string;
  nodes_by_kind: Record<string, number>;
  loan_history: {
    currency: string;
    principal_minor: number;
    repaid_minor: number;
    outstanding_minor: number;
  };
  replay_inventory: {
    products: number;
    stock_units: number;
    reserved_units: number;
    fulfilled_units: number;
  };
  manifest_sha256: string;
  boundary: string;
};
export function ReplayRegistry({ officer }: { officer: Officer }) {
  const [registry, setRegistry] = useState<Registry | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function load() {
    setBusy(true);
    setError("");
    try {
      setRegistry(await api<Registry>("/dataset", officer));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const money = (minor: number) =>
    new Intl.NumberFormat("en-KE", { style: "currency", currency: "KES" }).format(minor / 100);
  return (
    <details className="credit-new">
      <summary>Dataset provenance and replay balances</summary>
      <p>
        Inspect the isolated registry for {officer.lender_id}. These are synthetic histories,
        separate from active credit and payment.
      </p>
      <button disabled={busy} onClick={() => void load()}>
        {busy ? "Reading registry…" : "Read registry balances"}
      </button>
      {error && (
        <p role="alert" className="credit-error">
          {error}
        </p>
      )}
      {registry && (
        <>
          <dl className="credit-facts">
            <div>
              <dt>Synthetic farmers</dt>
              <dd>{(registry.nodes_by_kind.Farmer || 0).toLocaleString()}</dd>
            </div>
            <div>
              <dt>Historical ledger entries</dt>
              <dd>{(registry.nodes_by_kind.LedgerEvent || 0).toLocaleString()}</dd>
            </div>
            <div>
              <dt>Historical KES loan principal</dt>
              <dd>{money(registry.loan_history.principal_minor)}</dd>
            </div>
            <div>
              <dt>Repaid in authored history</dt>
              <dd>{money(registry.loan_history.repaid_minor)}</dd>
            </div>
            <div>
              <dt>Outstanding in authored history</dt>
              <dd>{money(registry.loan_history.outstanding_minor)}</dd>
            </div>
            <div>
              <dt>Replay inventory</dt>
              <dd>
                {registry.replay_inventory.products} products ·{" "}
                {registry.replay_inventory.stock_units.toLocaleString()} units in stock ·{" "}
                {registry.replay_inventory.reserved_units.toLocaleString()} reserved
              </dd>
            </div>
          </dl>
          <p>{registry.boundary}</p>
          <details>
            <summary>Dataset checksum</summary>
            <p style={{ overflowWrap: "anywhere" }}>{registry.manifest_sha256}</p>
          </details>
        </>
      )}
    </details>
  );
}
