import { useState } from 'react'
import {
  Check,
  CircleCheck,
  Clock3,
  FileText,
  GitBranch,
  Leaf,
  MailCheck,
  ShieldCheck,
  Wallet,
} from 'lucide-react'
import payment from '../../../datasets/reports/paypal-sandbox-2026-10-31.json'
import callback from '../../../datasets/reports/paypal-callback-2026-10-31.json'
import './payment-proof.css'

const stages = [
  {
    title: 'Invoice created',
    caption: 'Isolated fixture',
    icon: FileText,
    heading: 'Supplier invoice',
    body: 'Created against illustrative input credit.',
    verified: true,
  },
  {
    title: 'Invoice sent',
    caption: 'PayPal sandbox',
    icon: MailCheck,
    heading: 'Invoice issued',
    body: 'A sandbox payment link was issued.',
    verified: true,
  },
  {
    title: 'Buyer paid',
    caption: 'Actual sandbox payment',
    icon: Wallet,
    heading: 'Buyer payment',
    body: 'USD 18.00 paid through PayPal sandbox.',
    verified: payment.payment_verified,
  },
  {
    title: 'Payment verified',
    caption: 'Provider records checked',
    icon: ShieldCheck,
    heading: 'Payment confirmed',
    body: 'Authenticated payment records matched.',
    verified: payment.payment_verified,
  },
  {
    title: 'Callback verified',
    caption: 'Genuine event resent',
    icon: GitBranch,
    heading: 'One payment effect',
    body: 'Repeated network delivery stayed deduplicated.',
    verified: callback.signature_verified_by_paypal,
  },
  {
    title: 'Ready for collection',
    caption: 'Payment requirement met',
    icon: Leaf,
    heading: 'Collection permitted',
    body: 'A separate authorized handover is still required.',
    verified: payment.order_status === 'READY_FOR_COLLECTION',
  },
  {
    title: 'Collection',
    caption: 'No handover recorded',
    icon: Clock3,
    heading: 'Collection pending',
    body: 'Payment does not establish physical collection.',
    verified: false,
  },
]

const explanations = [
  'The invoice belongs to a preserved provider-check fixture. Its allocation is illustrative; it is not evidence of a real lender approving a customer loan.',
  'The sandbox invoicing workflow issued a payment link. This is separate from proving email or SMS delivery to a person.',
  'A buyer completed the sandbox payment. No real money moved, and a payment in this fixture cannot pay another order.',
  'The server retrieved authenticated PayPal records and matched the invoice, amount, currency and payment evidence. An invoice status alone does not pass this check.',
  'The payment was first reconciled manually. PayPal then resent its genuine event; the server verified the signature. Repeated callback delivery retained one payment effect. Network delivery is separate from physical handover.',
  'The recorded order met its payment requirement. A dealer must still verify the farmer’s collection code and record the handover through an authorized action.',
  'There is no physical collection record in this fixture. The page deliberately leaves this stage unverified; a paid invoice does not prove that inputs reached the farmer.',
]

export function PaymentProof() {
  const [selected, setSelected] = useState(4)
  const stage = stages[selected]
  const amount = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: payment.currency,
    currencyDisplay: 'code',
  }).format(payment.amount_cents / 100)
  const checked = new Date(payment.checked_at).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'Africa/Nairobi',
  })
  return (
    <section className="payment-proof-section" aria-labelledby="proof-title">
      <div className="payment-record-header">
        <div>
          <h2 id="proof-title">Input finance payment to supplier</h2>
          <p>Explore one preserved provider check, a stage at a time.</p>
          <span className="payment-provenance">
            PayPal sandbox · Synthetic allocation fixture · {checked}
          </span>
        </div>
        <div className="proof-amount">
          <span>Verified payment</span>
          <strong>{amount}</strong>
        </div>
      </div>
      <nav className="payment-stage-nav" aria-label="Sandbox payment stages">
        <ol>
          {stages.map((item, index) => (
            <li key={item.title}>
              <button
                aria-pressed={selected === index}
                aria-controls="payment-stage-evidence"
                onClick={() => setSelected(index)}
              >
                <span
                  className={
                    item.verified
                      ? 'payment-number is-verified'
                      : 'payment-number'
                  }
                >
                  {index + 1}
                </span>
                <span>{item.title}</span>
              </button>
            </li>
          ))}
        </ol>
      </nav>
      <label className="payment-stage-select">
        Explore a payment stage
        <select
          value={selected}
          onChange={(event) => setSelected(Number(event.target.value))}
        >
          {stages.map((item, index) => (
            <option key={item.title} value={index}>
              {index + 1}. {item.title}
            </option>
          ))}
        </select>
      </label>
      <div
        className="payment-stage-evidence"
        id="payment-stage-evidence"
        role="region"
        aria-live="polite"
        aria-labelledby="payment-stage-heading"
      >
        <stage.icon
          className="payment-focus-icon"
          size={40}
          aria-hidden="true"
        />
        <div>
          <span className="payment-focus-position">
            Stage {selected + 1} of {stages.length}
          </span>
          <h3 id="payment-stage-heading">{stage.heading}</h3>
          <p>{stage.body}</p>
          <p>{explanations[selected]}</p>
        </div>
        <span
          className={
            stage.verified ? 'payment-verdict verified' : 'payment-verdict'
          }
        >
          {stage.verified ? <CircleCheck size={18} /> : <Clock3 size={18} />}
          {stage.verified ? 'Verified in the check' : 'Not recorded'}
        </span>
      </div>
      <dl className="payment-record-facts">
        <div>
          <dt>Repeated delivery</dt>
          <dd>{callback.payment_effects} payment effect</dd>
        </div>
        <div>
          <dt>Recorded order status</dt>
          <dd>
            <Check size={15} />
            Ready for collection
          </dd>
        </div>
        <div>
          <dt>Physical collection</dt>
          <dd>No handover recorded</dd>
        </div>
      </dl>
      <p className="payment-record-note">
        A snapshot of a sandbox check, separate from the signed lender-workflow
        tests.{' '}
        <a href="https://github.com/Brikita/afracanet-input-finance/blob/main/docs/PROVIDER_CHECKS_2026-10-31.md">
          Inspect the recorded evidence
        </a>
        .
      </p>
    </section>
  )
}
