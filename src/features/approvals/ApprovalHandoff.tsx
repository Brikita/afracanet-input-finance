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
