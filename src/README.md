# Frontend structure

`main.tsx` mounts the app and loads fonts/styles. `app/App.tsx` composes the shell,
navigation, role screens, feedback, and selected transaction.

| Boundary                                          | Ownership                                                       |
| ------------------------------------------------- | --------------------------------------------------------------- |
| `app/useWorkspace.ts`                             | Session lifecycle, polling, participant choices, shared actions |
| `app/WorkspaceHeader.tsx`, `WorkspaceHeading.tsx` | Navigation and contextual headings                              |
| `features/access/`                                | Demonstration sign-in screen                                    |
| `features/farmer/`                                | Input request, interpretation, session-scoped draft state       |
| `features/lender/`                                | Lender queue, credit graphic, selected case                     |
| `features/orders/`                                | Search, details, timeline, collection and recovery controls     |
| `features/approvals/`                             | Mapping, CSV import, decision entry/review, history/revocation  |
| `features/catalogue/`                             | Dealer catalogue editing                                        |
| `features/management/`                            | Role-specific records screen composition                        |
| `features/issues/`, `features/notifications/`     | Support and contact/outbox workflows                            |
| `domain/`, `lib/`, `components/`                  | Models/arithmetic, transport/formatting, accessible primitives  |
| `demo/participants.ts`                            | Explicit walkthrough identities                                 |

Keep role-sensitive decisions on the server. Frontend visibility helps people
understand actions; it is not an authorization boundary. Feature modules receive
an authenticated requester rather than storing tokens themselves.

Farmer draft state survives tab changes and resets with the authenticated
workspace. Features do not read session tokens directly or call providers.

`styles.css` is an ordered manifest. `styles/` separates tokens, foundations,
shell, records, approvals, farmer requests, order details, management, access,
and responsive overrides. Import order preserves the reviewed cascade.
Waterline's visual system is unchanged.

```powershell
npm run check:types
npm run check:format
npm run build
npm run test:ui
```
