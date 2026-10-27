import { useRef, useState } from 'react'
import {
  ArrowRight,
  ArrowUpRight,
  CircleAlert,
  CircleCheck,
  CreditCard,
  FileText,
  MapPin,
  Package,
  Search,
  Wallet,
} from 'lucide-react'
import type { Order, State } from '../../domain/models'
import { money } from '../../lib/format'
import { Status } from '../../components/Status'
import { CreditAllocation } from './CreditAllocation'
import { labels } from '../../domain/orderStatus'
import { allocationActive, availableCredit } from '../../domain/credit'

type Props = {
  state: State
  busy: boolean
  onOpen: (order: Order) => void
  onAction: (path: string) => Promise<void>
  onAllocations: () => void
  onFarmer: () => void
}

function OrderPath({ order }: { order: Order }) {
  const status = order.status
  const approved = !['REQUESTED', 'CANCELLED'].includes(status)
  const paid = ['READY_FOR_COLLECTION', 'COLLECTED'].includes(status)
  const collected = status === 'COLLECTED'
  const stages = [
    {
      label: 'Request',
      detail: status === 'CANCELLED' ? 'Cancelled' : 'Received',
      icon: FileText,
      done: true,
    },
    {
      label: 'Order approval',
      detail: approved ? 'Approved' : 'Lender reviews',
      icon: CircleCheck,
      done: approved,
    },
    {
      label: 'Supplier payment',
      detail: paid
        ? order.payment_mode === 'mock'
          ? 'Simulated'
          : 'Verified in sandbox'
        : 'Not verified',
      icon: CreditCard,
      done: paid,
    },
    {
      label: 'Collection',
      detail: collected
        ? 'Handover recorded'
        : paid
          ? 'Dealer acts next'
          : 'After verified payment',
      icon: Package,
      done: collected,
    },
  ]
  return (
    <ol className="order-path" aria-label="Request to collection progress">
      {stages.map((stage) => (
        <li key={stage.label} className={stage.done ? 'complete' : ''}>
          <span className="path-icon">
            <stage.icon size={16} />
          </span>
          <div>
            <strong>{stage.label}</strong>
            <small>{stage.detail}</small>
          </div>
        </li>
      ))}
    </ol>
  )
}

export function LenderWorkspace({
  state,
  busy,
  onOpen,
  onAction,
  onAllocations,
  onFarmer,
}: Props) {
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('all')
  const [picked, setPicked] = useState<number | null>(null)
  const detailRef = useRef<HTMLElement>(null)
  const farmers = new Map(state.farmers.map((farmer) => [farmer.id, farmer]))
  const filtered = state.orders.filter(
    (order) =>
      (filter === 'all' || order.status === filter) &&
      `${order.reference} ${farmers.get(order.farmer_id)?.name ?? order.farmer_id} ${labels[order.status]}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  )
  const current = filtered.find((order) => order.id === picked) ?? filtered[0]
  const farmer = current && farmers.get(current.farmer_id)
  const held = current?.issues.some((issue) => !issue.resolved_at)
  const available = state.farmers.reduce(
    (sum, farmer) => sum + availableCredit(farmer),
    0,
  )
  const reserved = state.farmers.reduce(
    (sum, farmer) => sum + (farmer.reserved_cents ?? 0),
    0,
  )
  const paid = state.farmers.reduce(
    (sum, farmer) => sum + (farmer.spent_cents ?? 0),
    0,
  )

  function choose(order: Order) {
    setPicked(order.id)
    if (window.matchMedia('(max-width: 960px)').matches) {
      requestAnimationFrame(() => {
        detailRef.current?.focus({ preventScroll: true })
        detailRef.current?.scrollIntoView({
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)')
            .matches
            ? 'instant'
            : 'smooth',
          block: 'start',
        })
      })
    }
  }

  return (
    <>
      <dl className="workspace-metrics">
        {[
          [
            'Available allocation',
            money(available),
            'After reservations and payments',
          ],
          [
            'Reserved for inputs',
            money(reserved),
            'Awaiting the next transaction step',
          ],
          [
            'Paid to suppliers',
            money(paid),
            state.payment_mode === 'mock'
              ? 'Simulated payment records'
              : 'PayPal sandbox records',
          ],
          [
            'Farmer allocations',
            String(state.farmers.length),
            'Within your lender workspace',
          ],
        ].map(([label, value, note]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
            <small>{note}</small>
          </div>
        ))}
      </dl>
      <div className="lender-layout">
        <div className="lender-main">
          <CreditAllocation farmers={state.farmers} />
          <section className="case-queue" aria-labelledby="queue-title">
            <div className="block-heading">
              <h2 id="queue-title">
                Input requests{' '}
                <span className="record-count">{filtered.length}</span>
              </h2>
              <span>{state.orders.length} total</span>
            </div>
            <div className="queue-controls">
              <div className="search-field">
                <Search size={17} />
                <input
                  aria-label="Search input requests"
                  placeholder="Farmer or reference…"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>
              <label className="queue-filter">
                <span className="sr-only">Filter requests by status</span>
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option value="all">All statuses</option>
                  {Object.entries(labels).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            {filtered.length ? (
              <div className="table-scroll">
                <table className="request-table">
                  <thead>
                    <tr>
                      <th>Farmer / request</th>
                      <th>Next step</th>
                      <th className="numeric">Amount</th>
                      <th>
                        <span className="sr-only">Record</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((order) => (
                      <tr
                        key={order.id}
                        className={
                          current?.id === order.id ? 'selected-case' : ''
                        }
                      >
                        <td>
                          <button
                            className="case-select"
                            aria-label={`Select ${order.reference}`}
                            aria-pressed={current?.id === order.id}
                            onClick={() => choose(order)}
                          >
                            <span className="person-initial" aria-hidden="true">
                              {(farmers.get(order.farmer_id)?.name ?? 'F')
                                .split(' ')
                                .slice(0, 2)
                                .map((part) => part[0])
                                .join('')}
                            </span>
                            <span>
                              <strong>
                                {farmers.get(order.farmer_id)?.name ??
                                  order.farmer_id}
                              </strong>
                              <small>{order.reference}</small>
                            </span>
                          </button>
                        </td>
                        <td>
                          <Status status={order.status} />
                          {order.issues.some((issue) => !issue.resolved_at) && (
                            <small className="issue-flag">
                              Issue requires review
                            </small>
                          )}
                        </td>
                        <td className="numeric">
                          <strong>{money(order.amount_cents)}</strong>
                        </td>
                        <td>
                          <button
                            className="text-button"
                            aria-label={`Open ${order.reference}`}
                            onClick={() => onOpen(order)}
                          >
                            Details
                            <ArrowUpRight size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="queue-empty">
                <FileText size={26} />
                <h3>
                  {state.orders.length
                    ? 'No matching requests'
                    : 'Your next request starts here'}
                </h3>
                <p>
                  {state.orders.length
                    ? 'Change the status or search to see more requests.'
                    : 'Approved farmers can choose inputs. Their requests will appear here for your review.'}
                </p>
                {!state.orders.length && (
                  <button className="button secondary" onClick={onFarmer}>
                    Explore farmer experience <ArrowRight size={16} />
                  </button>
                )}
              </div>
            )}
            <div className="queue-caption">
              {filtered.length} {filtered.length === 1 ? 'request' : 'requests'}{' '}
              in this view · Amounts in illustrative USD
            </div>
          </section>
        </div>
        <section
          className="selected-record"
          ref={detailRef}
          aria-labelledby="selected-title"
          tabIndex={-1}
        >
          {current ? (
            <>
              <div className="block-heading">
                <span>Selected request</span>
                <button className="text-button" onClick={() => onOpen(current)}>
                  Full record
                  <ArrowUpRight size={15} />
                </button>
              </div>
              <div className="record-person">
                <span className="person-initial large" aria-hidden="true">
                  {(farmer?.name ?? 'F')
                    .split(' ')
                    .slice(0, 2)
                    .map((part) => part[0])
                    .join('')}
                </span>
                <div>
                  <h2 id="selected-title">
                    {farmer?.name ?? current.farmer_id}
                  </h2>
                  <p>
                    <MapPin size={13} />
                    {farmer?.location ?? 'Location unavailable'}
                  </p>
                </div>
              </div>
              <div className="record-total">
                <strong>{money(current.amount_cents)}</strong>
                <Status status={current.status} />
              </div>
              <OrderPath order={current} />
              <div className="record-products">
                {current.items.map((item) => (
                  <div key={item.product_id}>
                    <Package size={20} />
                    <span>
                      <strong>{item.name}</strong>
                      <small>
                        {item.quantity} × {item.unit}
                      </small>
                    </span>
                    <b>{money((item.price_cents ?? 0) * item.quantity)}</b>
                  </div>
                ))}
              </div>
              {farmer && (
                <dl className="record-balances">
                  <div>
                    <dt>Approved allocation</dt>
                    <dd>{money(farmer.limit_cents ?? 0)}</dd>
                  </div>
                  <div>
                    <dt>Available allocation</dt>
                    <dd>{money(availableCredit(farmer))}</dd>
                  </div>
                </dl>
              )}
              {held ? (
                <div className="record-help issue-hold">
                  <CircleAlert size={17} />
                  <span>
                    An open issue pauses this order. Review its details before
                    continuing.
                  </span>
                </div>
              ) : (
                <div className="record-help">
                  <FileText size={16} />
                  <span>
                    Credit assessment evidence
                    <small>Upstream application is not connected.</small>
                  </span>
                </div>
              )}
              {held ? (
                <button
                  className="button primary full"
                  onClick={() => onOpen(current)}
                >
                  Review order issue
                  <ArrowRight size={16} />
                </button>
              ) : current.status === 'REQUESTED' &&
                farmer &&
                !allocationActive(farmer) ? (
                <>
                  <p className="action-note">
                    Allocation expired or revoked. Record a new lender decision
                    before approval or invoicing.
                  </p>
                  <button
                    className="button secondary full"
                    onClick={onAllocations}
                  >
                    Review credit allocation
                  </button>
                </>
              ) : current.status === 'REQUESTED' ? (
                <>
                  <button
                    className="button primary full"
                    disabled={busy}
                    onClick={() =>
                      void onAction(`/orders/${current.id}/approve`)
                    }
                  >
                    Approve input order
                    <CircleCheck size={17} />
                  </button>
                  <p className="action-note">
                    The dealer can prepare an invoice after approval.
                  </p>
                </>
              ) : current.status === 'AWAITING_PAYMENT' &&
                current.payment_mode === 'mock' ? (
                <button
                  className="button primary full"
                  disabled={busy}
                  onClick={() =>
                    void onAction(`/orders/${current.id}/demo-pay`)
                  }
                >
                  Simulate lender payment
                  <CreditCard size={17} />
                </button>
              ) : current.status === 'AWAITING_PAYMENT' &&
                current.payment_url ? (
                <a
                  className="button primary full"
                  href={current.payment_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Pay in PayPal sandbox
                  <ArrowUpRight size={17} />
                </a>
              ) : (
                <button
                  className="button secondary full"
                  onClick={() => onOpen(current)}
                >
                  Review transaction
                  <ArrowRight size={16} />
                </button>
              )}
              {current.payment_mode === 'mock' && (
                <p className="action-note">Demonstration · no money moves</p>
              )}
            </>
          ) : (
            <div className="record-placeholder">
              <Wallet size={30} />
              <h2 id="selected-title">Every request has a path</h2>
              <p>
                Select an input request to see its quote, progress, and next
                action.
              </p>
              <div className="placeholder-path">
                <span>
                  <FileText size={17} />
                  Request
                </span>
                <ArrowRight size={14} />
                <span>
                  <CreditCard size={17} />
                  Payment
                </span>
                <ArrowRight size={14} />
                <span>
                  <Package size={17} />
                  Collection
                </span>
              </div>
              <button className="button secondary" onClick={onAllocations}>
                Review credit allocations
                <ArrowRight size={16} />
              </button>
            </div>
          )}
        </section>
      </div>
    </>
  )
}
