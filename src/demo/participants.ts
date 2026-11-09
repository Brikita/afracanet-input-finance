import { Package, Tractor, Wallet } from 'lucide-react'
import type { Role } from '../domain/models'

export type DemoParticipant = { id: string; name: string; role: Role }

/** Presentation copy only. Identities and organization names come from the API. */
export const participantRoles = [
  {
    role: 'lender',
    label: 'Lender workspace',
    detail: 'Approve, pay, and reconcile',
    icon: Wallet,
  },
  {
    role: 'farmer',
    label: 'Farmer experience',
    detail: 'Request and collect inputs',
    icon: Tractor,
  },
  {
    role: 'supplier',
    label: 'Agro-dealer workspace',
    detail: 'Invoice and fulfil orders',
    icon: Package,
  },
] as const
