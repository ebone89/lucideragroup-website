# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

lucideragroup.com — the public site for Lucid Era Group and its sub-brands (Media, Investigations, Technologies). No build step: plain static HTML/CSS, deployed via a Cloudflare Worker named `lucideragroup-website` (confirmed to exist in the account; a static-assets deployment with no custom script, consistent with Cloudflare's git-integrated "Workers Builds"). There's no in-repo Wrangler config — the build/deploy settings live entirely in the Cloudflare dashboard, not this repo.

**Standing priority:** mobile must always work — this is a standing priority on every site in this workspace, not a one-time check.

## Branch strategy

- **`main`** = production, believed to auto-deploy on push (same Workers Builds pattern as the Putnam Young Dems site) — **not yet confirmed in the Cloudflare dashboard**, but treat every push to `main` as a live deploy until that's checked.
- **`staging`** = testing branch, created 2026-08-06. Push here first; whether it gets its own Cloudflare preview URL depends on the dashboard's Git integration settings for this Worker, which haven't been checked yet — confirm in the dashboard, then merge to `main` once verified.

## Structure

- `index.html`, `about.html`, `media.html`, `investigations.html`, `technologies.html` — top-level pages, one per entity plus the group home. Each `<body>` carries an `entity-*` class (`entity-group`, `entity-media`, `entity-invest`, `entity-tech`).
- `east-palatka-data-center.html` — a standalone investigative article template (data center accountability piece), heavier on bespoke inline styling than the rest of the site — see `COLOR_SYSTEM.md`'s "known gaps" for what that means for its colors.
- `assets/css/styles.css` — the entire shared stylesheet. Token-based as of 2026-08-06 — see `COLOR_SYSTEM.md` before touching any color; never reintroduce a raw hex value where a token already exists for that role.
- `assets/images/` — logos per entity.

## Working conventions

- **Read `COLOR_SYSTEM.md` before touching any color.** Use semantic tokens (`--page-bg`, `--band-bg`, `--surface`, `--text-heading`, `--text-body`, `--text-muted`, `--text-on-dark`) for role-based styling; use scale tokens (`--teal-600`, `--amber-400`, etc.) directly only when a value is meant to be that brand color regardless of context.
- **The `--brand-accent` hook exists but isn't wired up yet** (see COLOR_SYSTEM.md) — Investigations/Technologies pages currently render with the same teal accent as Media/Group despite the per-entity token being set. Don't wire this silently as a side effect of unrelated work; it's a visible design change and should be its own deliberate task.
- **Responsive coverage is thin** — as of 2026-08-06 there are only two `@media` breakpoints in the whole stylesheet (`680px`, `600px`), versus the four PYD's site checks against. Any new component should be checked at a phone width (~390px) and a desktop width (~1440px) before being called done, not assumed to inherit adequate coverage from the rest of the sheet.
- No CMS/admin console exists for this site (unlike PYD's Decap CMS setup) — content changes are direct HTML edits for now. Whether this site needs one is an open question, not yet decided.
- No automated tests, no build step. Verify changes by opening the affected page(s) directly in a browser.
