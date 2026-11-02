import { useState } from "react";
import type { Analytics } from "./api";

export function GraphAnalytics({ value }: { value: Analytics }) {
  const [selected, setSelected] = useState(value.selected?.id || "");
  if (!value.available) return <p role="status">{value.reason}</p>;
  const all = value.nodes || [];
  const nodes = [...all]
    .sort((a, b) => Number(b.id === value.selected?.id) - Number(a.id === value.selected?.id))
    .slice(0, 60);
  const points = new Map(
    nodes.map((node, index) => [
      node.id,
      index === 0
        ? { x: 340, y: 205 }
        : {
            x: 340 + 255 * Math.cos((2 * Math.PI * (index - 1)) / Math.max(1, nodes.length - 1)),
            y: 205 + 155 * Math.sin((2 * Math.PI * (index - 1)) / Math.max(1, nodes.length - 1)),
          },
    ]),
  );
  const current = nodes.find((node) => node.id === selected) || nodes[0];
  return (
    <section className="credit-advice" aria-label="Computed graph analytics">
      <h4>Computed membership graph</h4>
      <p>
        PageRank and Louvain · GDS {value.gds_version} · synthetic history as of{" "}
        {value.as_of || "unavailable"}
      </p>
      <p>Scroll the diagram horizontally on a small screen, or use the node selector and table.</p>
      <div className="credit-table-wrap">
        <svg
          viewBox="0 0 680 410"
          role="img"
          aria-label="Computed membership connections. The node selector and table provide the same records."
          style={{ width: "100%", minWidth: 680, maxHeight: 410 }}
        >
          {(value.links || []).map((link, index) => {
            const a = points.get(link.source),
              b = points.get(link.target);
            return a && b ? (
              <line
                key={index}
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke="currentColor"
                opacity={link.source === current?.id || link.target === current?.id ? 0.7 : 0.16}
                strokeWidth={1.5}
              />
            ) : null;
          })}
          {nodes.map((node) => {
            const point = points.get(node.id)!;
            return (
              <g key={node.id}>
                <title>
                  {node.name} · community {node.community} · PageRank {node.page_rank.toFixed(4)}
                </title>
                <circle
                  cx={point.x}
                  cy={point.y}
                  r={node.id === current?.id ? 11 : 7}
                  fill={node.labels.includes("Farmer") ? "#25645d" : "#52779b"}
                />
                <text
                  x={point.x}
                  y={point.y + 24}
                  textAnchor="middle"
                  fill="currentColor"
                  fontSize="11"
                >
                  {node.id === value.selected?.id
                    ? "This farmer"
                    : node.id
                        .replace("farmer-synth-", "Farmer ")
                        .replace("SYN-SAVINGSGROUP-", "Chama ")
                        .replace("SYN-COOPERATIVE-", "Co-op ")}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <label>
        Inspect a computed node
        <select value={current?.id || ""} onChange={(event) => setSelected(event.target.value)}>
          {nodes.map((node) => (
            <option value={node.id} key={node.id}>
              {node.name}
            </option>
          ))}
        </select>
      </label>
      {current && (
        <dl className="credit-facts">
          <div>
            <dt>PageRank centrality</dt>
            <dd>{current.page_rank.toFixed(4)}</dd>
          </div>
          <div>
            <dt>Computed community</dt>
            <dd>{current.community}</dd>
          </div>
        </dl>
      )}
      <p>{value.limits_explanation}</p>
      <details>
        <summary>Run provenance and accessible node table</summary>
        <p>
          Run {value.id} · computed {value.created_at}
        </p>
        <p>Dataset SHA256: {value.manifest_sha256}</p>
        <div className="credit-table-wrap">
          <table>
            <caption>
              Computed nodes in this lender's projection; diagram limited to 60 nodes
            </caption>
            <thead>
              <tr>
                <th>Node</th>
                <th>PageRank</th>
                <th>Community</th>
              </tr>
            </thead>
            <tbody>
              {all.map((node) => (
                <tr key={node.id}>
                  <td>{node.name}</td>
                  <td>{node.page_rank.toFixed(4)}</td>
                  <td>{node.community}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}
