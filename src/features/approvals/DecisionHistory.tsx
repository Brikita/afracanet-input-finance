import { useState } from 'react'
import type { Farmer } from '../../domain/models'
import type { Requester } from '../../lib/api'
import { money } from '../../lib/format'
import type { HandoffRecord } from './models'
type Props = {
  farmers: Farmer[]
  lenderId: string
  request: Requester
  onSaved: () => Promise<void>
}

export function DecisionHistory({
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
        Latest 100 decisions in this lender workspace. Each record identifies
        whether it arrived through signed delivery or manual lender review.
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
          <details
            className="handoff-history-record"
            key={record.id}
            open={
              new URLSearchParams(window.location.search).get('approval') ===
                record.approval_reference || undefined
            }
          >
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
                <dt>Transfer method</dt>
                <dd>
                  {record.transfer_method === 'signed_lender_decision'
                    ? 'Signed lender service'
                    : 'Manual review · source file not authenticated'}
                </dd>
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
                <dt>Evidence provenance</dt>
                <dd>{record.payload.data_provenance}</dd>
              </div>
              <div>
                <dt>Source officer</dt>
                <dd>{record.payload.approved_by}</dd>
              </div>
              <div>
                <dt>
                  {record.transfer_method === 'signed_lender_decision'
                    ? 'Receiving lender'
                    : 'Confirmed here by'}
                </dt>
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
