# Lucid Era Group: Multi-Site Rebuild Design

Date: 2026-11-20
Status: Draft for owner review

## Intent and why

The current site (one static HTML site, five pages) presents Lucid Era Group as three entities, but only Investigations has real content, and the work the owner actually does is much broader. The owner wants the web presence to represent the whole project while keeping its very different lines of work strictly apart:

- Paid IT services for clients across the political and religious spectrum (churches, small businesses, nonprofits, individuals, political committees).
- Paid political and data consulting, including opposition research.
- Openly progressive investigative reporting and media.

These audiences must not bleed into each other. A church looking for IT help should never land next to opposition research, and the journalism must keep its credibility despite the group also doing paid political work. The 501(c)(4) A.C.T. League is kept completely off these sites for legal and reputational separation.

## Goals

1. Separate, self-contained websites, one per line of business, each deployable to its own domain.
2. One umbrella hub site (Lucid Era Group) that links to every branch site. Branch sites never link to each other; each links only back to the hub via a footer line.
3. Turn the Technologies and Media stubs into real sites with full service and editorial content.
4. Add a new Strategies site for data and political consulting.
5. Keep the existing East Palatka investigation intact and carry it into the newsroom site.
6. Publish an explicit editorial stance, standards, and a client firewall disclosure on the newsroom site.

## Non-goals

- Buying domains, configuring DNS, or setting up hosting. The sites are built so each folder can be pointed at a domain later.
- Splitting into separate git repositories now (possible later because each folder is self-contained).
- Contact forms, booking, payments, CMS, analytics. Contact is via email and Signal links.
- Any A.C.T. League content or links.
- Writing new investigative articles.

## Anti-goals (failure even if it works)

- Any link, shared nav, or "related services" block between branch sites (Technologies, Strategies, Newsroom). Only the hub cross-links.
- Political or editorial language on the Technologies site. It must read as a neutral professional IT business that a conservative church would comfortably hire.
- Opposition research or paid political services mentioned on the Newsroom site, other than in the disclosure policy.
- A site that breaks when moved to its own domain because it references files in another site's folder or uses root-absolute paths.
- Em dashes or AI-sounding filler copy anywhere (owner preference).

## Constraints

- Plain static HTML and CSS, no build step, no framework. Works on any static host (GitHub Pages, Cloudflare Pages, Netlify).
- All paths relative within each site folder.
- Keep the existing visual language: DM Serif Display and DM Sans, dark slate nav and footer, existing token palette in `assets/css/styles.css`. Each site gets its own accent color.
- Contact: `ethan@lucideragroup.com` is the single email on every site (owner decision). The old ProtonMail addresses are retired from the new sites. Signal `ecb.77` appears only on the newsroom site, as the secure channel for tips; Technologies and Strategies list email only.
- Hub domain: `https://lucideragroup.com`. Every branch footer links to it with that absolute URL so it keeps working after a folder moves to its own domain.
- Mobile friendly: the current nav has no mobile handling; each site needs a nav that wraps cleanly at phone width without JavaScript.

## Approaches considered

1. **Sections of one website with visual walls** (the original direction). Cheapest to maintain, but a visitor on any page is one click from every other branch. Rejected by the owner in favor of full separation.
2. **Separate sites, plain HTML, one folder each in this repo** (chosen). Each site is self-contained with its own copy of the stylesheet and logo. Any host works, the owner can edit by hand, and each folder can later move to its own repo or domain. Cost: nav and footer are repeated per page, mitigated because each site has only 3 to 6 pages.
3. **Separate sites via a static site generator (Eleventy)**. Shared templates, less duplication, but adds a build step and depends on the host supporting builds, which is unknown. Not worth it at this page count.

On how the sites relate, the owner chose **hub only**: the group site links to all branches, branches link only back to the hub. Rejected alternatives were fully walled off (no hub) and full cross-linking.

## Site structure

```
sites/
  group/          Lucid Era Group hub
  technologies/   Lucid Era Technologies
  strategies/     Lucid Era Strategies (new)
  newsroom/       Lucid Era Investigations + Lucid Era Media (one site)
```

Each site folder contains its own `index.html`, other pages, `assets/css/styles.css`, and `assets/images/` with only the logos it uses.

The current root-level files (`index.html`, `about.html`, etc. and root `assets/`) stay in place untouched until the owner has set up domains for the new sites, so merging this work cannot take down the live site or break links to the East Palatka article. Removing them is a later, separate step. A short root `README.md` explains the folder layout and how to point each folder at a domain.

### 1. Group hub (`sites/group/`)

Accent: teal (current group palette).

- `index.html`: hero with group logo and a one-paragraph mission. One card per branch (Technologies, Strategies, Investigations and Media) with a short description and an outbound link. A short "How we keep our work separate" section explaining that each company runs independently, the newsroom never covers anyone who is a client of any Lucid Era company, and each site has its own contact.
- `about.html`: who runs the group (Ethan Bradley, based in Palatka, Florida), what each branch does, and the separation policy in more detail.

Branch links on the hub point to relative paths for now (`../technologies/index.html`) and are clearly marked in a comment as the place to swap in real domains. Branch sites link back to the hub at `https://lucideragroup.com`.

### 2. Technologies (`sites/technologies/`)

Accent: coral (current tech accent). Tone: neutral, professional, nonpartisan.

- `index.html`: hero, a services overview, a "Who we serve" strip (small businesses, individuals and families, nonprofits, churches and faith organizations, political committees and campaigns), and a contact call to action.
- `services.html`: one section per service:
  - IT consulting and planning
  - Troubleshooting and repair
  - Systems administration and managed IT
  - Network and infrastructure build-outs
  - Website builds and hosting
  - Digital security and privacy hardening, including doxxing protection for at-risk people
  - Campaign and election security (account security, phishing defense, device hardening for campaign staff and committees; framed in a nonpartisan way)
  - Deepfake and manipulated media analysis
  - Digital literacy workshops and training
- `contact.html`: email and Signal, what to include in a first message, service area (Putnam County and Northeast Florida, remote work available).
- Footer: "A Lucid Era Group company" linking to the hub only.

### 3. Strategies (`sites/strategies/`)

Accent: amber or a new distinct color (builder's call within the existing token set). No existing logo: use a text wordmark until the owner supplies one.

- `index.html`: hero, service overview, who it's for (progressive and Democratic campaigns, committees, issue groups, nonprofits), contact call to action.
- `services.html`:
  - Data analysis and visualization
  - Surveys and polling
  - Focus groups
  - Voter file and targeting data
  - Campaign strategy and political consulting
  - Opposition and background research (public records based, documented sourcing)
- `contact.html`: email and Signal. Note confidentiality of client engagements.
- Footer: "A Lucid Era Group company" linking to the hub only.

### 4. Newsroom (`sites/newsroom/`)

Investigations and Media share one site because they share audience, voice, and standards. Brand name on the site: "Lucid Era Investigations and Media" in the nav is too long; use "Lucid Era Media" as the site name with "Investigations" as a section. Accent: teal for Media pages, amber for Investigations pages, matching the current entity accents.

Voice: openly progressive. People-first populism, workers' rights, environmental protection, anti-racism, anti-corruption, anti-greed, and collective responsibility over individualism. Reporting stays rigorous and sourced; commentary is labeled as commentary.

- `index.html`: hero, latest investigation (East Palatka), short intro to the podcast and commentary, tips call to action.
- `investigations.html`: published work list (East Palatka card), methodology summary, verification lab (deepfake and manipulated media detection as a newsroom capability), public records and Sunshine Law help (readers can suggest requests or ask how to file one), tips section.
- `east-palatka-data-center.html`: the existing article moved as is, with nav, footer, and asset paths updated.
- `media.html`: podcast and video production, commentary. No episodes exist yet, so this page describes the show and says episodes are coming, with no fake content.
- `stand.html` ("What we stand for"): the editorial platform. Populist and progressive values listed above, plus the tech policy positions: privacy rights, right to repair and digital ownership, tech regulation that makes technology safer and more beneficial for everyone, fiber internet for everyone, access to technology, and responsible use of technology.
- `standards.html` ("Standards and disclosure"): the current About principles (public sources, show your work, no advertising, community first), reporting versus commentary labeling, corrections policy, and the client firewall: "Lucid Era Media does not report on anyone who is a client of Lucid Era Group, including clients of Lucid Era Technologies and Lucid Era Strategies. Where any connection to a subject exists, we disclose it." Also who runs it and contact and tips.
- Footer: "A Lucid Era Group company" linking to the hub only.

The current `about.html` mislabels Investigations as "Lucid Era Media" in places; its content is merged into `standards.html` with consistent naming, so the problem goes away.

## Shared conventions

- Each site's stylesheet starts as a copy of the current `styles.css`, trimmed to what that site uses where convenient, plus: a mobile nav rule (links wrap under the brand below about 680px), a services section style, and a CTA block style.
- Each page keeps the `<!-- NAV -->` and `<!-- FOOTER -->` comments so hand edits stay easy.
- Every page has a real `<title>` and `<meta name="description">`.
- Logo PNGs are 220 to 240 KB each, too heavy for a 48px nav icon. The builder may downscale copies for nav and footer use; keep originals for the large hero image.

## Decided by the owner

- Separate websites, not sections of one site.
- Hub-only linking model.
- A.C.T. League removed entirely.
- Openly progressive newsroom with the values listed above.
- All additional services and pages proposed in conversation are included.
- The client firewall covers anyone the owner works with directly as a client, across every branch.
- One email for everything: `ethan@lucideragroup.com`.

## Calls made by Claude (owner can override)

- "Lucid Era Strategies" as the consulting brand name.
- Investigations and Media combined into one newsroom site.
- Tech policy positions live on the newsroom "What we stand for" page.
- Plain HTML, one folder per site in this repo.
- Signal kept only on the newsroom site for secure tips, since it protects sources better than email.
- The owner's full name appears on the hub and newsroom only. Technologies and Strategies show no personal name beyond the shared email address.
- Root-level legacy pages stay until domains are live.

## Left to the builder

- Exact copy for each section, following the voice rules above.
- Strategies accent color and text wordmark styling.
- Card and section layouts within the existing visual language.
- Whether to trim each site's stylesheet.
