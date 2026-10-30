import { Package, Tractor, Users, Wallet } from 'lucide-react'

/** Explicit local walkthrough identities, not operational organization records. */
export const participants = [
  {
    id: 'lender-demo',
    name: 'Demo Agricultural SACCO',
    label: 'Lender workspace',
    detail: 'Approve, pay, and reconcile',
    icon: Wallet,
  },
  {
    id: 'farmer-amina',
    name: 'Amina Wanjiku',
    label: 'Farmer experience',
    detail: 'Request and collect inputs',
    icon: Tractor,
  },
  {
    id: 'supplier-demo',
    name: 'Demo Green Valley Agrovet',
    label: 'Agro-dealer workspace',
    detail: 'Invoice and fulfil orders',
    icon: Package,
  },
  {
    id: 'farmer-kiptoo',
    name: 'David Kiptoo',
    label: 'Second farmer',
    detail: 'Explore a different credit limit',
    icon: Users,
  },
]
