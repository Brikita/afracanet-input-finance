import { useRef, useState } from 'react'
import {
  ArrowRight,
  ExternalLink,
  FileSearch,
  Network,
  ShieldCheck,
  Pause,
  Play,
} from 'lucide-react'
import { useViewportPlayback } from './useViewportPlayback'
import { evidenceSources } from './evidenceSources'
import { GdsExplorer } from './GdsExplorer'
import graph from '../../../datasets/reports/connected-v1-store-verification.json'
import development from '../../../datasets/reports/development-v1-manifest.json'
import './evidence.css'

const positions = [
  { x: 135, y: 82 },
  { x: 135, y: 300 },
  { x: 135, y: 518 },
  { x: 865, y: 82 },
  { x: 865, y: 300 },
  { x: 865, y: 518 },
]

export function EvidenceStory() {
  const [selectedId, setSelectedId] =
    useState<(typeof evidenceSources)[number]['id']>('chama')
  const selected = evidenceSources.find((source) => source.id === selectedId)!
  const frame = useRef<HTMLDivElement>(null)
  const playback = useViewportPlayback(
    frame,
    () =>
      setSelectedId(
        (current) =>
          evidenceSources[
            (evidenceSources.findIndex((source) => source.id === current) + 1) %
              evidenceSources.length
          ].id,
      ),
    9000,
  )
  const number = (value: number) => value.toLocaleString('en-US')
  const creditUrl =
    import.meta.env.VITE_CREDIT_WORKSPACE_URL ||
    (import.meta.env.DEV
      ? 'http://127.0.0.1:5174/'
      : 'https://github.com/Brikita/afracanet-input-finance/tree/main/modules/credit-intelligence')

  return (
    <section
      className="product-evidence"
      id="evidence"
      aria-labelledby="evidence-title"
    >
      <div className="evidence-story-intro">
        <h2 id="evidence-title">
          A financial history.
          <br />
          Beyond collateral.
        </h2>
        <div>
          <p>
            AFRACANet is building an alternative credit scoring and assessment
            system for smallholder farmers and small businesses whose financial
            activity may be documented outside a conventional bank file.
          </p>
          <p>
            A missing title deed should not make credible chama contributions,
            SACCO repayments or business records invisible. The aim is to
            connect that evidence into a history a lender can inspect—not to
            promise a loan or replace the lender’s decision.
          </p>
        </div>
      </div>

      <div className="evidence-explorer-heading">
        <div>
          <h3>See how the records connect</h3>
          <p>
            Select a source to explore its role, its limits and what is
            available today.
          </p>
        </div>
        <span>Illustrative map · No live personal records</span>
      </div>
      <div className="presentation-playback evidence-playback">
        <span>
          {playback.requested
            ? 'The evidence tour starts as the map enters view.'
            : 'Evidence tour paused'}
        </span>
        <button
          onClick={playback.toggle}
          aria-label={
            playback.requested ? 'Pause evidence tour' : 'Resume evidence tour'
          }
        >
          {playback.requested ? <Pause size={16} /> : <Play size={16} />}{' '}
          {playback.requested ? 'Pause tour' : 'Resume tour'}
        </button>
      </div>
      <div className="evidence-explorer" data-ui="evidence-source-inspector">
        <div
          className="evidence-map"
          ref={frame}
          aria-label="Interconnected applicant evidence sources"
        >
          <svg
            className="evidence-connections"
            viewBox="0 0 1000 600"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            {evidenceSources.map((source, index) => (
              <line
                key={source.id}
                x1={positions[index].x}
                y1={positions[index].y}
                x2="500"
                y2="300"
                className={source.id === selectedId ? 'connection-active' : ''}
              />
            ))}
          </svg>
          <div className="evidence-applicant">
            <FileSearch size={30} aria-hidden="true" />
            <strong>One applicant</strong>
            <span>
              Farmer or
              <br />
              small business
            </span>
          </div>
          {evidenceSources.map((source, index) => (
            <button
              key={source.id}
              className={`evidence-source evidence-source-${index}`}
              aria-pressed={source.id === selectedId}
              aria-controls="evidence-source-detail"
              onClick={() => {
                setSelectedId(source.id)
                playback.restart()
              }}
            >
              <source.icon size={24} aria-hidden="true" />
              <span>
                <strong>{source.title}</strong>
                <small>{source.subtitle}</small>
              </span>
              <ArrowRight size={15} aria-hidden="true" />
            </button>
          ))}
        </div>
        <div
          className="evidence-source-detail"
          id="evidence-source-detail"
          role="region"
          aria-labelledby="source-detail-title"
          aria-live={playback.playing ? 'off' : 'polite'}
        >
          <selected.icon size={28} aria-hidden="true" />
          <h3 id="source-detail-title">{selected.title}</h3>
          <p className="evidence-contribution">{selected.contribution}</p>
          <details
            key={selected.id}
            onToggle={(event) => {
              if (event.currentTarget.open) playback.pause()
            }}
          >
            <summary>
              Follow this source, its limits and prototype status
            </summary>
            <dl>
              <div>
                <dt>How it connects</dt>
                <dd>{selected.connection}</dd>
              </div>
              <div>
                <dt>What it does not establish</dt>
                <dd>{selected.limit}</dd>
              </div>
              <div className="evidence-availability">
                <dt>Available in this prototype</dt>
                <dd>{selected.availability}</dd>
              </div>
            </dl>
          </details>
        </div>
      </div>

      <GdsExplorer />

      <div className="evidence-method">
        <div className="evidence-method-copy">
          <Network size={32} aria-hidden="true" />
          <h3>Where graph data science fits</h3>
          <p>
            A graph stores the relationships between people, organizations and
            records. Graph data science (GDS) applies algorithms to that
            structure to derive features for investigation and underwriting
            research.
          </p>
          <p>
            AFRACANet’s research direction includes PageRank for network
            structure and Louvain for community patterns. Neither algorithm
            produces a creditworthiness verdict by itself.
          </p>
          <div className="evidence-gds-status">
            <strong>Current status: graph retrieval is implemented.</strong>
            <p>
              GDS has not been run on the current development pack. No
              calibrated alternative credit score is active. Partner data,
              outcome validation and fairness testing are still needed before
              lending-model claims.
            </p>
          </div>
        </div>
        <details className="evidence-technical-detail">
          <summary>
            Read the algorithm notes and validation requirements
          </summary>
          <dl className="evidence-algorithms">
            <div>
              <dt>
                PageRank{' '}
                <a
                  href="https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/"
                  target="_blank"
                  rel="noreferrer"
                  aria-label="Read Neo4j PageRank documentation (opens a new tab)"
                >
                  <ExternalLink size={16} />
                </a>
              </dt>
              <dd>
                Measures a node’s importance within the chosen network. Its
                meaning depends on which relationships the graph contains.
                Network prominence is not proof of repayment ability.
              </dd>
            </div>
            <div>
              <dt>
                Louvain{' '}
                <a
                  href="https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/"
                  target="_blank"
                  rel="noreferrer"
                  aria-label="Read Neo4j Louvain documentation (opens a new tab)"
                >
                  <ExternalLink size={16} />
                </a>
              </dt>
              <dd>
                Identifies more densely connected communities. This can describe
                network structure; belonging to a community is not evidence that
                an applicant will default.
              </dd>
            </div>
            <div>
              <dt>From features to a score</dt>
              <dd>
                A useful lending model would also need verified records,
                observed outcomes, calibrated predictions and checks for unfair
                treatment. A large graph or an AI-generated explanation cannot
                substitute for that work.
              </dd>
            </div>
          </dl>
        </details>
      </div>

      <div className="evidence-authority">
        <h3>
          Evidence informs.
          <br />
          Lenders decide.
        </h3>
        <ol>
          <li>
            <strong>Connect the records</strong>
            <p>
              Confirm applicant references, source provenance and dates. Real
              partner onboarding would require permission and a way to correct
              inaccurate records.
            </p>
          </li>
          <li>
            <strong>Explain the evidence</strong>
            <p>
              The current AI summary cites supplied facts and identifies missing
              information. It has no score, approval or payment authority.
            </p>
          </li>
          <li>
            <strong>Make an explicit decision</strong>
            <p>
              The lender reviews the application, sets any approved terms and
              authorizes the handoff into input finance.
            </p>
          </li>
          <li>
            <strong>Follow the execution</strong>
            <p>
              Trace the input order, supplier invoice, verified PayPal payment
              and collection separately. Approval alone does not make an order
              paid.
            </p>
          </li>
        </ol>
      </div>

      <div className="evidence-development">
        <div>
          <h3>
            Synthetic histories.
            <br />
            Clearly labelled.
          </h3>
          <p>
            The prototype uses {number(graph.farmer_count)} fictional farmer
            profiles over {development.months} authored months, including{' '}
            {number(development.nodes_by_kind.SavingsGroup)} savings groups and{' '}
            {number(development.nodes_by_kind.Cooperative)} cooperatives.
          </p>
          <p>
            The connected graph contains {number(graph.graph_nodes)} nodes and{' '}
            {number(graph.graph_relationships)} relationships. These are
            software and workflow scenarios, not real borrowers, customer
            traction or validated lending outcomes.
          </p>
        </div>
        <div className="evidence-next-step">
          <ShieldCheck size={30} aria-hidden="true" />
          <h3>
            From records
            <br />
            to a pilot.
          </h3>
          <p>
            The next step is a partner-backed pilot: authentic records,
            permissioned access, officer review and measured outcomes. General
            small-business integrations remain an expansion of the agricultural
            prototype.
          </p>
          <a href={creditUrl}>
            Explore the credit module <ArrowRight size={17} />
          </a>
          <a href="/">
            Open input finance <ArrowRight size={17} />
          </a>
        </div>
      </div>
    </section>
  )
}
