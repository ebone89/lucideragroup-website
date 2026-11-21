"""Tests for check_sites.py. Each test builds a temp tree (sites/ + design/) and runs the checker."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_sites  # noqa: E402

HUB = '<a href="https://lucideragroup.com">A Lucid Era Group company</a>'
MARKER = "<!-- SWAP FOR REAL DOMAIN -->"
CSS = "body{color:red}\n@media (prefers-reduced-motion: reduce){.cursor{animation:none}}\n"
LOGOS = ["lucid-era-logo-main.png", "lucid-era-detective-mark.png"]

# Required pages per site (mirrors the checker's list)
PAGES = {
    "group": ["index.html", "about.html"],
    "technologies": ["index.html", "services.html", "contact.html"],
    "strategies": ["index.html", "services.html", "contact.html"],
    "newsroom": ["index.html", "investigations.html", "east-palatka-data-center.html",
                 "media.html", "stand.html", "standards.html"],
}


def page(title, body="", hub=True):
    """A minimal valid page. Branch pages carry the hub link."""
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{title}</title>\n<meta name="description" content="About {title}">\n'
        '<link rel="icon" href="assets/images/lucid-era-detective-mark.png">\n'
        '<link rel="stylesheet" href="assets/css/base.css">\n</head>\n<body>\n'
        f'{body}\n{HUB if hub else ""}\n</body>\n</html>\n'
    )


class CheckSitesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        # Shared design source
        (self.root / "design").mkdir()
        (self.root / "design" / "base.css").write_text(CSS)
        # One valid site per folder, with a synced base.css and logos
        for site, pages in PAGES.items():
            sdir = self.root / "sites" / site
            (sdir / "assets" / "css").mkdir(parents=True)
            (sdir / "assets" / "images").mkdir(parents=True)
            (sdir / "assets" / "css" / "base.css").write_text(CSS)
            for logo in LOGOS:
                (sdir / "assets" / "images" / logo).write_bytes(b"png")
            for p in pages:
                (sdir / p).write_text(page(f"{site} {p}", hub=(site != "group")))

    def write(self, rel, text):
        (self.root / "sites" / rel).write_text(text, encoding="utf-8")

    def assertRule(self, rule, violations=None):
        violations = check_sites.run(self.root) if violations is None else violations
        self.assertTrue(any(f": {rule}: " in v for v in violations),
                        f"expected rule {rule!r} in {violations}")

    def test_clean_tree_passes(self):
        self.assertEqual(check_sites.run(self.root), [])

    def test_em_dash_flagged(self):
        self.write("group/about.html", page("About", "<p>a \u2014 b</p>", hub=False))
        self.assertRule("dash")

    def test_en_dash_in_css_flagged(self):
        (self.root / "sites/group/assets/css/site.css").write_text("/* a \u2013 b */")
        self.assertRule("dash")

    def test_dash_entities_flagged(self):
        # Named and numeric references for em and en dashes are caught too
        for ent in ("&mdash;", "&ndash;", "&#8212;", "&#8211;"):
            self.write("group/about.html", page("About", f"<p>a {ent} b</p>", hub=False))
            self.assertRule("dash")
        # A plain hyphen and other entities stay clean
        self.write("group/about.html", page("About", "<p>a - b &amp; c &rarr; d</p>", hub=False))
        self.assertEqual(check_sites.run(self.root), [])

    def test_branch_cross_link_flagged(self):
        self.write("technologies/index.html",
                   page("T", '<a href="../strategies/index.html">x</a>'))
        self.assertRule("cross-link")
        self.write("technologies/index.html",
                   page("T", '<a href="https://strategies.example.com">x</a>'))
        self.assertRule("cross-link")

    def test_root_absolute_path_flagged(self):
        self.write("strategies/index.html", page("S", '<img src="/assets/x.png">'))
        self.assertRule("relative-path")

    def test_unmarked_parent_path_flagged(self):
        # Branch site: never allowed, even with the marker
        self.write("technologies/index.html",
                   page("T", f'{MARKER}\n<a href="../group/index.html">x</a>'))
        self.assertRule("relative-path")
        self.write("technologies/index.html", page("T"))
        # Group: unmarked fails
        self.write("group/index.html",
                   page("G", '<a href="../technologies/index.html">x</a>', hub=False))
        self.assertRule("relative-path")
        # Group: marker on the line directly before passes
        self.write("group/index.html",
                   page("G", f'{MARKER}\n<a href="../technologies/index.html">x</a>', hub=False))
        self.assertEqual(check_sites.run(self.root), [])
        # Group: marker two lines up (blank line between) fails
        self.write("group/index.html",
                   page("G", f'{MARKER}\n\n<a href="../technologies/index.html">x</a>', hub=False))
        self.assertRule("relative-path")

    def test_missing_local_file_flagged(self):
        self.write("group/index.html", page("G", '<a href="nope.html">x</a>', hub=False))
        self.assertRule("missing-file")

    def test_signal_outside_newsroom_flagged(self):
        self.write("strategies/index.html", page("S", "<p>Signal ecb.77</p>"))
        self.assertRule("signal")
        # Allowed in the newsroom
        self.write("strategies/index.html", page("S"))
        self.write("newsroom/stand.html", page("Stand", "<p>Signal ecb.77</p>"))
        self.assertEqual(check_sites.run(self.root), [])

    def test_name_outside_allowed_flagged(self):
        self.write("technologies/index.html", page("T", "<p>Ethan Bradley</p>"))
        self.assertRule("owner-name")

    def test_banned_terms_flagged(self):
        cases = [
            ("group/about.html", "protonmail", False),
            ("group/about.html", "the FBI said", False),
            ("group/about.html", "A.C.T. League", False),
            ("technologies/index.html", "progressive", True),
        ]
        for rel, text, hub in cases:
            with self.subTest(text=text):
                self.write(rel, page("X", f"<p>{text}</p>", hub=hub))
                self.assertRule("banned-term")
                # Restore a clean page
                self.write(rel, page(f"{rel}", hub=hub))

    def test_banned_term_word_match_for_fbi(self):
        # "FBI" must be a whole word, so unrelated words do not trip it
        self.write("group/about.html", page("About", "<p>fbiology</p>", hub=False))
        self.assertEqual(check_sites.run(self.root), [])

    def test_progressive_allowed_outside_technologies(self):
        self.write("strategies/index.html", page("S", "<p>progressive</p>"))
        self.assertEqual(check_sites.run(self.root), [])

    def test_hub_link_required(self):
        self.write("strategies/contact.html", page("C", hub=False))
        self.assertRule("hub-link")

    def test_meta_required(self):
        self.write("group/about.html",
                   '<html lang="en"><head><meta name="viewport" content="x">'
                   '<meta name="description" content="d">'
                   '<link rel="icon" href="assets/images/lucid-era-detective-mark.png">'
                   '</head><body></body></html>')
        self.assertRule("meta")
        self.write("group/about.html",
                   page("About").replace('content="About About"', 'content=""'))
        self.assertRule("meta")

    def test_duplicate_titles_flagged(self):
        self.write("technologies/services.html", page("Same"))
        self.write("technologies/contact.html", page("Same"))
        self.assertRule("meta")

    def test_redact_needs_aria_hidden(self):
        self.write("newsroom/media.html", page("M", '<span class="redact">x</span>'))
        self.assertRule("redact")
        self.write("newsroom/media.html",
                   page("M", '<span class="redact" aria-hidden="true">x</span>'))
        self.assertEqual(check_sites.run(self.root), [])

    def test_synced_copy_drift_flagged(self):
        (self.root / "sites/group/assets/css/base.css").write_text(CSS + "/* edited */")
        self.assertRule("sync")

    def test_reduced_motion_required(self):
        (self.root / "design" / "base.css").write_text("body{}")
        self.assertRule("reduced-motion")

    def test_absent_site_folder_reports_missing_pages(self):
        import shutil
        shutil.rmtree(self.root / "sites" / "group")
        vs = check_sites.run(self.root)
        self.assertIn("sites/group/index.html: missing-page: required page not found in sites/group", vs)
        self.assertEqual(sum("missing-page" in x for x in vs), len(PAGES["group"]))

    def test_missing_required_page_flagged(self):
        (self.root / "sites/newsroom/standards.html").unlink()
        self.assertRule("missing-page")


if __name__ == "__main__":
    unittest.main()
