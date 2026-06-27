import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { toast } from "sonner";
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
  ArrowLeft,
  Clock,
  Banknote,
  Gauge,
  ChevronRight,
  Loader2,
  AlertTriangle,
} from "lucide-react";

const BACKEND_URL = "YOUR_NGROK_URL_HERE"; // I will update this string myself later.
const NGROK_HEADERS = {
  "Content-Type": "application/json",
  "ngrok-skip-browser-warning": "69420",
};

interface FarmerScore {
  farmerId: string;
  name: string;
  creditScore: number;
  aiMetrics: {
    pageRankTrustScore: number;
    degreeCentralityFootprint: number;
    louvainRiskCommunityId: number | string;
    knnSimilarEstablishedPeers: number;
  };
  traditionalMetrics: {
    simCardAgeDays: number;
  };
  environmentalRisk: string;
  evaluation: {
    decision: string;
    rationale: string;
  };
}

interface PendingApp {
  farmer_id: string;
  status: string;
  time: string;
}

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



type PreCheck = "High Confidence" | "Needs Review";

interface Application {
  date: string;
  name: string;
  nationalId: string;
  input: string;
  preCheck: PreCheck;
}

const APPLICATIONS: Application[] = [
  {
    date: "2026-06-24",
    name: "Wanjiru Kamau",
    nationalId: "28471936",
    input: "Seeds & Fertilizer",
    preCheck: "High Confidence",
  },
  {
    date: "2026-06-23",
    name: "Otieno Omondi",
    nationalId: "31902847",
    input: "Fertilizer",
    preCheck: "High Confidence",
  },
  {
    date: "2026-06-23",
    name: "Achieng Nyaga",
    nationalId: "29483017",
    input: "Maize Seeds",
    preCheck: "Needs Review",
  },
  {
    date: "2026-06-22",
    name: "Kipchoge Rotich",
    nationalId: "33019284",
    input: "Pesticides",
    preCheck: "High Confidence",
  },
  {
    date: "2026-06-22",
    name: "Mumbi Wairimu",
    nationalId: "27584012",
    input: "Dairy Feed",
    preCheck: "Needs Review",
  },
];

function TrustGauge({ score }: { score: number }) {
  const radius = 80;
  const stroke = 14;
  const normalizedRadius = radius - stroke / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  const color =
    score > 70 ? "var(--success)" : score >= 50 ? "#d97706" : "var(--destructive)";


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
          stroke={color}
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

function SummaryCard({
  icon: Icon,
  label,
  value,
  hint,
}: {
  icon: typeof Clock;
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
          {label}
        </span>
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent">
          <Icon className="h-5 w-5 text-accent-foreground" />
        </div>
      </div>
      <p className="mt-3 text-3xl font-extrabold tracking-tight text-foreground">{value}</p>
      <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
    </div>
  );
}

function PreCheckBadge({ status }: { status: PreCheck }) {
  const isHigh = status === "High Confidence";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${
        isHigh ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"
      }`}
    >
      {isHigh ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Sparkles className="h-3.5 w-3.5" />}
      {status}
    </span>
  );
}

function Dashboard() {
  const [nationalId, setNationalId] = useState("");
  const [showDetail, setShowDetail] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [farmer, setFarmer] = useState<FarmerScore | null>(null);
  const [selectedFarmerId, setSelectedFarmerId] = useState("");

  async function fetchFarmer(id: string) {
    const query = id.trim().toUpperCase();
    if (!query) return;
    setSelectedFarmerId(query);
    setLoading(true);
    setError(null);
    setShowDetail(true);
    setFarmer(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/evaluate`, {
        method: "POST",
        headers: NGROK_HEADERS,
        body: JSON.stringify({ farmer_id: query }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const data: FarmerScore = await res.json();
      setFarmer(data);
    } catch {
      setError("Farmer record not found. Try F-101, F-102, or F-103.");
    } finally {
      setLoading(false);
    }
  }

  function backToQueue() {
    setShowDetail(false);
    setError(null);
    setFarmer(null);
  }

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

          <form
            className="relative ml-auto w-full max-w-md"
            onSubmit={(e) => {
              e.preventDefault();
              fetchFarmer(nationalId);
            }}
          >
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={nationalId}
              onChange={(e) => setNationalId(e.target.value)}
              placeholder="Enter Farmer National ID"
              className="w-full rounded-lg border border-input bg-background py-2 pl-9 pr-3 text-sm text-foreground outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
            />
          </form>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        {showDetail ? (
          <DetailView
            onBack={backToQueue}
            loading={loading}
            error={error}
            farmer={farmer}
            selectedFarmerId={selectedFarmerId}
          />
        ) : (
          <OverviewQueue onOpen={(id) => fetchFarmer(id)} />
        )}
      </main>
    </div>
  );
}


function OverviewQueue({ onOpen }: { onOpen: (id: string) => void }) {
  const [pendingApps, setPendingApps] = useState<PendingApp[]>([]);

  useEffect(() => {
    let active = true;
    async function poll() {
      try {
        const res = await fetch(`${BACKEND_URL}/api/pending_loans`, {
          headers: NGROK_HEADERS,
        });
        if (!res.ok) return;
        const data = await res.json();
        if (active) setPendingApps(data.pending ?? []);
      } catch {
        /* backend offline — keep last known queue */
      }
    }
    poll();
    const interval = setInterval(poll, 3000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="flex flex-col gap-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <SummaryCard
          icon={Clock}
          label="Pending Approvals"
          value={String(pendingApps.length || 12)}
          hint="Awaiting officer review"
        />
        <SummaryCard
          icon={Banknote}
          label="Masumi Vouchers Disbursed (KES)"
          value="1.84M"
          hint="Across 214 approved facilities"
        />
        <SummaryCard
          icon={Gauge}
          label="Avg. Community Trust Score"
          value="78"
          hint="Across active applicant pool"
        />
      </div>

      {/* Live USSD queue */}
      {pendingApps.length > 0 && (
        <section className="rounded-xl border border-border bg-card shadow-sm">
          <div className="flex items-center gap-2 border-b border-border px-5 py-4">
            <Sparkles className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-bold uppercase tracking-wide text-foreground">
              Live USSD Applications
            </h3>
            <span className="ml-auto inline-flex items-center gap-1.5 rounded-full bg-success/10 px-2.5 py-1 text-xs font-semibold text-success">
              <span className="h-2 w-2 animate-pulse rounded-full bg-success" /> Live
            </span>
          </div>
          <div className="flex flex-col">
            {pendingApps.map((app, i) => (
              <button
                key={`${app.farmer_id}-${i}`}
                onClick={() => onOpen(app.farmer_id)}
                className="group flex items-center gap-3 border-b border-border px-5 py-3.5 text-left transition-colors last:border-0 hover:bg-secondary/50"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent">
                  <User className="h-4 w-4 text-accent-foreground" />
                </div>
                <div className="leading-tight">
                  <span className="block font-mono text-sm font-semibold text-foreground">
                    {app.farmer_id}
                  </span>
                  <span className="block text-xs text-muted-foreground">
                    {app.status} • {app.time}
                  </span>
                </div>
                <ChevronRight className="ml-auto h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-primary" />
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Pending applications table */}
      <section className="rounded-xl border border-border bg-card shadow-sm">
        <div className="flex items-center gap-2 border-b border-border px-5 py-4">
          <Users className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-bold uppercase tracking-wide text-foreground">
            Pending Loan Applications
          </h3>
        </div>
        <div className="relative w-full overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="px-5 py-3 font-medium text-muted-foreground">Date</th>
                <th className="px-5 py-3 font-medium text-muted-foreground">Farmer Name</th>
                <th className="px-5 py-3 font-medium text-muted-foreground">National ID</th>
                <th className="px-5 py-3 font-medium text-muted-foreground">Requested Input</th>
                <th className="px-5 py-3 font-medium text-muted-foreground">AI Pre-Check</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {APPLICATIONS.map((app) => (
                <tr
                  key={app.nationalId}
                  onClick={onOpen}
                  className="group cursor-pointer border-b border-border transition-colors last:border-0 hover:bg-secondary/50"
                >
                  <td className="px-5 py-3.5 text-muted-foreground">{app.date}</td>
                  <td className="px-5 py-3.5 font-semibold text-foreground">{app.name}</td>
                  <td className="px-5 py-3.5 font-mono text-xs text-muted-foreground">
                    {app.nationalId}
                  </td>
                  <td className="px-5 py-3.5 text-foreground">{app.input}</td>
                  <td className="px-5 py-3.5">
                    <PreCheckBadge status={app.preCheck} />
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <ChevronRight className="ml-auto h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-primary" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function DetailView({
  onBack,
  loading,
  error,
  farmer,
}: {
  onBack: () => void;
  loading: boolean;
  error: string | null;
  farmer: FarmerScore | null;
}) {
  const backButton = (
    <button
      onClick={onBack}
      className="mb-4 inline-flex items-center gap-1.5 text-sm font-semibold text-primary transition hover:opacity-80"
    >
      <ArrowLeft className="h-4 w-4" />
      Back to Queue
    </button>
  );

  if (loading) {
    return (
      <>
        {backButton}
        <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 rounded-xl border border-border bg-card p-10 shadow-sm">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="text-sm font-medium text-muted-foreground">
            Fetching farmer record from community graph…
          </p>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        {backButton}
        <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-10 text-center">
          <AlertTriangle className="h-10 w-10 text-destructive" />
          <p className="text-sm font-semibold text-destructive">{error}</p>
        </div>
      </>
    );
  }

  if (!farmer) return <>{backButton}</>;

  const m = farmer.metrics;
  const env = farmer.environmentalRisk;
  const rationale = `The applicant, ${farmer.name}, demonstrates a cooperative repayment score of ${m.cooperativeRepaymentScore} and a total cash flow of KES ${m.totalCashFlowKES}. The model factored in their SIM card age of ${m.simCardAgeDays} days and guaranteed Chama amount of KES ${m.guaranteedAmountKES}. Environmental overlay notes: ${env.status ?? "None"} (Penalty: ${env.penaltyScore}). Based on these graph metrics, the requested agricultural input voucher is conditionally recommended.`;

  return (
    <>
      {backButton}

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
                <h2 className="text-lg font-bold text-foreground">{farmer.name}</h2>
                <p className="text-xs text-muted-foreground">
                  National ID • {farmer.farmerId}
                </p>
              </div>
              <span className="ml-auto inline-flex items-center gap-1 rounded-full bg-success/10 px-2.5 py-1 text-xs font-semibold text-success">
                <ShieldCheck className="h-3.5 w-3.5" /> Verified
              </span>
            </div>
            <DetailRow icon={User} label="Name" value={farmer.name} />
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
              <TrustGauge score={farmer.creditScore} />
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
                <span className="text-xs font-medium">Network graph visualization</span>
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
            <p className="text-sm leading-relaxed text-muted-foreground">{rationale}</p>
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
    </>
  );
}

