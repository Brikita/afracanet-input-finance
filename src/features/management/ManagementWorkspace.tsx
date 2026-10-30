import { useState } from 'react'
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
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(0)
  const matches = state.farmers.filter((f) =>
    [f.id, f.name, f.approval_reference].some((value) =>
      value?.toLowerCase().includes(query.toLowerCase()),
    ),
  )
  const lastPage = Math.max(0, Math.ceil(matches.length / 50) - 1)
  const currentPage = Math.min(page, lastPage)
  const visibleFarmers = matches.slice(currentPage * 50, currentPage * 50 + 50)
  return (
    <section className="panel transaction-panel">
      <div className="section-title">
        <div>
          <h2>
            {role === 'lender' ? 'Farmer credit records' : 'Approved catalogue'}
          </h2>
          <p className="muted">
            {role === 'lender'
              ? 'Profiles and lender-authorized allocations. Credit intelligence is managed separately.'
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
      {role === 'lender' && (
        <div className="management-heading management-search">
          <label className="input-label">
            Find farmer record
            <input
              type="search"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                setPage(0)
              }}
              placeholder="Name, farmer ID, or approval reference"
            />
          </label>
          <p className="muted">
            {matches.length.toLocaleString()} matching records · 50 per page
          </p>
          <div className="management-buttons">
            <button
              className="button secondary"
              disabled={currentPage === 0}
              onClick={() => setPage(currentPage - 1)}
            >
              Previous
            </button>
            <span>
              Page {currentPage + 1} of {lastPage + 1}
            </span>
            <button
              className="button secondary"
              disabled={currentPage === lastPage}
              onClick={() => setPage(currentPage + 1)}
            >
              Next
            </button>
          </div>
        </div>
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
                {visibleFarmers.map((f) => (
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
