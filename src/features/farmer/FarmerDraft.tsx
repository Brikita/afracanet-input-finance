import { createContext, useContext, useState, type ReactNode } from 'react'

function useDraftState() {
  const [text, setText] = useState('')
  const [clarification, setClarification] = useState('')
  const [cart, setCart] = useState<Record<string, number>>({})
  const [requestId, setRequestId] = useState(() => crypto.randomUUID())
  return {
    text,
    setText,
    clarification,
    setClarification,
    cart,
    setCart,
    requestId,
    setRequestId,
  }
}

const FarmerDraft = createContext<ReturnType<typeof useDraftState> | null>(null)

/** Keep one participant's draft across workspace tabs; remount on identity change. */
export function FarmerDraftProvider({ children }: { children: ReactNode }) {
  const draft = useDraftState()
  return <FarmerDraft.Provider value={draft}>{children}</FarmerDraft.Provider>
}

export function useFarmerDraft() {
  const draft = useContext(FarmerDraft)
  if (!draft)
    throw new Error('Farmer requests require a workspace draft scope.')
  return draft
}
