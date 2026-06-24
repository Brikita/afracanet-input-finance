import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { History, CheckCircle2, XCircle, ListFilter } from "lucide-react";

export const Route = createFileRoute("/history")({
  head: () => ({
    meta: [
      { title: "Transaction Ledger — AFRACANet AI" },
      {
        name: "description",
        content:
          "Audit trail of past SACCO loan disbursements with community trust scores and Masumi transaction hashes.",
      },
    ],
  }),
  component: Ledger,
});

type Status = "Approved" | "Rejected";

interface LedgerRow {
  date: string;
  farmerId: string;
  name: string;
  score: number;
  status: Status;
  txHash: string;
}

const ROWS: LedgerRow[] = [
  { date: "2026-06-22", farmerId: "28471936", name: "Wanjiru Kamau", score: 82, status: "Approved", txHash: "0x7Ab…3F9c" },
  { date: "2026-06-20", farmerId: "31204857", name: "Otieno Omondi", score: 76, status: "Approved", txHash: "0x4Cd…9B2a" },
  { date: "2026-06-18", farmerId: "29948120", name: "Achieng Nyong'o", score: 91, status: "Approved", txHash: "0xE1f…7D4b" },
  { date: "2026-06-15", farmerId: "27613094", name: "Mutua Kilonzo", score: 41, status: "Rejected", txHash: "" },
  { date: "2026-06-12", farmerId: "30527841", name: "Njeri Mwangi", score: 88, status: "Approved", txHash: "0x9Bc…2E5f" },
];

const FILTERS = ["All", "Approved", "Rejected"] as const;

function StatusBadge({ status }: { status: Status }) {
  if (status === "Approved") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-success/10 px-2.5 py-1 text-xs font-bold text-success">
        <CheckCircle2 className="h-3.5 w-3.5" /> Approved
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-bold text-destructive">
      <XCircle className="h-3.5 w-3.5" /> Rejected
    </span>
  );
}

function Ledger() {
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("All");

  const rows = useMemo(
    () => (filter === "All" ? ROWS : ROWS.filter((r) => r.status === filter)),
    [filter],
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
          <History className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-xl font-extrabold tracking-tight text-foreground">
            Past Loan Disbursements &amp; Audit Trail
          </h1>
          <p className="text-xs text-muted-foreground">
            Immutable record of all underwriting decisions and Masumi settlements.
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-border bg-card shadow-sm">
        <div className="flex items-center justify-between border-b border-border px-5 py-3.5">
          <h2 className="text-sm font-bold uppercase tracking-wide text-foreground">
            Transaction Ledger
          </h2>
          <div className="relative flex items-center">
            <ListFilter className="pointer-events-none absolute left-3 h-4 w-4 text-muted-foreground" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as (typeof FILTERS)[number])}
              className="appearance-none rounded-lg border border-input bg-background py-2 pl-9 pr-8 text-sm font-semibold text-foreground outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
            >
              {FILTERS.map((f) => (
                <option key={f} value={f}>
                  Status: {f}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border bg-secondary/40 text-xs uppercase tracking-wide text-muted-foreground">
                <th className="px-5 py-3 font-semibold">Date</th>
                <th className="px-5 py-3 font-semibold">Farmer ID</th>
                <th className="px-5 py-3 font-semibold">Name</th>
                <th className="px-5 py-3 font-semibold">Community Trust Score</th>
                <th className="px-5 py-3 font-semibold">Loan Status</th>
                <th className="px-5 py-3 font-semibold">Masumi Tx Hash</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.farmerId}
                  className="border-b border-border last:border-0 transition-colors hover:bg-secondary/30"
                >
                  <td className="px-5 py-3.5 text-muted-foreground">{r.date}</td>
                  <td className="px-5 py-3.5 font-mono text-xs font-semibold text-foreground">
                    {r.farmerId}
                  </td>
                  <td className="px-5 py-3.5 font-semibold text-foreground">{r.name}</td>
                  <td className="px-5 py-3.5">
                    <span className="font-bold text-foreground">{r.score}</span>
                    <span className="text-xs text-muted-foreground"> / 100</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={r.status} />
                  </td>
                  <td className="px-5 py-3.5">
                    {r.txHash ? (
                      <span className="font-mono text-xs font-semibold text-primary">
                        {r.txHash}
                      </span>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-10 text-center text-sm text-muted-foreground">
                    No transactions match this filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
