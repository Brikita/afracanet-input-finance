import {
  ArrowRight,
  Check,
  CircleCheck,
  Clock3,
  FileCheck2,
  FileText,
  FileSearch,
  GitBranch,
  Leaf,
  MailCheck,
  Network,
  Receipt,
  ShieldCheck,
  Truck,
  Wallet,
} from 'lucide-react'
import { Brand } from '../../components/Brand'
import payment from '../../../datasets/reports/paypal-sandbox-2026-10-31.json'
import callback from '../../../datasets/reports/paypal-callback-2026-10-31.json'
import './product.css'

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

const flow = [
  {
    icon: FileCheck2,
    title: 'Graph evidence',
    body: 'Inspect connected records, provenance and missing facts.',
  },
  {
    icon: ShieldCheck,
    title: 'Lender authorizes credit',
    body: 'An officer explicitly approves terms and an expiry.',
  },
  {
    icon: FileText,
    title: 'Supplier issues invoice',
    body: 'Approved inputs reserve credit and available stock.',
  },
  {
    icon: Wallet,
    title: 'PayPal confirms payment',
    body: 'Actual payment records establish the paid amount.',
  },
  {
    icon: Truck,
    title: 'Handover recorded',
    body: 'The dealer verifies the farmer’s collection code.',
  },
  {
    icon: Receipt,
    title: 'Traceable collection',
    body: 'Record the actor, time and linked order history.',
  },
]

export function ProductPage() {
  const amount = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: payment.currency,
    currencyDisplay: 'code',
  }).format(payment.amount_cents / 100)
  return (
    <div className="product-page">
      <a className="product-skip" href="#product-main">
        Skip to product information
      </a>
      <header className="product-header">
        <a
          className="product-brand"
          href="/about"
          aria-label="AFRACANet AI product information"
        >
          <Brand light />
        </a>
        <nav aria-label="Product navigation">
          <a href="#how-it-works">How it works</a>
          <a href="#evidence">Evidence</a>
          <a href="/">Open prototype</a>
        </nav>
        <a className="product-open" href="/">
          Open prototype <ArrowRight size={17} />
        </a>
      </header>
      <main id="product-main">
        <section className="product-intro" aria-labelledby="product-title">
          <div className="product-proposition">
            <h1 id="product-title">
              A payment you can verify.
              <br />A case you can follow.
            </h1>
            <p>
              Connect credit evidence, authorized input finance, supplier
              payment and collection in one traceable record. This is a
              development prototype using sandbox data.
            </p>
          </div>
          <div className="product-benefits">
            <div>
              <FileSearch size={42} />
              <h2>
                Verifiable
                <br />
                evidence
              </h2>
              <p>
                See each step
                <br />
                with records.
              </p>
            </div>
            <div>
              <Network size={42} />
              <h2>Clear decisions</h2>
              <p>
                Lender, supplier
                <br />
                and payments
                <br />
                linked.
              </p>
            </div>
            <div>
              <Leaf size={42} />
              <h2>
                Designed for
                <br />
                agriculture
              </h2>
              <p>
                Inputs, payment
                <br />
                and collection
                <br />
                in context.
              </p>
            </div>
          </div>
        </section>
        <section className="product-proof" aria-labelledby="proof-title">
          <div className="proof-heading">
            <div>
              <div className="proof-label">
                Verification record <span>Sandbox · Demo allocation</span>
              </div>
              <h2 id="proof-title">Input finance payment to supplier</h2>
              <p className="proof-reference">
                Actual provider check · 31 October 2026
              </p>
            </div>
            <dl className="proof-context">
              <dt>Credit context</dt>
              <dd>Isolated synthetic fixture</dd>
              <dt>Physical collection</dt>
              <dd>Not recorded</dd>
            </dl>
            <div className="proof-amount">
              <span>Verified payment</span>
              <strong>{amount}</strong>
              <p>PayPal sandbox check</p>
            </div>
          </div>
          <ol
            className="proof-stages"
            aria-label="Verified sandbox payment stages"
          >
            {stages.map((stage, index) => (
              <li
                key={stage.title}
                className={stage.verified ? 'is-verified' : 'is-pending'}
              >
                <div className="proof-step-number">{index + 1}</div>
                <h3>{stage.title}</h3>
                <p className="proof-step-caption">{stage.caption}</p>
                <div className="proof-step-detail">
                  <stage.icon size={32} aria-hidden="true" />
                  <h4>{stage.heading}</h4>
                  <p>{stage.body}</p>
                  <span className="proof-step-status">
                    {stage.verified ? (
                      <CircleCheck size={16} />
                    ) : (
                      <Clock3 size={16} />
                    )}
                    {stage.verified ? 'Verified' : 'Not recorded'}
                  </span>
                </div>
              </li>
            ))}
          </ol>
          <dl className="proof-metadata">
            <div>
              <dt>Provider</dt>
              <dd>PayPal sandbox</dd>
            </div>
            <div>
              <dt>Payment record</dt>
              <dd>Authenticated and matched</dd>
            </div>
            <div>
              <dt>Repeated delivery</dt>
              <dd>{callback.payment_effects} payment effect</dd>
            </div>
            <div>
              <dt>Amount</dt>
              <dd>{amount}</dd>
            </div>
            <div>
              <dt>Order status</dt>
              <dd>
                <span className="proof-ready">
                  <Check size={14} />
                  Ready for collection
                </span>
              </dd>
            </div>
          </dl>
        </section>
        <section
          className="product-workflow"
          id="how-it-works"
          aria-labelledby="workflow-title"
        >
          <h2 id="workflow-title">Evidence supports the decision</h2>
          <p>
            A connected record shows who acts, what authorizes the action and
            how the stages connect.
          </p>
          <ol className="product-flow">
            {flow.map((step, index) => (
              <li key={step.title}>
                <span className="flow-number">{index + 1}</span>
                <step.icon size={34} aria-hidden="true" />
                <h3>{step.title}</h3>
                <p>{step.body}</p>
                {index < flow.length - 1 && (
                  <ArrowRight
                    className="flow-arrow"
                    size={20}
                    aria-hidden="true"
                  />
                )}
              </li>
            ))}
          </ol>
        </section>
      </main>
    </div>
  )
}
