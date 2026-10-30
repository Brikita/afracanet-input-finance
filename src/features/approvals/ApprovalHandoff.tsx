import { useEffect, useRef, useState } from 'react'
import { Link2 } from 'lucide-react'
import type { Farmer } from '../../domain/models'
import type { Requester } from '../../lib/api'
import type { FarmerMapping, HandoffRecord } from './models'
import { MappingForm } from './MappingForm'
import { DecisionReview } from './DecisionReview'
import { DecisionHistory } from './DecisionHistory'

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
  const reference = new URLSearchParams(window.location.search).get('approval')
  const historyPath =
    '/approval-handoffs' +
    (reference ? '?reference=' + encodeURIComponent(reference) : '')
  const [loadError, setLoadError] = useState('')
  const requester = useRef(request)
  requester.current = request

  async function load() {
    setLoading(true)
    setLoadError('')
    try {
      const [mapped, history] = await Promise.all([
        requester.current<FarmerMapping[]>('/approval-mappings'),
        requester.current<HandoffRecord[]>(historyPath),
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
      requester.current<HandoffRecord[]>(historyPath),
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
          <h3>Credit decisions</h3>
          <p className="muted">
            Follow a signed lender decision or review a manual handoff.
          </p>
        </div>
        <Link2 size={19} aria-hidden="true" />
      </div>
      <p className="handoff-disclosure">
        Signed service deliveries record authorized decisions automatically.
        Manual files require separate lender review and do not authenticate
        their sender.
      </p>
      <p className="fine-print">
        Signed-in lender: {lenderId}. This workspace uses demonstration
        sessions. Signed records identify the sending lender service; manual
        files retain their source officer as a claim.
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
      <DecisionHistory
        records={records}
        farmers={farmers}
        request={request}
        onSaved={saved}
      />
      <p>
        <a
          className="text-button"
          href={
            import.meta.env.VITE_CREDIT_WORKSPACE_URL ||
            'http://127.0.0.1:5174/'
          }
        >
          Open credit intelligence
        </a>
      </p>
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
    </div>
  )
}
