import { useState } from 'react'
import type { Farmer } from '../../domain/models'
import type { Decision, FarmerMapping } from './models'

type Props = {
  farmers: Farmer[]
  mappings: FarmerMapping[]
  lenderId: string
  busy: boolean
  onPreview: (decision: Decision) => Promise<void>
  onEdit: () => void
  onError: (message: string) => void
}

export function DecisionEntry({
  farmers,
  mappings,
  lenderId,
  busy,
  onPreview,
  onEdit,
  onError,
}: Props) {
  const names = new Map(farmers.map((farmer) => [farmer.id, farmer.name]))
  const [form, setForm] = useState({
    mapping: '',
    application: '',
    reference: '',
    officer: '',
    amount: '',
    approved: '',
    expiry: '',
    provenance: '',
  })

  function change(key: keyof typeof form, value: string) {
    setForm({ ...form, [key]: value })
    onEdit()
  }

  async function review(e: React.FormEvent) {
    e.preventDefault()
    const mapping = mappings.find((row) => row.id === form.mapping)
    if (!mapping) {
      onError('Confirm and choose a farmer link first.')
      return
    }
    if (!/^\d+(\.\d{1,2})?$/.test(form.amount)) {
      onError('Enter a USD amount with at most two decimal places.')
      return
    }
    const [whole, fraction = ''] = form.amount.split('.')
    try {
      await onPreview({
        schema_version: 1,
        source_system: 'afracanet-credit',
        source_application_id: form.application,
        source_farmer_id: mapping.source_farmer_id,
        farmer_id: mapping.farmer_id,
        lender_id: lenderId,
        approval_reference: form.reference,
        approved_by: form.officer,
        decision: 'LENDER_APPROVED',
        limit_cents: Number(whole) * 100 + Number(fraction.padEnd(2, '0')),
        currency: 'USD',
        approved_at: new Date(form.approved).toISOString(),
        expires_at: new Date(form.expiry).toISOString(),
        data_provenance: form.provenance as Decision['data_provenance'],
      })
    } catch {
      onError('Check the decision dates and try again.')
    }
  }

  return (
    <form onSubmit={(e) => void review(e)}>
      <div className="management-fields">
        <label className="input-label">
          Linked farmer
          <select
            required
            disabled={busy || mappings.length === 0}
            value={form.mapping}
            onChange={(e) => change('mapping', e.target.value)}
          >
            <option value="">Choose a confirmed link</option>
            {mappings.map((mapping) => (
              <option key={mapping.id} value={mapping.id}>
                {names.get(mapping.farmer_id) ?? mapping.farmer_id} ·{' '}
                {mapping.source_farmer_id}
              </option>
            ))}
          </select>
        </label>
        {(
          [
            ['application', 'Source application reference', 'text'],
            ['reference', 'Lender decision reference', 'text'],
            ['officer', 'Officer recorded on decision', 'text'],
            ['amount', 'Total allocation (USD)', 'text'],
            ['approved', 'Decision made', 'datetime-local'],
            ['expiry', 'Allocation expiry', 'datetime-local'],
          ] as const
        ).map(([key, label, type]) => (
          <label className="input-label" key={key}>
            {label}
            <input
              required
              type={type}
              maxLength={100}
              inputMode={key === 'amount' ? 'decimal' : undefined}
              disabled={busy}
              value={form[key]}
              onChange={(e) => change(key, e.target.value)}
            />
          </label>
        ))}
        <label className="input-label">
          Assessment data provenance
          <select
            required
            disabled={busy}
            value={form.provenance}
            onChange={(e) => change('provenance', e.target.value)}
          >
            <option value="">Choose the recorded source</option>
            <option value="synthetic">Synthetic demonstration data</option>
            <option value="real">Real source records (lender supplied)</option>
            <option value="mixed">Mixed real and synthetic data</option>
            <option value="unavailable">Source data unavailable</option>
          </select>
        </label>
      </div>
      <p className="fine-print">
        Enter a decision already approved by your lender. The amount is the
        total ceiling, including reserved and paid credit. Dates use your local
        timezone. Real-source labels remain lender-supplied claims.
      </p>
      {mappings.length === 0 && (
        <p className="fine-print">
          Confirm the farmer link above to start this review.
        </p>
      )}
      <button
        className="button secondary"
        disabled={busy || mappings.length === 0}
      >
        Preview lender decision
      </button>
    </form>
  )
}
