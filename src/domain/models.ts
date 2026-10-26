export type Issue = {
  id: number
  category: string
  detail: string
  reported_by: string
  created_at: string
  resolved_at: string | null
  resolved_by: string | null
  resolution: string | null
}

export type Role = 'farmer' | 'lender' | 'supplier'
export type Session = {
  token: string
  role: Role
  subject: string
  name: string
}
export type Farmer = {
  id: string
  name: string
  location: string
  limit_cents?: number
  reserved_cents?: number
  spent_cents?: number
  approval_reference?: string
  expires_at?: string
}
export type Product = {
  id: string
  name: string
  unit: string
  price_cents: number
  stock: number
  reserved: number
  category: string
  revision: string
}
export type Line = {
  product_id: string
  quantity: number
  name?: string
  unit?: string
  price_cents?: number
}
export type Order = {
  id: number
  reference: string
  farmer_id: string
  items: Line[]
  amount_cents: number
  status: string
  currency: string
  invoice_id: string | null
  payment_reference: string | null
  pickup_code?: string
  payment_url?: string
  payment_mode: string
  created_at: string
  issues: Issue[]
}
export type State = {
  user: Omit<Session, 'token'>
  farmers: Farmer[]
  products: Product[]
  orders: Order[]
  payment_mode: string
  ai_mode: string
}
export type Event = {
  id: number
  actor: string
  action: string
  detail: string
  created_at: string
}
