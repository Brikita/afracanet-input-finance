# Public product page — scoped design record

## Overview

This records the implemented `/about` and `/about.html` surface on 1 November 2026. It is an ordinary extension of **Waterline**, not a replacement visual world. [DESIGN.md](../DESIGN.md) and [.impeccable/design.json](../.impeccable/design.json) remain the authoritative working-app system and are preserved. This note introduces no global token schema or new sidecar.

The source of product truth is [PRODUCT.md](../PRODUCT.md); the six-block direction contract is [PRODUCT_PAGE_BRIEF.md](PRODUCT_PAGE_BRIEF.md). The latest user direction expands the alternative-credit story for farmers and small businesses without conventional collateral, with chama/SACCO evidence and fitting graph motion. It explicitly gives the story room to unfold through scrolling. The older dense proof composition is a historical critique reference, not a current spatial target.

The shipped hierarchy is proposition → preserved payment check → six responsibilities → alternative-credit evidence explorer → teaching network and algorithm limits → lender authority → development status and next steps. This lets readers inspect evidence without conflating an AI explanation, a lender decision, payment and physical collection.

Source ownership:

- [ProductPage.tsx](../src/features/product/ProductPage.tsx) and [product.css](../src/features/product/product.css): navigation, introduction, workflow and footer.
- [PaymentProof.tsx](../src/features/product/PaymentProof.tsx) and [payment-proof.css](../src/features/product/payment-proof.css): selectable provider-check snapshot.
- [EvidenceStory.tsx](../src/features/product/EvidenceStory.tsx), [evidenceSources.ts](../src/features/product/evidenceSources.ts) and [evidence.css](../src/features/product/evidence.css): six evidence sources, disclosures, authority and development story.
- [GdsExplorer.tsx](../src/features/product/GdsExplorer.tsx) and [gds.css](../src/features/product/gds.css): authored teaching network and optional animation.
- [entry.tsx](../src/features/product/entry.tsx), [tokens.css](../src/styles/tokens.css), [foundations.css](../src/styles/foundations.css) and [fonts.css](../src/styles/fonts.css): inherited fonts, shared colors, controls and focus treatment.

## Colors

The public page inherits dark teal navigation, teal connections/actions, pale blue ground, flat white surfaces and blue/green financial geometry. Shared `--teal-dark`, `--teal`, `--muted`, `--line`, `--control`, `--soft` and `--ink` remain bound to the application palette.

The implemented page also scopes a lighter ground (`--product-ground: #eaf4f6`), stronger page ink (`--product-ink: #102f3a`) and green prototype link (`--product-green: #227d43`) to its wrapper. Evidence uses an almost-white field; graph nodes use blue/green fills, selected teal, and fine connecting lines. These are recorded public-page variants, not new normative app tokens. Selected states combine color with pressed-state semantics and explanatory text. Verified/pending payment facts retain text and icons.

## Typography

Manrope headings and amounts, DM Sans body and controls, and tabular financial values inherit Waterline. Public storytelling deliberately uses a larger ramp than operational queues: the proposition is `clamp(40px, 4.7vw, 70px)` at weight 800 and line-height 1.08, with a 36px phone override. Introductory copy is 21px on desktop and 18px on phones. Evidence headings use `clamp(38px, 3.6vw, 54px)`; recurring major headings use `clamp(30px, 3vw, 44px)`. These expressions are surface-specific.

Paragraphs generally have bounded reading measures (60–72ch), with generous line-height (1.6–1.8). Small provenance, scope and technical captions qualify nearby claims; they do not become a new display-label pattern for the app.

## Layout

The page removes the workspace main-width cap within its own wrapper. Desktop side gutters are 4.36%; phone gutters are 5%. The introduction uses 80px top/72px bottom padding. The standalone payment surface and workflow each leave 96px below; evidence begins with 104px top padding. The source explorer, teaching graph, method notes, authority and development sections receive distinct spacing rather than sharing a crowded viewport.

At 1000px and below, the workflow changes from three to two columns and the graph's reading rail stacks below its canvas. At 600px and below, workflow and footer become single columns, navigation moves to a second row, the payment stage strip becomes a labelled native select, payment facts stack, and primary section gaps reduce to 64–72px. Payment content keeps its full explanations.

The evidence map has six selectable sources around a central applicant. Its spacing adapts at 1150px and 850px. Below 850px the method and development columns stack. At 520px and below, the applicant becomes a full-width banner above a two-column source grid and decorative connector lines disappear; the selected source and its textual relationship remain available. Authority steps also stack.

The teaching SVG preserves a 760px minimum width inside its own horizontal scroll container. Below 1000px a pan hint explains this behavior; the node select provides a compact alternative to direct graph selection. This internal graph scroll is intentional and does not authorize document overflow.

## Elevation & Depth

The public page carries Waterline's flat surface language. Fine borders, quiet field changes and a dark authority section create separation. It introduces no decorative panel shadows, photography or raster assets. The graph uses SVG geometry rather than a background illustration.

## Shapes

Public proof/explorer frames use 14px corners; evidence controls and graph mode controls use 10px; playback controls use 7px. These larger public frames do not replace the incumbent working-panel radius. Circular applicant and graph nodes describe relationships and importance, while rectangular surfaces hold records and explanations. Lucide outline icons support named actions and stages.

## Components

**Navigation and workflow.** The skip link appears on focus and targets the main content. Anchor links target workflow and evidence. Six ordered responsibilities retain distinct actors and facts. The prototype and module links lead to the working surfaces; they do not imply that public-page interaction executes a transaction.

**Payment snapshot.** Seven native buttons expose `aria-pressed` and control a labelled polite live region; a native select serves phones. The initial selection is the verified callback stage. Amount and provenance come from preserved report JSON, not a live PayPal request. The USD 18 sandbox check was initially reconciled manually; a genuine resent callback was subsequently signature-verified and deduplicated. This is separate from the signed lender-workflow fixture. No real money or customer loan is established, and physical collection remains unrecorded. Invoice status alone does not establish payment.

**Evidence sources.** Chama, SACCO/lender, cooperative, business cash flow, farm/climate and input-finance buttons select one polite live region. A native disclosure expands connection, limit and availability. Changing the source resets that disclosure through its keyed instance. No live personal records, real chama/SACCO feed or general small-business account integration are presented. Public weather reference context remains distinct from synthetic applicant history.

**Teaching graph.** Twelve authored nodes and 22 directed links drive browser-computed PageRank. Equal starting shares update through 12 iterations using damping 0.85. Play/Pause, Step and Reset make progression optional; the reading rail exposes the top shares. Selecting SVG nodes works by click, Enter or Space and highlights adjacent edges; the labelled native select offers the same node selection with incoming/outgoing counts. Focus uses a stronger circle stroke. Rank percentages describe importance within this toy network, never repayment probabilities or credit scores.

Community mode animates positions between a shared layout and two authored groups. Those labels and memberships are manually assigned; this is a Louvain concept illustration, not a Louvain execution. The actual loaded development graph has not had GDS run on it and has no calibrated alternative-credit score. The educational graph is separate from borrower data, the development pack and the provider fixture.

PageRank starts paused, advances on a 700ms timer only when requested, stops at its final iteration, and pauses when its observed frame leaves view or the document becomes hidden. Mode switching also pauses playback. Community layout changes use an 850ms eased interpolation. Reduced motion snaps positional changes and removes animated radius/evidence transitions; information remains reachable through controls. Reduced motion does not disable the user-requested numerical steps. Native controls retain the shared visible focus treatment, with a pale outline on dark navigation/footer surfaces.

## Do's and Don'ts

- **Do** retain the roomy scroll sequence, nearby provenance and selectable source detail.
- **Do** preserve text alongside selected colors, graph geometry and payment status.
- **Do** distinguish teaching results, synthetic history, attributed public context and actual sandbox checks.
- **Don't** treat graph connectivity, community membership or an AI summary as lender authority or a validated score.
- **Don't** turn these public-page sizes, colors or corner variants into working-app defaults.
- **Don't** infer physical delivery from callback delivery or payment verification.

The finish reviewer reported **SHIP**, with no material fixes, using the twelve required desktop/tablet/mobile captures: `product-*`, `evidence-selected-*`, `gds-*` and `gds-community-*` in `.impeccable/review/`. The supplied review reports zero document overflow and zero API calls. This documentation pass reads source and existing evidence; it makes no new browser-verification claim.

The existing detector report, [product-detector.json](../.impeccable/review/product-detector.json), contains 108 advisory findings (30 color, 72 size, six radius) and no hard findings. They are retained as scoped-variant/drift information, not cleared by changing the global specification. No inherited token drift is canonized or repaired, no detector was rerun, and no raster assets ship.
