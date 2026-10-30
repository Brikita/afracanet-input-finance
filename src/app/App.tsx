import type { Order } from '../domain/models'
import { Brand } from '../components/Brand'
import { Feedback } from '../components/Feedback'
import { OverviewMetrics } from '../components/OverviewMetrics'
import { SignIn } from '../features/access/SignIn'
import { FarmerRequest } from '../features/farmer/FarmerRequest'
import { FarmerDraftProvider } from '../features/farmer/FarmerDraft'
import { OrderDetails } from '../features/orders/OrderDetails'
import { OrderQueue } from '../features/orders/OrderQueue'
import { ManagementWorkspace } from '../features/management/ManagementWorkspace'
import { LenderWorkspace } from '../features/lender/LenderWorkspace'
import { Notifications } from '../features/notifications/Notifications'
import { useWorkspace } from './useWorkspace'
import { WorkspaceHeader } from './WorkspaceHeader'
import { ModeBanner, WorkspaceHeading } from './WorkspaceHeading'

export function App() {
  const {
    session,
    state,
    tab,
    setTab,
    accessCode,
    setAccessCode,
    persona,
    setPersona,
    error,
    setError,
    notice,
    setNotice,
    busy,
    setBusy,
    selected,
    setSelected,
    choices,
    refresh,
    refreshChoices,
    signIn,
    signOut,
    action,
    download,
    request,
  } = useWorkspace()
  const banner = (
    <Feedback
      error={error}
      notice={notice}
      setError={setError}
      setNotice={setNotice}
    />
  )
  if (!session)
    return (
      <SignIn
        persona={persona}
        setPersona={setPersona}
        accessCode={accessCode}
        setAccessCode={setAccessCode}
        busy={busy}
        signIn={signIn}
        banner={banner}
      />
    )
  if (!state)
    return (
      <div className="loading">
        <Brand />
        <p>Opening your workspace…</p>
        {banner}
        <button className="button secondary" onClick={() => void signOut()}>
          Back to sign in
        </button>
      </div>
    )
  const role = session.role
  const current = state.orders.find((order) => order.id === selected)
  const onOpen = (order: Order) => setSelected(order.id)
  return (
    <FarmerDraftProvider key={session.token}>
      <div className="app-shell">
        <div
          className="main-shell"
          aria-hidden={current ? true : undefined}
          inert={Boolean(current)}
        >
          <a className="skip-link" href="#workspace-content">
            Skip to workspace
          </a>
          <WorkspaceHeader
            session={session}
            tab={tab}
            setTab={setTab}
            choices={choices}
            busy={busy}
            signIn={signIn}
            signOut={signOut}
          />
          <main id="workspace-content" tabIndex={-1}>
            <ModeBanner state={state} />
            {banner}
            <WorkspaceHeading state={state} tab={tab} download={download} />
            {tab === 'overview' && role === 'lender' && (
              <LenderWorkspace
                state={state}
                busy={busy}
                onOpen={onOpen}
                onAction={action}
                onAllocations={() => setTab('people')}
                onFarmer={() => void signIn('farmer-amina')}
              />
            )}
            {tab === 'overview' && role !== 'lender' && (
              <OverviewMetrics state={state} />
            )}
            {role === 'farmer' && tab === 'overview' && (
              <FarmerRequest
                state={state}
                busy={busy}
                setBusy={setBusy}
                request={request}
                onError={setError}
                onNotice={setNotice}
                onOpen={onOpen}
                onSaved={refresh}
              />
            )}
            {role === 'farmer' && tab === 'sms' && (
              <Notifications request={request} />
            )}
            {tab !== 'people' &&
              tab !== 'sms' &&
              !(role === 'lender' && tab === 'overview') && (
                <OrderQueue
                  state={state}
                  onOpen={onOpen}
                  onFarmer={() => signIn('farmer-amina')}
                />
              )}
            {tab === 'people' && (
              <ManagementWorkspace
                state={state}
                request={request}
                onSaved={refresh}
                onParticipantsChanged={refreshChoices}
              />
            )}
            <footer className="page-footer">
              <span>AFRACANet AI · Input Finance</span>
              <span>
                Illustrative data · One lender, one dealer network · v0.1
              </span>
            </footer>
          </main>
        </div>
        {current && (
          <OrderDetails
            key={session.token + ':' + current.id}
            state={state}
            current={current}
            busy={busy}
            request={request}
            action={action}
            onSaved={refresh}
            onClose={() => setSelected(null)}
            onError={setError}
            banner={banner}
          />
        )}
      </div>
    </FarmerDraftProvider>
  )
}
