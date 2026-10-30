import { CheckCircle2, X } from 'lucide-react'

type Props = {
  error: string
  notice: string
  setError: (value: string) => void
  setNotice: (value: string) => void
}
export function Feedback({ error, notice, setError, setNotice }: Props) {
  return (
    <>
      {error && (
        <div role="alert" className="alert error">
          {error}
          <button aria-label="Dismiss error" onClick={() => setError('')}>
            <X size={16} />
          </button>
        </div>
      )}
      {notice && (
        <div role="status" className="alert notice">
          <CheckCircle2 size={17} />
          {notice}
          <button aria-label="Dismiss notice" onClick={() => setNotice('')}>
            <X size={16} />
          </button>
        </div>
      )}
    </>
  )
}
