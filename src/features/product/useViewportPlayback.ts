import { useCallback, useEffect, useRef, useState, type RefObject } from 'react'

/** Presentation-only playback. It never invokes a financial or provider API. */
export function useViewportPlayback(
  target: RefObject<HTMLElement | null>,
  advance: () => void,
  interval: number,
  enabled = true,
) {
  const [inView, setInView] = useState(false)
  const [visible, setVisible] = useState(true)
  const [reduced, setReduced] = useState(false)
  const [paused, setPaused] = useState(false)
  const [optedIn, setOptedIn] = useState(false)
  const [revision, setRevision] = useState(0)
  const callback = useRef(advance)
  useEffect(() => {
    callback.current = advance
  }, [advance])
  useEffect(() => {
    const preference = matchMedia('(prefers-reduced-motion: reduce)')
    const update = () => setReduced(preference.matches)
    const visibility = () => setVisible(!document.hidden)
    update()
    visibility()
    preference.addEventListener('change', update)
    document.addEventListener('visibilitychange', visibility)
    const observer = new IntersectionObserver(
      ([entry]) =>
        setInView(entry.isIntersecting && entry.intersectionRatio >= 0.2),
      { threshold: [0, 0.2] },
    )
    if (target.current) observer.observe(target.current)
    return () => {
      observer.disconnect()
      preference.removeEventListener('change', update)
      document.removeEventListener('visibilitychange', visibility)
    }
  }, [target])
  const requested = !paused && (!reduced || optedIn)
  const playing = enabled && requested && inView && visible
  useEffect(() => {
    if (!playing) return
    const timer = setTimeout(() => {
      callback.current()
      setRevision((value) => value + 1)
    }, interval)
    return () => clearTimeout(timer)
  }, [playing, interval, revision])
  const restart = useCallback(() => setRevision((value) => value + 1), [])
  const pause = useCallback(() => setPaused(true), [])
  const resume = useCallback(() => {
    setPaused(false)
    setOptedIn(true)
    setRevision((value) => value + 1)
  }, [])
  const toggle = () => {
    if (requested) pause()
    else resume()
  }
  return { playing, requested, reduced, pause, resume, toggle, restart }
}
