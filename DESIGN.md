---
name: AFRACANet AI — Waterline
description: A clear working surface for authorized input finance and traceable transactions.
colors:
  ground: "#eaf1f3"
  surface: "#fff"
  ink: "#17343c"
  muted: "#526a72"
  teal: "#17627a"
  teal-dark: "#123f4c"
  teal-hover: "#104e62"
  soft: "#e9f3f5"
  line: "#d5e1e5"
  control: "#afc2c9"
  reserved: "#4c86b7"
  paid: "#6e9544"
  attention-bg: "#fff3d9"
  attention-ink: "#73500e"
  danger-bg: "#fff0ed"
  danger-ink: "#8d3826"
  success-bg: "#edf5e7"
  success-ink: "#375b22"
  nav-muted: "#c4dce3"
  nav-active: "#d5ecac"
typography:
  display:
    fontFamily: "Manrope, sans-serif"
    fontSize: "clamp(30px, 3vw, 44px)"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Manrope, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "-0.015em"
  body:
    fontFamily: "'DM Sans', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "'DM Sans', sans-serif"
    fontSize: "13px"
    fontWeight: 500
    lineHeight: 1.5
  metric:
    fontFamily: "Manrope, sans-serif"
    fontSize: "28px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.035em"
rounded:
  badge: "5px"
  field: "6px"
  button: "7px"
  panel: "10px"
spacing:
  compact: "8px"
  control-gap: "10px"
  small: "12px"
  medium: "16px"
  mobile-panel: "18px"
  panel: "22px"
  section: "24px"
  drawer: "28px"
  desktop-gutter: "32px"
components:
  button-primary:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.button}"
    padding: "10px 15px"
  button-primary-hover:
    backgroundColor: "{colors.teal-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.button}"
    padding: "10px 15px"
  button-secondary-hover:
    backgroundColor: "{colors.soft}"
  button-text:
    textColor: "{colors.teal}"
    padding: "3px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "10px 12px"
  navigation:
    textColor: "{colors.nav-muted}"
    rounded: "{rounded.field}"
    padding: "10px 12px"
  status:
    backgroundColor: "{colors.soft}"
    textColor: "{colors.teal}"
    rounded: "{rounded.badge}"
    padding: "5px 7px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "22px"
  credit-track:
    backgroundColor: "{colors.soft}"
    rounded: "{rounded.badge}"
    height: "23px"
---

# Design System: AFRACANet AI — Waterline

## Overview

**Creative North Star: "Waterline"**

Waterline makes agricultural input finance readable through a deep teal navigation band, a pale blue ground, and white working surfaces. Compact typography and clearly separated records support repeated operational work. Color locates available credit, reservations, payments, and exceptions; outline icons identify actions and transaction stages.

The system is calm, practical, and explicit about evidence. Amounts, state labels, and the next permitted action carry the hierarchy. Mode disclosures remain part of the interface: simulated records, PayPal sandbox verification, and unavailable upstream evidence retain their distinct meanings. There are no shipping raster assets; diagrams are rendered from scoped application data.

**Key Characteristics:**
- Teal navigation and actions over a cool, pale ground.
- Flat white work surfaces with fine borders and modest rounding.
- Compact DM Sans text paired with Manrope headings and amounts.
- Labelled, reconciled financial graphics and explicit transaction stages.
- Responsive work queues with keyboard focus and reduced-motion support.

## Colors

The palette combines cool blue-teal structure with blue reservations, leaf-green paid amounts, and quiet semantic status fills. The frontmatter records the source values; CSS custom properties in `src/styles.css` implement the shared palette.

### Primary
- **Waterline Teal** (`teal`): primary actions, links, available allocation, complete stage icons, and active controls.
- **Deep Channel** (`teal-dark`): full-width workspace navigation and the sign-in story surface.
- **Deep Action Teal** (`teal-hover`): primary-button hover state.

### Secondary
- **Reservation Blue** (`reserved`): the reserved-credit segment and its legend marker.
- **Leaf Green** (`paid`): amounts recorded as paid to suppliers in the allocation graphic.
- **Attention Amber** (`attention-bg`, `attention-ink`): requested orders, awaiting-payment states, and issue holds.
- **Review Clay** (`danger-bg`, `danger-ink`): payment review and error messages.
- **Completion Green** (`success-bg`, `success-ink`): collection-ready and collected statuses, confirmation notices, and collection-code surfaces.

### Neutral
- **Pale Water** (`ground`): the workspace background.
- **Working White** (`surface`): fields, panels, and drawers.
- **Deep Ink** (`ink`) and **Slate Teal** (`muted`): primary text and secondary explanations.
- **Mist** (`soft`): quiet selected/help surfaces and default status fills.
- **Fine Divider** (`line`) and **Control Edge** (`control`): surface divisions and stronger input/secondary-button boundaries.
- **Header Mist** (`nav-muted`) and **Header Leaf** (`nav-active`): navigation labels and the active navigation/focus accent on the dark header.

**The Labelled Color Rule.** Pair financial and status colors with readable labels and amounts; the hue alone never establishes a transaction fact.

## Typography

**Display Font:** Manrope, with sans-serif fallback.
**Body Font:** DM Sans, with sans-serif fallback.

**Character:** Manrope supplies compact, confident headings and financial values. DM Sans keeps tables, explanations, and controls readable at operational density. Labels use sentence case; amounts and aligned numerical columns use tabular numerals.

### Hierarchy
- **Display:** the sign-in story headline uses the responsive display token; its mobile override is (29px). This is a contextual large heading, not a workspace banner pattern.
- **Headline:** page titles use the headline token; phone titles reduce to (24px).
- **Title:** panel headings use the title token. Subheadings use Manrope (15px, 700, line-height 1.5).
- **Body:** the root body token is the baseline. Most table and explanatory working text is (13px); supporting labels, statuses, and fine print are (12px). Fine print uses line-height (1.7).
- **Label:** field labels and primary/secondary buttons use the label token.
- **Metric:** plain summary amounts use the metric token; phone summaries reduce to (24px). Selected-case totals use (30px, 600, line-height 1.4); drawer amounts use (32px, 600).

**The Amount Alignment Rule.** Right-align comparable table amounts and preserve tabular numerals in metrics, balances, and financial columns.

## Layout

The workspace has a full-width header and a centered main region capped at (1600px), including desktop horizontal gutters (32px). Standard panel padding is (22px); the selected case uses (20px). Repeated gaps and internal spacing draw from the compact scale in the frontmatter rather than a rigid single increment.

The lender screen pairs a flexible allocation-and-queue column with a selected-case rail (350px), separated by (22px). Four plain numerical summaries sit above it, separated by vertical rules rather than boxed cards. The farmer form pairs a wider request region with an order summary. Tables use ruled rows and quiet headers; containers own horizontal scrolling when needed.

At (1180px) and below, navigation wraps onto a separate header row, main gutters become (24px), and the case rail narrows to (330px). At (960px) and below, lender and farmer regions stack. Selecting a lender request moves keyboard focus to the case detail and scrolls it into view; reduced motion removes the smooth scroll.

At (650px) and below, main gutters become (16px), panel padding becomes (18px), and the lender queue precedes the allocation graphic. Two compact lender summaries remain visible; the full allocation legend remains below the queue. Request and transaction tables become compact record grids. Search and status filtering share one row, navigation scrolls horizontally, and export becomes an accessible icon button. Case-stage cells use two columns on phones and four across on intermediate widths. These are surface-specific adaptations, not a rule to hide arbitrary data on every mobile screen.

## Elevation & Depth

Depth comes primarily from tonal layers and fine borders. Work panels have no resting shadow. The right-hand transaction drawer is the sole structural lifted surface: it sits above a translucent scrim, while keeping a flat white interior.

### Shadow Vocabulary
- **Drawer edge:** (`box-shadow: -8px 0 35px #0c273b14`) separates the modal drawer from the underlying workspace.
- **Drawer scrim:** (`background: #14323b66`) dims the workspace while the transaction dialog is active.

**The Working Surface Rule.** Keep ordinary work panels flat; reserve structural shadow for the modal drawer.

## Shapes

Working surfaces have gently rounded corners using the panel token. Controls use the smaller field and button radii; status chips and allocation tracks use the badge radius. One-pixel borders distinguish surfaces and fields. Small round nodes belong to stage icons and timelines; they coexist with rectangular work panels. Lucide outline SVGs carry recognizable actions and stages. Initial tiles identify people without portrait assets.

## Components

### Buttons

Compact and purposeful. Primary actions use Waterline Teal with white text; secondary actions use Working White with a Control Edge border. Both use the button radius, padding (10px 15px), an icon gap (9px), and minimum height (42px). The hover backgrounds are defined in frontmatter. Pressing an enabled button moves it down (1px); disabled controls have opacity (0.55) and a not-allowed cursor. Text actions are teal and underline on hover. Phone case/drawer primary actions have a minimum height (46px).

### Inputs / Fields

Plain, bordered white fields use the field radius and padding (10px 12px). Placeholders use muted text; the caret uses teal. The search variant groups an outline search icon and borderless inner input inside a single bordered container. Keep an explicit accessible label. Visible keyboard focus is a teal outline (2px) offset by (3px); the dark header uses Header Leaf for contrast. Error copy uses the review palette.

### Chips

Status chips are small rounded rectangles with text, a current-color dot, padding (5px 7px), type (12px), and line-height (1.4). Requested and awaiting-payment states use attention colors; payment review uses review colors; collection-ready and collected use completion colors. Cancelled states use a muted grey-blue fill and text. The chip reports state; it does not replace explanatory text or an action.

### Cards / Containers

White panels use the panel radius and a Fine Divider border. Standard padding comes from the panel token, with responsive and selected-case exceptions described in Layout. Queue panels clip the outer corners and contain their own headings, controls, ruled records, and footer captions. Empty states use an outline icon, a clear sentence, supporting copy, and a relevant action when available.

### Navigation

The dark teal header groups the brand, role-specific navigation, and account controls. Navigation uses DM Sans (13px), muted light labels, and the field radius. Active navigation combines Header Leaf text with a faint white tint (`#ffffff0d`); hover uses a stronger tint (`#ffffff16`) and white text. Focus remains visible on the dark surface. Preserve the phone scroll behavior and accessible names when an action loses its visible label.

### Credit destination graphic and request path

The allocation bar has three labelled segments: available, reserved, and paid to suppliers. The track is (23px) high with (3px) segment gaps. Its widths come from scoped integer amounts, and its legend exposes every amount in text; the graphic also has a complete accessible description. Zero allocation produces an import prompt rather than invented proportions.

The selected case uses four explicit stages: request, order approval, supplier payment, and collection. Small circular outline-icon nodes pair with stage names and detail text. Simulated payment and sandbox verification have distinct labels. Upstream AI evidence and lender authorization must remain distinct from execution progress; this UI does not contain a credit graph or a live underwriting visualization.

### Transaction drawer

A full-height white drawer opens from the right at width (`min(560px, 100%)`), with padding (28px), reduced on phones. It contains state, amount, line items, references, permitted actions, issue records, and a timeline. Opening moves focus into the dialog; Tab remains within it, Escape and scrim click close it, body scrolling is locked, and closing restores prior focus. Keep the labelled dialog semantics.

Motion is limited to short control feedback (0.15s) and selection scrolling. The reduced-motion media query disables transitions and animations and keeps every item of information available.

## Do's and Don'ts

### Do:
- **Do** use teal for the shared navigation/action language, blue for reservations, and leaf green for paid amounts.
- **Do** pair status color and graphic segments with readable text and amounts.
- **Do** preserve tabular numerals and comparable amount alignment.
- **Do** keep ordinary panels flat and use the drawer shadow only for modal depth.
- **Do** carry visible keyboard focus, accessible icon names, and reduced-motion behavior into new components.
- **Do** retain explicit simulation, sandbox, manual-handoff, and unavailable-evidence labels wherever they qualify a record.

### Don't:
- **Don't** give ordinary operational panels decorative lift or use gradients in place of the established flat surfaces.
- **Don't** substitute decorative imagery for the labelled financial graphic or actual transaction records.
- **Don't** treat an AI recommendation, lender authorization, invoice, payment, and collection as interchangeable visual states.
- **Don't** turn illustrative values, synthetic histories, or unavailable graph evidence into claims of live verified credit intelligence.
- **Don't** conceal payment mode or imply production readiness through a success treatment.
