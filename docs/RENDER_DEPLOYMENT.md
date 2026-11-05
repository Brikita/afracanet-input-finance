# Render deployment preparation - 5 November 2026

Status: local frontend/type/backend checks passed. All four Linux container
builds, production entry points, the static credit build, actual GDS version and
private graph import/retry passed in [container checks](https://github.com/Brikita/afracanet-input-finance/actions/runs/41998840097).
Synthetic service bootstrap/restart checks pass locally. Cloud acceptance remains.
No Render resources have been created and no sponsor usage is claimed yet.
The owner selected sponsor credits and requires the actual cost confirmed before
creating paid services. Do not click Deploy/Create paid resources from this plan.

## Intended hosted product

| Resource          | Purpose                                                        | Candidate sizing, to validate         |
| ----------------- | -------------------------------------------------------------- | ------------------------------------- |
| Input web/API     | Built React/public page and FastAPI execution API, same origin | 512 MB initially; 1 GB durable disk   |
| Credit web        | TanStack SPA shell on a free static site                       | No dedicated runtime                  |
| Credit API        | FastAPI officer/evidence/decision service                      | 512 MB initially; 1 GB durable disk   |
| Private Neo4j/GDS | Compact, isolated synthetic evidence graph                     | 2 GB RAM initially; 2 GB durable disk |

These are candidates, not measured cloud memory requirements. Use one region,
one instance per workflow API, and no autoscaling for the initial demonstration.
With persistent SQLite stores, do not scale to multiple independent replicas.
Render's current Blueprint identifiers include `0.5c-512mb` and `1c-2g`;
verify the account's quote rather than using older plan names blindly.

The first estimate used a paid Node server for credit web: $7 + $7 + $7 + $25
compute and four total GB of disks at $0.25/GB = $47/month. A successful static
build now removes that extra $7 runtime. The revised candidate is $40/month
($7 input, $7 credit API, $25 graph, $1 disks), before tax/usage overages. Published
rates were read in Render's live pricing page on 5 November; this is an estimate,
not an account-specific approved quote or a requirement to buy this architecture.
Do not create paid resources until the operator has reviewed the final setup and
its actual account quote, including ongoing costs after credits are exhausted.

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

## Deployment sequence and remaining work

1. Completed: clean Linux image builds, API health/web routes, both `/about` and
   `/about.html`, GDS 2.13.4, private Bolt connectivity and graph import retry.
   The application suite also passed on the preparation commit.
2. Review the actual compute/disk quotes and credit conditions before creating
   paid resources. All graph ports must remain private. No resource is approved
   merely because its draft form has a selected compute tier.
3. Configure the two separate persistent disks. Bootstrap generates the signing
   key only in credit storage. Transfer only public verification/trust policy
   through the explicit operator step. Confirm persistence on Render itself.
4. Provision individual officer accounts through the operator process. Keep
   test-access instructions scoped; no public operator endpoint or shared officer
   session. Require a generated strong input-demo access code in hosted mode.
5. Finish manual service configuration using these images and the static build,
   or author a complete Blueprint as an optional alternative. Set actual URLs,
   allowed hosts/CORS, service-specific provider secrets and the hosted callback.
   A running health endpoint alone is not a verified connected demo.

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

## Billing gate

Claim the sponsor offer through the official resource page and verify the credit
balance, expiry and conditions in the owner account. The official sponsor page
advertises a one-time $50 offer; it is not free recurring hosting or a spending
cap. Keep account-specific billing and payment-method details out of this public
repository. No paid resources have been created by this work.

Before deployment show the owner the actual four-service compute quote, disk
cost, expected credit duration, bandwidth/build/Workflow allowances and what can
bill after credits are exhausted. Credits are not a spending cap. Create paid
resources only after the owner confirms that concrete quote. Recheck actual RAM
use after launch before recommending a smaller plan.

Free Render web services have ephemeral local storage and cannot attach durable
disks. Free Postgres expires after 30 days. Avoid an arrangement where a restart
loses the order store while a PayPal invoice remains active.

## Hosted acceptance

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
