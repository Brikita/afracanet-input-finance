import { labels } from '../domain/orderStatus'

export function Status({ status }: { status: string }) {
  return (
    <span className={'status status-' + status.toLowerCase()}>
      <span />
      {labels[status] ?? status}
    </span>
  )
}
