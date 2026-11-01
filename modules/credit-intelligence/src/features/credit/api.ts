export type Officer = { token: string; officer_id: string; lender_id: string };
export type Application = {
  id: string;
  farmer_id: string;
  input_farmer_id: string;
  status: string;
  provenance: string;
  created_at: string;
};
export type Decision = {
  id: string;
  application_id: string;
  officer_id: string;
  decision: string;
  reason: string;
  terms: string;
  revoked_at: string | null;
};
export type Delivery = {
  id: string;
  decision_id: string;
  kind: string;
  status: string;
  attempts: number;
  last_error: string | null;
  next_attempt: string;
  receipt: string | null;
};
export type Workspace = {
  selected_application: Application | null;
  officer_id: string;
  lender_id: string;
  counts: Record<string, number>;
  applications: Application[];
  decisions: Decision[];
  deliveries: Delivery[];
  message: string;
  input_finance_url: string;
};
export type Context = {
  public_weather_context: {
    date: string;
    reference_point: string;
    precipitation_mm: number;
    attribution: string;
    limits: string;
  }[];
  profile: { display_name: string; scenario: string };
  relationship_count: number;
  provenance: string;
  explanation: string;
  relationship_types: { relationship: string; count: number }[];
  repayment_history: {
    available: boolean;
    reason?: string;
    currency?: string;
    loan_count?: number;
    principal_minor?: number;
    repaid_minor?: number;
    outstanding_minor?: number;
  };
  neighbors: { id: string; relationship: string; labels: string[] }[];
};
export type Advice = {
  headline: string;
  observations: { text: string; evidence_ids: string[] }[];
  missing_evidence: string[];
  model: string;
  provider: string;
  sources: { id: string; label: string; value: unknown }[];
};
const base = import.meta.env.VITE_CREDIT_API_URL || "http://127.0.0.1:8001";
export async function api<T>(
  path: string,
  officer: Officer | null,
  body?: unknown,
  method?: string,
): Promise<T> {
  const response = await fetch(base + "/api" + path, {
    method: method || (body === undefined ? "GET" : "POST"),
    headers: {
      "Content-Type": "application/json",
      ...(officer ? { Authorization: "Bearer " + officer.token } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok)
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : `Request failed (${response.status}). Check the fields and retry.`,
    );
  return data;
}
