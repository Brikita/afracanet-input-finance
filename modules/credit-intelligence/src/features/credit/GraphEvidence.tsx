import { useState } from "react";
import { ArrowUpRight, X } from "lucide-react";
import { api, type Context, type Officer } from "./api";

type RecordDetail = {
  id: string;
  relationship: string;
  source_kind: string;
  properties: Record<string, unknown>;
};
const words = (value: string) => value.toLowerCase().replaceAll("_", " ");
const money = (minor = 0) =>
  new Intl.NumberFormat("en-KE", { style: "currency", currency: "KES" }).format(minor / 100);

export function GraphEvidence({
  context,
  applicationId,
  officer,
  busy,
  filter,
  onFilter,
}: {
  context: Context;
  applicationId: string;
  officer: Officer;
  busy: boolean;
  filter: string;
  onFilter: (relationship: string) => void;
}) {
  const [record, setRecord] = useState<RecordDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [allTypes, setAllTypes] = useState(false);
  async function inspect(id: string) {
    setLoading(true);
    setError("");
    setRecord(null);
    try {
      setRecord(
        await api<RecordDetail>(
          `/applications/${applicationId}/evidence/${encodeURIComponent(id)}`,
          officer,
        ),
      );
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }
  const history = context.repayment_history;
  const types = context.relationship_types || [];
  const maximum = Math.max(1, ...types.map((row) => row.count));
  return (
    <div className="graph-evidence">
      <div className="evidence-heading">
        <div>
          <h4>{context.profile.display_name}</h4>
          <p>
            {context.relationship_count.toLocaleString()} graph relationships · {context.provenance}
          </p>
        </div>
        <span className="credit-status">Retrieved evidence</span>
      </div>
      <p>{context.explanation}</p>
      <div className="evidence-overview">
        <section aria-labelledby="connections-heading">
          <h4 id="connections-heading">Connections to inspect</h4>
          <p>Choose a connection to retrieve its records.</p>
          <button
            className="evidence-reset"
            disabled={busy}
            onClick={() => onFilter("")}
            aria-pressed={!filter}
          >
            All connections
          </button>
          <div className="evidence-connections">
            {(allTypes ? types : types.slice(0, 4)).map((row) => (
              <button
                key={row.relationship}
                disabled={busy}
                className="evidence-connection"
                aria-pressed={filter === row.relationship}
                onClick={() => {
                  setRecord(null);
                  onFilter(row.relationship);
                }}
              >
                <span>{words(row.relationship)}</span>
                <strong>{row.count.toLocaleString()}</strong>
                <span className="evidence-bar" aria-hidden="true">
                  <i style={{ width: `${(row.count / maximum) * 100}%` }} />
                </span>
              </button>
            ))}
          </div>
          {types.length > 4 && (
            <button className="evidence-reset" onClick={() => setAllTypes(!allTypes)}>
              {allTypes
                ? "Show fewer connections"
                : `Show ${types.length - 4} more connection types`}
            </button>
          )}
        </section>
        <section aria-labelledby="history-evidence-heading">
          <h4 id="history-evidence-heading">Authored loan history</h4>
          {history?.available ? (
            <>
              <dl className="evidence-balances">
                <div>
                  <dt>Historical principal</dt>
                  <dd>{money(history.principal_minor)}</dd>
                </div>
                <div>
                  <dt>Repaid in the dataset</dt>
                  <dd>{money(history.repaid_minor)}</dd>
                </div>
                <div>
                  <dt>Outstanding in the dataset</dt>
                  <dd>{money(history.outstanding_minor)}</dd>
                </div>
              </dl>
              <p>
                {history.loan_count} authored loans · KES. These are synthetic histories, separate
                from active USD input credit.
              </p>
            </>
          ) : (
            <p>
              {history?.reason || "Repayment history is unavailable. No totals have been inferred."}
            </p>
          )}
        </section>
      </div>
      {context.public_weather_context.length > 0 && (
        <details className="credit-public-context">
          <summary>Public weather at a reference point</summary>
          <h4>Public weather at a reference point</h4>
          <p>
            {context.public_weather_context[0].reference_point} ·{" "}
            {context.public_weather_context.length} daily records ·{" "}
            {context.public_weather_context
              .reduce((total, row) => total + row.precipitation_mm, 0)
              .toFixed(1)}{" "}
            mm total precipitation
          </p>
          <p>{context.public_weather_context[0].limits}</p>
          <p>
            {context.public_weather_context[0].attribution}{" "}
            <a href="https://open-meteo.com/en/docs/historical-weather-api">Source documentation</a>{" "}
            · CC BY 4.0
          </p>
        </details>
      )}
      <div className="credit-table-wrap">
        <table>
          <caption>Up to 40 connected records{filter ? ` · ${words(filter)}` : ""}</caption>
          <thead>
            <tr>
              <th>Record</th>
              <th>Connection</th>
            </tr>
          </thead>
          <tbody>
            {context.neighbors.map((row, i) => (
              <tr key={row.id + i}>
                <td>
                  <button
                    className="evidence-record-link"
                    disabled={loading}
                    onClick={() => void inspect(row.id)}
                  >
                    {row.id}
                    <ArrowUpRight size={14} aria-hidden="true" />
                  </button>
                </td>
                <td>{words(row.relationship)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {context.neighbors.length === 0 && <p>No matching connected records were retrieved.</p>}
      </div>
      {loading && <p role="status">Reading the connected source record…</p>}
      {error && (
        <p role="alert" className="credit-error">
          {error}
        </p>
      )}
      {record && (
        <section className="evidence-record" aria-label="Connected source record">
          <header>
            <h4>{record.id}</h4>
            <button aria-label="Close source record" onClick={() => setRecord(null)}>
              <X size={16} />
            </button>
          </header>
          <p>
            {words(record.relationship)} · {record.source_kind}
          </p>
          <dl className="credit-facts">
            {Object.entries(record.properties).map(([key, value]) => (
              <div key={key}>
                <dt>{words(key)}</dt>
                <dd>{typeof value === "object" ? JSON.stringify(value) : String(value)}</dd>
              </div>
            ))}
          </dl>
        </section>
      )}
    </div>
  );
}
