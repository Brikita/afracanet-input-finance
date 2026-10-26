# Frontend structure

- `main.tsx`: fonts, global styles, and mounting the application.
- `app/`: session orchestration and workspace composition.
- `domain/`: shared API models and order-status vocabulary.
- `lib/`: API transport and display formatting.
- `components/`: shared presentation primitives.
- `features/`: management, issues, and notification workflows.

Keep role-sensitive decisions on the server. Frontend visibility helps people
understand actions; it is not an authorization boundary. Feature modules receive
an authenticated requester rather than storing tokens themselves.

The workspace composition is still being split into feature screens. This first
extraction preserves current interaction behavior ahead of the visual redesign.
