import { useFarmerDraft } from './FarmerDraft'
import type { State, Line, Order } from '../../domain/models'
import type { Requester } from '../../lib/api'
import { allocationActive, availableCredit } from '../../domain/credit'
import { money } from '../../lib/format'
import {
  ArrowRight,
  CircleHelp,
  Package,
  Plus,
  ShoppingBasket,
  Sparkles,
  Sprout,
} from 'lucide-react'

type Props = {
  state: State
  busy: boolean
  setBusy: (value: boolean) => void
  request: Requester
  onError: (value: string) => void
  onNotice: (value: string) => void
  onOpen: (order: Order) => void
  onSaved: () => Promise<void>
}
export function FarmerRequest({
  state,
  busy,
  setBusy,
  request,
  onError,
  onNotice,
  onOpen,
  onSaved,
}: Props) {
  const {
    text,
    setText,
    clarification,
    setClarification,
    cart,
    setCart,
    requestId,
    setRequestId,
  } = useFarmerDraft()
  const available = state.farmers.reduce(
    (sum, f) => sum + availableCredit(f),
    0,
  )
  const cartLines = state.products.filter((p) => (cart[p.id] ?? 0) > 0)
  const cartTotal = cartLines.reduce(
    (sum, p) => sum + p.price_cents * cart[p.id],
    0,
  )
  async function interpret() {
    setBusy(true)
    onError('')
    setClarification('')
    try {
      const result = await request<{
        items: Line[]
        clarification: string | null
      }>('/assistant', { text })
      if (result.clarification) setClarification(result.clarification)
      else {
        setCart(
          Object.fromEntries(
            result.items.map((i) => [i.product_id, i.quantity]),
          ),
        )
        setRequestId(crypto.randomUUID())
        onNotice(
          'Request interpreted. Review your items and total before confirming.',
        )
      }
    } catch (err) {
      onError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function submitOrder() {
    setBusy(true)
    onError('')
    onNotice('')
    try {
      const order = await request<Order>('/orders', {
        client_request_id: requestId,
        items: Object.entries(cart)
          .filter(([, q]) => q > 0)
          .map(([product_id, quantity]) => ({ product_id, quantity })),
      })
      setCart({})
      setText('')
      setRequestId(crypto.randomUUID())
      onOpen(order)
      onNotice(
        'Request sent. Your credit and inputs are reserved for lender review.',
      )
      await onSaved()
    } catch (err) {
      onError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="farmer-grid">
      <section className="panel request-panel">
        <div className="section-title">
          <div>
            <h2>What does your farm need?</h2>
          </div>
          <Sparkles size={22} />
        </div>
        <p className="muted">
          Write in English or Swahili, or choose directly from the catalogue.
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
                Edit your request above with the missing details, then interpret
                again.
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
            Your allocation has expired or been revoked. Contact your lender to
            renew it.
          </p>
        )}
        {cartTotal > available && (
          <p className="inline-error">
            This order exceeds your available credit. Reduce the quantity.
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
          Confirming reserves credit for these items and sends the request to
          your lender. No payment occurs at this step.
        </p>
      </section>
    </div>
  )
}
