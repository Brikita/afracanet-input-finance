import { useEffect, useRef, useState } from 'react'
import { CheckCircle2, Link2 } from 'lucide-react'
import type { Farmer } from '../../domain/models'
import type { Requester } from '../../lib/api'
import { money } from '../../lib/format'
import type { DecisionPreview, FarmerMapping, HandoffRecord } from './models'
import { DecisionEntry } from './DecisionEntry'

type Props = {
  farmers: Farmer[]
  lenderId: string
  request: Requester
  onSaved: () => Promise<void>
}

export function ApprovalHandoff({
  farmers,
  lenderId,
  request,
  onSaved,
}: Props) {
  const [mappings, setMappings] = useState<FarmerMapping[]>([])
  const [records, setRecords] = useState<HandoffRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const requester = useRef(request)
  requester.current = request

  async function load() {
    setLoading(true)
    setLoadError('')
    try {
      const [mapped, history] = await Promise.all([
        requester.current<FarmerMapping[]>('/approval-mappings'),
        requester.current<HandoffRecord[]>('/approval-handoffs'),
      ])
      setMappings(mapped)
      setRecords(history)
    } catch (err) {
      setLoadError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let active = true
    Promise.all([
      requester.current<FarmerMapping[]>('/approval-mappings'),
      requester.current<HandoffRecord[]>('/approval-handoffs'),
    ])
      .then(([mapped, history]) => {
        if (active) {
          setMappings(mapped)
          setRecords(history)
        }
      })
      .catch((err: Error) => {
        if (active) setLoadError(err.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [lenderId])

  async function saved() {
    await Promise.all([load(), onSaved()])
  }

  return (
    <div className="management-panel handoff-workspace">
      <div className="management-heading">
        <div>
          <h3>Link a credit decision</h3>
          <p className="muted">
            Confirm the farmer, review the lender decision, then authorize its
            allocation here.
          </p>
        </div>
        <Link2 size={19} aria-hidden="true" />
      </div>
      <p className="handoff-disclosure">
        Manual lender review. Automatic transfer from credit intelligence is not
        connected. A file does not authenticate its sender or authorize credit
        by itself.
      </p>
      <p className="fine-print">
        Signed-in lender: {lenderId}. This prototype uses demonstration
        sessions; the source officer identity remains a claim in the reviewed
        file.
      </p>
      {loadError && (
        <div className="alert error" role="alert">
          {loadError}{' '}
          <button className="text-button" onClick={() => void load()}>
            Retry decision history
          </button>
        </div>
      )}
      {loading && (
        <p role="status" className="muted">
          Loading farmer links and decisions…
        </p>
      )}
      <MappingForm
        farmers={farmers}
        mappings={mappings}
        request={request}
        onSaved={saved}
      />
      <DecisionReview
        farmers={farmers}
        mappings={mappings}
        lenderId={lenderId}
        request={request}
        onSaved={saved}
      />
      <DecisionHistory
        records={records}
        farmers={farmers}
        request={request}
        onSaved={saved}
      />
    </div>
  )
}

function MappingForm({
  farmers,
  mappings,
  request,
  onSaved,
}: Omit<Props, 'lenderId'> & { mappings: FarmerMapping[] }) {
  const [sourceId, setSourceId] = useState('')
  const [farmerId, setFarmerId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function save(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    setNotice('')
    try {
      await request('/approval-mappings', {
        source_system: 'afracanet-credit',
        source_farmer_id: sourceId.trim(),
        farmer_id: farmerId,
      })
      setNotice('Farmer mapping confirmed. Matching names alone were not used.')
      setSourceId('')
      setFarmerId('')
      await onSaved()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="handoff-step" aria-labelledby="mapping-heading">
      <h3 id="mapping-heading">Confirm the farmer link</h3>
      <p className="muted">
        Use an opaque farmer reference from credit intelligence. Check it
        against your existing farmer record. Links cannot be silently
        reassigned.
      </p>
      <form onSubmit={(e) => void save(e)}>
        <div className="management-fields">
          <label className="input-label">
            Source farmer reference
            <input
              required
              maxLength={100}
              pattern="[A-Za-z0-9][A-Za-z0-9_.:\-]*"
              value={sourceId}
              disabled={busy}
              onChange={(e) => {
                setSourceId(e.target.value)
                setNotice('')
              }}
            />
          </label>
          <label className="input-label">
            Farmer in input finance
            <select
              required
              value={farmerId}
              disabled={busy}
              onChange={(e) => {
                setFarmerId(e.target.value)
                setNotice('')
              }}
            >
              <option value="">Choose a farmer</option>
              {farmers.map((farmer) => (
                <option key={farmer.id} value={farmer.id}>
                  {farmer.name} · {farmer.id}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="fine-print">
          If the farmer is missing, import their lender-approved profile below
          first. Do not use a phone number or national ID as the source
          reference.
        </p>
        {error && (
          <div className="alert error" role="alert">
            {error}
          </div>
        )}
        {notice && (
          <p className="alert notice" role="status">
            {notice}
          </p>
        )}
        <button
          className="button secondary"
          disabled={busy || !sourceId.trim() || !farmerId}
        >
          Confirm farmer mapping
        </button>
      </form>
      {mappings.length > 0 && (
        <details className="handoff-mappings">
          <summary>
            {mappings.length} confirmed farmer link
            {mappings.length === 1 ? '' : 's'}
          </summary>
          <ul>
            {mappings.map((mapping) => (
              <li key={mapping.id}>
                {mapping.source_farmer_id} → {mapping.farmer_id}
              </li>
            ))}
          </ul>
        </details>
      )}
    </section>
  )
}

function DecisionReview({
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

function DecisionHistory({
  records,
  farmers,
  request,
  onSaved,
}: Pick<Props, 'farmers' | 'request' | 'onSaved'> & {
  records: HandoffRecord[]
}) {
  const [selected, setSelected] = useState<string | null>(null)
  const [reason, setReason] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function revoke(e: React.FormEvent) {
    e.preventDefault()
    if (!selected) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await request<{ message: string }>(
        '/approval-handoffs/' + selected + '/revoke',
        { reason },
      )
      setNotice(result.message)
      setSelected(null)
      setReason('')
      await onSaved()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="handoff-step" aria-labelledby="handoff-history-heading">
      <h3 id="handoff-history-heading">Recorded lender decisions</h3>
      <p className="muted">
        Latest 100 decisions in this lender workspace. These are manually
        reviewed records; the source file is not independently authenticated.
      </p>
      {records.length === 0 && (
        <p className="fine-print">
          No linked decisions recorded yet. Existing CSV allocations remain
          separate.
        </p>
      )}
      {records.map((record) => {
        const current =
          farmers.find((farmer) => farmer.id === record.farmer_id)
            ?.approval_reference === record.approval_reference
        const expired =
          new Date(record.payload.expires_at).getTime() <= Date.now()
        return (
          <details className="handoff-history-record" key={record.id}>
            <summary>
              <strong>{record.approval_reference}</strong>
              <span>
                {record.revoked_at
                  ? 'Revoked'
                  : !current
                    ? 'Superseded'
                    : expired
                      ? 'Expired'
                      : 'Current allocation'}
              </span>
            </summary>
            <dl className="handoff-facts">
              <div>
                <dt>Farmer</dt>
                <dd>{record.farmer_id}</dd>
              </div>
              <div>
                <dt>Source application</dt>
                <dd>{record.payload.source_application_id}</dd>
              </div>
              <div>
                <dt>Source farmer</dt>
                <dd>{record.payload.source_farmer_id}</dd>
              </div>
              <div>
                <dt>Total allocation</dt>
                <dd>{money(record.payload.limit_cents)} USD</dd>
              </div>
              <div>
                <dt>Provenance (file claim)</dt>
                <dd>{record.payload.data_provenance}</dd>
              </div>
              <div>
                <dt>Source officer (file claim)</dt>
                <dd>{record.payload.approved_by}</dd>
              </div>
              <div>
                <dt>Confirmed here by</dt>
                <dd>{record.recorded_by}</dd>
              </div>
              <div>
                <dt>Recorded here</dt>
                <dd>{new Date(record.received_at).toLocaleString()}</dd>
              </div>
              <div>
                <dt>Handoff reference</dt>
                <dd>{record.id}</dd>
              </div>
            </dl>
            {record.revoked_at ? (
              <p className="fine-print">
                Revoked {new Date(record.revoked_at).toLocaleString()}:{' '}
                {record.revocation_reason}
              </p>
            ) : (
              <>
                {selected !== record.id ? (
                  <button
                    className="text-button"
                    disabled={busy}
                    onClick={() => {
                      setSelected(record.id)
                      setReason('')
                      setError('')
                      setNotice('')
                    }}
                  >
                    Review revocation for {record.approval_reference}
                  </button>
                ) : (
                  <form onSubmit={(e) => void revoke(e)}>
                    <p className="fine-print">
                      Revocation expires this allocation if it is still current.
                      It does not cancel existing invoices, reverse payments,
                      release reservations, or undo collection. Reconcile those
                      records separately.
                    </p>
                    <label className="input-label">
                      Reason for revoking {record.approval_reference}
                      <textarea
                        required
                        minLength={5}
                        maxLength={500}
                        value={reason}
                        disabled={busy}
                        onChange={(e) => setReason(e.target.value)}
                      />
                    </label>
                    <div className="management-buttons">
                      <button
                        className="button secondary"
                        disabled={busy || reason.trim().length < 5}
                      >
                        Revoke {record.approval_reference}
                      </button>
                      <button
                        className="text-button"
                        type="button"
                        disabled={busy}
                        onClick={() => setSelected(null)}
                      >
                        Keep decision
                      </button>
                    </div>
                  </form>
                )}
              </>
            )}
          </details>
        )
      })}
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
    </section>
  )
}
