import { useCallback, useEffect, useRef, useState } from 'react'
import {
  ArrowDownToLine,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  CreditCard,
  Leaf,
  LogOut,
  MessageSquare,
  Package,
  Plus,
  Search,
  ShieldCheck,
  ShoppingBasket,
  Sparkles,
  Sprout,
  Tractor,
  Users,
  Wallet,
  X,
} from 'lucide-react'
import {
  ApprovalImport,
  CatalogueEditor,
} from '../features/management/Management'
import { Issues } from '../features/issues/Issues'
import { Notifications } from '../features/notifications/Notifications'

import type { Session, Line, Order, State, Event } from '../domain/models'
import { api } from '../lib/api'
import { money } from '../lib/format'
import { allocationActive, availableCredit } from '../domain/credit'
import { labels } from '../domain/orderStatus'
import { Brand } from '../components/Brand'
import { Status } from '../components/Status'
import { Stat } from '../components/Stat'
import { LenderWorkspace } from '../features/lender/LenderWorkspace'
import { Dialog } from '../components/Dialog'
import { ApprovalHandoff } from '../features/approvals/ApprovalHandoff'

const participants = [
  {
    id: 'lender-demo',
    name: 'Demo Agricultural SACCO',
    label: 'Lender workspace',
    detail: 'Approve, pay, and reconcile',
    icon: Wallet,
  },
  {
    id: 'farmer-amina',
    name: 'Amina Wanjiku',
    label: 'Farmer experience',
    detail: 'Request and collect inputs',
    icon: Tractor,
  },
  {
    id: 'supplier-demo',
    name: 'Demo Green Valley Agrovet',
    label: 'Agro-dealer workspace',
    detail: 'Invoice and fulfil orders',
    icon: Package,
  },
  {
    id: 'farmer-kiptoo',
    name: 'David Kiptoo',
    label: 'Second farmer',
    detail: 'Explore a different credit limit',
    icon: Users,
  },
]

export function App() {
  const [session, setSession] = useState<Session | null>(() => {
    try {
      return JSON.parse(sessionStorage.getItem('afracanet-session') ?? 'null')
    } catch {
      return null
    }
  })
  const [accessCode, setAccessCode] = useState('afracanet-demo')
  const activeToken = useRef(session?.token ?? null)
  const [state, setState] = useState<State | null>(null)
  const [persona, setPersona] = useState('lender-demo')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [tab, setTab] = useState('overview')
  const [selected, setSelected] = useState<number | null>(null)
  const [events, setEvents] = useState<Event[]>([])
  const [collectionCode, setCollectionCode] = useState('')
  const [recoveryInvoice, setRecoveryInvoice] = useState('')
  const [query, setQuery] = useState('')
  const [text, setText] = useState('')
  const [clarification, setClarification] = useState('')
  const [cart, setCart] = useState<Record<string, number>>({})
  const [requestId, setRequestId] = useState(() => crypto.randomUUID())
  const [choices, setChoices] =
    useState<{ id: string; name: string }[]>(participants)

  const refresh = useCallback(async () => {
    if (!session) return
    try {
      const next = await api<State>('/state', session.token)
      if (activeToken.current === session.token) setState(next)
    } catch (err) {
      if (activeToken.current === session.token)
        setError((err as Error).message)
    }
  }, [session])
  useEffect(() => {
    if (!session) return
    void refresh()
    const timer = window.setInterval(() => {
      void refresh()
    }, 6000)
    return () => clearInterval(timer)
  }, [refresh, session])
  const refreshChoices = useCallback(async () => {
    if (!session) return
    const next = await api<{ id: string; name: string }[]>(
      '/participants',
      session.token,
    )
    if (activeToken.current === session.token) setChoices(next)
  }, [session])
  useEffect(() => {
    void refreshChoices().catch(() => {})
  }, [refreshChoices])
  useEffect(() => {
    if (!selected || !session) return
    void api<Event[]>('/orders/' + selected + '/timeline', session.token)
      .then((next) => {
        if (activeToken.current === session.token) setEvents(next)
      })
      .catch((err) => {
        if (activeToken.current === session.token) setError(err.message)
      })
  }, [selected, state, session])

  async function signIn(id: string) {
    setBusy(true)
    setError('')
    const previousState = state
    activeToken.current = null
    setState(null)
    setSelected(null)
    setEvents([])
    setRecoveryInvoice('')
    try {
      const next = await api<Session>('/session', undefined, {
        persona: id,
        access_code: accessCode,
      })
      if (session)
        await api('/session', session.token, undefined, 'DELETE').catch(
          () => {},
        )
      activeToken.current = next.token
      sessionStorage.setItem('afracanet-session', JSON.stringify(next))
      setSession(next)
      setState(null)
      setSelected(null)
      setCart({})
      setTab('overview')
      setNotice('')
    } catch (err) {
      activeToken.current = session?.token ?? null
      setState(previousState)
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  async function signOut() {
    activeToken.current = null
    if (session)
      await api('/session', session.token, undefined, 'DELETE').catch(() => {})
    sessionStorage.removeItem('afracanet-session')
    setSession(null)
    setState(null)
    setSelected(null)
  }
  async function action(path: string, body: unknown = {}) {
    if (!session) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await api<{ message?: string }>(path, session.token, body)
      setNotice(result.message ?? 'Transaction updated.')
      await refresh()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  async function interpret() {
    if (!session) return
    setBusy(true)
    setError('')
    setClarification('')
    try {
      const result = await api<{ items: Line[]; clarification: string | null }>(
        '/assistant',
        session.token,
        { text },
      )
      if (result.clarification) setClarification(result.clarification)
      else {
        setCart(
          Object.fromEntries(
            result.items.map((i) => [i.product_id, i.quantity]),
          ),
        )
        setRequestId(crypto.randomUUID())
        setNotice(
          'Request interpreted. Review your items and total before confirming.',
        )
      }
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  async function submitOrder() {
    if (!session) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const order = await api<Order>('/orders', session.token, {
        client_request_id: requestId,
        items: Object.entries(cart)
          .filter(([, q]) => q > 0)
          .map(([product_id, quantity]) => ({ product_id, quantity })),
      })
      setCart({})
      setText('')
      setRequestId(crypto.randomUUID())
      setSelected(order.id)
      setNotice(
        'Request sent. Your credit and inputs are reserved for lender review.',
      )
      await refresh()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  async function download() {
    if (!session) return
    setError('')
    try {
      const response = await fetch('/api/reconciliation.csv', {
        headers: { Authorization: 'Bearer ' + session.token },
      })
      if (!response.ok)
        throw new Error('Could not export reconciliation records.')
      const url = URL.createObjectURL(await response.blob())
      const link = document.createElement('a')
      link.href = url
      link.download = 'afracanet-reconciliation.csv'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const banner = (
    <>
      {error && (
        <div role="alert" className="alert error">
          {error}
          <button aria-label="Dismiss error" onClick={() => setError('')}>
            <X size={16} />
          </button>
        </div>
      )}
      {notice && (
        <div role="status" className="alert notice">
          <CheckCircle2 size={17} />
          {notice}
          <button aria-label="Dismiss notice" onClick={() => setNotice('')}>
            <X size={16} />
          </button>
        </div>
      )}
    </>
  )

  if (!session)
    return (
      <div className="login-page">
        <section className="login-story">
          <Brand light />
          <div className="story-content">
            <h1>Credit, connected.</h1>
            <p>
              A shared path from approved agricultural credit to supplier
              payment and farmer collection.
            </p>
            <div className="story-proof">
              <ShieldCheck size={24} />
              <div>
                Every step, accounted for.
                <small>Farmer · Lender · Agro-dealer</small>
              </div>
            </div>
          </div>

          <footer>Built for agricultural finance in Kenya.</footer>
        </section>
        <section className="login-panel">
          <div className="login-top">
            <span className="prototype-pill">Working prototype</span>
            <span>Demonstration access</span>
          </div>
          <div className="login-form">
            <h2>Step into the workspace.</h2>
            <p>
              Choose a demonstration participant to follow the full input
              finance journey.
            </p>
            <div className="participant-options">
              {participants.slice(0, 3).map((p) => (
                <button
                  key={p.id}
                  className={
                    'participant-option ' + (persona === p.id ? 'chosen' : '')
                  }
                  onClick={() => setPersona(p.id)}
                >
                  <p.icon size={21} />
                  <span>
                    <strong>{p.label}</strong>
                    <small>{p.detail}</small>
                  </span>
                  <span className="radio-dot">
                    {persona === p.id && <Check size={12} />}
                  </span>
                </button>
              ))}
            </div>
            <label className="input-label" htmlFor="access-code">
              Demo access code
            </label>
            <input
              id="access-code"
              type="password"
              value={accessCode}
              onChange={(e) => setAccessCode(e.target.value)}
            />
            {banner}
            <button
              className="button primary full"
              disabled={busy}
              onClick={() => void signIn(persona)}
            >
              {busy ? 'Opening workspace…' : 'Open workspace'}
              <ArrowRight size={18} />
            </button>
            <div className="demo-disclosure">
              <CircleHelp size={17} />
              <p>
                All participants, approvals, and prices are illustrative. The
                initial walkthrough simulates payments. PayPal sandbox and
                Gemini modes require server configuration.
              </p>
            </div>
          </div>
          <footer>
            AFRACANet AI <span>Input finance module · v0.1</span>
          </footer>
        </section>
      </div>
    )
  if (!state)
    return (
      <div className="loading">
        <Brand />
        <p>Opening your workspace…</p>
        {banner}
        <button className="button secondary" onClick={() => void signOut()}>
          Back to sign in
        </button>
      </div>
    )

  const role = session.role
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
  const awaitingApproval = state.orders.filter(
    (o) => o.status === 'REQUESTED',
  ).length
  const current = state.orders.find((o) => o.id === selected)
  const openIssues =
    current?.issues?.some((issue) => !issue.resolved_at) ?? false
  const cartLines = state.products.filter((p) => (cart[p.id] ?? 0) > 0)
  const cartTotal = cartLines.reduce(
    (sum, p) => sum + p.price_cents * cart[p.id],
    0,
  )
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
    <div className="app-shell">
      <div
        className="main-shell"
        aria-hidden={current ? true : undefined}
        inert={Boolean(current)}
      >
        <a className="skip-link" href="#workspace-content">
          Skip to workspace
        </a>
        <header className="workspace-header">
          <Brand light />
          <nav aria-label="Workspace navigation">
            {nav.map((n) => (
              <button
                key={n.id}
                className={
                  tab === n.id ? 'workspace-nav active' : 'workspace-nav'
                }
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
        <main id="workspace-content" tabIndex={-1}>
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
          {banner}
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
              <button
                className="button secondary"
                onClick={() => void download()}
              >
                <ArrowDownToLine size={16} />
                <span className="export-label">Export records</span>
              </button>
            )}
          </div>
          {tab === 'overview' && role === 'lender' && (
            <LenderWorkspace
              state={state}
              busy={busy}
              onOpen={(order) => {
                setSelected(order.id)
                setCollectionCode('')
                setRecoveryInvoice(order.invoice_id ?? '')
              }}
              onAction={action}
              onAllocations={() => setTab('people')}
              onFarmer={() => void signIn('farmer-amina')}
            />
          )}
          {tab === 'overview' && role !== 'lender' && (
            <>
              <section className="stats-grid">
                <Stat
                  label={
                    role === 'supplier'
                      ? 'Confirmed payments'
                      : 'Available input credit'
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
            </>
          )}
          {role === 'farmer' && tab === 'overview' && (
            <div className="farmer-grid">
              <section className="panel request-panel">
                <div className="section-title">
                  <div>
                    <h2>What does your farm need?</h2>
                  </div>
                  <Sparkles size={22} />
                </div>
                <p className="muted">
                  Write in English or Swahili, or choose directly from the
                  catalogue.
                </p>
                <label className="sr-only" htmlFor="request-text">
                  Describe your input request
                </label>
                <textarea
                  id="request-text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Nahitaji mifuko 2 ya DAP ya kilo 50."
                  rows={3}
                />
                <div className="assistant-row">
                  <small>
                    {state.ai_mode === 'demo'
                      ? 'Limited deterministic parser'
                      : 'AI assists; you confirm the order'}
                  </small>
                  <button
                    className="button secondary"
                    disabled={busy || !text.trim()}
                    onClick={() => void interpret()}
                  >
                    <Sparkles size={15} />
                    Interpret request
                  </button>
                </div>
                {clarification && (
                  <div className="clarification">
                    <CircleHelp size={18} />
                    <span>
                      {clarification}
                      <small>
                        Edit your request above with the missing details, then
                        interpret again.
                      </small>
                    </span>
                  </div>
                )}
                <div className="catalogue">
                  {state.products.map((p) => (
                    <div className="product-row" key={p.id}>
                      <span className="product-icon">
                        {p.category === 'Seed' ? (
                          <Sprout size={22} />
                        ) : (
                          <Package size={22} />
                        )}
                      </span>
                      <div>
                        <strong>{p.name}</strong>
                        <small>
                          {p.unit} · {p.stock - p.reserved} available
                        </small>
                      </div>
                      <b>{money(p.price_cents)}</b>
                      <button
                        className="add-product"
                        aria-label={'Add ' + p.name + ' ' + p.unit}
                        disabled={p.stock <= p.reserved}
                        onClick={() => {
                          setCart((c) => ({ ...c, [p.id]: (c[p.id] ?? 0) + 1 }))
                          setRequestId(crypto.randomUUID())
                        }}
                      >
                        <Plus size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              </section>
              <section className="panel order-summary">
                <h2>Your input order</h2>
                <p className="muted">Supplier: Demo Green Valley Agrovet</p>
                {cartLines.length === 0 ? (
                  <div className="cart-empty">
                    <ShoppingBasket size={36} />
                    <p>Your basket is ready for inputs.</p>
                    <small>Add a catalogue item to get started.</small>
                  </div>
                ) : (
                  <div className="cart-lines">
                    {cartLines.map((p) => (
                      <div key={p.id}>
                        <strong>
                          {p.name}
                          <small>{p.unit}</small>
                        </strong>
                        <label className="sr-only" htmlFor={'qty-' + p.id}>
                          Quantity for {p.name} {p.unit}
                        </label>
                        <input
                          id={'qty-' + p.id}
                          type="number"
                          min="0"
                          max="100"
                          value={cart[p.id]}
                          onChange={(e) => {
                            setCart((c) => ({
                              ...c,
                              [p.id]: Math.max(
                                0,
                                Math.min(100, Number(e.target.value) || 0),
                              ),
                            }))
                            setRequestId(crypto.randomUUID())
                          }}
                        />
                        <b>{money(p.price_cents * cart[p.id])}</b>
                      </div>
                    ))}
                  </div>
                )}
                <div className="summary-total">
                  <span>Order total</span>
                  <strong>{money(cartTotal)}</strong>
                </div>
                <div className="summary-credit">
                  <span>Available credit</span>
                  <b>{money(available)}</b>
                </div>
                {state.farmers[0] && !allocationActive(state.farmers[0]) && (
                  <p className="limit-warning">
                    Your allocation has expired or been revoked. Contact your
                    lender to renew it.
                  </p>
                )}
                {cartTotal > available && (
                  <p className="inline-error">
                    This order exceeds your available credit. Reduce the
                    quantity.
                  </p>
                )}
                <button
                  className="button primary full"
                  disabled={busy || cartTotal === 0 || cartTotal > available}
                  onClick={() => void submitOrder()}
                >
                  Confirm input request
                  <ArrowRight size={17} />
                </button>
                <p className="fine-print">
                  Confirming reserves credit for these items and sends the
                  request to your lender. No payment occurs at this step.
                </p>
              </section>
            </div>
          )}
          {role === 'farmer' && tab === 'sms' && (
            <Notifications
              key={session.token}
              request={(path, body, method) =>
                api(path, session.token, body, method)
              }
            />
          )}
          {tab !== 'people' &&
            tab !== 'sms' &&
            !(role === 'lender' && tab === 'overview') && (
              <section className="panel transaction-panel">
                <div className="section-title">
                  <div>
                    <h2>
                      {role === 'farmer'
                        ? 'Your requests'
                        : 'Transaction activity'}
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
                        onClick={() => void signIn('farmer-amina')}
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
                                {state.farmers.find((f) => f.id === o.farmer_id)
                                  ?.name ?? o.farmer_id}
                              </small>
                            </td>
                            <td>
                              {o.items
                                .map((i) => i.quantity + ' × ' + i.name)
                                .join(', ')}
                              <small>
                                {o.items.map((i) => i.unit).join(', ')}
                              </small>
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
                              {o.issues?.some(
                                (issue) => !issue.resolved_at,
                              ) && (
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
                                  setSelected(o.id)
                                  setCollectionCode('')
                                  setRecoveryInvoice(o.invoice_id ?? '')
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
            )}
          {tab === 'people' && (
            <section className="panel transaction-panel">
              <div className="section-title">
                <div>
                  <h2>
                    {role === 'lender'
                      ? 'Pre-approved farmers'
                      : 'Approved catalogue'}
                  </h2>
                  <p className="muted">
                    {role === 'lender'
                      ? 'Approvals supplied by the lender. Credit scoring is external.'
                      : 'Illustrative inventory and prices. Reservations prevent concurrent over-ordering.'}
                  </p>
                </div>
              </div>
              {role === 'lender' ? (
                <>
                  <ApprovalHandoff
                    key={'handoff-' + session.token}
                    farmers={state.farmers}
                    lenderId={state.user.subject}
                    request={(path, body, method) =>
                      api(path, session.token, body, method)
                    }
                    onSaved={refresh}
                  />
                  <ApprovalImport
                    key={session.token}
                    request={(path, body, method) =>
                      api(path, session.token, body, method)
                    }
                    onSaved={async () => {
                      await refresh()
                      await refreshChoices()
                    }}
                  />
                </>
              ) : (
                <CatalogueEditor
                  key={session.token}
                  products={state.products}
                  request={(path, body, method) =>
                    api(path, session.token, body, method)
                  }
                  onSaved={refresh}
                />
              )}
              <div className="table-scroll">
                <table className="management-table">
                  {role === 'lender' ? (
                    <>
                      <thead>
                        <tr>
                          <th>Farmer</th>
                          <th>Approval</th>
                          <th>Limit</th>
                          <th>Reserved</th>
                          <th>Paid to suppliers</th>
                          <th>Available</th>
                        </tr>
                      </thead>
                      <tbody>
                        {state.farmers.map((f) => (
                          <tr key={f.id}>
                            <td>
                              <strong>{f.name}</strong>
                              <small>{f.location}</small>
                            </td>
                            <td>
                              {f.approval_reference}
                              <small>
                                Expires{' '}
                                {f.expires_at
                                  ? new Date(f.expires_at).toLocaleDateString()
                                  : '—'}
                              </small>
                            </td>
                            <td>{money(f.limit_cents ?? 0)}</td>
                            <td>{money(f.reserved_cents ?? 0)}</td>
                            <td>{money(f.spent_cents ?? 0)}</td>
                            <td>
                              <strong>{money(availableCredit(f))}</strong>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </>
                  ) : (
                    <>
                      <thead>
                        <tr>
                          <th>Product</th>
                          <th>Unit price</th>
                          <th>On hand</th>
                          <th>Reserved</th>
                          <th>Available</th>
                        </tr>
                      </thead>
                      <tbody>
                        {state.products.map((p) => (
                          <tr key={p.id}>
                            <td>
                              <strong>{p.name}</strong>
                              <small>{p.unit}</small>
                            </td>
                            <td>{money(p.price_cents)}</td>
                            <td>{p.stock}</td>
                            <td>{p.reserved}</td>
                            <td>{p.stock - p.reserved}</td>
                          </tr>
                        ))}
                      </tbody>
                    </>
                  )}
                </table>
              </div>
            </section>
          )}
          <footer className="page-footer">
            <span>AFRACANet AI · Input Finance</span>
            <span>
              Illustrative data · One lender, one dealer network · v0.1
            </span>
          </footer>
        </main>
      </div>
      {current && (
        <Dialog
          title={'Order ' + current.reference}
          onClose={() => setSelected(null)}
        >
          <div className="drawer-header">
            <div>
              <h2>{current.reference}</h2>
            </div>
            <button
              aria-label="Close transaction"
              onClick={() => setSelected(null)}
            >
              <X size={22} />
            </button>
          </div>
          <Status status={current.status} />
          <div className="drawer-amount">
            {money(current.amount_cents)}
            <small>
              {current.payment_mode === 'mock'
                ? 'Simulated payment workflow'
                : 'PayPal sandbox workflow'}
            </small>
          </div>
          <div className="detail-items">
            {current.items.map((i) => (
              <div key={i.product_id}>
                <span>
                  {i.quantity} × {i.name}
                  <small>{i.unit}</small>
                </span>
                <strong>{money((i.price_cents ?? 0) * i.quantity)}</strong>
              </div>
            ))}
          </div>
          {current.invoice_id && (
            <div className="record-field">
              <span>Invoice reference</span>
              <code>{current.invoice_id}</code>
            </div>
          )}
          {current.payment_reference && (
            <div className="record-field">
              <span>Payment reference</span>
              <code>{current.payment_reference}</code>
            </div>
          )}
          {role === 'farmer' &&
            current.pickup_code &&
            current.status === 'READY_FOR_COLLECTION' && (
              <div className="pickup-code">
                <span>Your collection code</span>
                <strong>{current.pickup_code}</strong>
                <p>
                  Share this code with the agro-dealer when collecting your
                  inputs.
                </p>
              </div>
            )}
          {banner}
          <Issues
            key={session.token + ':' + current.id}
            orderId={current.id}
            issues={current.issues ?? []}
            role={role}
            request={(path, body) => api(path, session.token, body)}
            onSaved={refresh}
          />
          <div className="drawer-actions">
            {role === 'lender' &&
              !openIssues &&
              current.status === 'REQUESTED' && (
                <button
                  className="button primary full"
                  disabled={busy}
                  onClick={() =>
                    void action('/orders/' + current.id + '/approve')
                  }
                >
                  Approve input order
                  <Check size={17} />
                </button>
              )}
            {role === 'supplier' &&
              !openIssues &&
              current.status === 'APPROVED' && (
                <>
                  <p className="fine-print">
                    Confirm you can supply the listed quantities at the quoted
                    prices before issuing the invoice.
                  </p>
                  <button
                    className="button primary full"
                    disabled={busy}
                    onClick={() =>
                      void action('/orders/' + current.id + '/invoice')
                    }
                  >
                    Confirm stock & issue invoice
                    <ArrowRight size={17} />
                  </button>
                </>
              )}
            {role === 'lender' &&
              !openIssues &&
              current.status === 'AWAITING_PAYMENT' &&
              (current.payment_mode === 'mock' ? (
                <button
                  className="button primary full"
                  disabled={busy}
                  onClick={() =>
                    void action('/orders/' + current.id + '/demo-pay')
                  }
                >
                  Simulate lender payment
                  <CreditCard size={17} />
                </button>
              ) : (
                current.payment_url && (
                  <a
                    className="button primary full"
                    href={current.payment_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Pay invoice in PayPal sandbox
                    <ArrowRight size={17} />
                  </a>
                )
              ))}
            {role !== 'farmer' &&
              current.payment_mode === 'sandbox' &&
              current.invoice_id &&
              ['AWAITING_PAYMENT', 'PAYMENT_REVIEW', 'INVOICING'].includes(
                current.status,
              ) && (
                <button
                  className="button secondary full"
                  disabled={busy}
                  onClick={() =>
                    void action('/orders/' + current.id + '/reconcile')
                  }
                >
                  Check PayPal payment status
                </button>
              )}
            {role === 'supplier' &&
              !openIssues &&
              current.status === 'READY_FOR_COLLECTION' && (
                <>
                  <label className="input-label" htmlFor="collection-code">
                    Farmer's collection code
                  </label>
                  <input
                    id="collection-code"
                    inputMode="numeric"
                    maxLength={6}
                    value={collectionCode}
                    onChange={(e) =>
                      setCollectionCode(e.target.value.replace(/\D/g, ''))
                    }
                    placeholder="Enter six-digit code"
                  />
                  <button
                    className="button primary full"
                    disabled={busy || collectionCode.length !== 6}
                    onClick={() =>
                      void action('/orders/' + current.id + '/collect', {
                        code: collectionCode,
                      })
                    }
                  >
                    Record farmer collection
                    <Package size={17} />
                  </button>
                </>
              )}
            {role !== 'supplier' &&
              ['REQUESTED', 'APPROVED'].includes(current.status) && (
                <button
                  className="button secondary full"
                  disabled={busy}
                  onClick={() =>
                    void action('/orders/' + current.id + '/cancel')
                  }
                >
                  Cancel request & release credit
                </button>
              )}
            {current.status === 'PAYMENT_REVIEW' && (
              <p className="inline-error">
                Provider confirmation is uncertain. Review the PayPal invoice
                records before any retry. Credit remains reserved.
              </p>
            )}
            {role === 'supplier' &&
              current.payment_mode === 'sandbox' &&
              ['PAYMENT_REVIEW', 'INVOICING', 'AWAITING_PAYMENT'].includes(
                current.status,
              ) && (
                <div className="recovery-panel">
                  <h3>Recover an existing invoice</h3>
                  <p className="fine-print">
                    Check the supplier's PayPal sandbox records for this order.
                    Recovery verifies an existing invoice and its payment
                    records. Allow two minutes after interrupted preparation.
                    Credit remains reserved until payment or an unpaid
                    cancellation is verified.
                  </p>
                  <label className="input-label" htmlFor="recovery-invoice">
                    Existing PayPal invoice ID
                  </label>
                  <input
                    id="recovery-invoice"
                    value={current.invoice_id ?? recoveryInvoice}
                    readOnly={Boolean(current.invoice_id)}
                    placeholder="INV2-…"
                    maxLength={106}
                    onChange={(e) =>
                      setRecoveryInvoice(e.target.value.trim().toUpperCase())
                    }
                  />
                  <button
                    className="button secondary full"
                    disabled={busy || !(current.invoice_id ?? recoveryInvoice)}
                    onClick={() =>
                      void action(
                        '/orders/' + current.id + '/recover-invoice',
                        { invoice_id: current.invoice_id ?? recoveryInvoice },
                      )
                    }
                  >
                    Verify & recover existing invoice
                  </button>
                  <p className="fine-print">
                    If PayPal still shows a draft, send that same invoice in its
                    dashboard, then verify again here. Partial payments and
                    refunds require operator review.
                  </p>
                </div>
              )}
          </div>
          <h3 className="timeline-title">Transaction timeline</h3>
          <ol className="timeline">
            {events.map((e) => (
              <li key={e.id}>
                <span className="timeline-dot">
                  <Check size={12} />
                </span>
                <strong>{e.action.replaceAll('_', ' ').toLowerCase()}</strong>
                <p>{e.detail}</p>
                <small>
                  {e.actor} · {new Date(e.created_at).toLocaleString()}
                </small>
              </li>
            ))}
          </ol>
        </Dialog>
      )}
    </div>
  )
}
