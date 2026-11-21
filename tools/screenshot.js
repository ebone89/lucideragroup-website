#!/usr/bin/env node
/*
 * Screenshot every site page at desktop and phone width, and flag horizontal overflow.
 *
 * Usage:
 *   node tools/screenshot.js                       # every sites/**\/*.html
 *   node tools/screenshot.js sites/newsroom/a.html  # only the pages given
 *   SHOT_DIR=/some/dir node tools/screenshot.js     # choose where PNGs go
 *
 * For each page and each viewport (1280x900 desktop, 390x844 phone, deviceScaleFactor 1)
 * it writes a full-page PNG named <path with / as _>-<width>.png into SHOT_DIR, and prints
 *   OVERFLOW <path> <width>
 * when document.documentElement.scrollWidth is wider than the viewport (horizontal scroll).
 * Exit code is 1 if any page overflowed or failed to load, 0 otherwise.
 */
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const ROOT = path.resolve(__dirname, '..');
const SHOT_DIR = process.env.SHOT_DIR ||
  path.join(require('os').tmpdir(), 'lucid-era-shots');
const VIEWPORTS = [
  { width: 1280, height: 900 },
  { width: 390, height: 844 },
];
// Time to let fonts and Chart.js animations finish before capturing
const SETTLE_MS = 1500;

// Recursively collect .html files under a directory, as paths relative to ROOT
function findHtml(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...findHtml(full));
    else if (entry.name.endsWith('.html')) out.push(path.relative(ROOT, full));
  }
  return out.sort();
}

async function main() {
  // Pages from the command line, or every page under sites/
  const pages = process.argv.length > 2
    ? process.argv.slice(2).map(p => path.relative(ROOT, path.resolve(p)))
    : findHtml(path.join(ROOT, 'sites'));
  fs.mkdirSync(SHOT_DIR, { recursive: true });

  const browser = await chromium.launch();
  let problems = 0;
  try {
    for (const vp of VIEWPORTS) {
      // One context per viewport so the size and scale factor apply to every page
      const context = await browser.newContext({ viewport: vp, deviceScaleFactor: 1 });
      const page = await context.newPage();
      for (const rel of pages) {
        const url = pathToFileURL(path.join(ROOT, rel)).href;
        try {
          await page.goto(url, { waitUntil: 'networkidle' });
          await page.evaluate(() => document.fonts.ready);
          await page.waitForTimeout(SETTLE_MS);
        } catch (err) {
          console.log(`ERROR ${rel} ${vp.width} ${err.message.split('\n')[0]}`);
          problems++;
          continue;
        }
        // Horizontal scroll check: page wider than the viewport
        const { scrollWidth, innerWidth } = await page.evaluate(() => ({
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
        }));
        if (scrollWidth > innerWidth) {
          console.log(`OVERFLOW ${rel} ${vp.width}`);
          problems++;
        }
        const file = path.join(SHOT_DIR, `${rel.replace(/[\\/]/g, '_').replace(/\.html$/, '')}-${vp.width}.png`);
        await page.screenshot({ path: file, fullPage: true });
        console.log(`shot ${file}`);
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }
  process.exit(problems ? 1 : 0);
}

main().catch(err => { console.error(err); process.exit(1); });
