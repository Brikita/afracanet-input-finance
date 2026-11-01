// Adapted from Scroll Reveal Image by unlumen, retrieved via 21st.dev.
// https://21st.dev/@unlumen/components/scroll-reveal-image
import { useRef } from 'react'
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
} from 'framer-motion'

export function ScrollRevealImage({
  src,
  alt,
  className = '',
}: {
  src: string
  alt: string
  className?: string
}) {
  const target = useRef<HTMLDivElement>(null)
  const reduced = useReducedMotion()
  const { scrollYProgress } = useScroll({
    target,
    offset: ['start end', 'end start'],
  })
  const scale = useTransform(scrollYProgress, [0, 1], [1.12, 1])
  return (
    <div ref={target} className={`scroll-reveal-image ${className}`}>
      <motion.img
        src={src}
        alt={alt}
        loading="lazy"
        decoding="async"
        style={{ scale: reduced ? 1 : scale }}
      />
    </div>
  )
}
