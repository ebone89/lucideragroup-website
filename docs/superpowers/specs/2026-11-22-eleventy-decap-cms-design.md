# Lucid Era: Eleventy Build and Decap CMS

Date: 2026-11-22
Status: Draft for owner review
Builds on: `2026-11-20-lucid-era-multisite-design.md` (the four-site rebuild, now complete on branch `claude/keen-bell-emsl7a`)

## Intent and why

The four sites (Headquarters, Technologies, Strategies, Newsroom) exist as hand-written HTML. The owner wants to add and edit content without touching code: new investigations, commentary, podcast episodes, polling methodology, research papers, and updates to service descriptions and page text. They already run a Decap CMS setup on the Putnam County Young Dems site and want the same kind of editing experience here, with one login that reaches all four sites.

Publishing is the point of the newsroom, so new articles must be real HTML pages that search engines and social link previews can read. That rules out building content in the visitor's browser and is why a build step is used.

The owner also wants every deliverable to read as clean, professional code: no narrated or chatty comments anywhere in the repo.

## Goals

1. Convert the four sites to Eleventy templates that produce the same pages and look as today.
2. Decap CMS at `/admin` on the Headquarters domain, one GitHub sign-in, editing content for all four sites.
3. Content types the owner can create and edit:
   - Newsroom: investigations, commentary posts, podcast episodes, and the text of the What We Stand For and Standards pages.
   - Strategies: research entries (polling methodology, research papers, poll results) with an optional PDF; service descriptions; page text.
   - Technologies: service descriptions; page text.
   - Headquarters: page text.
4. One Cloudflare Worker serves all four domains, handles the GitHub sign-in for Decap, and sets security headers.
5. Cloudflare rebuilds and redeploys automatically on every push to `main`, so a CMS save is live within a few minutes.
6. Rename the hub to Headquarters and soften its separation messaging.
7. A comment cleanup pass across the whole repo.

## Non-goals

- Hosting podcast audio. Episodes are hosted on an external podcast platform; the site embeds the player.
- Comments, newsletters, analytics, search, contact forms, or sign-up forms.
- Editing the East Palatka article's charts or layout through the CMS.
- Multiple CMS users or roles. One owner account.
- Buying domains or configuring DNS (the owner does this in Cloudflare; the design must make it a config change, not a code change).

## Anti-goals

- Any page whose main content only appears after JavaScript runs.
- A CMS that can break the site layout from a text field (no raw HTML fields for page structure).
- Narrated, chatty, or decorative comments in any file, including the Worker and admin page. The Young Dems repo is the counterexample: long paragraph comments explaining history and reasoning, and banner dividers like `# ── Section ──────`.
- Branch sites linking to each other (unchanged rule from the multisite design).
- Em dashes or en dashes in any file (unchanged rule).

## Constraints

- Hosting: Cloudflare Workers with static assets, deployed by Workers Builds from the GitHub repo `ebone89/lucideragroup-website`, matching the Young Dems setup.
- Auth: GitHub OAuth App; secrets `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` stored as Worker secrets, never in the repo.
- Decap CMS loaded from a pinned version on unpkg, GitHub backend, `branch: main`.
- Eleventy 3.x, pinned in `package.json`. No other site framework. Node version pinned for the build.
- Visual design, copy, palette, fonts, and the rule checker's rules from the multisite design all carry over unchanged unless this document says otherwise.
- Every built page must work with JavaScript disabled, except the East Palatka charts and embedded podcast players.

## Approaches considered

1. **Young Dems pattern** (hand HTML, JSON data swapped in by browser JavaScript). Simplest and familiar, but articles, episodes, and papers would be built in the browser, so search engines and link previews often see blank or generic pages. Rejected.
2. **Eleventy build on every publish** (chosen by the owner). The CMS writes Markdown and data files; Cloudflare rebuilds the sites into plain HTML. Real article pages, shared layouts per site, no copied nav and footer. Cost: a build step and a one-time conversion of existing pages to templates.
3. **Hand HTML plus a custom generator script.** No new tools, but the owner would maintain a homemade version of what Eleventy does. Rejected.

## Architecture

### Repository layout

```
src/
  _shared/            base.css, logos, shared partials (head meta, scanlines), filters
  hq/                 Headquarters site (renamed from group)
  technologies/
  strategies/
  newsroom/
  admin/              Decap index.html and config.yml (served on the HQ domain only)
content/              everything the CMS edits, one folder per site
  hq/  technologies/  strategies/  newsroom/
eleventy.config.js
worker.js
wrangler.jsonc
package.json
tools/check_sites.py  (updated to check dist/)
dist/                 build output, git-ignored
  hq/  technologies/  strategies/  newsroom/
```

Each site has its own base layout (nav, footer, accent) in `src/<site>/_layouts/`. The shared stylesheet and logos are copied into every site's output by the build, replacing `tools/sync_shared.py`.

### Content model (what the CMS edits)

All content is Markdown with front matter or small JSON/YAML data files under `content/`. Field lists below are the minimum; the builder may add obvious ones (for example an SEO description) but not new content types.

**Newsroom**
- Investigations (`content/newsroom/investigations/*.md`): title, slug, published date, updated date (optional), case number, location, subject tags, status (Active, Closed, Updated), summary, body (Markdown), sources (list of label + URL), draft flag. Each becomes `/investigations/<slug>/`. The case file card on the newsroom home and investigations index is generated from these fields.
- Commentary (`content/newsroom/commentary/*.md`): title, date, summary, body, draft flag. Every commentary page is visibly labeled "Commentary", per the standards page. This is the blog.
- Episodes (`content/newsroom/episodes/*.md`): title, episode number, date, platform URL (Spotify, Apple Podcasts, YouTube, or Buzzsprout), show notes (Markdown), draft flag. The build turns a supported URL into the matching embedded player; an unsupported URL renders as a plain "Listen" link. The media page lists episodes newest first and shows "Coming soon" when there are none.
- Page text: What We Stand For (values and tech positions as editable lists of title + text) and Standards (sections as editable Markdown). The client firewall sentence on the Standards page is in the layout, not an editable field.

**Strategies**
- Research (`content/strategies/research/*.md`): title, date, type (Methodology, Research paper, Poll results), summary, body, optional PDF upload, draft flag. New "Research" page in the nav plus one page per entry.
- Services: ordered list of title, id, short description, full description.
- Page text: home hero and intro, who it's for, contact text.

**Technologies**
- Services: ordered list, same fields as Strategies. The file tree navigation is generated from this list.
- Page text: home hero and intro, who we serve, contact text.

**Headquarters**
- Page text: home hero, company card descriptions, about page sections.

**Uploads**: images and PDFs go to `content/<site>/uploads/` and are copied to that site's output. Images are resized in the browser on upload as on the Young Dems site, rewritten without narrated comments.

**Drafts**: entries with the draft flag set are skipped by the build. Decap's editorial workflow (pull-request based) is not used.

### East Palatka article

Stays a hand-built template (it has three Chart.js charts and custom components). It is registered as an investigation entry so it appears in listings and cards, with a front matter flag telling the build to use its custom template instead of the Markdown body. Its text stays unchanged.

### Domains and the Worker

One Worker, `worker.js`, with static assets from `dist/`:
- A hostname map in one config file (`sites.config.json` or similar) maps each domain to its output folder: `lucideragroup.com` to `hq`, and placeholders for the three branch domains. Requests are served from the mapped folder.
- Until the branch domains exist, every site is also reachable on the HQ domain under a preview path (for example `/_preview/technologies/`) so the owner can review it. These preview paths are not linked anywhere and send `noindex`.
- `/admin/` and `/api/auth` exist only on the HQ domain. `/api/auth` is a GitHub OAuth flow with a state cookie, functionally like the Young Dems `handleGitHubOAuth`, rewritten clean.
- Security headers on every response; a Content Security Policy that allows only Google Fonts, cdn.jsdelivr.net (Chart.js), unpkg.com (Decap, admin only), GitHub API (admin only), and the four podcast platforms' embed hosts (newsroom only).
- Unknown hostnames get a 404.

The hub's cards link to the branch domains from the same hostname map, so swapping in real domains is one config edit.

### Headquarters changes

- Nav wordmark `LUCID_ERA://hq`; the site is called "Headquarters" in the nav and title.
- The home page's "How we keep our work separate" memo is replaced by one line linking to the newsroom's Standards page. The about page keeps a short paragraph on how the companies relate, without the "hub" framing.

### Comment standard (applies to every file in the repo)

- A comment exists only to state something the code cannot: a non-obvious reason, a constraint, or a warning. One line where possible.
- No narration of what the next line does, no history ("we fixed X earlier"), no decorative banners or divider lines, no section labels that restate a heading or class name.
- HTML: no section comments except where a template boundary would otherwise be unclear.
- Applies retroactively to everything on the branch: `design/base.css`, the site pages (which become templates), `tools/`, README.

### Checking

- `tools/check_sites.py` checks `dist/` after a build instead of `sites/`, with its existing rules, updated for the new hub name, generated pages, and embedded players.
- A build plus check runs before every commit locally (`npm run check`). Workers Builds runs the build; the check is the owner's and Claude's pre-push gate, not a deploy gate.

### Rollout (owner confirmed: the live site is a Cloudflare Worker connected to this GitHub repo)

The live Worker most likely redeploys whenever `main` changes, so nothing from this work is merged to `main` until cutover.
1. All work stays on `claude/keen-bell-emsl7a`.
2. The owner creates a second Worker (name set in `wrangler.jsonc`, e.g. `lucidera-sites`) connected to the same repo with its production branch set to `claude/keen-bell-emsl7a`. It runs on its `*.workers.dev` address for testing, including the admin login.
3. The Decap backend branch is a config value; during testing it points at `claude/keen-bell-emsl7a`, so CMS saves land on the branch the test Worker deploys.
4. Cutover: merge to `main`, switch the new Worker's production branch and the Decap branch to `main`, move `lucideragroup.com` from the old Worker to the new one, then disconnect the old Worker. The README lists these steps in order, including checking in the Cloudflare dashboard which branch the old Worker deploys from.

### Root legacy files

The old root pages (`index.html`, `about.html`, etc.) and the `sites/` folder are removed in this work, because Workers deploys only `dist/` and `src/` replaces `sites/`. The live site is unaffected until the owner switches the domain to the new Worker; the README states that switch step.

## Decided by the owner

- Option 2: Eleventy build on every publish.
- Cloudflare hosting, one login for everything. The current live site is a Cloudflare Worker connected to this repo.
- Podcast audio hosted externally, embedded on the site.
- Content types: investigations, commentary (blog), episodes, polling methodology and research papers, service descriptions, page text.
- Hub named Headquarters; less emphasis on separation messaging on the homepage.
- No narrated comments anywhere.

## Calls made by Claude (owner can override)

- One Worker serving all four domains with a hostname map, plus unlinked preview paths until branch domains exist.
- Research section lives on the Strategies site; commentary lives on the newsroom.
- East Palatka stays a custom template, listed through an investigation entry.
- Drafts via a draft flag rather than Decap's pull-request workflow.
- Firewall sentence fixed in the layout, not editable.
- Legacy root pages and `sites/` removed in this work.
- Until branch domains exist, Headquarters cards link to the preview paths; those paths send `noindex`. The checker treats preview links from HQ as allowed hub links.
- Before the domain switch, the owner signs in at the Worker's `*.workers.dev` URL. The admin host, Decap `base_url`, and OAuth callback come from one config value, so the switch to `lucideragroup.com` is a config change. The README walks through creating the GitHub OAuth App and setting the two secrets.
- Pretty URLs (`/investigations/`, `/investigations/<slug>/`) replace the `.html` names. The Worker redirects the old article URL `/east-palatka-data-center.html` to its new address so existing shared links keep working; other old `.html` pages redirect to their new equivalents.
- Only the draft flag hides an entry. Future dates publish immediately; no scheduling.
- Editable page text covers exactly the copy currently on each page, extracted into data files. Nothing new becomes editable beyond the content types above.

## Left to the builder

- Template language (Nunjucks recommended) and partial structure.
- Exact Decap field widgets and hints.
- Slug generation and URL format details within the patterns above.
- Image resize thresholds.
