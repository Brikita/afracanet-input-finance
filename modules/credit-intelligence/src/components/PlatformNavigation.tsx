import { Link } from "@tanstack/react-router";
import { Sprout, ClipboardList, History, ArrowUpRight } from "lucide-react";

const navItems = [
  { to: "/", label: "Lender review", icon: ClipboardList },
  { to: "/history", label: "Decision history", icon: History },
] as const;

export function PlatformNavigation() {
  return (
    <header className="platform-navigation">
      <a href="/" className="platform-brand">
        <Sprout size={24} aria-hidden="true" />
        <span>
          <strong>AFRACANet AI</strong>
          <small>Credit intelligence</small>
        </span>
      </a>

      <nav aria-label="Credit workspace navigation">
        {navItems.map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to} activeOptions={{ exact: to === "/" }}>
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
        <a href={import.meta.env.VITE_INPUT_FINANCE_URL || "http://127.0.0.1:5173/"}>
          <ArrowUpRight size={18} />
          Input finance
        </a>
      </nav>
      <span className="platform-environment">Development workspace</span>
    </header>
  );
}
