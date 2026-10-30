import type { State } from '../domain/models'
import { money } from '../lib/format'
import { availableCredit } from '../domain/credit'
import { Stat } from './Stat'
export function OverviewMetrics({ state }: { state: State }) {
  const role = state.user.role
  const available = state.farmers.reduce(
    (sum, f) => sum + availableCredit(f),
    0,
  )
  const funded = state.orders.filter((o) =>
    ['READY_FOR_COLLECTION', 'COLLECTED'].includes(o.status),
  )
  const totalFunded = funded.reduce((sum, o) => sum + o.amount_cents, 0)
  const pending = state.orders.filter((o) =>
    [
      'REQUESTED',
      'APPROVED',
      'INVOICING',
      'AWAITING_PAYMENT',
      'PAYMENT_REVIEW',
    ].includes(o.status),
  )
  const collected = state.orders.filter((o) => o.status === 'COLLECTED')
  return (
    <section className="stats-grid">
      <Stat
        label={
          role === 'supplier' ? 'Confirmed payments' : 'Available input credit'
        }
        value={money(role === 'supplier' ? totalFunded : available)}
        note={
          role === 'farmer'
            ? 'After reservations and payments'
            : 'Illustrative USD allocations'
        }
      />
      <Stat
        label="In progress"
        value={String(pending.length)}
        note="Requests requiring the next step"
      />
      <Stat
        label="Ready for collection"
        value={String(funded.length - collected.length)}
        note="Payment confirmed, handover pending"
      />
      <Stat
        label="Collected orders"
        value={String(collected.length)}
        note="Dealer recorded farmer collection"
      />
    </section>
  )
}
