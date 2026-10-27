import type { Farmer } from '../../domain/models'
import { money } from '../../lib/format'
import { availableCredit } from '../../domain/credit'

export function CreditAllocation({ farmers }: { farmers: Farmer[] }) {
  const total = farmers.reduce(
    (sum, farmer) => sum + (farmer.limit_cents ?? 0),
    0,
  )
  const reserved = farmers.reduce(
    (sum, farmer) => sum + (farmer.reserved_cents ?? 0),
    0,
  )
  const paid = farmers.reduce(
    (sum, farmer) => sum + (farmer.spent_cents ?? 0),
    0,
  )
  const available = farmers.reduce(
    (sum, farmer) => sum + availableCredit(farmer),
    0,
  )
  const unavailable = total - reserved - paid - available
  const parts = [
    {
      label: 'Available',
      value: available,
      className: 'credit-available',
    },
    { label: 'Reserved', value: reserved, className: 'credit-reserved' },
    { label: 'Paid to suppliers', value: paid, className: 'credit-paid' },
    ...(unavailable > 0
      ? [
          {
            label: 'Unavailable unused credit',
            value: unavailable,
            className: 'credit-unavailable',
          },
        ]
      : []),
  ]

  return (
    <section className="credit-allocation" aria-labelledby="credit-title">
      <div className="block-heading">
        <h2 id="credit-title">Where credit stands</h2>
        <span>{money(total)} allocated</span>
      </div>
      <div
        className="credit-track"
        role="img"
        aria-label={parts
          .map((part) => `${part.label}: ${money(part.value)}`)
          .join('. ')}
      >
        {total > 0 &&
          parts
            .filter((part) => part.value > 0)
            .map((part) => (
              <span
                key={part.label}
                className={part.className}
                style={{ flexGrow: part.value, flexBasis: 0 }}
              />
            ))}
      </div>
      <dl className="credit-legend">
        {parts.map((part) => (
          <div key={part.label}>
            <dt>
              <i className={part.className} aria-hidden="true" />
              {part.label}
            </dt>
            <dd>{money(part.value)}</dd>
          </div>
        ))}
      </dl>
      {unavailable > 0 && (
        <p className="fine-print">
          Expired or revoked unused credit is unavailable. Existing reservations
          and payments remain shown.
        </p>
      )}
      {!total && (
        <p className="muted">
          Import a lender-approved allocation to get started.
        </p>
      )}
    </section>
  )
}
