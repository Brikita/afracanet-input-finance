import { useCallback, useEffect, useRef, useState } from 'react'
import type { Session, State } from '../domain/models'
import { api } from '../lib/api'
import { participants } from '../demo/participants'

export function useWorkspace() {
  const [session, setSession] = useState<Session | null>(() => {
    try {
      return JSON.parse(sessionStorage.getItem('afracanet-session') ?? 'null')
    } catch {
      return null
    }
  })
  const [accessCode, setAccessCode] = useState('afracanet-demo')
  const activeToken = useRef(session?.token ?? null)
  const [state, setState] = useState<State | null>(null)
  const [persona, setPersona] = useState('lender-demo')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [tab, setTab] = useState(
    new URLSearchParams(window.location.search).has('approval')
      ? 'people'
      : 'overview',
  )
  const [selected, setSelected] = useState<number | null>(null)

  const [choices, setChoices] =
    useState<{ id: string; name: string }[]>(participants)

  const refresh = useCallback(async () => {
    if (!session) return
    try {
      const next = await api<State>('/state', session.token)
      if (activeToken.current === session.token) setState(next)
    } catch (err) {
      if (activeToken.current === session.token)
        setError((err as Error).message)
    }
  }, [session])
  useEffect(() => {
    if (!session) return
    void refresh()
    const timer = window.setInterval(() => {
      void refresh()
    }, 6000)
    return () => clearInterval(timer)
  }, [refresh, session])
  const refreshChoices = useCallback(async () => {
    if (!session) return
    const next = await api<{ id: string; name: string }[]>(
      '/participants',
      session.token,
    )
    if (activeToken.current === session.token) setChoices(next)
  }, [session])
  useEffect(() => {
    void refreshChoices().catch(() => {})
  }, [refreshChoices])

  async function signIn(id: string) {
    setBusy(true)
    setError('')
    const previousState = state
    activeToken.current = null
    setState(null)
    setSelected(null)

    try {
      const next = await api<Session>('/session', undefined, {
        persona: id,
        access_code: accessCode,
      })
      if (session)
        await api('/session', session.token, undefined, 'DELETE').catch(
          () => {},
        )
      activeToken.current = next.token
      sessionStorage.setItem('afracanet-session', JSON.stringify(next))
      setSession(next)
      setState(null)
      setSelected(null)

      setTab(
        new URLSearchParams(window.location.search).has('approval')
          ? 'people'
          : 'overview',
      )
      setNotice('')
    } catch (err) {
      activeToken.current = session?.token ?? null
      setState(previousState)
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  async function signOut() {
    activeToken.current = null
    if (session)
      await api('/session', session.token, undefined, 'DELETE').catch(() => {})
    sessionStorage.removeItem('afracanet-session')
    setSession(null)
    setState(null)
    setSelected(null)
  }
  async function action(path: string, body: unknown = {}) {
    if (!session) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await api<{ message?: string }>(path, session.token, body)
      setNotice(result.message ?? 'Transaction updated.')
      await refresh()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function download() {
    if (!session) return
    setError('')
    try {
      const response = await fetch('/api/reconciliation.csv', {
        headers: { Authorization: 'Bearer ' + session.token },
      })
      if (!response.ok)
        throw new Error('Could not export reconciliation records.')
      const url = URL.createObjectURL(await response.blob())
      const link = document.createElement('a')
      link.href = url
      link.download = 'afracanet-reconciliation.csv'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const request = useCallback(
    <T>(path: string, body?: unknown, method?: string): Promise<T> => {
      if (!session) return Promise.reject(new Error('Sign in to continue.'))
      return api<T>(path, session.token, body, method)
    },
    [session],
  )

  return {
    session,
    state,
    accessCode,
    setAccessCode,
    persona,
    setPersona,
    error,
    setError,
    notice,
    setNotice,
    busy,
    setBusy,
    tab,
    setTab,
    selected,
    setSelected,
    choices,
    refresh,
    refreshChoices,
    signIn,
    signOut,
    action,
    download,
    request,
  }
}
