import { useRef, useState } from 'react'
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
  Pause,
  Play,
} from 'lucide-react'
import { useViewportPlayback } from './useViewportPlayback'
import payment from '../../../datasets/reports/connected-sandbox-2026-11-02.json'
import './payment-proof.css'

const stages = [
  {
    title: 'Invoice created',
    caption: 'Linked synthetic case',
    icon: FileText,
    heading: 'Supplier invoice',
    body: 'Linked to an explicitly authorized synthetic allocation.',
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
    verified: payment.provider_payment_verified,
  },
  {
    title: 'Payment verified',
    caption: 'Provider records checked',
    icon: ShieldCheck,
    heading: 'Payment confirmed',
    body: 'Authenticated payment records matched.',
    verified: payment.provider_payment_verified,
  },
  {
    title: 'Reconciliation repeated',
    caption: 'Actual provider checks',
    icon: GitBranch,
    heading: 'One payment effect',
    body: 'Repeated payment checks left balances unchanged.',
    verified: payment.repeat_reconciliation_and_collection_unchanged,
  },
  {
    title: 'Ready for collection',
    caption: 'Payment requirement met',
    icon: Leaf,
    heading: 'Collection permitted',
    body: 'The collection code required a separate dealer action.',
    verified: ['READY_FOR_COLLECTION', 'COLLECTED'].includes(
      payment.order_status,
    ),
  },
  {
    title: 'Collection',
    caption: 'Demonstration recorded',
    icon: CircleCheck,
    heading: 'Demonstration handover',
    body: 'A code-based demonstration handover was recorded.',
    verified: payment.collection_events === 1,
  },
]

const explanations = [
  'This invoice belongs to one linked synthetic rehearsal: retrieved graph evidence, actual Gemini, explicit officer authorization and a verified signed allocation. It is not a real customer loan.',
  'The existing sandbox draft was correlated and recovered before being sent. No duplicate invoice was created. Issuing a payment link is separate from proving email or SMS delivery to a person.',
  'A buyer completed the sandbox payment. No real money moved, and a payment in this fixture cannot pay another order.',
  'The server retrieved authenticated PayPal records and matched the invoice, amount, currency and payment evidence. An invoice status alone does not pass this check.',
  'Authenticated reconciliation was repeated and retained one payment effect. No incoming callback was verified for this scenario; the genuine callback check from 31 October is separate evidence.',
  'The recorded order met its payment requirement. A dealer must still verify the farmer’s collection code and record the handover through an authorized action.',
  'The dealer recorded a synthetic demonstration handover using the farmer’s collection code. Repeating that action retained one collection event. This does not establish physical delivery of real goods.',
]

export function PaymentProof() {
  const [selected, setSelected] = useState(0)
  const frame = useRef<HTMLElement>(null)
  const playback = useViewportPlayback(
    frame,
    () => setSelected((value) => (value + 1) % stages.length),
    10000,
  )
  const choose = (index: number) => {
    setSelected(index)
    playback.restart()
  }
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
    <section
      ref={frame}
      className="payment-proof-section"
      data-ui="preserved-payment-walkthrough"
      aria-labelledby="proof-title"
    >
      <div className="payment-record-header">
        <div>
          <h2 id="proof-title">Input finance to supplier</h2>
          <p>One connected sandbox rehearsal, unfolding a stage at a time.</p>
          <span className="payment-provenance">
            PayPal sandbox · Explicit synthetic officer authorization ·{' '}
            {checked}
          </span>
        </div>
        <div className="proof-amount">
          <strong>{amount}</strong>
          <span>Verified sandbox payment</span>
        </div>
      </div>
      <div className="presentation-playback payment-playback">
        <span>
          {playback.requested
            ? 'Automatic walkthrough · 10 seconds per stage'
            : 'Walkthrough paused'}
        </span>
        <button
          onClick={playback.toggle}
          aria-label={
            playback.requested
              ? 'Pause payment walkthrough'
              : 'Resume payment walkthrough'
          }
        >
          {playback.requested ? <Pause size={16} /> : <Play size={16} />}{' '}
          {playback.requested ? 'Pause' : 'Resume'}
        </button>
      </div>
      <nav className="payment-stage-nav" aria-label="Sandbox payment stages">
        <ol>
          {stages.map((item, index) => (
            <li key={item.title}>
              <button
                aria-pressed={selected === index}
                aria-controls="payment-stage-evidence"
                onClick={() => choose(index)}
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
          onChange={(event) => choose(Number(event.target.value))}
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
        aria-live={playback.playing ? 'off' : 'polite'}
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
          <dt>Repeated reconciliation</dt>
          <dd>{payment.payment_confirmed_events} payment effect</dd>
        </div>
        <div>
          <dt>Recorded order status</dt>
          <dd>
            <Check size={15} />
            Demonstration handover recorded
          </dd>
        </div>
        <div>
          <dt>Physical delivery</dt>
          <dd>Not established</dd>
        </div>
      </dl>
      <p className="payment-record-note">
        A connected synthetic rehearsal with actual PayPal sandbox payment and a
        recorded demonstration handover. The earlier callback fixture is
        separate.{' '}
        <a href="https://github.com/Brikita/afracanet-input-finance/blob/main/docs/SPRINT_2026-11-02.md">
          Inspect the recorded evidence
        </a>
        .
      </p>
    </section>
  )
}
