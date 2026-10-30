import type { ReactNode } from 'react'
import { Brand } from '../../components/Brand'
import { participants } from '../../demo/participants'
import { ArrowRight, Check, CircleHelp, ShieldCheck } from 'lucide-react'

type Props = {
  persona: string
  setPersona: (value: string) => void
  accessCode: string
  setAccessCode: (value: string) => void
  busy: boolean
  signIn: (id: string) => Promise<void>
  banner: ReactNode
}
export function SignIn({
  persona,
  setPersona,
  accessCode,
  setAccessCode,
  busy,
  signIn,
  banner,
}: Props) {
  return (
    <div className="login-page">
      <section className="login-story">
        <Brand light />
        <div className="story-content">
          <h1>Credit, connected.</h1>
          <p>
            A shared path from approved agricultural credit to supplier payment
            and farmer collection.
          </p>
          <div className="story-proof">
            <ShieldCheck size={24} />
            <div>
              Every step, accounted for.
              <small>Farmer · Lender · Agro-dealer</small>
            </div>
          </div>
        </div>

        <footer>Built for agricultural finance in Kenya.</footer>
      </section>
      <section className="login-panel">
        <div className="login-top">
          <span className="prototype-pill">Working prototype</span>
          <span>Demonstration access</span>
        </div>
        <div className="login-form">
          <h2>Step into the workspace.</h2>
          <p>
            Choose a demonstration participant to follow the full input finance
            journey.
          </p>
          <div className="participant-options">
            {participants.slice(0, 3).map((p) => (
              <button
                key={p.id}
                className={
                  'participant-option ' + (persona === p.id ? 'chosen' : '')
                }
                onClick={() => setPersona(p.id)}
              >
                <p.icon size={21} />
                <span>
                  <strong>{p.label}</strong>
                  <small>{p.detail}</small>
                </span>
                <span className="radio-dot">
                  {persona === p.id && <Check size={12} />}
                </span>
              </button>
            ))}
          </div>
          <label className="input-label" htmlFor="access-code">
            Demo access code
          </label>
          <input
            id="access-code"
            type="password"
            value={accessCode}
            onChange={(e) => setAccessCode(e.target.value)}
          />
          {banner}
          <button
            className="button primary full"
            disabled={busy}
            onClick={() => void signIn(persona)}
          >
            {busy ? 'Opening workspace…' : 'Open workspace'}
            <ArrowRight size={18} />
          </button>
          <div className="demo-disclosure">
            <CircleHelp size={17} />
            <p>
              All participants, approvals, and prices are illustrative. The
              initial walkthrough simulates payments. PayPal sandbox and Gemini
              modes require server configuration.
            </p>
          </div>
        </div>
        <footer>
          AFRACANet AI <span>Input finance module · v0.1</span>
        </footer>
      </section>
    </div>
  )
}
