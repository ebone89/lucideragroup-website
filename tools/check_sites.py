#!/usr/bin/env python3
"""Rule checker for the four static sites under sites/.

Usage: python3 tools/check_sites.py
Prints ALL CHECKS PASSED and exits 0, or one line per violation
(<path>: <rule>: <detail>) and exits 1. Standard library only.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Pages every site must contain
REQUIRED_PAGES = {
    "group": ["index.html", "about.html"],
    "technologies": ["index.html", "services.html", "contact.html"],
    "strategies": ["index.html", "services.html", "contact.html"],
    "newsroom": ["index.html", "investigations.html", "east-palatka-data-center.html",
                 "media.html", "stand.html", "standards.html"],
}
BRANCHES = ["technologies", "strategies", "newsroom"]
# Strings that identify another branch inside a link (name or its likely domain words)
BRANCH_TOKENS = {
    "technologies": ["technologies"],
    "strategies": ["strategies"],
    "newsroom": ["newsroom", "lucideramedia", "lucidera-media"],
}
HUB_URL = "https://lucideragroup.com"
MARKER = "<!-- SWAP FOR REAL DOMAIN -->"
LOGOS = ["lucid-era-logo-main.png", "lucid-era-detective-mark.png"]
# File types scanned as text for the content rules
TEXT_EXT = {".html", ".css", ".js", ".json", ".txt", ".xml", ".svg", ".md"}

# Banned terms: (rule detail, compiled pattern, sites it applies to or None for all)
BANNED = [
    ("protonmail", re.compile(r"protonmail", re.I), None),
    ("FBI", re.compile(r"\bFBI\b"), None),
    ("A.C.T. League", re.compile(r"A\.C\.T\.\s*League", re.I), None),
] + [
    (w, re.compile(re.escape(w), re.I), {"technologies"})
    for w in ("progressive", "Democratic", "opposition research", "populism")
]


class PageParser(HTMLParser):
    """Collects the facts the rules need: links, title, meta, redact spans."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []          # (attr, value, line)
        self.title = None
        self._in_title = False
        self.description = None  # None means the tag is missing
        self.has_viewport = False
        self.has_icon = False
        self.lang = None
        self.redacts = []        # (line, has_aria_hidden)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._in_title = True
            self.title = ""
        if tag == "meta":
            if a.get("name", "").lower() == "description":
                self.description = a.get("content", "")
            if a.get("name", "").lower() == "viewport":
                self.has_viewport = True
        if tag == "link" and "icon" in a.get("rel", "").lower().split():
            self.has_icon = True
        for attr in ("href", "src"):
            if attr in a:
                self.links.append((attr, a[attr], line))
        if "redact" in a.get("class", "").split():
            self.redacts.append((line, a.get("aria-hidden") == "true"))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and self.title is not None:
            self.title += data


def run(root: Path) -> list[str]:
    """Check root/sites and root/design. Returns violation strings (empty means pass)."""
    root = Path(root)
    out: list[str] = []

    def v(path: Path, rule: str, detail: str):
        out.append(f"{path.relative_to(root).as_posix()}: {rule}: {detail}")

    # Rule: shared base.css must honor reduced motion
    base = root / "design" / "base.css"
    if not base.is_file():
        out.append("design/base.css: reduced-motion: file missing")
    elif "prefers-reduced-motion" not in base.read_text(encoding="utf-8"):
        v(base, "reduced-motion", "no prefers-reduced-motion block")

    for site, required in REQUIRED_PAGES.items():
        sdir = root / "sites" / site
        titles: dict[str, Path] = {}

        # Rule: required pages exist
        for name in required:
            if not (sdir / name).is_file():
                v(sdir / name, "missing-page", f"required page not found in sites/{site}")

        # Rule: synced shared files match design/
        pairs = [(sdir / "assets/css/base.css", base)]
        pairs += [(sdir / "assets/images" / n, root / "design/logos" / n) for n in LOGOS]
        for copy, src in pairs:
            if copy.is_file() and src.is_file() and copy.read_bytes() != src.read_bytes():
                v(copy, "sync", "differs from design/ source, run tools/sync_shared.py")

        # Content rules over every text file in the site
        for f in sorted(p for p in sdir.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_EXT):
            text = f.read_text(encoding="utf-8", errors="replace")
            check_text(f, site, text, v)
            if f.suffix.lower() == ".html":
                check_html(f, site, sdir, text, titles, v)

    return out


def check_text(f: Path, site: str, text: str, v):
    """Rules that apply to the raw text of any file."""
    # Dash rule: no em dash (U+2014) or en dash (U+2013)
    for ch, name in (("\u2014", "em dash"), ("\u2013", "en dash")):
        if ch in text:
            line = text[: text.index(ch)].count("\n") + 1
            v(f, "dash", f"{name} on line {line}")
    # Signal handle only on the newsroom
    if site != "newsroom" and "ecb.77" in text:
        v(f, "signal", "Signal handle ecb.77 outside sites/newsroom")
    # Owner name only on group and newsroom
    if site not in ("group", "newsroom") and "Ethan Bradley" in text:
        v(f, "owner-name", f"'Ethan Bradley' not allowed in sites/{site}")
    # Banned terms
    for label, pat, only in BANNED:
        if (only is None or site in only) and pat.search(text):
            v(f, "banned-term", label)


def check_html(f: Path, site: str, sdir: Path, text: str, titles: dict, v):
    """Rules that need parsed HTML."""
    p = PageParser()
    p.feed(text)
    lines = text.splitlines()

    # Meta rules: title, description, lang, viewport, icon, unique title
    if not (p.title or "").strip():
        v(f, "meta", "missing or empty <title>")
    else:
        t = p.title.strip()
        if t in titles:
            v(f, "meta", f"duplicate title also used by {titles[t].name}")
        titles[t] = f
    if not (p.description or "").strip():
        v(f, "meta", "missing or empty meta description")
    if not p.lang:
        v(f, "meta", "missing lang on <html>")
    if not p.has_viewport:
        v(f, "meta", "missing viewport meta")
    if not p.has_icon:
        v(f, "meta", "missing rel=icon link")

    # Redaction bars must be hidden from assistive tech
    for line, ok in p.redacts:
        if not ok:
            v(f, "redact", f'class="redact" without aria-hidden="true" on line {line}')

    # Branch pages must link the hub with the exact URL
    if site in BRANCHES and not any(val == HUB_URL for _, val, _ in p.links):
        v(f, "hub-link", f'missing href="{HUB_URL}"')

    for attr, val, line in p.links:
        val = val.strip()
        # Cross-link rule (branches only): no link may point at another branch
        if site in BRANCHES:
            for other in BRANCHES:
                if other != site and any(t in val.lower() for t in BRANCH_TOKENS[other]):
                    v(f, "cross-link", f"{attr}={val!r} points at {other} (line {line})")
        # Skip other external links and pure fragments
        if val.startswith("#") or val == "":
            continue
        if val.startswith(("http:", "https:", "mailto:", "tel:", "data:", "javascript:")):
            continue
        # Root-absolute and protocol-relative paths break when a folder moves to a domain root
        if val.startswith("/"):
            v(f, "relative-path", f"{attr}={val!r} is root-absolute (line {line})")
            continue
        path_part = re.split(r"[?#]", val)[0]
        if path_part.startswith("../") or "/../" in path_part:
            # Only the hub may use ../, and only directly under the swap marker
            prev = lines[line - 2].strip() if line >= 2 else ""
            if site == "group" and prev == MARKER:
                continue
            v(f, "relative-path", f"{attr}={val!r} leaves the site folder without marker (line {line})")
            continue
        # Local file must exist
        target = f.parent / path_part
        if path_part.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            v(f, "missing-file", f"{attr}={val!r} not found (line {line})")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    violations = run(root)
    if violations:
        print("\n".join(violations))
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
