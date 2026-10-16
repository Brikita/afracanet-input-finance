import React, { useCallback, useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/dm-sans/latin-400.css'
import '@fontsource/dm-sans/latin-500.css'
import '@fontsource/dm-sans/latin-600.css'
import '@fontsource/dm-sans/latin-700.css'
import '@fontsource/manrope/latin-400.css'
import '@fontsource/manrope/latin-500.css'
import '@fontsource/manrope/latin-600.css'
import '@fontsource/manrope/latin-700.css'
import '@fontsource/manrope/latin-800.css'
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
import './styles.css'
import { ApprovalImport, CatalogueEditor } from './Management'

type Role = 'farmer' | 'lender' | 'supplier'
type Session = { token: string; role: Role; subject: string; name: string }
type Farmer = {
  id: string
  name: string
  location: string
  limit_cents?: number
  reserved_cents?: number
  spent_cents?: number
  approval_reference?: string
  expires_at?: string
}
type Product = {
  id: string
  name: string
  unit: string
  price_cents: number
  stock: number
  reserved: number
  category: string
  revision: string
}
type Line = {
  product_id: string
  quantity: number
  name?: string
  unit?: string
  price_cents?: number
}
type Order = {
  id: number
  reference: string
  farmer_id: string
  items: Line[]
  amount_cents: number
  status: string
  currency: string
  invoice_id: string | null
  payment_reference: string | null
  pickup_code?: string
  payment_url?: string
  payment_mode: string
  created_at: string
}
type State = {
  user: Omit<Session, 'token'>
  farmers: Farmer[]
  products: Product[]
  orders: Order[]
  payment_mode: string
  ai_mode: string
}
type Event = {
  id: number
  actor: string
  action: string
  detail: string
  created_at: string
}

const money = (cents: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(
    cents / 100,
  )
const labels: Record<string, string> = {
  REQUESTED: 'Needs approval',
  APPROVED: 'Ready to invoice',
  INVOICING: 'Preparing invoice',
  AWAITING_PAYMENT: 'Awaiting payment',
  READY_FOR_COLLECTION: 'Ready for collection',
  COLLECTED: 'Collected',
  CANCELLED: 'Cancelled',
  PAYMENT_REVIEW: 'Operator review',
}
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

async function api<T>(
  path: string,
  token?: string,
  body?: unknown,
  method?: string,
): Promise<T> {
  const response = await fetch('/api' + path, {
    method: method ?? (body === undefined ? 'GET' : 'POST'),
    headers: {
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: 'Bearer ' + token } : {}),
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  })
  if (!response.ok) {
    const result = await response.json().catch(() => ({}))
    throw new Error(
      typeof result.detail === 'string'
        ? result.detail
        : 'This request could not be completed.',
    )
  }
  return response.json() as Promise<T>
}

function Brand({ light = false }: { light?: boolean }) {
  return (
    <div className={'brand ' + (light ? 'brand-light' : '')}>
      <span className="brand-symbol">
        <Sprout size={24} />
      </span>
      <div>
        AFRACANet<small>INPUT FINANCE</small>
      </div>
    </div>
  )
}

function App() {
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
            <span className="eyebrow light">
              <span /> FROM APPROVAL TO THE FIELD
            </span>
            <h1>
              Good credit.
              <br />
              Real inputs.
              <br />
              <em>Growing futures.</em>
            </h1>
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
          <svg className="field-art" viewBox="0 0 800 300" aria-hidden="true">
            <path
              d="M-50 290 Q300 -70 870 160M-50 330 Q300 -30 870 200M-50 370 Q300 10 870 240M-50 410 Q300 50 870 280M-50 450 Q300 90 870 320M-50 490 Q300 130 870 360"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            />
            <circle cx="640" cy="60" r="35" fill="currentColor" opacity=".3" />
          </svg>
          <footer>Built for agricultural finance in Kenya.</footer>
        </section>
        <section className="login-panel">
          <div className="login-top">
            <span className="prototype-pill">WORKING PROTOTYPE</span>
            <span>01 / Explore</span>
          </div>
          <div className="login-form">
            <span className="eyebrow">
              ONE TRANSACTION. THREE PERSPECTIVES.
            </span>
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
            AFRACANet Input Finance <span>Independent project · v0.1</span>
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
    (sum, f) =>
      sum +
      (f.limit_cents ?? 0) -
      (f.reserved_cents ?? 0) -
      (f.spent_cents ?? 0),
    0,
  )
  const funded = state.orders.filter((o) =>
    ['READY_FOR_COLLECTION', 'COLLECTED'].includes(o.status),
  )
  const totalFunded = funded.reduce((sum, o) => sum + o.amount_cents, 0)
  const pending = state.orders.filter((o) =>
    ['REQUESTED', 'APPROVED', 'AWAITING_PAYMENT', 'PAYMENT_REVIEW'].includes(
      o.status,
    ),
  )
  const collected = state.orders.filter((o) => o.status === 'COLLECTED')
  const current = state.orders.find((o) => o.id === selected)
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
      <aside className="sidebar">
        <Brand light />
        <span className="workspace-label">
          {role === 'lender'
            ? 'LENDER WORKSPACE'
            : role === 'supplier'
              ? 'AGRO-DEALER WORKSPACE'
              : 'FARMER WORKSPACE'}
        </span>
        <nav aria-label="Workspace navigation">
          {nav.map((n) => (
            <button
              key={n.id}
              className={tab === n.id ? 'nav-item active' : 'nav-item'}
              onClick={() => setTab(n.id)}
            >
              <n.icon size={18} />
              {n.label}
              {n.id === 'orders' && <span>{state.orders.length}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <Sprout size={27} />
          <strong>
            Credit that reaches
            <br />
            the field.
          </strong>
          <p>Connect the request, the payment, and the collection.</p>
        </div>
        <div className="sidebar-bottom">
          <span className="live-dot" /> Prototype workspace
          <button aria-label="Sign out" onClick={() => void signOut()}>
            <LogOut size={18} />
          </button>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span>{' '}
            <strong>{nav.find((n) => n.id === tab)?.label}</strong>
          </div>
          <div className="topbar-right">
            <span className="prototype-pill">PROTOTYPE</span>
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
              <ChevronDown size={15} />
            </div>
            <div className="avatar">
              {session.name
                .split(' ')
                .slice(0, 2)
                .map((s) => s[0])
                .join('')}
            </div>
            <button
              className="mobile-signout"
              aria-label="Sign out of workspace"
              onClick={() => void signOut()}
            >
              <LogOut size={17} />
            </button>
          </div>
        </header>
        <main>
          <div className="mode-banner">
            <ShieldCheck size={16} />
            <span>
              {state.payment_mode === 'mock'
                ? 'Simulated payments · no money moves'
                : 'PayPal sandbox · test funds only'}
              <span className="mode-divider">|</span>
              {state.ai_mode === 'demo'
                ? 'Demo request parser · no AI model connected'
                : 'Gemini request assistant'}
            </span>
            <small>USD illustrative prices</small>
          </div>
          {banner}
          <div className="page-title">
            <div>
              <span className="eyebrow">
                {role === 'farmer'
                  ? 'YOUR NEXT SEASON STARTS HERE'
                  : 'AGRICULTURAL INPUT FINANCE'}
              </span>
              <h1>
                {role === 'farmer'
                  ? 'From your credit to your farm.'
                  : tab === 'people'
                    ? role === 'lender'
                      ? 'Approved credit allocations'
                      : 'Your input inventory'
                    : tab === 'orders'
                      ? 'Every transaction, in view.'
                      : 'A clearer path to the field.'}
              </h1>
              <p>
                {role === 'farmer'
                  ? 'Choose your inputs. Your lender pays the agro-dealer directly.'
                  : 'Coordinate approved credit, supplier payments, and farmer collection.'}
              </p>
            </div>
            {role === 'lender' && (
              <button
                className="button secondary"
                onClick={() => void download()}
              >
                <ArrowDownToLine size={16} />
                Export records
              </button>
            )}
          </div>
          {tab === 'overview' && (
            <>
              {role !== 'farmer' && (
                <section className="hero-strip">
                  <div>
                    <span className="eyebrow light">
                      CONNECTED FROM START TO FINISH
                    </span>
                    <h2>
                      One shared record.
                      <br />
                      Every step of the journey.
                    </h2>
                    <p>
                      Give credit a clear destination and keep every participant
                      informed.
                    </p>
                  </div>
                  <div className="journey-inline">
                    {[
                      { icon: Tractor, label: 'Farmer requests' },
                      { icon: Wallet, label: 'Lender pays' },
                      { icon: Package, label: 'Dealer fulfils' },
                    ].map((step, i) => (
                      <React.Fragment key={step.label}>
                        {i > 0 && <span className="journey-line" />}
                        <div>
                          <span>
                            <step.icon size={23} />
                          </span>
                          <small>{step.label}</small>
                        </div>
                      </React.Fragment>
                    ))}
                  </div>
                </section>
              )}
              <section className="stats-grid">
                <Stat
                  icon={Wallet}
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
                  icon={Clock3}
                  label="In progress"
                  value={String(pending.length)}
                  note="Requests requiring the next step"
                />
                <Stat
                  icon={Package}
                  label="Ready for collection"
                  value={String(funded.length - collected.length)}
                  note="Payment confirmed, handover pending"
                />
                <Stat
                  icon={CheckCircle2}
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
                    <span className="eyebrow">START A REQUEST</span>
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
                <span className="eyebrow">REVIEW & CONFIRM</span>
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
          {tab !== 'people' && (
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
                  <table>
                    <thead>
                      <tr>
                        <th>ORDER / FARMER</th>
                        <th>INPUTS</th>
                        <th>AMOUNT</th>
                        <th>STATUS</th>
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
                          </td>
                          <td>
                            <button
                              className="text-button"
                              aria-label={'Open ' + o.reference}
                              onClick={() => {
                                setSelected(o.id)
                                setCollectionCode('')
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
                <table>
                  {role === 'lender' ? (
                    <>
                      <thead>
                        <tr>
                          <th>FARMER</th>
                          <th>APPROVAL</th>
                          <th>LIMIT</th>
                          <th>RESERVED</th>
                          <th>PAID TO SUPPLIERS</th>
                          <th>AVAILABLE</th>
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
                              <strong>
                                {money(
                                  (f.limit_cents ?? 0) -
                                    (f.reserved_cents ?? 0) -
                                    (f.spent_cents ?? 0),
                                )}
                              </strong>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </>
                  ) : (
                    <>
                      <thead>
                        <tr>
                          <th>PRODUCT</th>
                          <th>UNIT PRICE</th>
                          <th>ON HAND</th>
                          <th>RESERVED</th>
                          <th>AVAILABLE</th>
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
          {tab === 'overview' && role !== 'farmer' && (
            <div className="bottom-grid">
              <div className="panel insight-card">
                <ShieldCheck size={22} />
                <div>
                  <h3>Purpose recorded. Progress visible.</h3>
                  <p>
                    Credit reservations, supplier invoices, and collection
                    records stay connected. Payment confirmation and fulfilment
                    are tracked separately.
                  </p>
                </div>
              </div>
              <div className="panel insight-card">
                <Leaf size={22} />
                <div>
                  <h3>Built around existing approvals.</h3>
                  <p>
                    The lender owns credit decisions and loan terms. AFRACANet
                    coordinates the journey from an approved allocation to
                    inputs.
                  </p>
                </div>
              </div>
            </div>
          )}
          <footer className="page-footer">
            <span>AFRACANet · Input Finance</span>
            <span>
              Illustrative data · One lender, one dealer network · v0.1
            </span>
          </footer>
        </main>
      </div>
      {current && (
        <div className="drawer-backdrop" onClick={() => setSelected(null)}>
          <section
            className="drawer"
            role="dialog"
            aria-modal="true"
            aria-label={'Order ' + current.reference}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drawer-header">
              <div>
                <span className="eyebrow">TRANSACTION RECORD</span>
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
            <div className="drawer-actions">
              {role === 'lender' && current.status === 'REQUESTED' && (
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
              {role === 'supplier' && current.status === 'APPROVED' && (
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
          </section>
        </div>
      )}
    </div>
  )
}
function Status({ status }: { status: string }) {
  return (
    <span className={'status status-' + status.toLowerCase()}>
      <span />
      {labels[status] ?? status}
    </span>
  )
}
function Stat({
  icon: Icon,
  label,
  value,
  note,
}: {
  icon: typeof Wallet
  label: string
  value: string
  note: string
}) {
  return (
    <div className="stat-card">
      <div>
        <span>{label}</span>
        <Icon size={18} />
      </div>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  )
}
createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
