import { useEffect, useState } from 'react'
import { MessageSquare, RefreshCw, ShieldCheck } from 'lucide-react'

type Preferences = {
  mode: 'demo' | 'sandbox'
  contact: {
    phone: string
    language: 'en' | 'sw'
    consented_at: string | null
    verified_at: string | null
  } | null
  messages: {
    id: number
    action: string
    body?: string
    mode: string
    status: string
    detail: string | null
    created_at: string
  }[]
}
type Props = {
  request: <T>(path: string, body?: unknown, method?: string) => Promise<T>
}

export function Notifications({ request }: Props) {
  const [state, setState] = useState<Preferences | null>(null)
  const [phone, setPhone] = useState('')
  const [language, setLanguage] = useState('en')
  const [consent, setConsent] = useState(false)
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function load(syncForm = false) {
    const next = await request<Preferences>('/sms')
    setState(next)
    if (syncForm && next.contact) {
      setPhone(next.contact.phone)
      setLanguage(next.contact.language)
      setConsent(Boolean(next.contact.consented_at))
    }
  }
  useEffect(() => {
    let active = true
    void request<Preferences>('/sms')
      .then((next) => {
        if (!active) return
        setState(next)
        if (next.contact) {
          setPhone(next.contact.phone)
          setLanguage(next.contact.language)
          setConsent(Boolean(next.contact.consented_at))
        }
      })
      .catch((err) => {
        if (active) setError(err.message)
      })
    return () => {
      active = false
    }
    // The workspace keys this component by session. Keep a draft while state polls elsewhere.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function perform(path: string, body: unknown = {}, method?: string) {
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await request<{ message: string }>(path, body, method)
      setNotice(result.message)
      setCode('')
      await load(true)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <section className="panel notifications-panel">
      <div className="section-title">
        <div>
          <h2>Farmer SMS updates</h2>
          <p className="muted">
            Order progress in English or Swahili, sent only after consent and
            number verification.
          </p>
        </div>
        <MessageSquare size={24} />
      </div>
      <div className="management-panel">
        <div className="mode-banner">
          <ShieldCheck size={17} />
          <span>
            {state?.mode === 'sandbox'
              ? "Africa's Talking sandbox · simulator only"
              : 'Local SMS previews · no messages leave this application'}
          </span>
        </div>
        <p className="fine-print">
          This channel sends updates about orders placed in the app. SMS
          ordering and USSD are not available. Neither mode delivers to a real
          handset.
        </p>
        {error && (
          <div className="alert error" role="alert">
            {error}
          </div>
        )}
        {notice && (
          <div className="alert notice" role="status">
            {notice}
          </div>
        )}
        {state?.contact && (
          <p className="contact-status">
            <strong>{state.contact.phone}</strong> ·{' '}
            {!state.contact.consented_at
              ? 'Updates turned off'
              : state.contact.verified_at
                ? 'Verified · updates enabled'
                : 'Awaiting number verification'}
          </p>
        )}
        <form
          onSubmit={(e) => {
            e.preventDefault()
            void perform('/sms/contact', { phone, language, consent }, 'PUT')
          }}
        >
          <div className="management-fields">
            <label className="input-label">
              Kenyan mobile number
              <input
                type="tel"
                value={phone}
                placeholder="+254700000001"
                pattern="\+254[17][0-9]{8}"
                required
                disabled={busy || !state}
                onChange={(e) => setPhone(e.target.value.trim())}
              />
            </label>
            <label className="input-label">
              Message language
              <select
                aria-label="Message language"
                value={language}
                disabled={busy || !state}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="sw">Kiswahili</option>
              </select>
            </label>
          </div>
          <label className="consent-label">
            <input
              type="checkbox"
              checked={consent}
              disabled={busy || !state}
              onChange={(e) => setConsent(e.target.checked)}
            />
            <span>
              I control this number and agree to receive order updates and
              collection codes. I can turn updates off here.
            </span>
          </label>
          <button
            type="submit"
            className="button primary"
            disabled={busy || !state}
          >
            Save SMS preferences
          </button>
        </form>
        {state?.contact?.consented_at && !state.contact.verified_at && (
          <form
            className="verification-form"
            onSubmit={(e) => {
              e.preventDefault()
              void perform('/sms/verify', { code })
            }}
          >
            <label className="input-label">
              Phone verification code
              <input
                inputMode="numeric"
                pattern="[0-9]{6}"
                maxLength={6}
                value={code}
                required
                disabled={busy}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
              />
            </label>
            <p className="fine-print">
              {state.mode === 'demo'
                ? 'Preview the queued verification SMS below, then enter its six-digit code. This demonstrates verification locally.'
                : "Send the queued verification SMS below and read its code in Africa's Talking's sandbox simulator."}{' '}
              Codes expire after ten minutes; five attempts are allowed.
            </p>
            <button
              type="submit"
              className="button secondary"
              disabled={busy || code.length !== 6}
            >
              Verify mobile number
            </button>
          </form>
        )}
        <div className="management-heading">
          <div>
            <h3>Message queue</h3>
            <p className="muted">
              Each update keeps its own processing record. Uncertain sends stay
              held for review.
            </p>
          </div>
          <button
            className="button secondary"
            disabled={busy}
            onClick={() => {
              void load().catch((err) => setError(err.message))
            }}
          >
            <RefreshCw size={15} /> Refresh messages
          </button>
        </div>
        <button
          className="button secondary"
          disabled={
            busy ||
            !state?.messages.some((message) => message.status === 'QUEUED')
          }
          onClick={() => void perform('/sms/dispatch')}
        >
          {state?.mode === 'sandbox'
            ? 'Send next SMS to sandbox'
            : 'Preview next queued SMS'}
        </button>
        <p className="fine-print">
          SIMULATED = local preview. ACCEPTED = sandbox gateway acceptance, not
          handset delivery. An interrupted SENDING or UNCERTAIN message requires
          operator review before another send.
        </p>
        <div className="message-list">
          {state?.messages.length === 0 && (
            <p className="muted">
              No updates yet. Save and verify a number, then follow an order.
            </p>
          )}
          {state?.messages.map((message) => (
            <article key={message.id}>
              <div>
                <strong>
                  {message.action.replaceAll('_', ' ').toLowerCase()}
                </strong>
                <span className="prototype-pill">{message.status}</span>
              </div>
              {message.body && <p className="sms-preview">{message.body}</p>}
              <p className="fine-print">
                {message.detail ??
                  (message.status === 'QUEUED'
                    ? 'Saved for processing.'
                    : 'Awaiting a confirmed processing outcome.')}{' '}
                · {new Date(message.created_at).toLocaleString()}
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
