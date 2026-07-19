"""I/O concern: read a CSV export into plain row dicts."""
import csv


def read_sheet(path):
    """Return a CSV as a list of dicts keyed by its header row."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
