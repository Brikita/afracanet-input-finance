import { useState } from 'react'
import { CircleHelp, CheckCircle2 } from 'lucide-react'

export type Issue = {
  id: number
  category: string
  detail: string
  reported_by: string
  created_at: string
  resolved_at: string | null
  resolved_by: string | null
  resolution: string | null
}

export function Issues({
  orderId,
  issues,
  role,
  request,
  onSaved,
}: {
  orderId: number
  issues: Issue[]
  role: string
  request: <T>(path: string, body?: unknown) => Promise<T>
  onSaved: () => Promise<void>
}) {
  const [reporting, setReporting] = useState(false)
  const [category, setCategory] = useState('stock')
  const [detail, setDetail] = useState('')
  const [requestId, setRequestId] = useState(() => crypto.randomUUID())
  const [resolutions, setResolutions] = useState<Record<number, string>>({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  async function report(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await request<{ message: string }>(
        `/orders/${orderId}/issues`,
        { category, detail, client_request_id: requestId },
      )
      setDetail('')
      setRequestId(crypto.randomUUID())
      setReporting(false)
      setNotice(result.message)
      await onSaved()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  async function resolve(id: number) {
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const result = await request<{ message: string }>(
        `/orders/${orderId}/issues/${id}/resolve`,
        { resolution: resolutions[id] },
      )
      setNotice(result.message)
      await onSaved()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }
  const open = issues.filter((issue) => !issue.resolved_at)
  return (
    <section className="issues-panel" aria-label="Order issues">
      <div className="management-heading">
        <h3>Issues & resolutions</h3>
        <button
          className="text-button"
          onClick={() => {
            setReporting(!reporting)
            setError('')
            setNotice('')
          }}
        >
          {reporting ? 'Close report form' : 'Report an issue'}
          <CircleHelp size={16} />
        </button>
      </div>
      {open.length > 0 && (
        <div className="issue-hold" role="status">
          {open.length} open issue{open.length === 1 ? '' : 's'}. Approval,
          invoicing, payment initiation, and collection are paused for lender
          review. Incoming payments are still reconciled.
        </div>
      )}
      {issues.map((issue) => (
        <article className="issue-record" key={issue.id}>
          <strong>
            {issue.category.charAt(0).toUpperCase() + issue.category.slice(1)} ·{' '}
            {issue.resolved_at ? 'Resolved' : 'Open'}
          </strong>
          <p>{issue.detail}</p>
          <small>
            {issue.reported_by} · {new Date(issue.created_at).toLocaleString()}
          </small>
          {issue.resolved_at ? (
            <div className="issue-resolution">
              <CheckCircle2 size={16} />
              <div>
                <p>{issue.resolution}</p>
                <small>
                  {issue.resolved_by} ·{' '}
                  {new Date(issue.resolved_at).toLocaleString()}
                </small>
              </div>
            </div>
          ) : (
            role === 'lender' && (
              <div>
                <label
                  className="input-label"
                  htmlFor={`resolution-${issue.id}`}
                >
                  Resolution for issue {issue.id}
                </label>
                <textarea
                  id={`resolution-${issue.id}`}
                  value={resolutions[issue.id] ?? ''}
                  maxLength={1000}
                  rows={2}
                  disabled={busy}
                  onChange={(e) =>
                    setResolutions({
                      ...resolutions,
                      [issue.id]: e.target.value,
                    })
                  }
                  placeholder="Record what was checked and agreed with the participants."
                />
                <p className="fine-print">
                  Resolving an issue records your operational decision. It does
                  not refund a payment, change credit, or record collection.
                </p>
                <button
                  className="button secondary full"
                  disabled={
                    busy || (resolutions[issue.id]?.trim().length ?? 0) < 5
                  }
                  onClick={() => void resolve(issue.id)}
                >
                  Record issue resolution
                </button>
              </div>
            )
          )}
        </article>
      ))}
      {reporting && (
        <form onSubmit={(e) => void report(e)} className="issue-report">
          <label className="input-label" htmlFor="issue-category">
            Issue category
          </label>
          <select
            id="issue-category"
            value={category}
            disabled={busy}
            onChange={(e) => {
              setCategory(e.target.value)
              setRequestId(crypto.randomUUID())
            }}
          >
            <option value="stock">Stock or inputs</option>
            <option value="payment">Payment</option>
            <option value="collection">Collection</option>
            <option value="other">Other</option>
          </select>
          <label className="input-label" htmlFor="issue-detail">
            Describe the issue
          </label>
          <textarea
            id="issue-detail"
            minLength={5}
            maxLength={1000}
            required
            rows={3}
            disabled={busy}
            value={detail}
            onChange={(e) => {
              setDetail(e.target.value)
              setRequestId(crypto.randomUUID())
            }}
            placeholder="What happened and what needs to be checked?"
          />
          <p className="fine-print">
            The farmer, lender, and dealer can see this report. Keep passwords,
            payment credentials, and sensitive personal information out of it.
          </p>
          <button
            className="button secondary full"
            type="submit"
            disabled={busy || detail.trim().length < 5}
          >
            Submit issue report
          </button>
        </form>
      )}
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
