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
    """Build the model for each row, naming the offending row if parsing fails."""
    out = []
    for row in read_sheet(ODS_PATH, sheet_name):
        try:
            m = model.from_row(row)
        except (ValueError, TypeError) as e:
            raise ValueError(f"bad {sheet_name} row: {row}") from e
        if m:
            out.append(m)
    return out


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
