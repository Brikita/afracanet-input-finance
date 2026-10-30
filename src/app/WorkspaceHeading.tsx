import type { State } from '../domain/models'
import { ArrowDownToLine, ShieldCheck } from 'lucide-react'

export function ModeBanner({ state }: { state: State }) {
  return (
    <div className="mode-banner">
      <ShieldCheck size={16} />
      <span>
        {state.payment_mode === 'mock'
          ? 'Simulated payments · no money moves'
          : 'PayPal sandbox · test funds only'}
        <span className="assistant-disclosure">
          <span className="mode-divider">|</span>
          {state.ai_mode === 'demo'
            ? 'Demo request parser · no AI model connected'
            : 'Gemini request assistant'}
        </span>
      </span>
      <small>USD illustrative prices</small>
    </div>
  )
}
export function WorkspaceHeading({
  state,
  tab,
  download,
}: {
  state: State
  tab: string
  download: () => Promise<void>
}) {
  const role = state.user.role
  const awaitingApproval = state.orders.filter(
    (o) => o.status === 'REQUESTED',
  ).length
  return (
    <div className="page-title">
      <div>
        <h1>
          {tab === 'sms'
            ? 'SMS updates'
            : role === 'farmer'
              ? 'From your credit to your farm.'
              : tab === 'people'
                ? role === 'lender'
                  ? 'Approved credit allocations'
                  : 'Your input inventory'
                : tab === 'orders'
                  ? 'Transactions'
                  : 'Keep credit moving.'}
        </h1>
        <p>
          {role === 'farmer'
            ? 'Choose your inputs. Your lender pays the agro-dealer directly.'
            : role === 'lender' && tab === 'overview'
              ? awaitingApproval
                ? `${awaitingApproval} ${awaitingApproval === 1 ? 'request awaits' : 'requests await'} lender approval. Review the next step in each case.`
                : 'No requests are waiting for lender approval.'
              : 'Coordinate approved credit, supplier payments, and farmer collection.'}
        </p>
      </div>
      {role === 'lender' && (
        <button className="button secondary" onClick={() => void download()}>
          <ArrowDownToLine size={16} />
          <span className="export-label">Export records</span>
        </button>
      )}
    </div>
  )
}
