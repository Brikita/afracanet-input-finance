// Adapted from Aether Flow Hero by dhileepkumargm, retrieved via 21st.dev.
// https://21st.dev/@dhileepkumargm/components/aether-flow-hero
import { useEffect, useRef, useState } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { ArrowDown, ArrowRight, Pause, Play } from 'lucide-react'
import './aether-flow-hero.css'

type Particle = { x: number; y: number; vx: number; vy: number; size: number }

export default function AetherFlowHero() {
  const host = useRef<HTMLElement>(null)
  const canvas = useRef<HTMLCanvasElement>(null)
  const reduced = useReducedMotion()
  const [paused, setPaused] = useState(false)
  useEffect(() => {
    const element = canvas.current,
      section = host.current
    const context = element?.getContext('2d')
    if (!element || !section || !context) return
    let width = 0,
      height = 0,
      frame = 0,
      last = 0,
      inView = true,
      particles: Particle[] = []
    const pointer: { x: number | null; y: number | null } = { x: null, y: null }
    let seed = 1081
    const random = () => {
      seed = (seed * 16807) % 2147483647
      return (seed - 1) / 2147483646
    }
    const draw = () => {
      context.clearRect(0, 0, width, height)
      for (let a = 0; a < particles.length; a++) {
        const p = particles[a]
        context.fillStyle = 'rgba(157,219,180,.6)'
        context.beginPath()
        context.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        context.fill()
        for (let b = a + 1; b < particles.length; b++) {
          const q = particles[b],
            distance = Math.hypot(p.x - q.x, p.y - q.y)
          if (distance < 170) {
            context.strokeStyle = `rgba(128,194,159,${0.22 * (1 - distance / 170)})`
            context.lineWidth = 1
            context.beginPath()
            context.moveTo(p.x, p.y)
            context.lineTo(q.x, q.y)
            context.stroke()
          }
        }
      }
    }
    const animate = (time: number) => {
      if (time - last > 32) {
        const delta = Math.min(2, (time - last) / 33)
        last = time
        particles.forEach((p) => {
          if (p.x < 0 || p.x > width) p.vx *= -1
          if (p.y < 0 || p.y > height) p.vy *= -1
          if (pointer.x !== null && pointer.y !== null) {
            const dx = p.x - pointer.x,
              dy = p.y - pointer.y,
              d = Math.hypot(dx, dy)
            if (d > 1 && d < 130) {
              p.x += (dx / d) * (1 - d / 130) * 0.6
              p.y += (dy / d) * (1 - d / 130) * 0.6
            }
          }
          p.x += p.vx * delta
          p.y += p.vy * delta
        })
        draw()
      }
      frame = requestAnimationFrame(animate)
    }
    const start = () => {
      cancelAnimationFrame(frame)
      if (inView && !document.hidden && !paused && !reduced) {
        last = performance.now()
        frame = requestAnimationFrame(animate)
      } else draw()
    }
    const resize = () => {
      const bounds = section.getBoundingClientRect()
      width = bounds.width
      height = bounds.height
      const ratio = Math.min(devicePixelRatio || 1, 1.5)
      element.width = width * ratio
      element.height = height * ratio
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
      particles = Array.from(
        {
          length: Math.min(
            72,
            Math.max(24, Math.floor((width * height) / 15000)),
          ),
        },
        () => ({
          x: random() * width,
          y: random() * height,
          vx: (random() - 0.5) * 0.35,
          vy: (random() - 0.5) * 0.35,
          size: random() * 1.5 + 0.8,
        }),
      )
      draw()
    }
    const move = (event: PointerEvent) => {
      const bounds = section.getBoundingClientRect()
      pointer.x = event.clientX - bounds.left
      pointer.y = event.clientY - bounds.top
    }
    const leave = () => {
      pointer.x = null
      pointer.y = null
    }
    const observer = new IntersectionObserver(([entry]) => {
      inView = entry.isIntersecting
      start()
    })
    const resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(section)
    observer.observe(section)
    resize()
    start()
    section.addEventListener('pointermove', move)
    section.addEventListener('pointerleave', leave)
    document.addEventListener('visibilitychange', start)
    return () => {
      cancelAnimationFrame(frame)
      observer.disconnect()
      resizeObserver.disconnect()
      section.removeEventListener('pointermove', move)
      section.removeEventListener('pointerleave', leave)
      document.removeEventListener('visibilitychange', start)
    }
  }, [paused, reduced])
  return (
    <section className="aether-hero" ref={host} aria-labelledby="product-title">
      <canvas ref={canvas} className="aether-canvas" aria-hidden="true" />
      <div className="aether-copy">
        <motion.h1
          id="product-title"
          initial={reduced ? false : { opacity: 0.85, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          Connect the records.
          <br />
          <span>See the whole story.</span>
        </motion.h1>
        <p>
          Chama contributions. SACCO repayments. Business activity.
          <br className="aether-desktop-break" /> Financial histories a lender
          can review—and a path from authorized credit to agricultural inputs.
        </p>
        <div className="aether-actions">
          <a href="#evidence" className="aether-primary">
            Explore AFRACANet <ArrowDown size={18} />
          </a>
          <a href="/" className="aether-secondary">
            Open the prototype <ArrowRight size={18} />
          </a>
        </div>
        <p className="aether-scope">
          Development prototype · Synthetic histories · PayPal sandbox
        </p>
      </div>
      <div className="aether-bottom">
        <a href="#people">
          Meet the purpose <ArrowDown size={15} />
        </a>
        <button
          disabled={Boolean(reduced)}
          onClick={() => setPaused((value) => !value)}
          aria-label={
            reduced
              ? 'Hero motion disabled by your preference'
              : paused
                ? 'Resume hero background'
                : 'Pause hero background'
          }
        >
          {paused || reduced ? <Play size={14} /> : <Pause size={14} />}
          <span>
            {reduced
              ? 'Reduced motion'
              : paused
                ? 'Resume motion'
                : 'Pause motion'}
          </span>
        </button>
      </div>
    </section>
  )
}
