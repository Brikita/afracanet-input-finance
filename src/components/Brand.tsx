import { Sprout } from 'lucide-react'

export function Brand({ light = false }: { light?: boolean }) {
  return (
    <div className={'brand ' + (light ? 'brand-light' : '')}>
      <span className="brand-symbol">
        <Sprout size={24} />
      </span>
      <div>
        AFRACANet AI<small>INPUT FINANCE</small>
      </div>
    </div>
  )
}
