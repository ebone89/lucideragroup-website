# Color System

Reference for every color used on the site: what it's named, what it's for, and its value. Use the **token names** (the `--name` column) when giving feedback on a specific area ("the `--band-bg` looks off" is unambiguous; "the dark part" isn't).

All tokens are defined once in `assets/css/styles.css` (`:root`) and used everywhere else in the CSS by name, never as a raw hex value, so a color only ever needs to change in one place. (This file documents the system as of the 2026-08-06 refactor that completed the token layer — the palette values themselves didn't change, only how consistently they're referenced.)

There is currently **one theme** (no dark/light mode toggle, unlike the Putnam Young Dems site). If dark mode is ever added, the semantic tokens below are exactly the layer that would need a second `:root[data-theme="dark"]` set of values — the brand scale would stay fixed.

## Brand scale (fixed, the site's palette)

Five color scales, each running light (`-50`) to dark (`-900`), plus two fixed utility colors:

| Scale | Tokens | Used for |
|---|---|---|
| **Teal** | `--teal-900` `#04342C` → `--teal-50` `#E1F5EE` | Primary brand color. Nav/footer borders, links, section labels, card accents, the Group/Media sub-brand accent. |
| **Green** | `--green-700` `#3B6D11`, `--green-600` `#639922`, `--green-50` `#EAF3DE`, `--green-100` `#C0DD97` | "Positive" indicators — the East Palatka data center article's "gains" balance card. |
| **Slate** | `--slate-900` `#111B17` → `--slate-50` `#EDF4EF` | Neutral scale: dark-band backgrounds, all body/heading text, borders. The full 900→50 range: `900` `#111B17`, `800` `#1A2920`, `700` `#243729`, `600` `#2E3B35`, `500` `#4A5E53`, `200` `#B8CEC0`, `100` `#D6E5DA`, `50` `#EDF4EF`. |
| **Amber** | `--amber-600` `#BA7517`, `--amber-400` `#EF9F27`, `--amber-50` `#FAEEDA`, `--amber-100` `#FAC775` | Warning callouts, the Investigations sub-brand accent, one stat-card variant. |
| **Coral** | `--coral-600` `#993C1D`, `--coral-400` `#D85A30`, `--coral-50` `#FAECE7`, `--coral-100` `#F5C4B3` | "Cost/negative" indicators, the Technologies sub-brand accent, one stat-card variant. |
| **Utility** | `--ink` `#0A100E`, `--paper` `#FAFCFB`, `--white` `#FFFFFF` | Base text/background before any semantic role is applied, and pure white for text on dark surfaces. |

## Semantic tokens (role-based, built from the scale above)

| Token | Role | Value |
|---|---|---|
| `--page-bg` | Base page background | `var(--paper)` |
| `--band-bg` | The recurring dark "band" sections — nav, footer, hero, page-hero, article-hero, group-hero, stub-hero, tips-section, chart-panel | `var(--slate-900)` |
| `--surface` | Raised card backgrounds (e.g. `.article-card`) | `var(--white)` |
| `--text` | Default body text (base, rarely visible directly — most content sits inside a more specific role below) | `var(--ink)` |
| `--text-heading` | Non-brand-colored headings on light backgrounds (h2s, card titles, emphasis text) | `var(--slate-900)` |
| `--text-body` | Standard paragraph copy on light backgrounds | `var(--slate-600)` |
| `--text-muted` | De-emphasized copy on light backgrounds (excerpts, methodology notes) | `var(--slate-500)` |
| `--text-on-dark` | Headings/emphasis text on a dark band or dark card | `var(--white)` |

Text that's de-emphasized *on a dark band* (nav links, footer tagline, hero subtitles) uses `--slate-200` directly rather than a semantic alias — it's already applied consistently everywhere that role appears, so a wrapper token wouldn't add clarity.

## The design principle behind the palette

Nearly every page opens with a `--band-bg` (near-black slate) hero/nav pairing, with page content sitting on the light `--page-bg` in between and closing back into a `--band-bg` footer — a dark→light→dark rhythm on every page, not just a themed nav. Sub-brand pages (Media, Investigations, Technologies) currently render with the same teal accent regardless of section — see "Known gaps" below.

## Known gaps (not fixed in the 2026-08-06 token pass — flagged for a deliberate follow-up, not silently changed)

1. **`--brand-accent` is defined but unused.** `body.entity-group`/`entity-media` set it to teal, `entity-invest` to amber, `entity-tech` to coral — but no component actually reads `var(--brand-accent)`; every page still hardcodes `--teal-*` for links, section labels, and card accents. So Investigations and Technologies pages look identical to Media/Group today despite the hook existing for them to look distinct. Wiring this up is a visual change, not a pure refactor — worth a deliberate decision on which components should shift accent (nav underline? section labels? links?) rather than doing it silently.
2. **`east-palatka-data-center.html` still has ~15 inline `style="color:#2E3B35"` / `var(--teal-400)` etc. attributes** for its bespoke timeline/chart/legend elements. These weren't touched in this pass since they're one-off article layout, not reusable component CSS, and inline-style cleanup is lower value than the shared stylesheet. Worth revisiting if this article template gets reused for future investigations.

## Plain-English → token cheat sheet

- "The dark banner at the top with the logo and menu" → `--band-bg` (via `.site-nav`)
- "The big dark section with the headline" (homepage/page hero) → `--band-bg`
- "The white/light space most of the page content sits in" → `--page-bg`
- "The white boxes that hold articles/cards" → `--surface`
- "The dark bar at the very bottom" → `--band-bg` (via `.site-footer`)
- "The main heading text on a light background" → `--text-heading`
- "The main paragraph text on a light background" → `--text-body`
- "The smaller, grayer text under headings" → `--text-muted`
- "White text sitting on a dark section" → `--text-on-dark`
