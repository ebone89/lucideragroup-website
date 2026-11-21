# Lucid Era Group websites

Four separate static sites, one folder each. There is no build step and no framework.

| Folder | Site |
| --- | --- |
| `sites/group/` | Lucid Era Group hub (the umbrella) |
| `sites/technologies/` | Lucid Era Technologies |
| `sites/strategies/` | Lucid Era Strategies |
| `sites/newsroom/` | Lucid Era Media newsroom |

## Layout

- `design/` holds the shared design source: `base.css` and the logos. Edit shared styling here only.
- `sites/<name>/assets/` holds each site's synced copy of the shared files, plus its own `css/site.css`.
- `tools/` holds the checker, the sync script, and the screenshot script.
- `docs/` holds planning notes.
- The files at the repo root (`index.html`, `about.html`, `technologies.html`, and so on) are the legacy site. They stay in place until the new domains are live.

## Editing shared design

Never hand edit the synced copies under `sites/*/assets/`. Change `design/base.css`, then copy it out:

```bash
# edit design/base.css, then push it into every site
python3 tools/sync_shared.py
```

Site-only styling goes in that site's `assets/css/site.css`.

## Checks before committing

```bash
# links, shared files, required tags, banned punctuation
python3 tools/check_sites.py

# tests for the checker itself
python3 -m unittest tools/test_check_sites.py
```

Both must pass.

## Local preview and screenshots

Open any page directly in a browser, for example `sites/group/index.html`. Pages use relative links, so no server is needed.

```bash
# screenshot every page at 1280px and 390px, and print OVERFLOW lines for horizontal scroll
node tools/screenshot.js

# only some pages, with a chosen output folder
SHOT_DIR=/tmp/shots node tools/screenshot.js sites/newsroom/index.html
```

This needs Node with Playwright installed. Fonts and the newsroom charts load from public CDNs, so they appear blank or fall back to default fonts when the machine is offline.

## Deploying

Each `sites/<name>/` folder is a complete site. On any static host, create one project per site and set its publish directory to that folder, then attach the domain:

- `sites/group/` to the main Lucid Era Group domain
- `sites/technologies/` to the Technologies domain
- `sites/strategies/` to the Strategies domain
- `sites/newsroom/` to the newsroom domain

Nothing in a site depends on files outside its own folder.

## Swapping the hub's branch links

The hub links to the three company sites with relative paths so it works before any domain exists. When the domains are live, edit the three company cards in `sites/group/index.html` (the `<a class="card" href="...">` lines) and replace `../technologies/index.html`, `../strategies/index.html`, and `../newsroom/index.html` with the full URLs. The branch sites already link to the hub at https://lucideragroup.com and need no change.
