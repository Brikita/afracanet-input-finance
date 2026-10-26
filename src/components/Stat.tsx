import type { Wallet } from 'lucide-react'

export function Stat({
  icon: Icon,
  label,
  value,
  note,
}: {
  icon: typeof Wallet
  label: string
  value: string
  note: string
}) {
  return (
    <div className="stat-card">
      <div>
        <span>{label}</span>
        <Icon size={18} />
      </div>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  )
}
