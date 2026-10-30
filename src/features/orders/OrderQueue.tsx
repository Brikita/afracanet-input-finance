import { useState } from 'react'
import type { Order, State } from '../../domain/models'
import { Status } from '../../components/Status'
import { money } from '../../lib/format'
import { labels } from '../../domain/orderStatus'
import { ArrowRight, Search, Sprout } from 'lucide-react'

export function OrderQueue({
  state,
  onOpen,
  onFarmer,
}: {
  state: State
  onOpen: (order: Order) => void
  onFarmer: () => Promise<void>
}) {
  const role = state.user.role
  const [query, setQuery] = useState('')
  const filtered = state.orders.filter((o) =>
    (
      o.reference +
      ' ' +
      (state.farmers.find((f) => f.id === o.farmer_id)?.name ?? '') +
      ' ' +
      labels[o.status]
    )
      .toLowerCase()
      .includes(query.toLowerCase()),
  )
  return (
    <section className="panel transaction-panel">
      <div className="section-title">
        <div>
          <h2>
            {role === 'farmer' ? 'Your requests' : 'Transaction activity'}
          </h2>
          <p className="muted">
            A connected record from request to collection.
          </p>
        </div>
        <div className="search-field">
          <Search size={16} />
          <input
            aria-label="Search transactions"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search transactions…"
          />
        </div>
      </div>
      {filtered.length === 0 ? (
        <div className="empty-state">
          <span>
            <Sprout size={28} />
          </span>
          <h3>
            {state.orders.length
              ? 'No matching transactions'
              : 'The next growing season starts with a request.'}
          </h3>
          <p>
            {state.orders.length
              ? 'Try a different reference, farmer, or status.'
              : role === 'farmer'
                ? 'Choose inputs above to start your first request.'
                : 'Open the farmer experience to request inputs, then follow the journey here.'}
          </p>
          {!state.orders.length && role !== 'farmer' && (
            <button
              className="button secondary"
              onClick={() => void onFarmer()}
            >
              Explore farmer experience
              <ArrowRight size={16} />
            </button>
          )}
        </div>
      ) : (
        <div className="table-scroll">
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Order / farmer</th>
                <th>Inputs</th>
                <th>Amount</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {filtered.map((o) => (
                <tr key={o.id}>
                  <td>
                    <strong>{o.reference}</strong>
                    <small>
                      {state.farmers.find((f) => f.id === o.farmer_id)?.name ??
                        o.farmer_id}
                    </small>
                  </td>
                  <td>
                    {o.items.map((i) => i.quantity + ' × ' + i.name).join(', ')}
                    <small>{o.items.map((i) => i.unit).join(', ')}</small>
                  </td>
                  <td>
                    <strong>{money(o.amount_cents)}</strong>
                    <small>
                      {o.payment_mode === 'mock'
                        ? 'Simulated'
                        : 'PayPal sandbox'}
                    </small>
                  </td>
                  <td>
                    <Status status={o.status} />
                    {o.issues?.some((issue) => !issue.resolved_at) && (
                      <small className="issue-flag">
                        Issue requires review
                      </small>
                    )}
                  </td>
                  <td>
                    <button
                      className="text-button"
                      aria-label={'Open ' + o.reference}
                      onClick={() => {
                        onOpen(o)
                      }}
                    >
                      View
                      <ArrowRight size={15} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
