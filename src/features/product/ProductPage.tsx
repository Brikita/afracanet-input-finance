import {
  ArrowRight,
  FileCheck2,
  FileText,
  Leaf,
  Network,
  Receipt,
  ShieldCheck,
  Truck,
  Wallet,
} from 'lucide-react'
import { Brand } from '../../components/Brand'
import { EvidenceStory } from './EvidenceStory'
import { PaymentProof } from './PaymentProof'
import './product.css'

const flow = [
  {
    icon: FileCheck2,
    title: 'Connect the evidence',
    body: 'Review connected financial records, source provenance and missing facts.',
  },
  {
    icon: ShieldCheck,
    title: 'The lender authorizes',
    body: 'An officer explicitly approves terms and an expiry. An AI explanation cannot do this.',
  },
  {
    icon: FileText,
    title: 'Reserve the inputs',
    body: 'An approved input request reserves the available credit and supplier stock.',
  },
  {
    icon: Wallet,
    title: 'Verify the payment',
    body: 'Match the supplier invoice to actual PayPal payment records before enabling collection.',
  },
  {
    icon: Truck,
    title: 'Record the handover',
    body: 'The dealer verifies the farmer’s collection code and records physical collection.',
  },
  {
    icon: Receipt,
    title: 'Follow the record',
    body: 'Keep the actors, decisions, payment and collection linked without treating them as the same event.',
  },
]

export function ProductPage() {
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
          <Brand light subtitle="Credit & input finance" />
        </a>
        <nav aria-label="Product navigation">
          <a href="#how-it-works">How it works</a>
          <a href="#evidence">Evidence</a>
        </nav>
        <a className="product-open" href="/">
          Open prototype <ArrowRight size={17} />
        </a>
      </header>
      <main id="product-main">
        <section className="product-intro" aria-labelledby="product-title">
          <h1 id="product-title">
            A payment you can verify.
            <br />A case you can follow.
          </h1>
          <p>
            AFRACANet connects alternative credit evidence with
            lender-authorized input finance, supplier payment and recorded
            collection.
          </p>
          <ul className="product-benefits" aria-label="Platform principles">
            <li>
              <Network size={21} />
              Connected financial records
            </li>
            <li>
              <ShieldCheck size={21} />
              Explicit lender decisions
            </li>
            <li>
              <Leaf size={21} />
              Traceable input finance
            </li>
          </ul>
          <p className="product-demo-scope">
            Development prototype · Synthetic financial histories · PayPal
            sandbox
          </p>
        </section>
        <PaymentProof />
        <section
          className="product-workflow"
          id="how-it-works"
          aria-labelledby="workflow-title"
        >
          <h2 id="workflow-title">One journey. Distinct responsibilities.</h2>
          <p>
            Understand the evidence, authorize the finance, then follow what
            happens next.
          </p>
          <ol className="product-flow">
            {flow.map((step, index) => (
              <li key={step.title}>
                <span className="flow-number">{index + 1}</span>
                <step.icon size={28} aria-hidden="true" />
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </li>
            ))}
          </ol>
        </section>
        <EvidenceStory />
      </main>
      <footer className="product-footer">
        <Brand light subtitle="Credit & input finance" />
        <p>
          A development prototype for making financial histories reviewable and
          input finance traceable.
        </p>
        <div>
          <a href="https://github.com/Brikita/afracanet-green-path">
            Credit intelligence source
          </a>
          <a href="https://github.com/Brikita/afracanet-input-finance">
            Input finance source
          </a>
          <a href="#product-main">Back to the top</a>
        </div>
      </footer>
    </div>
  )
}
