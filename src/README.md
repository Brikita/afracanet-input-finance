# Frontend structure

- `main.tsx`: fonts, global styles, and mounting the application.
- `app/`: session orchestration and workspace composition.
- `domain/`: shared API models, order-status vocabulary, and available-credit
  calculations that exclude expired/revoked unused credit.
- `lib/`: API transport and display formatting.
- `components/`: shared presentation primitives.
- `features/`: lender case flow, reviewed approval handoffs, management, issues,
  and notification workflows.

Keep role-sensitive decisions on the server. Frontend visibility helps people
understand actions; it is not an authorization boundary. Feature modules receive
an authenticated requester rather than storing tokens themselves.

The workspace composition is still being split into feature screens. This first
extraction preserves transaction behavior. Waterline supplies the current visual
system; new workflows inherit it rather than creating another theme.
