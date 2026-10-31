---
name: AFRACANet AI — Waterline credit workspace
description: A clear working surface for scoped credit evidence and accountable lender decisions.
colors:
  ground: "#eaf1f3"
  surface: "#fff"
  ink: "#17343c"
  muted: "#526a72"
  teal: "#17627a"
  teal-dark: "#123f4c"
  soft: "#e9f3f5"
  line: "#d5e1e5"
  control: "#afc2c9"
  danger-bg: "#fff0ed"
  danger-ink: "#8d3826"
  success-bg: "#edf5e7"
  success-ink: "#375b22"
  nav-muted: "#c4dce3"
  nav-active: "#d5ecac"
  nav-hover: "#1c4b59"
typography:
  display:
    fontFamily: "Manrope, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Manrope, sans-serif"
    fontSize: "20px"
    fontWeight: 650
    lineHeight: 1.4
  queue-title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "19px"
    fontWeight: 650
    lineHeight: 1.4
  title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "16px"
    fontWeight: 650
  evidence-title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.5
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  body-mobile:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "14px"
    fontWeight: 550
    lineHeight: 1.6
  supporting:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "13px"
  detail-label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "12px"
  metric:
    fontFamily: "Manrope, sans-serif"
    fontSize: "26px"
    fontWeight: 600
  metric-mobile:
    fontFamily: "Manrope, sans-serif"
    fontSize: "23px"
    fontWeight: 600
  display-mobile:
    fontFamily: "Manrope, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.025em"
rounded:
  track: "3px"
  badge: "4px"
  relationship: "5px"
  control: "6px"
  inset: "8px"
  disclosure: "10px"
  panel: "12px"
spacing:
  compact: "8px"
  action-gap: "10px"
  small: "12px"
  medium: "16px"
  mobile-panel: "18px"
  section: "20px"
  panel: "22px"
  tablet-gutter: "24px"
  signin: "28px"
  desktop-gutter: "32px"
components:
  button-primary:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-secondary-hover:
    backgroundColor: "{colors.soft}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "9px 11px"
  navigation:
    backgroundColor: "{colors.teal-dark}"
    textColor: "{colors.nav-muted}"
    rounded: "{rounded.control}"
    padding: "12px"
  navigation-active:
    backgroundColor: "{colors.nav-hover}"
    textColor: "{colors.nav-active}"
  status:
    backgroundColor: "{colors.soft}"
    rounded: "{rounded.badge}"
    padding: "4px 8px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "22px"
  relationship:
    rounded: "{rounded.relationship}"
    padding: "10px 8px"
    typography: "{typography.supporting}"
  source-record:
    backgroundColor: "{colors.soft}"
    rounded: "{rounded.inset}"
    padding: "18px"
---

# Design System: AFRACANet AI — Waterline credit workspace

## Overview

**Creative North Star: "Waterline"**

Waterline makes agricultural finance readable through a deep teal navigation band, a pale blue ground, and white working surfaces. Compact typography and clearly separated records support repeated operational work. This credit extension preserves the user-selected world in [the shared direction](../Paypal/docs/WATERLINE.md) and applies it to evidence inspection and accountable lender review, as scoped in [the credit brief](docs/WATERLINE_CREDIT_BRIEF.md).

The system is calm, practical, and explicit about evidence. Retrieved relationships, authored balances, source records, advisory summaries, officer decisions, and delivery receipts retain separate labels. Outline SVG icons identify real actions. No raster asset ships in the credit interface; its relationship bars are rendered from retrieved counts. The execution module's allocation graphic and transaction drawer remain its own components rather than assumed features of this module.

**Key Characteristics:**
- Teal navigation and actions over a cool, pale ground.
- Flat white work surfaces with fine borders and modest rounding.
- DM Sans working text paired with Manrope headings and counts.
- Labelled relationship filters leading to inspectable source records.
- Responsive queue-to-case navigation with visible keyboard focus.

## Colors

The shared palette retains cool blue-teal structure and quiet semantic fills. The frontmatter records this module's actual values from `src/styles.css`, `src/styles/platform.css`, and `src/features/credit/credit.css`; execution-only reservation and paid colors are not credit evidence categories.

### Primary
- **Waterline Teal** (`teal`): primary decisions, relationship bars, record links, selection, and workspace focus.
- **Deep Channel** (`teal-dark`): shared full-width navigation.
- **Header Channel** (`nav-hover`): active and hovered navigation backgrounds.

### Secondary
- **Review Clay** (`danger-bg`, `danger-ink`): provider unavailability, validation failures, and other errors.
- **Completion Green** (`success-bg`, `success-ink`): recorded action notices. The copy states the actual event; color does not extend its meaning to payment or collection.

### Neutral
- **Pale Water** (`ground`) and **Working White** (`surface`): workspace and flat working panels.
- **Deep Ink** (`ink`) and **Slate Teal** (`muted`): primary text and secondary explanations.
- **Mist** (`soft`): selected applications, selected relationship filters, source details, advisory summaries, and status labels.
- **Fine Divider** (`line`) and **Control Edge** (`control`): divisions and stronger control boundaries.
- **Header Mist** (`nav-muted`) and **Header Leaf** (`nav-active`): navigation labels and active/focus accents on the dark header.

**The Labelled Color Rule.** Pair relationship and status colors with readable labels and counts; the hue alone never establishes a credit or transaction fact.

## Typography

**Display Font:** Manrope, with sans-serif fallback.
**Body Font:** DM Sans, with sans-serif fallback.

**Character:** Manrope gives headings and numerical counts a compact, confident hierarchy. DM Sans keeps explanations, forms, and records readable at operational density. Labels use sentence case. The global body uses tabular numerals.

### Hierarchy
- **Display:** page title; the mobile display token applies at the credit breakpoint.
- **Headline:** selected-case and sign-in headings. The queue uses the smaller queue-title token.
- **Title:** section headings; the retrieved-profile heading uses the evidence-title token.
- **Body:** the workspace baseline, with larger mobile body text and a maximum explanatory measure of (75ch).
- **Label:** fields and buttons inherit the workspace size. On mobile they inherit the larger body size. Source metadata uses the detail-label token; tables and balance labels use the supporting token. Mobile status labels remain (13px), and mobile relationship filters become (14px).
- **Metric:** plain application counts use the metric token and its mobile variant.

The source requests intermediate weights (550 and 650); font imports provide DM Sans 400/500/600 and Manrope 600/700. These values describe CSS requests, not additional bundled font files.

**The Amount Alignment Rule.** Preserve tabular numerals and right-align comparable balances, with their currency and synthetic-history qualifiers visible.

## Layout

The full-width navigation sits above a centered main region capped at (1500px), with desktop gutters (32px). The heading, lender/officer scope, explicit boundary text, and plain counts precede the workspace. Two collapsible tools share a row; opening one spans that row. This is an evidence-review surface, not a repeated metric-card dashboard.

The main region pairs an applications queue (270–320px) with a flexible selected case, separated by (20px). White queue and case panels use padding (22px). Queue records scroll within a maximum height (620px). Within the selected case, relationships and authored balances share two columns, with a gap (24px). Facts and decision fields use two columns. Ruled sections divide evidence, decisions, and delivery receipts. Connected-record tables use a fixed (62%/38%) split and scroll inside a region capped at (280px).

At (1100px) and below, main gutters become (24px), the queue becomes (270px), and both evidence overview and case facts use one column. The environment label leaves the header. At (850px) and below, main gutters and panel padding become (18px), tools and decision fields use one column, and the selected case replaces the queue. Back to applications restores the queue; the hidden region remains a navigation state rather than discarded data. The queue scroll region is capped at (440px). Body text becomes larger while controls retain a minimum height (44px).

At (700px) and below, navigation stacks below the brand, while the Input finance link occupies the upper-right position. Navigation labels reduce to (13px); the cross-module link uses (12px). The brand retains its product and module labels. The sign-in panel is capped at (520px), with padding (28px); at the credit mobile breakpoint its margin and padding become (20px).

## Elevation & Depth

Depth comes from tonal layers and fine borders. This module has no panel shadows, scrim, or modal drawer. Source-record inspection expands a Mist inset in the selected case; advisory summaries use the same flat inset language.

**The Working Surface Rule.** Keep ordinary work panels flat; use borders and tonal insets to distinguish nested evidence.

## Shapes

Queue, case, and sign-in panels use the panel radius. Fields and buttons share the control radius. Status labels use the smaller badge radius; relationship rows and their thin bars use relationship and track radii. Advisory and source-record insets share the inset radius; tool disclosures use the disclosure radius. Borders are (1px). Lucide outline SVGs identify navigation, retrieved evidence, refresh, exit, and source-record actions without raster imagery.

## Components

### Buttons

Compact and purposeful. Primary decisions use Waterline Teal with white text and a matching border. Secondary actions use white with a Control Edge border and become Mist on hover. Both use padding (8px 12px), gap (8px), and minimum height (44px). The primary background stays teal under the current CSS specificity. Disabled buttons use opacity (0.55) and a wait cursor. Text-style relationship reset and source-record controls retain clear labels without boxed backgrounds.

Workspace buttons and links transition background and text color over (140ms ease-out). The reduced-motion query removes these transitions. Workspace interactive elements receive a teal outline (3px), offset (3px). There is no source-defined press translation.

### Inputs / Fields

Plain white fields use the control radius, a Control Edge border, and padding (9px 11px). Labels form a grid with a gap (6px). Placeholders are opaque muted text and the caret is teal. Textareas have a minimum height (85px) and resize vertically. Decision confirmation uses a labelled (18px) checkbox. Error and action notice copy use their semantic foreground/background pairs and retain alert/status roles.

### Chips

Small rectangular Mist status labels use the badge radius and padding (4px 8px). They identify the surface or evidence role; application status and provenance remain readable in the case heading and queue text. Do not import execution transaction-status semantics into this neutral credit label.

### Cards / Containers

White queue and case panels use the panel radius, Fine Divider border, and panel padding. Sign-in uses the same flat material. Tool disclosures use padding (14px 18px). Source details and advisory summaries use Mist inset surfaces with padding (18px). The empty selected case offers a direct instruction and explanation rather than invented evidence.

### Navigation

The deep teal header groups product/module identity, Lender review, Decision history, and Input finance. Brand type is Manrope (20px, 700, line-height 1.3). Desktop links use DM Sans (14px), padding (12px), and minimum height (44px). Active links combine Header Leaf text with Header Channel fill; hover uses white text on the same fill. Focus uses a Header Leaf outline (3px) offset (3px). Mobile behavior is described in Layout; cross-module navigation does not transfer the officer session.

### Application queue

Flat, full-width record buttons use ruled rows, padding (13px 8px), and square row corners inside the rounded queue. The selected record uses Mist and `aria-pressed`. Each record keeps its farmer ID, status, provenance, and date visible. Search and status filtering precede the list.

### Retrieved relationships and source records

A relationship is a labelled button with a count and a thin teal bar. Bar width is the retrieved count divided by the largest retrieved category count; it is not a score, confidence, or credit allocation. Four categories appear initially, with an explicit control to reveal the remaining types. Selection filters the retrieved records and is exposed through `aria-pressed`. The thin bar is decorative to assistive technology because the label and count carry the facts.

Connected records appear in a ruled table. Activating a record fetches its tenant-scoped source detail and reveals an inline inset with its ID, relationship, source kind, properties, and labelled close control. Source loading and errors remain explicit. Authored KES balances stay separate from active illustrative USD credit. Public weather is a collapsible, attributed context block with its reference-point limitations.

### Advisory summary and decision record

The advisory inset retains an explicit advisory-only heading, observations with source citations, missing evidence, provider/model identity, and expandable facts supplied to AI. Provider failure leaves an error rather than substituting a decision. The lender form separately requests allocation, expiry, reason, and explicit authorization confirmation. Recorded decisions and handoff delivery attempts retain their references, actor, status, and acknowledgment text.

## Do's and Don'ts

### Do:
- **Do** use teal for shared navigation, actions, and labelled relationship bars.
- **Do** pair status and relationship colors with readable labels and counts.
- **Do** preserve tabular numerals, currency labels, and comparable balance alignment.
- **Do** keep working panels flat and use tonal insets for nested evidence.
- **Do** carry visible keyboard focus, accessible action labels, and reduced-motion behavior into new components.
- **Do** retain synthetic-data, public-context, advisory-only, and handoff qualifiers wherever they explain a record.

### Don't:
- **Don't** give ordinary operational panels decorative lift or replace established flat surfaces with gradients.
- **Don't** substitute decorative imagery for retrieved relationships or inspectable source records.
- **Don't** treat a relationship count, AI summary, lender decision, payment, and collection as interchangeable facts.
- **Don't** turn authored histories or public reference-point weather into calibrated risk scores or verified farmer outcomes.
- **Don't** imply production readiness through a success treatment or a recorded delivery receipt.
