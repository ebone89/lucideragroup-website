# Lucid Era Multi-Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build four self-contained static websites (hub, Technologies, Strategies, Newsroom) in `sites/`, in the approved noir hacker style, without touching the current live root pages.

**Architecture:** Plain HTML and CSS, one folder per site, no build step. A shared `design/base.css` and the two logo files are copied into each site by `tools/sync_shared.py`, so every folder stays deployable on its own. `tools/check_sites.py` is the test suite: it enforces the separation, path, copy, and contact rules from the spec, and every task ends by running it.

**Tech Stack:** HTML5, CSS (no framework), Google Fonts (IBM Plex Mono, IBM Plex Sans, Special Elite), Chart.js 4.4.1 (East Palatka article only), Python 3 standard library for tooling, Playwright (pre-installed) for screenshots.

**Spec:** `docs/superpowers/specs/2026-11-20-lucid-era-multisite-design.md`. Visual reference: `docs/superpowers/specs/assets/style-mockup.html`.

## Global Constraints

- Root-level files (`index.html`, `about.html`, `media.html`, `investigations.html`, `technologies.html`, `east-palatka-data-center.html`, `assets/`) are not modified or deleted.
- Every path inside a site is relative and resolves inside that site's folder. The only exceptions are the hub's outbound branch links (`../technologies/index.html` etc., each preceded by `<!-- SWAP FOR REAL DOMAIN -->`).
- Branch sites link to the hub only, at exactly `https://lucideragroup.com`, via the footer line "A Lucid Era Group company". No branch site links to another branch site.
- Email everywhere: `ethan@lucideragroup.com`. Signal `ecb.77` appears only in `sites/newsroom/`. The old ProtonMail addresses appear nowhere in `sites/`.
- The name "Ethan Bradley" appears only in `sites/group/` and `sites/newsroom/`.
- No em dashes (U+2014) or en dashes (U+2013) in any file under `sites/`. Use commas, periods, colons, or "to".
- No "FBI", agency seals, or government insignia. Generic CLASSIFIED / DECLASSIFIED wording only.
- No mention of A.C.T. League anywhere in `sites/`.
- Technologies copy is nonpartisan: none of the words "progressive", "Democratic", "opposition research", "populism" appear in `sites/technologies/`.
- Firewall sentence, verbatim, on `sites/newsroom/standards.html`: "Lucid Era Media does not report on anyone who is a client of Lucid Era Group, including clients of Lucid Era Technologies and Lucid Era Strategies. Where any connection to a subject exists, we disclose it."
- Palette, fonts, and shared elements exactly as the spec's "Visual style" section. Per-site accent (`--accent`): group `#36A03E`, technologies `#36A03E`, strategies `#D8C08A`, newsroom `#A3322A`. (The spec's older coral/amber/teal accent notes are superseded by the Visual style section; these match the approved mockup cards.)
- Logos: `lucid-era-logo-main.png` in heroes, `lucid-era-detective-mark.png` in navs, footers, and as favicon. No per-company logo images.
- Every page has a unique `<title>`, a non-empty `<meta name="description">`, `lang="en"`, the viewport meta, and `<link rel="icon" href="assets/images/lucid-era-detective-mark.png">`.

## Review Focus

1. **Phone width (390px):** no horizontal page scroll on any page; the nav wraps under the wordmark; the Technologies file tree and newsroom folders fit. Pinned by the Task 6 screenshot check.
2. **Reduced motion:** with `prefers-reduced-motion: reduce`, the blinking cursor stops and the scanline overlay is hidden. Pinned by a `check_sites.py` rule in Task 1 that `base.css` contains a `prefers-reduced-motion` block.
3. **Redaction bars hide nothing real:** a redaction bar wraps a short decorative word whose real text is already public elsewhere on the page, and carries `aria-hidden="true"`. Text under a CSS bar can be selected and copied, so it must never be used to hide actual sensitive material. Pinned by a check in Task 1 that every `class="redact"` element has `aria-hidden="true"`.
4. **East Palatka article after the move:** all three Chart.js charts render and the article's existing components (stat cards, balance grid, callouts) still look right. Pinned by Task 5's screenshot step looking for three non-blank canvases.
5. **Site moved to its own domain root:** a folder served at `/` must still work. Pinned by the Task 1 relative-path rule (no `/`-rooted paths, no `../` except the hub's marked links).

---

## File Structure

```
design/base.css                 shared tokens, nav, footer, hero, cards, memo, folder, scanlines (source of truth)
design/logos/                   lucid-era-logo-main.png, lucid-era-detective-mark.png
tools/sync_shared.py            copies base.css + logos into every sites/<name>/assets/
tools/check_sites.py            the rule checker (test suite)
tools/screenshot.js             Playwright: every page at 1280 and 390, writes to a scratch dir
sites/<name>/assets/css/base.css   synced copy (never hand edited)
sites/<name>/assets/css/site.css   that site's accent and site-only components
sites/<name>/assets/images/        synced logos (+ nothing else, except newsroom article needs none)
sites/<name>/*.html
README.md                        folder layout, how to point a folder at a domain, how to run sync and check
```

Every page links `assets/css/base.css` then `assets/css/site.css`. Nav and footer markup is repeated per page between `<!-- NAV -->` / `<!-- /NAV -->` and `<!-- FOOTER -->` / `<!-- /FOOTER -->` comments.

---

### Task 1: Shared design, sync tool, and rule checker

**Files:**
- Create: `design/base.css`, `design/logos/lucid-era-logo-main.png`, `design/logos/lucid-era-detective-mark.png` (copy from `docs/superpowers/specs/assets/`)
- Create: `tools/sync_shared.py`, `tools/check_sites.py`, `tools/test_check_sites.py`

**Interfaces:**
- Produces: `python3 tools/sync_shared.py` (copies into every existing `sites/*/assets/`), `python3 tools/check_sites.py` (exit 0 and prints `ALL CHECKS PASSED`, else exit 1 and one line per violation as `<path>: <rule>: <detail>`).
- Produces CSS class names later tasks use: `.site-nav`, `.wordmark` (`LUCID_ERA://<site>` with the suffix in `<span>`), `.hero`, `.kicker`, `.cursor`, `.readout`, `.sec`, `.rule`, `.grid`, `.card`, `.card .id`, `.go`, `.memo`, `.folder-wrap`, `.tab`, `.folder`, `.stamp`, `.redact`, `.btn`, `.site-footer`, `.wrap`, `.prose` (long-form text on dark), `.doc` (light paper document panel for long-form newsroom pages).

- [ ] **Step 1: Write `tools/test_check_sites.py`** (unittest, builds a temp `sites/` tree per test and calls `check_sites.run(root) -> list[str]`). Tests and assertions:
  - `test_clean_tree_passes`: a minimal valid site per folder returns `[]`.
  - `test_em_dash_flagged`: a page containing `—` yields a violation containing `dash`.
  - `test_branch_cross_link_flagged`: `technologies/index.html` linking `../strategies/index.html` or any `strategies` domain yields `cross-link`.
  - `test_root_absolute_path_flagged`: `src="/assets/x.png"` yields `relative-path`.
  - `test_unmarked_parent_path_flagged`: `../` in a branch site yields `relative-path`; in `group/` it passes only when the preceding line is `<!-- SWAP FOR REAL DOMAIN -->`.
  - `test_missing_local_file_flagged`: `href="nope.html"` yields `missing-file`.
  - `test_signal_outside_newsroom_flagged`: `ecb.77` in `strategies/` yields `signal`.
  - `test_name_outside_allowed_flagged`: `Ethan Bradley` in `technologies/` yields `owner-name`.
  - `test_banned_terms_flagged`: `protonmail`, `FBI` (word match), `A.C.T. League` anywhere, and `progressive` in `technologies/` each yield `banned-term`.
  - `test_hub_link_required`: a branch page without `href="https://lucideragroup.com"` yields `hub-link`.
  - `test_meta_required`: missing `<title>` or empty description yields `meta`; duplicate titles within a site yield `meta`.
  - `test_redact_needs_aria_hidden`: `<span class="redact">x</span>` yields `redact`.
  - `test_synced_copy_drift_flagged`: a site `base.css` differing from `design/base.css` yields `sync`.
  - `test_reduced_motion_required`: `design/base.css` lacking `prefers-reduced-motion` yields `reduced-motion`.

- [ ] **Step 2: Run, expect failure.** `python3 -m unittest tools/test_check_sites.py -v` fails with `ModuleNotFoundError: check_sites`.

- [ ] **Step 3: Implement `tools/check_sites.py`** with `run(root: Path) -> list[str]` and `main()`. Parse HTML with `html.parser`; collect every `href`/`src`; ignore `http(s):`, `mailto:`, `#` fragments, and `https://fonts.googleapis.com`, `https://fonts.gstatic.com`, `https://cdn.jsdelivr.net`. Required pages per site: group `index.html, about.html`; technologies `index.html, services.html, contact.html`; strategies `index.html, services.html, contact.html`; newsroom `index.html, investigations.html, east-palatka-data-center.html, media.html, stand.html, standards.html`. Missing required page is rule `missing-page`. Also scan `.css` files for the dash rule.

- [ ] **Step 4: Write `design/base.css`** from the mockup's `<style>` block, generalized: tokens on `:root` per the spec palette plus `--accent`; `body::after` scanlines; nav and footer; all classes in Interfaces; `.card` top border uses `var(--accent)`; `.doc` is a `--paper` panel with `--ink` text, IBM Plex Sans body, mono headings; nav links wrap below 680px; `@media (prefers-reduced-motion: reduce)` disables `.cursor` animation and hides `body::after`; favicon not in CSS.

- [ ] **Step 5: Write `tools/sync_shared.py`**: for each `sites/*/`, create `assets/css/` and `assets/images/`, copy `design/base.css` and both logos. Idempotent.

- [ ] **Step 6: Run tests, expect pass.** `python3 -m unittest tools/test_check_sites.py -v` → all OK.

- [ ] **Step 7: Commit** `git add design tools && git commit -m "Add shared design, sync tool, and site rule checker"`

### Task 2: Hub site (`sites/group/`)

**Files:** Create `sites/group/index.html`, `sites/group/about.html`, `sites/group/assets/css/site.css` (`--accent:#36A03E`), synced assets.

**Interfaces:** Consumes Task 1 classes and tools.

- [ ] **Step 1: Run checker, expect failure.** `python3 tools/sync_shared.py; python3 tools/check_sites.py` reports `missing-page` for `group/index.html`.
- [ ] **Step 2: Build `index.html`** following the mockup: nav wordmark `LUCID_ERA://group`, links Companies (`#companies`), How we work (`#separate`), About (`about.html`), Contact (`mailto:ethan@lucideragroup.com`). Hero: main logo (`width="240" height="240"`), kicker `PALATKA, FLORIDA`, headline "Technology, strategy, and the truth" with `<em>truth</em>` and `.cursor`, `status --all` readout. `// THE COMPANIES` with three file cards (FILE 01 Technologies, FILE 02 Strategies, FILE 03 Newsroom titled "Lucid Era Media") each linking to `../<site>/index.html` with the SWAP comment. Separation memo with the firewall in plain words. Footer with detective mark and email.
- [ ] **Step 3: Build `about.html`**: who runs it (Ethan Bradley, Palatka, Florida), one paragraph per company, separation policy in full including the firewall covering all direct clients.
- [ ] **Step 4: Run checker, expect group checks to pass** (other sites still report `missing-page`; that is expected until Task 5).
- [ ] **Step 5: Commit** `git commit -m "Add Lucid Era Group hub site"`

### Task 3: Technologies site (`sites/technologies/`)

**Files:** Create `index.html`, `services.html`, `contact.html`, `assets/css/site.css`.

**Interfaces:** Consumes Task 1. Produces `.tree` component in this site's `site.css` only.

- [ ] **Step 1: Run checker, expect `missing-page` for technologies.**
- [ ] **Step 2: Add the file tree component to `site.css`:** `.tree` is a mono list rendered with `├──` / `└──` glyphs (in markup, not pseudo content, so it copies cleanly), each entry a link to `services.html#<id>`. On desktop the services page shows the tree as a sticky left sidebar beside the content; below 680px the tree sits above the content as a block.
- [ ] **Step 3: Build pages.** Nav `LUCID_ERA://technologies`. Hero headline names the company "Technologies" in type beside the main logo. `index.html`: services overview as the tree (`/services/consulting`, `/troubleshooting`, `/managed-it`, `/networks`, `/websites`, `/security`, `/election-security`, `/deepfake-analysis`, `/training`), "Who we serve" strip (small businesses, individuals and families, nonprofits, churches and faith organizations, political committees and campaigns), contact CTA. `services.html`: one section per service with those nine ids, in the spec order. `contact.html`: email, what to include in a first message, service area Putnam County and Northeast Florida, remote available. No stamps, no redactions. Footer hub line.
- [ ] **Step 4: Run checker, expect technologies checks to pass.**
- [ ] **Step 5: Commit** `git commit -m "Add Lucid Era Technologies site"`

### Task 4: Strategies site (`sites/strategies/`)

**Files:** Create `index.html`, `services.html`, `contact.html`, `assets/css/site.css` (`--accent:#D8C08A`).

- [ ] **Step 1: Run checker, expect `missing-page` for strategies.**
- [ ] **Step 2: Build pages** in a dossier and data readout feel (builder's call within base classes; e.g. services as numbered dossier cards with a mono readout line). Nav `LUCID_ERA://strategies`. `index.html`: overview, who it's for (progressive and Democratic campaigns, committees, issue groups, nonprofits), CTA. `services.html`: the six services in spec order with ids `data`, `polling`, `focus-groups`, `voter-data`, `strategy`, `research`. `contact.html`: email and a confidentiality note. No owner name, no Signal. Footer hub line.
- [ ] **Step 3: Run checker, expect strategies checks to pass.**
- [ ] **Step 4: Commit** `git commit -m "Add Lucid Era Strategies site"`

### Task 5: Newsroom site (`sites/newsroom/`)

**Files:** Create `index.html`, `investigations.html`, `east-palatka-data-center.html`, `media.html`, `stand.html`, `standards.html`, `assets/css/site.css` (`--accent:#A3322A`, plus the article component styles copied from root `assets/css/styles.css` sections "from east-palatka-data-center.html" scoped under `.doc`).

- [ ] **Step 1: Run checker, expect `missing-page` for newsroom.**
- [ ] **Step 2: Port the article.** Copy root `east-palatka-data-center.html` into the new shell: new nav/footer, article body wrapped in `.doc` (light paper document, so the existing light components keep working), a `DECLASSIFIED / PUBLIC RECORD` header strip, Chart.js script unchanged, `Chart.defaults.font.family` set to `'IBM Plex Sans'`, old logo `<img>` tags removed, the closing contact line changed to `ethan@lucideragroup.com`. Article text otherwise unchanged except replacing any em or en dashes.
- [ ] **Step 3: Build the other pages.** Nav `LUCID_ERA://newsroom` with links Investigations, Media, What we stand for, Standards. `index.html`: hero, East Palatka as a case file folder (`CASE NO. 2026-001`, stamp `PUBLISHED`), podcast and commentary intro, tips CTA (email + Signal). `investigations.html`: published work folders, methodology summary, verification lab section (deepfake detection), public records and Sunshine Law help, tips. `media.html`: show description, "Episodes coming soon", no fake episodes. `stand.html`: the values and tech positions from the spec, each as a `CLASSIFIED`-style file header with plain text. `standards.html`: principles, reporting vs commentary labels, corrections policy, firewall sentence verbatim, who runs it (Ethan Bradley), contact and tips. Every `.redact` has `aria-hidden="true"` and covers only a decorative word.
- [ ] **Step 4: Run checker, expect `ALL CHECKS PASSED`.**
- [ ] **Step 5: Screenshot the article** with `node tools/screenshot.js sites/newsroom/east-palatka-data-center.html` (Task 6 creates the script; write it here if Task 6 has not run) and confirm three charts render.
- [ ] **Step 6: Commit** `git commit -m "Add Lucid Era Media newsroom site"`

### Task 6: Visual verification and README

**Files:** Create `tools/screenshot.js`, `README.md`.

- [ ] **Step 1: Write `tools/screenshot.js`**: takes page paths (default every `sites/**/*.html`), opens each at 1280x900 and 390x844 with `deviceScaleFactor: 1`, full-page screenshot to a scratch dir, and prints `OVERFLOW <path> <width>` when `document.documentElement.scrollWidth > innerWidth`.
- [ ] **Step 2: Run it.** `node tools/screenshot.js` prints no `OVERFLOW` lines. Review each screenshot against the mockup; fix and re-run until clean.
- [ ] **Step 3: Write `README.md`**: folder layout, "edit `design/base.css` then run `python3 tools/sync_shared.py`", "run `python3 tools/check_sites.py` before committing", how to point each `sites/<name>/` folder at its own domain (any static host, publish directory = that folder), where to swap the hub's branch links, and that root legacy files stay until domains are live.
- [ ] **Step 4: Final run.** `python3 -m unittest tools/test_check_sites.py && python3 tools/check_sites.py` → all pass.
- [ ] **Step 5: Commit and push** `git commit -m "Add screenshot tool and README" && git push origin claude/keen-bell-emsl7a`
