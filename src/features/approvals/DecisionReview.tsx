import { useState } from 'react'
import type { Farmer } from '../../domain/models'
import type { Requester } from '../../lib/api'
import { CheckCircle2 } from 'lucide-react'
import { money } from '../../lib/format'
import { DecisionEntry } from './DecisionEntry'
import type { DecisionPreview, FarmerMapping } from './models'
type Props = {
  farmers: Farmer[]
  lenderId: string
  request: Requester
  onSaved: () => Promise<void>
}

export function DecisionReview({
  farmers,
  mappings,
  lenderId,
  request,
  onSaved,
}: Props & { mappings: FarmerMapping[] }) {
  const [text, setText] = useState('')
  const [preview, setPreview] = useState<DecisionPreview | null>(null)
  const [confirmed, setConfirmed] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  function edit(value: string) {
    setText(value)
    setPreview(null)
    setConfirmed(false)
    setError('')
    setNotice('')
  }

  async function upload(file?: File) {
    if (!file) return
    edit('')
    if (file.size > 20000) {
      setError('Choose a decision file smaller than 20 KB.')
      return
    }
    try {
      edit(await file.text())
    } catch {
      setError('Could not read the decision file. Choose it again.')
    }
  }

  async function reviewPayload(decision: unknown) {
    setBusy(true)
    setError('')
    setNotice('')
    setPreview(null)
    setConfirmed(false)
    try {
      const result = await request<DecisionPreview>(
        '/approval-handoffs/preview',
        decision,
      )
      setPreview(result)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  async function review(e: React.FormEvent) {
    e.preventDefault()
    try {
      await reviewPayload(JSON.parse(text))
    } catch {
      setPreview(null)
      setError('The decision file must contain valid JSON.')
    }
  }

  async function authorize() {
    if (!preview || !confirmed) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await request<{ message: string }>('/approval-handoffs', {
        handoff: preview.handoff,
        allocation_revision: preview.allocation_revision,
        confirm_lender_authorization: confirmed,
      })
      setNotice(result.message)
      setPreview(null)
      setText('')
      setConfirmed(false)
      await onSaved()
    } catch (err) {
      setError((err as Error).message)
      setPreview(null)
      setConfirmed(false)
    } finally {
      setBusy(false)
    }
  }

  const decision = preview?.handoff
  return (
    <section className="handoff-step" aria-labelledby="decision-heading">
      <h3 id="decision-heading">Review the lender decision</h3>
      <p className="muted">
        Record the terms of an existing lender approval. An AI recommendation is
        not a lender decision. KES amounts cannot be relabelled as USD.
      </p>
      <DecisionEntry
        farmers={farmers}
        mappings={mappings}
        lenderId={lenderId}
        busy={busy}
        onPreview={reviewPayload}
        onEdit={() => edit('')}
        onError={setError}
      />
      <details className="handoff-mappings">
        <summary>Import a prepared decision file instead</summary>
        <p className="fine-print">
          Use the version 1 handoff format. File transfer still requires your
          review and authorization below.
        </p>
        <form onSubmit={(e) => void review(e)}>
          <label className="input-label" htmlFor="handoff-file">
            Lender decision JSON file
          </label>
          <input
            id="handoff-file"
            type="file"
            accept=".json,application/json"
            disabled={busy}
            onChange={(e) => void upload(e.target.files?.[0])}
          />
          <label className="input-label" htmlFor="handoff-json">
            Or paste lender decision JSON
          </label>
          <textarea
            id="handoff-json"
            rows={5}
            maxLength={20000}
            value={text}
            disabled={busy}
            onChange={(e) => edit(e.target.value)}
          />
          <button className="button secondary" disabled={busy || !text.trim()}>
            Preview decision file
          </button>
        </form>
      </details>
      {error && (
        <div className="alert error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="alert notice" role="status">
          <CheckCircle2 size={17} aria-hidden="true" />
          {notice}
        </div>
      )}
      {preview && decision && (
        <div className="handoff-preview" aria-label="Lender decision preview">
          <h3>{preview.farmer_name}</h3>
          <dl className="handoff-facts">
            <div>
              <dt>Source application</dt>
              <dd>{decision.source_application_id}</dd>
            </div>
            <div>
              <dt>Farmer link</dt>
              <dd>
                {decision.source_farmer_id} → {decision.farmer_id}
              </dd>
            </div>
            <div>
              <dt>Decision reference</dt>
              <dd>{decision.approval_reference}</dd>
            </div>
            <div>
              <dt>Source officer (file claim)</dt>
              <dd>{decision.approved_by}</dd>
            </div>
            <div>
              <dt>Assessment provenance (file claim)</dt>
              <dd>{decision.data_provenance}</dd>
            </div>
            <div>
              <dt>Decision made</dt>
              <dd>{new Date(decision.approved_at).toLocaleString()}</dd>
            </div>
            <div>
              <dt>Current total allocation</dt>
              <dd>{money(preview.current_limit_cents)}</dd>
            </div>
            <div>
              <dt>Proposed total allocation</dt>
              <dd>{money(decision.limit_cents)} USD</dd>
            </div>
            <div>
              <dt>Reserved and paid</dt>
              <dd>{money(preview.committed_cents)}</dd>
            </div>
            <div>
              <dt>Decision expires</dt>
              <dd>{new Date(decision.expires_at).toLocaleString()}</dd>
            </div>
          </dl>
          {preview.already_recorded ? (
            <p className="alert notice" role="status">
              This exact decision is already recorded
              {preview.revoked ? ' and revoked' : ''}. It will not change the
              current allocation.
            </p>
          ) : (
            <>
              <label className="handoff-confirm">
                <input
                  type="checkbox"
                  checked={confirmed}
                  disabled={busy}
                  onChange={(e) => setConfirmed(e.target.checked)}
                />
                <span>
                  I have reviewed this lender decision and authorize this
                  allocation.
                </span>
              </label>
              <p className="fine-print">
                Reserved and paid amounts remain intact. This confirms an
                allocation only; every input order still needs its own approval
                and verified payment.
              </p>
              <button
                className="button primary"
                disabled={busy || !confirmed}
                onClick={() => void authorize()}
              >
                {busy ? 'Recording decision…' : 'Authorize reviewed allocation'}
              </button>
            </>
          )}
        </div>
      )}
    </section>
  )
}
