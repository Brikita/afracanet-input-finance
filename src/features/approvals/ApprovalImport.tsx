import { useState } from 'react'
import { ArrowDownToLine, CheckCircle2 } from 'lucide-react'
import { money } from '../../lib/format'
import type { Requester } from '../../lib/api'
type Props = { request: Requester; onSaved: () => Promise<void> }
type Preview = {
  rows: {
    farmer_id: string
    name: string
    change: string
    limit_cents: number
    committed_cents: number
    expires_at: string
  }[]
  message: string
}
export function ApprovalImport({ request, onSaved }: Props) {
  const [csv, setCsv] = useState('')
  const [preview, setPreview] = useState<Preview | null>(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  async function upload(file?: File) {
    if (!file) return
    setPreview(null)
    setNotice('')
    setError('')
    if (file.size > 200_000) {
      setError('Choose a CSV smaller than 200 KB.')
      return
    }
    try {
      setCsv(await file.text())
    } catch {
      setError('Could not read this file. Choose it again.')
    }
  }
  function template() {
    const expiry = new Date(Date.now() + 90 * 86400000).toISOString()
    const content = `farmer_id,name,location,limit_cents,expires_at,approval_reference\nfarmer-example,Example Farmer,Nakuru,15000,${expiry},EXAMPLE-001\n`
    const url = URL.createObjectURL(new Blob([content], { type: 'text/csv' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'afracanet-approval-template.csv'
    link.click()
    URL.revokeObjectURL(url)
  }
  async function run(previewOnly: boolean) {
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await request<Preview>('/approvals/import', {
        csv_text: csv,
        preview: previewOnly,
      })
      if (previewOnly) setPreview(result)
      else {
        setPreview(null)
        setCsv('')
        setNotice(result.message)
        await onSaved()
      }
    } catch (err) {
      setPreview(null)
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="management-panel">
      <div className="management-heading">
        <div>
          <h3>Import lender approvals</h3>
          <p className="muted">
            Upload decisions already made by your lender. Limits are total
            allocations, including reserved and previously paid amounts.
          </p>
        </div>
        <button className="button secondary" onClick={template}>
          <ArrowDownToLine size={16} /> CSV template
        </button>
      </div>
      <label className="input-label" htmlFor="approval-file">
        Approval CSV file
      </label>
      <input
        id="approval-file"
        type="file"
        accept=".csv,text/csv"
        disabled={busy}
        onChange={(e) => void upload(e.target.files?.[0])}
      />
      <label className="input-label" htmlFor="approval-csv">
        Or paste approval CSV
      </label>
      <textarea
        id="approval-csv"
        rows={5}
        value={csv}
        maxLength={200000}
        disabled={busy}
        onChange={(e) => {
          setCsv(e.target.value)
          setPreview(null)
          setNotice('')
        }}
        placeholder="farmer_id,name,location,limit_cents,expires_at,approval_reference"
      />
      <p className="fine-print">
        USD whole cents: 15000 means $150.00. Use a future expiry with a
        timezone, e.g. 2027-01-31T23:59:59+03:00. Existing reservations and
        payments are preserved. Imported farmers become available in the demo
        participant switcher. Allocations linked to a reviewed source decision
        must be updated through the decision handoff above.
      </p>
      {error && (
        <div role="alert" className="alert error">
          {error}
        </div>
      )}
      {notice && (
        <div role="status" className="alert notice">
          <CheckCircle2 size={17} />
          {notice}
        </div>
      )}
      <div className="management-buttons">
        <button
          className="button secondary"
          disabled={busy || !csv.trim()}
          onClick={() => void run(true)}
        >
          Preview approvals
        </button>
        {preview && (
          <button
            className="button primary"
            disabled={busy}
            onClick={() => void run(false)}
          >
            Import {preview.rows.length} approval
            {preview.rows.length === 1 ? '' : 's'}
          </button>
        )}
      </div>
      {preview && (
        <div className="table-scroll">
          <p className="fine-print" role="status">
            {preview.message} Import rechecks credit before saving the entire
            batch.
          </p>
          <table>
            <thead>
              <tr>
                <th>FARMER</th>
                <th>CHANGE</th>
                <th>TOTAL LIMIT</th>
                <th>RESERVED + PAID</th>
                <th>EXPIRES</th>
              </tr>
            </thead>
            <tbody>
              {preview.rows.map((row) => (
                <tr key={row.farmer_id}>
                  <td>
                    <strong>{row.name}</strong>
                    <small>{row.farmer_id}</small>
                  </td>
                  <td>{row.change}</td>
                  <td>{money(row.limit_cents)}</td>
                  <td>{money(row.committed_cents)}</td>
                  <td>{new Date(row.expires_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
