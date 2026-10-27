export type FarmerMapping = {
  id: string
  source_farmer_id: string
  farmer_id: string
  source_system: 'afracanet-credit'
}

export type Decision = {
  schema_version: 1
  source_system: 'afracanet-credit'
  source_application_id: string
  source_farmer_id: string
  farmer_id: string
  lender_id: string
  approval_reference: string
  approved_by: string
  decision: 'LENDER_APPROVED'
  limit_cents: number
  currency: 'USD'
  approved_at: string
  expires_at: string
  data_provenance: 'real' | 'synthetic' | 'mixed' | 'unavailable'
}

export type DecisionPreview = {
  handoff: Decision
  farmer_name: string
  allocation_revision: string
  already_recorded: boolean
  revoked: boolean
  current_limit_cents: number
  committed_cents: number
}

export type HandoffRecord = {
  id: string
  farmer_id: string
  approval_reference: string
  payload: Decision
  transfer_method: 'manual_lender_review'
  recorded_by: string
  received_at: string
  revoked_at: string | null
  revocation_reason: string | null
}
