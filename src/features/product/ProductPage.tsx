import { motion, useReducedMotion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Brand } from '../../components/Brand'
import { EvidenceStory } from './EvidenceStory'
import { PaymentProof } from './PaymentProof'
import AetherFlowHero from '../../components/ui/aether-flow-hero'
import { ScrollRevealImage } from '../../components/ui/scroll-reveal-image'
import './product.css'

const flow = [
  {
    title: 'Connect the evidence',
    body: 'Review connected financial records, source provenance and missing facts.',
  },
  {
    title: 'The lender authorizes',
    body: 'An officer explicitly approves terms and an expiry. An AI explanation cannot do this.',
  },
  {
    title: 'Reserve the inputs',
    body: 'An approved input request reserves the available credit and supplier stock.',
  },
  {
    title: 'Verify the payment',
    body: 'Match the supplier invoice to actual PayPal payment records before enabling collection.',
  },
  {
    title: 'Record the handover',
    body: 'The dealer verifies the farmer’s collection code and records physical collection.',
  },
  {
    title: 'Follow the record',
    body: 'Keep the actors, decisions, payment and collection linked without treating them as the same event.',
  },
]

export function ProductPage() {
  const reduced = useReducedMotion()
  const reveal = {
    initial: reduced ? (false as const) : { opacity: 0.85, y: 18 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true, amount: 0.25 },
    transition: {
      duration: 0.6,
      ease: [0.16, 1, 0.3, 1] as [number, number, number, number],
    },
  }

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
        <AetherFlowHero />
        <section
          className="product-purpose"
          id="people"
          aria-labelledby="purpose-title"
        >
          <div className="purpose-heading">
            <motion.h2 {...reveal} id="purpose-title">
              A fuller picture
              <br />
              of financial life.
            </motion.h2>
            <motion.p {...reveal}>
              For a farmer or small business, a conventional credit file may
              tell only part of the story. Savings groups, cooperatives and
              everyday trading can hold evidence that deserves a closer look.
            </motion.p>
          </div>
          <figure className="purpose-photo">
            <ScrollRevealImage
              src="/images/mount-kenya-farmer.jpg"
              alt="A woman tending crops on a farm in the Mount Kenya region"
            />
            <figcaption>
              Mount Kenya region, 2010 · Neil Palmer / CIAT ·{' '}
              <a href="https://commons.wikimedia.org/wiki/File:Woman_farmer_in_Kenya.jpg">
                CC BY-SA 2.0 photograph
              </a>
              . Contextual photography; not an AFRACANet customer.
            </figcaption>
          </figure>
          <div className="purpose-closing">
            <p>
              Our starting point is simple: make credible records visible,
              connected and reviewable.
            </p>
            <a href="#evidence">
              Explore the evidence <ArrowRight size={19} />
            </a>
          </div>
        </section>
        <EvidenceStory />
        <section className="product-lives" aria-labelledby="lives-title">
          <div>
            <motion.h2 {...reveal} id="lives-title">
              Built around
              <br />
              working lives.
            </motion.h2>
            <motion.p {...reveal}>
              The vision reaches from a farmer’s cooperative to a trader’s
              business records. Each source needs consent, provenance and a
              clear explanation of what it can—and cannot—establish.
            </motion.p>
            <p>
              These photographs show the world the project aims to serve.
              Partner records and customer deployments remain future work.
            </p>
          </div>
          <figure>
            <ScrollRevealImage
              src="/images/kenya-farming-group.jpg"
              alt="Women smallholder farmers tending a cultivated plot in Machakos, Kenya"
            />
            <figcaption>
              Mbini Self-Help Group, 2010 · McKay Savage ·{' '}
              <a href="https://commons.wikimedia.org/wiki/File:Women_smallholder_farmers_in_Kenya.jpg">
                CC BY 2.0
              </a>
            </figcaption>
          </figure>
          <figure>
            <ScrollRevealImage
              src="/images/nairobi-market-vendor.jpg"
              alt="A woman at a market in Nairobi"
            />
            <figcaption>
              Nairobi market · Charles Lichinga ·{' '}
              <a href="https://www.pexels.com/photo/smiling-african-woman-at-kenyan-market-33569521/">
                Pexels photograph
              </a>
            </figcaption>
          </figure>
        </section>
        <section
          className="product-workflow"
          id="how-it-works"
          aria-labelledby="workflow-title"
        >
          <motion.h2 {...reveal} id="workflow-title">
            One journey. Distinct responsibilities.
          </motion.h2>
          <motion.p {...reveal}>
            Understand the evidence, authorize the finance, then follow what
            happens next.
          </motion.p>
          <ol className="product-flow">
            {flow.map((step) => (
              <li key={step.title}>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </li>
            ))}
          </ol>
        </section>
        <PaymentProof />
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
