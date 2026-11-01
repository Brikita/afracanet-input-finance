import { useEffect, useRef, useState } from 'react'
import { Pause, Play, RotateCcw, StepForward } from 'lucide-react'
import './gds.css'

// Authored teaching network. This is never a borrower or lending-model result.
const nodes = [
  { label: 'Applicant A', x: 120, y: 100, cx: 140, cy: 140, group: 0 },
  { label: 'Chama A', x: 310, y: 70, cx: 280, cy: 100, group: 0 },
  { label: 'Contribution A', x: 530, y: 100, cx: 180, cy: 300, group: 0 },
  { label: 'Applicant B', x: 740, y: 80, cx: 420, cy: 180, group: 0 },
  { label: 'Cooperative A', x: 880, y: 180, cx: 350, cy: 280, group: 0 },
  { label: 'Receipt A', x: 180, y: 260, cx: 310, cy: 415, group: 0 },
  { label: 'Applicant C', x: 400, y: 245, cx: 620, cy: 100, group: 1 },
  { label: 'SACCO B', x: 600, y: 260, cx: 760, cy: 170, group: 1 },
  { label: 'Repayment B', x: 820, y: 360, cx: 720, cy: 330, group: 1 },
  { label: 'Applicant D', x: 100, y: 420, cx: 880, cy: 300, group: 1 },
  { label: 'Cooperative B', x: 350, y: 415, cx: 850, cy: 420, group: 1 },
  { label: 'Receipt B', x: 660, y: 440, cx: 680, cy: 440, group: 1 },
]
const edges = [
  [0, 1],
  [0, 4],
  [1, 2],
  [2, 1],
  [3, 1],
  [3, 4],
  [4, 5],
  [5, 4],
  [1, 4],
  [4, 1],
  [6, 7],
  [6, 10],
  [7, 8],
  [8, 7],
  [9, 7],
  [9, 10],
  [10, 11],
  [11, 10],
  [7, 10],
  [10, 7],
  [4, 7],
  [7, 4],
]
const iterations = 12

function nextRanks(previous: number[]) {
  const damping = 0.85
  const next = nodes.map(() => (1 - damping) / nodes.length)
  const out = nodes.map(
    (_, index) => edges.filter(([from]) => from === index).length,
  )
  previous.forEach((rank, index) => {
    if (!out[index])
      next.forEach((_, target) => {
        next[target] += (damping * rank) / nodes.length
      })
    else
      edges
        .filter(([from]) => from === index)
        .forEach(([, target]) => {
          next[target] += (damping * rank) / out[index]
        })
  })
  return next
}
const ranks = [nodes.map(() => 1 / nodes.length)]
for (let i = 0; i < iterations; i++) ranks.push(nextRanks(ranks[i]))

export function GdsExplorer() {
  const [mode, setMode] = useState<'rank' | 'community'>('rank')
  const [step, setStep] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [grouped, setGrouped] = useState(true)
  const [layout, setLayout] = useState(0)
  const [selected, setSelected] = useState(1)
  const [reduced, setReduced] = useState(false)
  const frame = useRef<HTMLDivElement>(null)
  const layoutValue = useRef(0)
  useEffect(() => {
    const preference = matchMedia('(prefers-reduced-motion: reduce)')
    const update = () => setReduced(preference.matches)
    update()
    preference.addEventListener('change', update)
    return () => preference.removeEventListener('change', update)
  }, [])
  useEffect(() => {
    const target = mode === 'community' && grouped ? 1 : 0
    if (Math.abs(layoutValue.current - target) < 0.001) return
    if (reduced) {
      layoutValue.current = target
      setLayout(target)
      return
    }
    const start = performance.now(),
      from = layoutValue.current
    let request = 0
    const animate = (time: number) => {
      const progress = Math.min(1, (time - start) / 850)
      const value = from + (target - from) * (1 - Math.pow(1 - progress, 4))
      layoutValue.current = value
      setLayout(value)
      if (progress < 1) request = requestAnimationFrame(animate)
    }
    request = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(request)
  }, [mode, grouped, reduced])
  useEffect(() => {
    if (!playing || mode !== 'rank') return
    if (step >= iterations) {
      setPlaying(false)
      return
    }
    const timer = setTimeout(() => setStep((value) => value + 1), 700)
    return () => clearTimeout(timer)
  }, [playing, step, mode])
  useEffect(() => {
    const stop = () => {
      if (document.hidden) setPlaying(false)
    }
    const observer = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) setPlaying(false)
    })
    if (frame.current) observer.observe(frame.current)
    document.addEventListener('visibilitychange', stop)
    return () => {
      observer.disconnect()
      document.removeEventListener('visibilitychange', stop)
    }
  }, [])
  const points = nodes.map((node) => ({
    x: node.x + (node.cx - node.x) * layout,
    y: node.y + (node.cy - node.y) * layout,
  }))
  const top = nodes
    .map((node, index) => ({ ...node, index, value: ranks[step][index] }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 3)
  function chooseMode(value: 'rank' | 'community') {
    setPlaying(false)
    setMode(value)
  }

  return (
    <div className="gds-explorer" ref={frame}>
      <div className="gds-intro">
        <h3>Watch the connections take shape.</h3>
        <p>
          Explore a teaching network before applying these ideas to a lending
          model.
        </p>
      </div>
      <div
        className="gds-mode-controls"
        role="group"
        aria-label="Graph concept"
      >
        <button
          aria-pressed={mode === 'rank'}
          onClick={() => chooseMode('rank')}
        >
          Network importance <span>PageRank</span>
        </button>
        <button
          aria-pressed={mode === 'community'}
          onClick={() => chooseMode('community')}
        >
          Community patterns <span>Louvain concept</span>
        </button>
      </div>
      <div className="gds-stage">
        <div className="gds-canvas">
          <div className="gds-data-label">
            Teaching example · {nodes.length} authored nodes · {edges.length}{' '}
            directed links
          </div>
          <div className="gds-graph-scroll">
            <svg
              viewBox="0 0 1000 540"
              aria-label="Interactive authored teaching network"
              role="group"
            >
              <defs>
                <marker
                  id="gds-direction"
                  markerWidth="6"
                  markerHeight="6"
                  refX="5"
                  refY="3"
                  orient="auto"
                  markerUnits="strokeWidth"
                >
                  <path d="M0,0 L6,3 L0,6 Z" fill="#7896a4" />
                </marker>
              </defs>
              {mode === 'community' && (
                <g
                  className="gds-community-fields"
                  style={{ opacity: layout }}
                  aria-hidden="true"
                >
                  <ellipse cx="270" cy="265" rx="225" ry="225" />
                  <ellipse cx="760" cy="270" rx="205" ry="225" />
                  <text x="150" y="35">
                    Illustrative group A
                  </text>
                  <text x="690" y="35">
                    Illustrative group B
                  </text>
                </g>
              )}
              <g aria-hidden="true">
                {edges.map(([from, to], index) => {
                  const a = points[from],
                    b = points[to],
                    dx = b.x - a.x,
                    dy = b.y - a.y,
                    distance = Math.hypot(dx, dy)
                  const startRadius =
                    (mode === 'rank' ? 14 + ranks[step][from] * 100 : 22) + 3
                  const endRadius =
                    (mode === 'rank' ? 14 + ranks[step][to] * 100 : 22) + 9
                  const sx = a.x + (dx / distance) * startRadius,
                    sy = a.y + (dy / distance) * startRadius
                  const tx = b.x - (dx / distance) * endRadius,
                    ty = b.y - (dy / distance) * endRadius
                  const curve = edges.some(([x, y]) => x === to && y === from)
                    ? 18
                    : 0
                  return (
                    <path
                      key={index}
                      d={`M${sx},${sy} Q${(a.x + b.x) / 2 - (dy / distance) * curve},${(a.y + b.y) / 2 + (dx / distance) * curve} ${tx},${ty}`}
                      markerEnd="url(#gds-direction)"
                      className={`gds-edge ${from === selected || to === selected ? 'gds-edge-selected' : ''}`}
                    />
                  )
                })}
              </g>
              {nodes.map((node, index) => (
                <g
                  key={node.label}
                  className={`gds-node gds-group-${node.group} ${selected === index ? 'gds-node-selected' : ''}`}
                  transform={`translate(${points[index].x} ${points[index].y})`}
                  role="button"
                  tabIndex={0}
                  aria-label={`Inspect ${node.label}`}
                  aria-pressed={selected === index}
                  onClick={() => setSelected(index)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      setSelected(index)
                    }
                  }}
                >
                  <circle
                    r={mode === 'rank' ? 14 + ranks[step][index] * 100 : 22}
                  />
                  <text y="52" textAnchor="middle">
                    {node.label}
                  </text>
                </g>
              ))}
            </svg>
          </div>
          <p className="gds-pan-hint">
            Scroll the network horizontally, or choose a node below.
          </p>
          <div className="gds-playback">
            {mode === 'rank' ? (
              <>
                <button
                  onClick={() => {
                    if (step === iterations) setStep(0)
                    setPlaying((value) => !value)
                  }}
                  aria-label={
                    playing
                      ? 'Pause PageRank animation'
                      : 'Play PageRank animation'
                  }
                >
                  {playing ? <Pause size={17} /> : <Play size={17} />}
                  {playing ? 'Pause' : 'Play'}
                </button>
                <button
                  onClick={() => {
                    setPlaying(false)
                    setStep((value) => Math.min(iterations, value + 1))
                  }}
                  disabled={step === iterations}
                >
                  <StepForward size={17} />
                  Step
                </button>
                <button
                  onClick={() => {
                    setPlaying(false)
                    setStep(0)
                  }}
                >
                  <RotateCcw size={16} />
                  Reset
                </button>
                <span>
                  Iteration {step} / {iterations}
                </span>
              </>
            ) : (
              <>
                <button onClick={() => setGrouped((value) => !value)}>
                  {grouped ? 'Show shared network' : 'Separate the groups'}
                </button>
                <span>Community labels are authored, not computed.</span>
              </>
            )}
          </div>
        </div>
        <div className="gds-reading">
          <h4>
            {mode === 'rank'
              ? 'Importance changes as links are followed.'
              : 'Connections can reveal groups.'}
          </h4>
          <p>
            {mode === 'rank'
              ? 'Start with equal importance. Each iteration redistributes it along directed links. The larger circles receive a larger share of this network’s PageRank.'
              : 'The same records move into two illustrative groups. Within-group relationships and the links between groups become easier to see. This arrangement explains the idea of community detection.'}
          </p>
          {mode === 'rank' ? (
            <ol
              className="gds-rank-list"
              aria-label="PageRank shares in the teaching network"
            >
              {top.map((node) => (
                <li key={node.label}>
                  <span>{node.label}</span>
                  <strong>{(node.value * 100).toFixed(1)}%</strong>
                </li>
              ))}
            </ol>
          ) : (
            <div className="gds-community-key">
              <span>
                Group A · {nodes.filter((node) => node.group === 0).length}{' '}
                nodes
              </span>
              <span>
                Group B · {nodes.filter((node) => node.group === 1).length}{' '}
                nodes
              </span>
            </div>
          )}
          <label htmlFor="gds-node-select">Inspect a teaching node</label>
          <select
            id="gds-node-select"
            value={selected}
            onChange={(event) => setSelected(Number(event.target.value))}
          >
            {nodes.map((node, index) => (
              <option key={node.label} value={index}>
                {node.label}
              </option>
            ))}
          </select>
          <p className="gds-selected-node">
            {nodes[selected].label}:{' '}
            {edges.filter(([from]) => from === selected).length} outgoing and{' '}
            {edges.filter(([, to]) => to === selected).length} incoming links.
          </p>
          <p className="gds-boundary">
            {mode === 'rank'
              ? 'Percentages are shares of importance in this example—not repayment probabilities or credit scores.'
              : 'These illustrative groups are manually assigned. No Louvain result, risk label or borrower classification is being claimed.'}
          </p>
        </div>
      </div>
      <p className="gds-caption">
        PageRank is computed on this small authored graph in the browser. This
        is an educational illustration, separate from the development dataset
        and the unvalidated lending model. Animation is optional; every step is
        available through the controls.
      </p>
    </div>
  )
}
