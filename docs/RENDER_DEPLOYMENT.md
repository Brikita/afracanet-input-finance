# Render deployment — 9 November 2026

The input application, public product page, credit API and credit static frontend
are deployed. Public routes and exact-origin CORS have been checked. This is a
working deployment under acceptance testing, not a claim of production readiness
or a completed hosted payment rehearsal.

- [Product page](https://afracanet-inputs.onrender.com/about)
- [Input finance](https://afracanet-inputs.onrender.com/)
- [Credit review](https://afracanet-credit.onrender.com/)
- [Credit API health](https://afracanet-credit-api.onrender.com/api/health)
- [Public evidence brief](PROJECT_EVIDENCE.md)

The private graph contains 1,746 entities and 3,405 relationships from the
verified 32-farmer synthetic fixture. Hosted PageRank/Louvain runs completed for
all four lender partitions with GDS 2.13.4. Each scoped membership projection has
11 nodes. These are descriptive analytics, not calibrated credit scores.

The hosted input API uses PayPal sandbox and Gemini. Its PayPal paid-invoice
callback is registered. Registration does not establish receipt of a genuine
hosted payment event: the new invoice/payment/collection rehearsal remains to be
verified. The credit module has its own Gemini key. No provider credentials,
private signing key or officer session is shared between the two services.

Hosted credit review has now exercised actual Gemini advice, explicit officer
authorization, one acknowledged signed handoff and the corresponding $180
illustrative input allocation. Input requests select one supplier before AI
interpretation; the server bounds the model catalogue and order items to that
selection. No hosted order or payment is claimed by these credit checks.

The initial preparation and container verification are historical checkpoints;
[container checks](https://github.com/Brikita/afracanet-input-finance/actions)
now also exercise a computed GDS result after import and retry.

## Hosted resources

| Resource          | Purpose                                                        | Deployed sizing                       |
| ----------------- | -------------------------------------------------------------- | ------------------------------------- |
| Input web/API     | Built React/public page and FastAPI execution API, same origin | 512 MB initially; 1 GB durable disk   |
| Credit web        | TanStack SPA shell on a free static site                       | No dedicated runtime                  |
| Credit API        | FastAPI officer/evidence/decision service                      | 512 MB initially; 1 GB durable disk   |
| Private Neo4j/GDS | Compact, isolated synthetic evidence graph                     | 2 GB RAM initially; 2 GB durable disk |

The runtime services use Oregon; the static frontend is distributed globally.
Memory sizing remains subject to runtime observation. Use
one instance per workflow API, and no autoscaling for the initial demonstration.
With persistent SQLite stores, do not scale to multiple independent replicas.
Render's current Blueprint identifiers include `0.5c-512mb` and `1c-2g`;
verify the account's quote rather than using older plan names blindly.

The selected configuration has a $40/month base: $7 input, $7 credit API,
$25 private graph and $1 total disks, before applicable tax or usage overages.
The free static frontend avoids the additional $7 Node runtime in the earlier
estimate. These are temporary demonstration resources; review actual charges
and memory use before extending or changing the deployment.

The private graph's auto-deploy included paths are
`modules/credit-intelligence/deploy/render/**` and `.dockerignore`. Changes to
the frontend or documentation therefore do not restart the database. Importer
code lives in the credit API image; running it remains an explicit operator step.

Render does not supply a native managed Neo4j database. A separately operated
private container (including a compatible GDS plugin) or an external graph
service supporting the required GDS calls is necessary. Do not assume an external
free Neo4j tier includes our GDS pipeline. Begin with the compact 32-farmer world,
not the large development graph. No live farmer information is involved.

## Prepared application images

Build context for every Dockerfile is the repository root:

```sh
docker build -f deploy/render/Dockerfile.inputs --build-arg VITE_CREDIT_WORKSPACE_URL=https://ACTUAL-CREDIT-WEB-HOST .
docker build -f deploy/render/Dockerfile.credit-api .
docker build -f deploy/render/Dockerfile.credit-web --build-arg VITE_CREDIT_API_URL=https://ACTUAL-CREDIT-API-HOST --build-arg VITE_INPUT_FINANCE_URL=https://ACTUAL-INPUT-HOST .
```

Replace the example host labels with assigned service URLs. The credit web build
sets `AFRACANET_DEPLOY_TARGET=node`; normal builds retain the original target.
The runtime entry is `.output/server/index.mjs`. Both Python images bind to
`0.0.0.0:$PORT`. The root image builds the existing public/payment-proof assets.
`.dockerignore` excludes local environments, keys, stores and generated media.
Docker is unavailable in the current shell; clean Linux container builds and
runtime smoke checks were verified by the linked GitHub Actions run.

The lower-cost credit web alternative uses a Render Static Site, with the credit
module as root directory. Build: `npm ci && AFRACANET_DEPLOY_TARGET=static npm run build`.
Publish `dist/client`, and rewrite `/*` to `/_shell.html` with status 200. Set
`VITE_CREDIT_API_URL` and `VITE_INPUT_FINANCE_URL` to the actual HTTPS service URLs
before building. Only that public client output is published; never publish
`dist/server`, private disks or local environments. A Node image remains an
optional alternative; do not create both frontends.

`bootstrap.py` creates 32 fictional farmers, fresh stock, zero active execution
credit/orders/payments and the labelled credit review cohorts from a newly built
fixture. It stores service state under `/var/data/afracanet`; mount separate
disks at `/var/data` in the two APIs. Restart preserves data, officer accounts
and the credit-only private signing key. Partial initialization or a changed
fixture fails closed and requires operator recovery/migration, rather than reset.
`public-trust.json` is the only key artifact transferred to input finance, through
a Render secret file and `CREDIT_TRUST_FILE`. Officer passwords stay in the credit
disk's operator-only `local-officer-accounts.json`; never expose them in logs.

The module-owned graph Dockerfile pins Neo4j 5.26.32 and checksum-verified GDS
2.13.4. Run it privately with a disk at `/data` and a fresh `NEO4J_AUTH` secret.
Configure credit's `WORKFLOW_NEO4J_*` against its internal Bolt address, then run
`python modules/credit-intelligence/scripts/seed_hosted_graph.py /app/fixture`
inside the credit API service. It imports one verified fixture transactionally,
preserves a matching completed import, and rejects unrelated graphs. Verify GDS
and evidence queries afterward. Do not publish graph HTTP/Bolt on the internet.

## Deployment and acceptance status

1. Deployed: the two APIs, free static frontend and private graph, with the
   persistent disks listed above. Public graph ports are not exposed.
2. Separate provider settings, public-key trust and the hosted callback are
   configured. The signing key remains on the credit disk.
3. Fresh service bootstrap, import retry and actual hosted GDS computations have
   been checked. After a further restart, verify saved decisions, analytics and
   transaction state through their authenticated APIs.
4. The input sign-in choices come from the public demonstration allowlist, not
   hardcoded local identities. `DEMO_STARTER_PERSONAS` accepts a JSON list of
   explicitly public fictional IDs. Hosted bootstrap selects its first synthetic
   lender, farmer and dealer; other imported profiles remain behind sign-in.
5. Verified: hosted evidence, GDS, Gemini advice, explicit decision, signed
   receipt and received allocation. Remaining acceptance: input interpretation
   within the selected supplier catalogue, new sandbox invoice/payment, genuine
   webhook delivery, reconciliation duplicates and recorded collection.
6. Capture actual browser operation, finish the revised 175-second video and
   update Devpost with verified access instructions and Render usage.

## Configuration and data ownership

- Input owns `DATABASE_URL`, `DEMO_ACCESS_CODE`, `ALLOWED_HOSTS`, PayPal sandbox
  credentials/webhook ID, its own Gemini key and public-key trust policy.
- Credit owns `CREDIT_DATABASE_URL`, `CREDIT_DATA_DIR`, its signing private key,
  local officer accounts, replay registry, graph access and its own Gemini key.
- Credit browser URLs (`VITE_*`) are public build-time configuration, never keys.
- Set explicit production CORS origins and continuation URLs. No localhost URLs
  may remain in browser requests after deployment.
- Do not upload either existing `.env`, a historical-source credential file,
  officer session, signing key or the paid local rehearsal database. Configure
  each hosted service's provider access separately in Render secret settings.
- Persist input transaction state and credit workflow state on separate disks.
  Never reset invoice-associated data during redeploy. Do not auto-seed credit
  or import replay payments as provider evidence.

## Hosting cost and lifetime

Claim the sponsor offer through the official resource page and verify the credit
balance, expiry and conditions in the owner account. The official sponsor page
advertises a one-time $50 offer; it is not free recurring hosting or a spending
cap. Keep account-specific billing and payment-method details out of this public
repository. The listed resources were created on 8 November after account-specific review and authorization.

Account-specific quotes and paid creation were reviewed before deployment. The
base service configuration is $40/month before applicable tax or usage overages.
Credits are not a spending cap. Keep access available through judging, ending
15 December 2026 at 19:00 Africa/Nairobi, and reassess the resources and charges
with the owner. No automatic shutdown is configured. Keep account balances,
card details and private budget approvals out of this repository.

Free Render web services have ephemeral local storage and cannot attach durable
disks. Free Postgres expires after 30 days. Avoid an arrangement where a restart
loses the order store while a PayPal invoice remains active.

## Hosted acceptance

### Recorded rehearsal update, 12 November 2026

The [hosted walkthrough](HOSTED_WALKTHROUGH.md) now identifies **AFC-000002**,
the new USD 18 sandbox order shown in the
[browser demonstration](https://www.youtube.com/watch?v=YEZz_objHR0).
The rehearsal observed PayPal-webhook payment confirmation and a subsequent
recorded collection. Separate repeat reconciliation/collection checks retained
one event per stage. See the [dated report](../datasets/reports/hosted-sandbox-2026-11-12.json).
This records the observed journey, not completion of every acceptance item
below or production readiness. AFC-000001 remains the older unpaid order.

All public HTTPS routes must work in an unauthenticated browser; transaction
actions must remain authenticated. Exercise the signed authorization, scoped
evidence, actual Gemini interpretation and new sandbox invoice/payment workflow
against fresh hosted stores. Verify repeated callbacks/reconciliation, stock and
credit balances, unpaid collection blocking, persistence after restart and
provider timeout recovery. Configure PayPal's hosted webhook URL and verify a
genuine event for that hosted scenario. Keep physical handover labelled a demo.

Then add the real demo URL and actual sponsor usage to Devpost, repeat the judge
journey and document any differences from the submitted video. Public submission
is already visible at https://devpost.com/software/afracanet-ai; old release docs
describing pre-submission status are historical checkpoints.

## Sponsor strategy

First deliver useful hosting on Render. A later Render Workflow could run bounded
evidence preparation or a read-only integrity report; it must not become lending
authorization or an additional automatic payment path. The resource guide
encourages Workflows, while prize eligibility in the rules is use of any Render
tool. Hosting does not guarantee a prize.

Next best product fit is an officer/reconciliation analytics dashboard with AG
Grid/Charts/Studio, scoped to the authenticated lender. The sponsor encourages
polished custom widgets, layout and its Agent Framework, beyond adding a table.
APIMatic could assist a real remaining PayPal integration change; record the
actual plugin/tool usage instead of retroactively crediting it for existing code.
Postman collections would make judge/operator API verification easier.

Bryntum fits a future dealer pickup/resource scheduler. Channel3 fits external
product discovery only if relevant agricultural inventory coverage is established;
discovery results cannot replace our supplier's trusted catalogue or stock.
Elastic could add evidence search, but requires another data service and access
boundary. Zapier fits consented notifications; Kernel fits browser agents;
Astropods fits a managed agent runtime. These are optional future integrations,
not current implementation claims. No extra sponsor is being added merely as a
tag. Rules allow at most one sponsor prize alongside a permitted main prize.

## Official references checked 5 November

- [Render offer and sponsor guide](https://paypalaihackathon.devpost.com/details/render)
- [Prize eligibility and multiple-prize limits](https://paypalaihackathon.devpost.com/rules)
- [Render free-service limitations](https://render.com/docs/free)
- [Blueprint specification](https://render.com/docs/blueprint-spec)
- [Pricing, to confirm in the account](https://render.com/pricing)
- [AG Grid](https://paypalaihackathon.devpost.com/details/aggrid)
- [APIMatic](https://paypalaihackathon.devpost.com/details/apimatic)
- [Postman](https://paypalaihackathon.devpost.com/details/postman)
- Other sponsors: https://paypalaihackathon.devpost.com/resources
