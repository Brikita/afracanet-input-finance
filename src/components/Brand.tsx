import { Sprout } from 'lucide-react'

export function Brand({
  light = false,
  subtitle = 'Input finance',
}: {
  light?: boolean
  subtitle?: string
}) {
  return (
    <div className={'brand ' + (light ? 'brand-light' : '')}>
      <span className="brand-symbol">
        <Sprout size={24} />
      </span>
      <div>
        AFRACANet AI<small>{subtitle}</small>
      </div>
    </div>
  )
}
