import { Link } from "@tanstack/react-router";
import { Sprout, Home, List } from "lucide-react";

const navItems = [
  { to: "/", label: "Underwriting Dashboard", icon: Home },
  { to: "/history", label: "Transaction Ledger", icon: List },
] as const;

export function AppSidebar() {
  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-border bg-card md:flex">
      <div className="flex items-center gap-2.5 border-b border-border px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
          <Sprout className="h-5 w-5 text-primary-foreground" />
        </div>
        <div className="leading-tight">
          <span className="block text-base font-extrabold tracking-tight text-foreground">
            AFRACANet <span className="text-primary">AI</span>
          </span>
          <span className="block text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            SACCO Platform
          </span>
        </div>
      </div>

      <nav className="flex flex-col gap-1 p-3">
        {navItems.map(({ to, label, icon: Icon }) => (
          <Link
            key={to}
            to={to}
            activeOptions={{ exact: to === "/" }}
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-muted-foreground transition hover:bg-secondary hover:text-foreground data-[status=active]:bg-primary data-[status=active]:text-primary-foreground"
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
