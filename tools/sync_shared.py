#!/usr/bin/env python3
"""Copy the shared design files into every existing sites/<name>/assets/ folder.

Run from anywhere: python3 tools/sync_shared.py
Safe to run repeatedly. Synced copies must never be hand edited.
"""
import shutil
import sys
from pathlib import Path

# Repo root is the parent of the tools/ folder this file lives in
ROOT = Path(__file__).resolve().parent.parent
LOGOS = ["lucid-era-logo-main.png", "lucid-era-detective-mark.png"]


def sync(root: Path) -> list[Path]:
    """Copy base.css and logos into each site. Returns the sites touched."""
    sites_dir = root / "sites"
    touched = []
    if not sites_dir.is_dir():
        return touched
    for site in sorted(p for p in sites_dir.iterdir() if p.is_dir()):
        css_dir = site / "assets" / "css"
        img_dir = site / "assets" / "images"
        css_dir.mkdir(parents=True, exist_ok=True)
        img_dir.mkdir(parents=True, exist_ok=True)
        # Stylesheet
        shutil.copyfile(root / "design" / "base.css", css_dir / "base.css")
        # Logos
        for name in LOGOS:
            shutil.copyfile(root / "design" / "logos" / name, img_dir / name)
        touched.append(site)
    return touched


def main() -> int:
    touched = sync(ROOT)
    for site in touched:
        print(f"synced {site.relative_to(ROOT)}")
    if not touched:
        print("no sites/ folders found, nothing to sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
