---
name: AFRACANet AI — Public Product Site
description: A forest-green public explanation of connected evidence and traceable input finance.
colors:
  forest-ground: '#071f18'
  ivory-ink: '#edf3df'
  celadon-accent: '#bed8a7'
  muted-ink: '#b4c6ba'
  body-ink: '#c2d1c5'
  forest-surface: '#103226'
  forest-raised: '#1b4031'
  forest-deep: '#163d2f'
  control-stroke: '#708c7b'
  soft-state: '#214735'
  focus: '#c5e9a8'
  action-fill: '#c0de9e'
  action-ink: '#10261c'
  action-hover: '#d2ebba'
  secondary-fill: '#163729'
  secondary-ink: '#e8efe2'
typography:
  display:
    fontFamily: 'Bricolage Grotesque Variable, sans-serif'
    fontSize: 'clamp(44px, 6.3vw, 96px)'
    fontWeight: 550
    lineHeight: 1.04
    letterSpacing: '-0.04em'
  headline:
    fontFamily: 'Bricolage Grotesque Variable, sans-serif'
    fontSize: 'clamp(36px, 4.4vw, 64px)'
    fontWeight: 550
    lineHeight: 1.08
    letterSpacing: '-0.04em'
  title:
    fontFamily: 'Bricolage Grotesque Variable, sans-serif'
    fontSize: '24px'
    fontWeight: 550
    lineHeight: 1.3
  body:
    fontFamily: 'Hanken Grotesk Variable, sans-serif'
    fontSize: '19px'
    lineHeight: 1.7
  label:
    fontFamily: 'Hanken Grotesk Variable, sans-serif'
    fontSize: '13px'
    lineHeight: 1.65
rounded:
  frame: '4px'
  action: '6px'
  field: '7px'
  stage: '8px'
  source: '10px'
  applicant-mobile: '12px'
  circle: '50%'
spacing:
  inline: '16px'
  group: '24px'
  reading: '28px'
  panel: '32px'
  heading: '36px'
  block: '40px'
  wide: '48px'
  mobile-section: '72px'
  section-gap: '96px'
components:
  button-primary:
    backgroundColor: '{colors.action-fill}'
    textColor: '{colors.action-ink}'
    rounded: '{rounded.action}'
    padding: '14px 24px'
  button-primary-hover:
    backgroundColor: '{colors.action-hover}'
  button-secondary:
    backgroundColor: '{colors.secondary-fill}'
    textColor: '{colors.secondary-ink}'
    rounded: '{rounded.action}'
    padding: '14px 24px'
  button-playback:
    backgroundColor: '{colors.forest-raised}'
    textColor: '{colors.ivory-ink}'
    rounded: '{rounded.frame}'
    padding: '10px 16px'
  field-select:
    backgroundColor: '{colors.forest-surface}'
    textColor: '{colors.ivory-ink}'
    rounded: '{rounded.field}'
    padding: '9px 12px'
  evidence-source:
    backgroundColor: '{colors.forest-surface}'
    textColor: '{colors.ivory-ink}'
    rounded: '{rounded.source}'
    padding: '20px'
  evidence-source-selected:
    backgroundColor: '{colors.forest-raised}'
  explorer-frame:
    backgroundColor: '{colors.forest-surface}'
    rounded: '{rounded.frame}'
---

# Design System: AFRACANet AI — Public Product Site

## Overview

**Creative North Star: "Aether Flow — connected financial life"**

This authority covers the public Persuade world at `/about` and `/about.html`, under the product-page wrapper, including its Aether hero and image-reveal components. Forest ground, ivory reading, celadon connections and substantial Kenyan photographs give the explanation room to unfold. The user pinned the Aether Flow code and requested new fonts, web photographs and spacious scrolling; no new Impeccable concept roll or QUALITY BAR card applies.

This is a scoped visual world, not a global token migration. The working Operate application retains [root DESIGN.md](../../../DESIGN.md), root `.impeccable/design.json` and Waterline. Public CSS locally overrides shared variable names; do not transfer those overrides to the application root. This file's frontmatter owns public primitives; [the paired sidecar](.impeccable/design.json) owns extension metadata and component previews. The [six-block brief](../../../docs/PRODUCT_PAGE_BRIEF.md) owns page strategy; [PRODUCT.md](../../../PRODUCT.md) owns product truth.

**Key Characteristics:**

- A quiet living network behind readable centered hero text.
- Open editorial sections and large, credited contextual photographs.
- Flat tonal explorers with explicit controls and nearby limits.
- Automatic explanations that remain pausable and usable with reduced motion.

## Colors

Dark forest fields hold ivory copy; celadon makes connections and actions visible without disguising evidence as approval.

The sidecar's tonal ramps are synthesized preview metadata, not additional shipped CSS tokens. Frontmatter colors retain their actual source values.

### Primary

- **Celadon accent:** connections, action cues and selected graph emphasis.
- **Action fill / ink / hover:** the hero's filled primary destination and its hover response.

### Neutral

- **Forest ground:** continuous page and hero field.
- **Forest surface / raised / deep:** explorers, selected sources, reading rails and the lender-authority block.
- **Ivory ink / body ink / muted ink:** headings, narrative and contextual notes respectively.
- **Control stroke / focus:** actual form boundaries and visible keyboard focus.
- **Secondary fill / ink / soft state:** secondary hero destination and restrained control hover states.

**The Scoped Forest Rule.** Apply these tokens within the public wrapper; working financial screens continue to use Waterline.

## Typography

**Display Font:** Bricolage Grotesque Variable, with sans-serif fallback. **Body Font:** Hanken Grotesk Variable, with sans-serif fallback. Both ship locally with OFL notices; their public-repository licensing clarity is the implemented replacement for the separately dealt Erode direction.

The display face gives the proposition character, while body copy, native controls and numerical explanations remain calm. Headings and brand use the public display face; buttons and selects use the public body face. Financial values use tabular numerals where shown.

### Hierarchy

- **Display:** the frontmatter role is the desktop hero. At 600px and below it becomes `clamp(36px, 8.5vw, 50px)` with line-height 1.08.
- **Headline:** the frontmatter role serves purpose and working-lives sections. Evidence uses `clamp(38px, 3.6vw, 54px)` at line-height 1.15; workflow uses `clamp(32px, 3.8vw, 54px)` at 1.15. These are observed surface variants, not a universal fixed type scale.
- **Title:** the recurring responsibility title. Explorer headings range with their informational role; this record does not canonize every one-off size.
- **Body:** the frontmatter role serves editorial paragraphs, reducing to 17px below 700px. Hero support is 20px/1.7, reducing to 17px below 600px. Detailed explorer prose generally uses 14–18px at 1.6–1.8.
- **Label:** captions and provenance generally start at 13px. These qualify nearby claims; they are not decorative eyebrows. Page paragraphs are capped at 65ch, with narrower local measures where the layout requires them.

## Layout

The public page removes the working main-width cap. Main editorial sections use 5% side gutters and 120px vertical padding, reducing to 72px below 700px. Evidence and payment use 4.36% desktop gutters and 5% mobile gutters. Editorial introductions use paired columns with 10% separation; the working-lives photographs form a staggered two-column pair. Preserve these spatial relationships rather than repeating a generic card grid.

The desktop header has an 86px minimum height; below 700px navigation becomes a second row. The hero uses `min(840px, calc(100svh - 86px))` minimum height, 6% gutters and a 1150px copy cap. Below 600px it has a 720px minimum height, stacked actions and 5% gutters.

At 1000px the graph reading rail stacks under its canvas. Its SVG keeps a 760px minimum width inside an explicitly signposted horizontal scroller; the labelled node selector provides another inspection route. This internal scroll is deliberate, and does not permit document overflow. Below 850px method/development layouts stack; below 520px the evidence applicant becomes a full-width banner above a two-column source grid and decorative connectors disappear. Below 600px the payment strip becomes a labelled native select and record facts stack.

## Elevation & Depth

Depth comes from forest tonal layers, open spacing, subdued network linework and photographic framing. The public implementation introduces no decorative box-shadow vocabulary. A raised tone means selected or supporting content rather than floating cards. Hero particles and teaching-graph geometry explain connections; they do not imitate a physical material.

## Shapes

Explorers and proof frames use the restrained frame radius; hero destinations use the action radius; selects use the field radius. Evidence-source controls use the larger source radius. Applicant and graph circles communicate relationship and graph weight, while rectangular frames contain explanations. Mobile evidence replaces its applicant circle with a gently rounded banner. Photo frames remain square-cornered and crop real images with `object-fit: cover`.

## Components

### Buttons and navigation

Hero primary and secondary destinations are links with a 54px minimum height, 15px type, weight 600 and a 16px icon gap. Mobile actions stack, cap at 320px wide and use a 50px minimum height. The primary lightens on hover; the secondary keeps its forest fill. Header links use understated text and underline on hover. The prototype link is a real destination. The skip link appears on focus. Public keyboard focus uses a 3px outline with a 5px offset; the hero uses its local pale-green focus color.

### Evidence and graph controls

Evidence-source buttons expose pressed state and change to the raised tone on hover/selection; text and an adjacent explanation retain meaning beyond color. A native disclosure exposes provenance, limits and actual availability. Graph mode buttons use bounded form-control strokes; selected mode uses the deep tone. Graph nodes expose keyboard operation, a visible selected/focused stroke and a native selector alternative. Do not invent chip/tag or text-entry primitives: this public surface has neither a general chip library nor a text-entry form.

### Explorers and payment record

The evidence explorer, graph stage and preserved-payment record use flat forest frames. Payment stage buttons are sequential controls, not approval indicators: verification remains expressed by the underlying record and text. Seven desktop stage buttons become one mobile select. The amount uses display type at weight 800 and tabular numerals. The collection stage remains unverified because this preserved fixture contains no physical handover.

**The Presentation Only Rule.** Public controls reveal synthetic teaching data or a preserved provider snapshot; they never execute a financial action or call a financial API.

### Motion and photographs

The hero canvas has a pause control, caps particle count and display density, and suspends offscreen or when hidden. Reduced motion keeps its static network and disables hero animation. Section reveals settle from small offsets; image scale moves from 1.12 to 1 over scrolling and becomes static under reduced motion. Three actual Kenyan photographs retain visible creator/source/license captions; no customer or partner endorsement is implied.

Evidence cycles every 9 seconds and payment every 10 seconds while at least 20% of their target is visible and the document is active. Manual source/stage selection restarts the interval and continues from that selection unless paused. The graph tour advances PageRank, then shows authored community arrangements and stops. Pause/resume and native controls stay available; reduced-motion users explicitly opt into tours, while positional graph changes snap.

## Do's and Don'ts

### Do:

- **Do** keep public forest tokens and public fonts scoped to the two public routes.
- **Do** preserve visible focus, pause/resume, native selectors and offscreen/hidden suspension.
- **Do** use credited contextual photographs with their source terms and nearby captions.
- **Do** keep lender authority, teaching data, verified payment and physical collection visually and verbally distinct.

### Don't:

- **Don't** migrate the working application away from Waterline through this authority.
- **Don't** replace real provenance with fictional customer logos or imply that photographs show customers.
- **Don't** present authored community labels as Louvain output or browser PageRank as a calibrated borrower score.
- **Don't** turn advisory findings or one-off implementation values into rules for future surfaces.

Not canonized: the inspector's type-size-variety warning and its absence-of-video warning are recorded observations, not prescriptions. The one existing detector's 94 global Waterline-token advisories do not govern this explicitly scoped public world; no primary finding was reported. No craft-floor defect was identified by the finish reviewer, and this documentation pass repairs no application code.
