# AFRACANet public product site — 1 November 2026

The public `/about` and `/about.html` routes explain alternative financial histories and authorized input finance through the user-pinned Aether Flow hero, new Bricolage Grotesque/Hanken Grotesk fonts, three credited Kenyan photographs and spacious scrolling. The initial Waterline public iteration is superseded here; the working finance application retains Waterline. Current authority: [six-block brief](PRODUCT_PAGE_BRIEF.md), [public DESIGN.md](../src/features/product/DESIGN.md) and [paired sidecar](../src/features/product/.impeccable/design.json). The [design record](PRODUCT_PAGE_DESIGN_2026-11-01.md) explains the two visual scopes.

## What visitors can explore

The page moves from a living-network proposition to human context, connected evidence, graph explanation, working lives, lender responsibilities and preserved payment proof. Six selectable evidence sources explain chama contributions, SACCO/lender histories, cooperative deliveries, business activity, farm/climate context and execution records. Nearby disclosures expose provenance, limits and actual availability.

Evidence starts cycling in view every nine seconds. The teaching graph automatically progresses through PageRank and authored community arrangements. Seven payment stages cycle every ten seconds; selecting a stage restarts the interval and continues from the selected stage. Pause/resume remains available. Playback suspends offscreen or when the document is hidden; reduced-motion users start with manual controls and may opt into tours. The hero has its own pause control and a static reduced-motion state. Photographs use a subtle scroll-linked scale with a static fallback.

The twelve-node, twenty-two-link teaching network computes PageRank locally with damping 0.85 and twelve iterations. Visitors can step, reset and inspect a node. Its two community groups and layouts are authored, not Louvain results or applicant classifications. Official [PageRank](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/) and [Louvain](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/) references accompany the explanation; this teaching example adds no underwriting or Neo4j/GDS service to the execution backend.

## Data and authority

Financial histories are synthetic. Real chama, SACCO and general small-business feeds are not connected; permissioned partner onboarding and source verification remain work. GDS has not run on the loaded development pack, and no calibrated credit score is active. The broader vision includes farmers and small businesses without conventional collateral; the working workflow currently focuses on agricultural input finance.

The preserved USD 18 actual sandbox payment is separate from signed lender-workflow tests. It was initially reconciled manually; a genuine resent callback was subsequently signature-verified and deduplicated, retaining one payment effect. Physical collection was not recorded. The public tour reveals this sanitized historical snapshot and makes no transaction or provider calls. An invoice status alone is insufficient payment evidence. Contextual photographs depict Kenyan subjects, not claimed customers, partners or endorsers; their captions link sources and terms. See [full credits](PRODUCT_SITE_CREDITS.md) and [asset hashes/origins](PRODUCT_SITE_ASSETS.json).

## Access and verification

Local route: `http://127.0.0.1:5173/about#evidence`. `npm run build` produces `dist/index.html` and `dist/about.html`; hosts without an SPA rewrite can serve the latter directly. Non-secret `VITE_CREDIT_WORKSPACE_URL` sets a hosted credit-workspace destination at build time. Without it, production links the credit source repository and local development uses port 5174. Stable public hosting remains separate work.

Recorded checks for this redesign:

- Production build, strict TypeScript and formatting passed. The complete Edge run passed 11 cases, including six transaction journeys; the final targeted public rerun passed five cases.
- All 21 captures in `.impeccable/review/redesign-{desktop,tablet,mobile}-{full,hero,purpose,evidence,graph,payment,community}.png` were reviewed at desktop 1440, tablet 768 and phone 390 widths. [Runtime evidence](../.impeccable/review/redesign-runtime.json) records zero document overflow, page errors or API requests at all three widths.
- The graph retains readable labels through signposted internal horizontal scrolling and a native node selector. Phones use a labelled payment select.
- The final [Taste inspector record](../.taste-skill/after/report.json) has zero FAIL and two WARN findings (type-size variety and no video). It observed 22 moving elements on desktop/tablet and 10 on mobile; these counts describe the capture, not a motion quota.
- The existing Impeccable detector ran once: `.impeccable/review/redesign-detector.json` records 94 advisory global Waterline-token mismatches and zero primary findings. It was not rerun during documentation.
- Three shipping JPEGs contain embedded origin metadata; the supplied provenance scan found three images and zero missing origins. Source/license/full SHA-256 records live in the asset manifest; font OFL notices ship in `public/licenses/`.

The [finish reviewer](PRODUCT_SITE_FINISH_REVIEW_2026-11-01.md) returned **ship**, with no material fixes, against the supplied component and current brief. The pinned code integration has no new Impeccable concept roll or QUALITY BAR card. This record reports the supplied checks and review; the documentation pass changed no application behavior and ran no detector.
