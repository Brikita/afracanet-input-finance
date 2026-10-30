import type { Session } from '../domain/models'
import { Brand } from '../components/Brand'
import {
  ChevronDown,
  Clock3,
  CreditCard,
  Leaf,
  LogOut,
  MessageSquare,
  Package,
  ShoppingBasket,
  Users,
} from 'lucide-react'

type Props = {
  session: Session
  tab: string
  setTab: (tab: string) => void
  choices: { id: string; name: string }[]
  busy: boolean
  signIn: (id: string) => Promise<void>
  signOut: () => Promise<void>
}
export function WorkspaceHeader({
  session,
  tab,
  setTab,
  choices,
  busy,
  signIn,
  signOut,
}: Props) {
  const role = session.role
  const nav =
    role === 'farmer'
      ? [
          { id: 'overview', label: 'My inputs', icon: ShoppingBasket },
          { id: 'orders', label: 'My requests', icon: Clock3 },
          { id: 'sms', label: 'SMS updates', icon: MessageSquare },
        ]
      : [
          { id: 'overview', label: 'Overview', icon: Leaf },
          { id: 'orders', label: 'Transactions', icon: CreditCard },
          {
            id: 'people',
            label: role === 'lender' ? 'Credit allocations' : 'Inventory',
            icon: role === 'lender' ? Users : Package,
          },
        ]
  return (
    <header className="workspace-header">
      <Brand light />
      <nav aria-label="Workspace navigation">
        {nav.map((n) => (
          <button
            key={n.id}
            className={tab === n.id ? 'workspace-nav active' : 'workspace-nav'}
            aria-current={tab === n.id ? 'page' : undefined}
            onClick={() => setTab(n.id)}
          >
            <n.icon size={17} />
            <span>{n.label}</span>
          </button>
        ))}
      </nav>
      <div className="workspace-account">
        <div className="persona-select">
          <label htmlFor="persona">View as</label>
          <select
            id="persona"
            value={session.subject}
            disabled={busy}
            onChange={(e) => void signIn(e.target.value)}
          >
            {choices.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <ChevronDown size={14} />
        </div>
        <button
          className="signout-button"
          aria-label="Sign out of workspace"
          onClick={() => void signOut()}
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  )
}
