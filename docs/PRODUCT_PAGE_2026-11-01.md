# AFRACANet product explanation — 1 November 2026

The public route now tells the shared credit-intelligence and input-finance
story. It inherits Waterline and uses scrolling, readable sections and
progressive disclosure rather than fitting every record into one viewport.

## What visitors can explore

- One stage at a time in the preserved USD 18 sandbox payment check, including
  the difference between callback delivery and physical collection.
- A six-source evidence map: chama contributions, SACCO/lender histories,
  cooperative deliveries, business activity, farm/climate context and execution
  records. Selecting a source explains its contribution; a disclosure exposes
  provenance, limitations and actual prototype availability.
- A twelve-node, twenty-two-link teaching network. PageRank is computed locally
  with damping 0.85 and twelve available iterations; visitors can play, step,
  pause, reset and inspect a node. Playback stops offscreen or when hidden.
- A bounded layout transition between the shared network and two authored
  communities. Those groups illustrate the community-detection concept; they are
  not computed Louvain results or applicant classifications.
- The lender's explicit authority, the current synthetic dataset and remaining
  requirements for partner records and a validated alternative credit model.

The PageRank explanation follows the official [Neo4j documentation](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/).
The community explanation links [Neo4j's Louvain documentation](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/).
The client-side teaching example does not introduce underwriting or a Neo4j/GDS
service into the execution backend.

## Data and authority

The broader vision includes farmers and small businesses without conventional
collateral. Today's working workflow focuses on agricultural input finance.
Real chama, SACCO and general small-business feeds are not connected; permissioned
partner onboarding and source verification remain work. The loaded development
graph has not had GDS run on it and provides no calibrated credit score.

Development counts come from committed dataset/store verification reports.
The payment record comes from separately committed, sanitized provider checks;
it is a historical snapshot, not a live order feed. It is separate from the
signed lender-workflow fixture. Physical collection was not recorded there.
No raw provider IDs, private records, credentials or payment URLs are exposed.

## Access and verification

Local route: `http://127.0.0.1:5173/about#evidence`.
`npm run build` produces both `dist/index.html` and `dist/about.html`; hosts without
an SPA rewrite can serve the latter directly. Configure the non-secret
`VITE_CREDIT_WORKSPACE_URL` at build time to link a hosted credit workspace.
Without it, production links the credit source repository; local development
uses port 5174. Stable public hosting remains separate deployment work.

The production build, strict TypeScript and formatting checks passed. Nine Edge
browser cases passed, including public-route API isolation, evidence exploration,
payment-stage boundaries, graph controls, offscreen pause, mobile reduced-motion
behavior and the six existing transaction journeys. One test's expected teaching
node degree was corrected from four incoming links to the actual five, then
that case passed on rerun.

Desktop (1440), tablet (768) and phone (390) captures showed no document overflow,
page errors or API requests on the public route. Narrow graph canvases scroll
horizontally and have a native node selector. Reduced motion snaps layout changes
while preserving controls and the same information. No raster assets ship.

The fresh Impeccable finish reviewer returned **ship**, with no material fixes,
against the user's revised, spacious scroll direction. The old dense comp is a
historical reference; it no longer imposes a first-viewport packing obligation.
