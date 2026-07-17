"""Orchestrator: read the ODS, build view-models, render the map HTML.

Run from anywhere:  python build_map.py
Paths resolve relative to this file, not the current working directory.
"""
from pathlib import Path

from ods_reader import read_sheet
from normalize import corrected_region  # noqa: F401  (kept for discoverability)
from models import Site, Camp
from display import region_colors
from html_builder import build_html

_HERE = Path(__file__).resolve().parent
ODS_PATH = _HERE / ".." / "france" / "data_ecrins.ods"
TEMPLATE_PATH = _HERE / "template.html"
OUTPUT_PATH = _HERE / ".." / "france" / "carte_ecrins.html"


def _load(sheet_name, model):
    """Read a sheet and build the model for each row that has coordinates."""
    return [m for m in (model.from_row(r) for r in read_sheet(ODS_PATH, sheet_name)) if m]


def main():
    sites = _load("sites", Site)
    camps = _load("campings", Camp)
    colors = region_colors({s.region for s in sites})
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    OUTPUT_PATH.write_text(build_html(template, sites, camps, colors), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.resolve()}  ({len(sites)} sites, {len(camps)} camps, "
          f"{len(colors)} regions)")


if __name__ == "__main__":
    main()
