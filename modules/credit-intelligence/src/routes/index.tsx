import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  Sprout,
  Search,
  User,
  Users,
  Network,
  Sparkles,
  Wallet,
  Store,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  Ruler,
  Cake,
  Accessibility,
  TrendingUp,
} from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "AFRACANet AI — SACCO Loan Underwriting Dashboard" },
      {
        name: "description",
        content:
          "AI-powered loan underwriting dashboard for rural SACCO officers in Kenya. Community trust scoring, Chama data, and agentic voucher disbursement.",
      },
      { property: "og:title", content: "AFRACANet AI — SACCO Underwriting" },
      {
        property: "og:description",
        content:
          "Community trust scoring and AI underwriting for rural agricultural lending.",
      },
    ],
  }),
  component: Dashboard,
});

const TRUST_SCORE = 82;

function TrustGauge({ score }: { score: number }) {
  const radius = 80;
  const stroke = 14;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center">
      <svg height={radius * 2} width={radius * 2} className="-rotate-90">
        <circle
          stroke="var(--secondary)"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke="var(--success)"
          fill="transparent"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${circumference} ${circumference}`}
          style={{ strokeDashoffset: offset, transition: "stroke-dashoffset 1s ease" }}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-4xl font-extrabold text-foreground">{score}</span>
        <span className="text-xs font-medium text-muted-foreground">/ 100</span>
      </div>
    </div>
  );
}

function DetailRow({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof User;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between border-b border-border py-2.5 last:border-0">
      <span className="flex items-center gap-2 text-sm text-muted-foreground">
        <Icon className="h-4 w-4 text-primary" />
        {label}
      </span>
      <span className="text-sm font-semibold text-foreground">{value}</span>
    </div>
  );
}

function Dashboard() {
  const [nationalId, setNationalId] = useState("");

  return (
    <div className="min-h-screen bg-background">
      {/* Top navigation */}
      <header className="sticky top-0 z-10 border-b border-border bg-card/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
              <Sprout className="h-5 w-5 text-primary-foreground" />
            </div>
            <div className="leading-tight">
              <span className="block text-base font-extrabold tracking-tight text-foreground">
                AFRACANet <span className="text-primary">AI</span>
              </span>
              <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                SACCO Underwriting
              </span>
            </div>
          </div>

          <div className="relative ml-auto w-full max-w-md">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={nationalId}
              onChange={(e) => setNationalId(e.target.value)}
              placeholder="Enter Farmer National ID"
              className="w-full rounded-lg border border-input bg-background py-2 pl-9 pr-3 text-sm text-foreground outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
            />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* LEFT COLUMN — Data & Score */}
          <div className="flex flex-col gap-6">
            {/* Farmer profile */}
            <section className="rounded-xl border border-border bg-card p-5 shadow-sm">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent">
                  <User className="h-6 w-6 text-accent-foreground" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-foreground">Wanjiru Kamau</h2>
                  <p className="text-xs text-muted-foreground">National ID • 28471936</p>
                </div>
                <span className="ml-auto inline-flex items-center gap-1 rounded-full bg-success/10 px-2.5 py-1 text-xs font-semibold text-success">
                  <ShieldCheck className="h-3.5 w-3.5" /> Verified
                </span>
              </div>
              <DetailRow icon={User} label="Name" value="Wanjiru Kamau" />
              <DetailRow icon={Cake} label="Age" value="37 years" />
              <DetailRow icon={Users} label="Gender" value="Female" />
              <DetailRow icon={Accessibility} label="Disability Status" value="None" />
              <DetailRow icon={Ruler} label="Farm Size" value="2.4 acres" />
            </section>

            {/* Community Trust Score */}
            <section className="rounded-xl border border-border bg-card p-5 shadow-sm">
              <div className="mb-2 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-bold uppercase tracking-wide text-foreground">
                  Community Trust Score
                </h3>
              </div>
              <div className="flex flex-col items-center py-3">
                <TrustGauge score={TRUST_SCORE} />
                <p className="mt-3 text-center text-xs text-muted-foreground">
                  Strong standing across Chama repayments and cooperative activity.
                </p>
              </div>
            </section>

            {/* Neo4j graph placeholder */}
            <section className="rounded-xl border border-border bg-card p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <Network className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-bold uppercase tracking-wide text-foreground">
                  Neo4j Community Graph
                </h3>
              </div>
              <div className="flex h-56 items-center justify-center rounded-lg border-2 border-dashed border-border bg-secondary/40">
                <div className="flex flex-col items-center gap-2 text-muted-foreground">
                  <Network className="h-10 w-10 opacity-40" />
                  <span className="text-xs font-medium">
                    Network graph visualization
                  </span>
                </div>
              </div>
            </section>
          </div>

          {/* RIGHT COLUMN — AI Underwriting & Action */}
          <div className="flex flex-col gap-6">
            {/* Featherless AI rationale */}
            <section className="rounded-xl border border-border bg-card p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-bold uppercase tracking-wide text-foreground">
                  Featherless AI Underwriting Rationale
                </h3>
              </div>
              <span className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-success/10 px-3 py-1 text-xs font-bold text-success">
                <CheckCircle2 className="h-3.5 w-3.5" /> RECOMMENDED: APPROVE
              </span>
              <p className="text-sm leading-relaxed text-muted-foreground">
                The applicant demonstrates a consistent 24-month repayment record within
                the <span className="font-semibold text-foreground">Mwihoko Women's Chama</span>,
                contributing KES 1,200 monthly without default. Cross-referenced cooperative
                data from the <span className="font-semibold text-foreground">Kiambu Dairy
                Cooperative</span> confirms steady milk deliveries and reliable income flow.
                Her central position in the community trust graph — endorsed by 14 high-standing
                members — significantly de-risks this facility. Combined with a stable 2.4-acre
                holding, the model assesses a low probability of default and recommends approval
                of the requested agricultural input voucher.
              </p>
            </section>

            {/* Agentic fulfillment */}
            <section className="rounded-xl border border-border bg-card p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <Store className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-bold uppercase tracking-wide text-foreground">
                  Agentic Fulfillment
                </h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-lg bg-secondary/50 p-3">
                  <span className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Store className="h-4 w-4 text-primary" /> Target Agrovet
                  </span>
                  <span className="text-sm font-semibold text-foreground">
                    Githunguri Farm Supplies
                  </span>
                </div>
                <div className="flex items-center justify-between rounded-lg bg-secondary/50 p-3">
                  <span className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Wallet className="h-4 w-4 text-primary" /> Wallet Address
                  </span>
                  <span className="font-mono text-xs font-semibold text-foreground">
                    0x7Ab…3F9c
                  </span>
                </div>
              </div>
            </section>

            {/* Action buttons */}
            <div className="mt-auto flex flex-col gap-3 sm:flex-row">
              <button className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-primary px-5 py-4 text-base font-bold text-primary-foreground shadow-sm transition hover:opacity-90 active:scale-[0.99]">
                <CheckCircle2 className="h-5 w-5" />
                Approve &amp; Disburse Voucher (Masumi)
              </button>
              <button className="inline-flex items-center justify-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-5 py-4 text-base font-bold text-destructive transition hover:bg-destructive/20 active:scale-[0.99] sm:flex-none">
                <XCircle className="h-5 w-5" />
                Reject
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
