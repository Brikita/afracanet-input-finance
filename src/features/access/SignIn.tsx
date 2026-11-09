import type { ReactNode } from 'react'
import { Brand } from '../../components/Brand'
import { participantRoles, type DemoParticipant } from '../../demo/participants'
import { ArrowRight, Check, CircleHelp, ShieldCheck } from 'lucide-react'

type Props = {
  persona: string
  entryPoints: DemoParticipant[]
  setPersona: (value: string) => void
  accessCode: string
  setAccessCode: (value: string) => void
  busy: boolean
  signIn: (id: string) => Promise<void>
  banner: ReactNode
}
export function SignIn({
  persona,
  entryPoints,
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
            {participantRoles.flatMap((p) => {
              const entry = entryPoints.find((item) => item.role === p.role)
              return entry
                ? [
                    <button
                      key={entry.id}
                      className={
                        'participant-option ' +
                        (persona === entry.id ? 'chosen' : '')
                      }
                      onClick={() => setPersona(entry.id)}
                    >
                      <p.icon size={21} />
                      <span>
                        <strong>{p.label}</strong>
                        <small>{p.detail}</small>
                        <small>{entry.name}</small>
                      </span>
                      <span className="radio-dot">
                        {persona === entry.id && <Check size={12} />}
                      </span>
                    </button>,
                  ]
                : []
            })}
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
            disabled={busy || !persona}
            onClick={() => void signIn(persona)}
          >
            {busy ? 'Opening workspace…' : 'Open workspace'}
            <ArrowRight size={18} />
          </button>
          <div className="demo-disclosure">
            <CircleHelp size={17} />
            <p>
              Participants and allocations are illustrative. The workspace
              identifies its payment and AI modes. A sandbox payment is a
              provider test; physical collection is recorded separately.
            </p>
          </div>
        </div>
        <footer>
          AFRACANet AI <a href="/about">About the platform</a>
        </footer>
      </section>
    </div>
  )
}
