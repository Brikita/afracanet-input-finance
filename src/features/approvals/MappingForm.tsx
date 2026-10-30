import { useState } from 'react'
import type { Farmer } from '../../domain/models'
import type { Requester } from '../../lib/api'
import type { FarmerMapping } from './models'
type Props = {
  farmers: Farmer[]
  lenderId: string
  request: Requester
  onSaved: () => Promise<void>
}

export function MappingForm({
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
