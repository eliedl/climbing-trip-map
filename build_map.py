"""Orchestrator: read the CSVs, build view-models, render the map HTML.

Run from anywhere:  python build_map.py
Paths resolve relative to this file, not the current working directory.
"""
from pathlib import Path

from csv_reader import read_sheet
from models import Site, Camp
from display import region_colors
from html_builder import build_html

_HERE = Path(__file__).resolve().parent
SITES_CSV = _HERE / ".." / "france" / "sites.csv"
CAMPS_CSV = _HERE / ".." / "france" / "camping.csv"
TEMPLATE_PATH = _HERE / "template.html"
OUTPUT_PATH = _HERE / ".." / "france" / "carte_ecrins.html"


def _load(csv_path, label, model):
    """Build the model for each row; name the row number if a cell fails to parse."""
    out = []
    for n, row in enumerate(read_sheet(csv_path), start=2):  # header is row 1
        try:
            m = model.from_row(row)
        except (ValueError, TypeError) as e:
            raise ValueError(f"bad {label} row {n}") from e
        if m:
            out.append(m)
    return out


def main():
    sites = _load(SITES_CSV, "sites", Site)
    camps = _load(CAMPS_CSV, "campings", Camp)
    colors = region_colors({s.region for s in sites})
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    OUTPUT_PATH.write_text(build_html(template, sites, camps, colors), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.resolve()}  ({len(sites)} sites, {len(camps)} camps, "
          f"{len(colors)} regions)")


if __name__ == "__main__":
    main()
