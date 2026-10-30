import type { State } from '../../domain/models'
import type { Requester } from '../../lib/api'
import { ApprovalImport } from '../approvals/ApprovalImport'
import { CatalogueEditor } from '../catalogue/CatalogueEditor'
import { ApprovalHandoff } from '../approvals/ApprovalHandoff'
import { availableCredit } from '../../domain/credit'
import { money } from '../../lib/format'
export function ManagementWorkspace({
  state,
  request,
  onSaved,
  onParticipantsChanged,
}: {
  state: State
  request: Requester
  onSaved: () => Promise<void>
  onParticipantsChanged: () => Promise<void>
}) {
  const role = state.user.role
  return (
    <section className="panel transaction-panel">
      <div className="section-title">
        <div>
          <h2>
            {role === 'lender' ? 'Pre-approved farmers' : 'Approved catalogue'}
          </h2>
          <p className="muted">
            {role === 'lender'
              ? 'Approvals supplied by the lender. Credit scoring is external.'
              : 'Illustrative inventory and prices. Reservations prevent concurrent over-ordering.'}
          </p>
        </div>
      </div>
      {role === 'lender' ? (
        <>
          <ApprovalHandoff
            key={'handoff-' + state.user.subject}
            farmers={state.farmers}
            lenderId={state.user.subject}
            request={request}
            onSaved={onSaved}
          />
          <ApprovalImport
            key={state.user.subject}
            request={request}
            onSaved={async () => {
              await onSaved()
              await onParticipantsChanged()
            }}
          />
        </>
      ) : (
        <CatalogueEditor
          key={state.user.subject}
          products={state.products}
          request={request}
          onSaved={onSaved}
        />
      )}
      <div className="table-scroll">
        <table className="management-table">
          {role === 'lender' ? (
            <>
              <thead>
                <tr>
                  <th>Farmer</th>
                  <th>Approval</th>
                  <th>Limit</th>
                  <th>Reserved</th>
                  <th>Paid to suppliers</th>
                  <th>Available</th>
                </tr>
              </thead>
              <tbody>
                {state.farmers.map((f) => (
                  <tr key={f.id}>
                    <td>
                      <strong>{f.name}</strong>
                      <small>{f.location}</small>
                    </td>
                    <td>
                      {f.approval_reference}
                      <small>
                        Expires{' '}
                        {f.expires_at
                          ? new Date(f.expires_at).toLocaleDateString()
                          : '—'}
                      </small>
                    </td>
                    <td>{money(f.limit_cents ?? 0)}</td>
                    <td>{money(f.reserved_cents ?? 0)}</td>
                    <td>{money(f.spent_cents ?? 0)}</td>
                    <td>
                      <strong>{money(availableCredit(f))}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </>
          ) : (
            <>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Unit price</th>
                  <th>On hand</th>
                  <th>Reserved</th>
                  <th>Available</th>
                </tr>
              </thead>
              <tbody>
                {state.products.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <strong>{p.name}</strong>
                      <small>{p.unit}</small>
                    </td>
                    <td>{money(p.price_cents)}</td>
                    <td>{p.stock}</td>
                    <td>{p.reserved}</td>
                    <td>{p.stock - p.reserved}</td>
                  </tr>
                ))}
              </tbody>
            </>
          )}
        </table>
      </div>
    </section>
  )
}
