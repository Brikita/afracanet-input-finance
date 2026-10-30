import { useEffect, useState, type ReactNode } from 'react'
import type { State, Order, Event } from '../../domain/models'
import type { Requester } from '../../lib/api'
import { Dialog } from '../../components/Dialog'
import { Status } from '../../components/Status'
import { Issues } from '../issues/Issues'
import { money } from '../../lib/format'
import { ArrowRight, Check, CreditCard, Package, X } from 'lucide-react'

type Props = {
  state: State
  current: Order
  busy: boolean
  request: Requester
  action: (path: string, body?: unknown) => Promise<void>
  onSaved: () => Promise<void>
  onClose: () => void
  onError: (value: string) => void
  banner: ReactNode
}
export function OrderDetails({
  state,
  current,
  busy,
  request,
  action,
  onSaved,
  onClose,
  onError,
  banner,
}: Props) {
  const role = state.user.role
  const openIssues =
    current.issues?.some((issue) => !issue.resolved_at) ?? false
  const [collectionCode, setCollectionCode] = useState('')
  const [recoveryInvoice, setRecoveryInvoice] = useState(
    current.invoice_id ?? '',
  )
  const [events, setEvents] = useState<Event[]>([])
  useEffect(() => {
    let active = true
    request<Event[]>('/orders/' + current.id + '/timeline')
      .then((next) => {
        if (active) setEvents(next)
      })
      .catch((err: Error) => {
        if (active) onError(err.message)
      })
    return () => {
      active = false
    }
  }, [current.id, state, request, onError])
  return (
    <Dialog title={'Order ' + current.reference} onClose={onClose}>
      <div className="drawer-header">
        <div>
          <h2>{current.reference}</h2>
        </div>
        <button aria-label="Close transaction" onClick={onClose}>
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
              Share this code with the agro-dealer when collecting your inputs.
            </p>
          </div>
        )}
      {banner}
      <Issues
        key={current.id}
        orderId={current.id}
        issues={current.issues ?? []}
        role={role}
        request={request}
        onSaved={onSaved}
      />
      <div className="drawer-actions">
        {role === 'lender' && !openIssues && current.status === 'REQUESTED' && (
          <button
            className="button primary full"
            disabled={busy}
            onClick={() => void action('/orders/' + current.id + '/approve')}
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
              onClick={() => void action('/orders/' + current.id + '/demo-pay')}
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
              onClick={() => void action('/orders/' + current.id + '/cancel')}
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
                Recovery verifies an existing invoice and its payment records.
                Allow two minutes after interrupted preparation. Credit remains
                reserved until payment or an unpaid cancellation is verified.
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
                  void action('/orders/' + current.id + '/recover-invoice', {
                    invoice_id: current.invoice_id ?? recoveryInvoice,
                  })
                }
              >
                Verify & recover existing invoice
              </button>
              <p className="fine-print">
                If PayPal still shows a draft, send that same invoice in its
                dashboard, then verify again here. Partial payments and refunds
                require operator review.
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
  )
}
