# Public site: sources and integration

The /about and /about.html public pages use contextual Kenyan photographs. None of the subjects is claimed as an AFRACANet customer, partner, borrower or endorser. Photographs are not synthetic. Credits and source links appear directly below each photograph; this document records the full terms. Assets retain their own licenses, separately from repository code.

| Photograph | Creator | License | Source |
| --- | --- | --- | --- |
| Women smallholder farmers in Kenya, Machakos, 14 October 2010 | McKay Savage | [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Women_smallholder_farmers_in_Kenya.jpg) |
| Woman farmer in Kenya, Mount Kenya region, 15 October 2010 | Neil Palmer / CIAT | [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Woman_farmer_in_Kenya.jpg) |
| Smiling African Woman at Kenyan Market | Charles Lichinga | [Pexels License](https://www.pexels.com/license/) | [Pexels](https://www.pexels.com/photo/smiling-african-woman-at-kenyan-market-33569521/) |

The Commons farming group file is the official 1280px thumbnail. The CIAT image is the original JPEG. The market image is a published 1600px delivery variant. Origin metadata is embedded in every JPEG; source URLs, sizes and SHA-256 hashes are in PRODUCT_SITE_ASSETS.json. Images are displayed with responsive CSS crops and subtle scroll scaling. The CIAT image and any adapted photographic rendition remain CC BY-SA 2.0. No endorsement is implied.

## 21st.dev components

Retrieved through the 21st.dev MCP and adapted to the existing React/Vite/TypeScript stack:

- [Aether Flow Hero by dhileepkumargm](https://21st.dev/@dhileepkumargm/components/aether-flow-hero): src/components/ui/aether-flow-hero.tsx and its stylesheet. Green canvas network, product copy, typed particles, capped density/DPI, local pointer coordinates, ResizeObserver, offscreen/hidden suspension and reduced motion.
- [Scroll Reveal Image by unlumen](https://21st.dev/@unlumen/components/scroll-reveal-image): src/components/ui/scroll-reveal-image.tsx. Native image replaces Next Image; responsive frame and a modest scroll-linked scale replace width/radius animation.

Framer Motion is installed; Lucide React already existed. The repository uses source-root components/ui, plain CSS and TypeScript. It does not use Tailwind or shadcn scaffolding. These adaptations need neither. To integrate future unmodified shadcn/Tailwind registry snippets, first follow their current official Vite setup instructions, configure the source alias and components.json, then review the generated dependency and stylesheet changes; do not run a starter generator over this existing application.

## Fonts

The public site uses self-hosted Bricolage Grotesque Variable for display and Hanken Grotesk Variable for reading, via @fontsource-variable packages. Their SIL Open Font License notices ship in public/licenses/. Working finance screens retain their existing Waterline typography. The public site downloads no remote font API at runtime.
