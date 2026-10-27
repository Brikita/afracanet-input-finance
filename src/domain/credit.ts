import type { Farmer } from './models'

export function allocationActive(farmer: Farmer, at = Date.now()) {
  return Boolean(
    farmer.expires_at && new Date(farmer.expires_at).getTime() > at,
  )
}

export function availableCredit(farmer: Farmer, at = Date.now()) {
  return allocationActive(farmer, at)
    ? Math.max(
        0,
        (farmer.limit_cents ?? 0) -
          (farmer.reserved_cents ?? 0) -
          (farmer.spent_cents ?? 0),
      )
    : 0
}
