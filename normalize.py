"""Normalisation concern: canonicalise region names."""

import math
import random
from datetime import date

# Canonical region names keyed by lower-cased raw spelling. The source sheet mixes
# casing and typos (Valouise/Vallousie, "Tramouillonb"), which we fold here.
REGION_ALIASES = {
    "vallousie": "Vallouise",
    "valouise": "Vallouise",
    "vallée de la guisane": "Vallée de la Guisane",
    "vallée de la clarée et vallée étroite": "Clarée / Vallée Étroite",
    "vallée de la tramouillon champcella, saint-crépin": "Tramouillon / Champcella",
    "vallée de tramouillonb champcella": "Tramouillon / Champcella",
    "l'argentière-la bessée": "L'Argentière-la-Bessée",
    "la roche de rame": "La Roche-de-Rame",
}


def corrected_region(raw):
    """Map a raw region string to its canonical display name."""
    key = (raw or "").strip().lower()
    if key in REGION_ALIASES:
        return REGION_ALIASES[key]
    return key[:1].upper() + key[1:] if key else "Autre"


# --- orientation aliases + bearings (folded by Orientation.from_raw) ---
# French cardinals with the odd stray case/space; "tous" is the directionless
# sentinel: no bearing, drawn as a plain disk.
TOUS = "T"              # directionless sentinel label
SENTINEL_DEGREE = -9    # its bearing: draw a plain disk, no point

ORIENTATION_ALIASES = {
    "nord": "N", "nord-est": "N-E", "est": "E", "sud-est": "S-E",
    "sud": "S", "sud-ouest": "S-O", "ouest": "O", "nord-ouest": "N-O",
    "tous": TOUS,
}

ORIENTATION_DEGREES = {
    "N": 0, "N-E": 45, "E": 90, "S-E": 135,
    "S": 180, "S-O": 225, "O": 270, "N-O": 315,
    TOUS: SENTINEL_DEGREE,
}


def resolve_orientation(raw):
    """Map a raw orientation string to its canonical (label, bearing) pair."""
    label = ORIENTATION_ALIASES.get(raw.strip().lower())
    if label is None:
        raise ValueError(f"unknown orientation {raw!r}")
    return label, ORIENTATION_DEGREES[label]


# --- position de-duplication: separate markers that share a coordinate ---
JITTER_DEGREES = 0.001  # ~100 m: nudge overlapping markers apart

# The 8 real bearings; TOUS is directionless and excluded.
_JITTER_BEARINGS = [deg for label, deg in ORIENTATION_DEGREES.items() if label != TOUS]


def _shifted(lat, lon, bearing):
    """Offset a coordinate by JITTER_DEGREES along a compass bearing (0=N, clockwise)."""
    rad = math.radians(bearing)
    return (round(lat + JITTER_DEGREES * math.cos(rad), 6),
            round(lon + JITTER_DEGREES * math.sin(rad), 6))


def dedupe_positions(items, rng=None):
    """Nudge any markers sharing a (lat, lon) so they don't stack on the map.

    The first item at a coordinate keeps it; each later collider is shifted
    ~100 m along a random distinct compass bearing to the first free slot.
    Mutates each item's .lat/.lon in place. Works on any object exposing
    those two attributes (Site, Camp).
    """
    rng = rng or random.Random(0)  # fixed seed -> stable output across rebuilds
    occupied = set()
    for item in items:
        pos = (item.lat, item.lon)
        if pos not in occupied:
            occupied.add(pos)
            continue
        for bearing in rng.sample(_JITTER_BEARINGS, k=len(_JITTER_BEARINGS)):
            candidate = _shifted(item.lat, item.lon, bearing)
            if candidate not in occupied:
                pos = candidate
                break
        item.lat, item.lon = pos
        occupied.add(pos)


# --- trip calendar: the itinerary sheet carries no year and names months as French
# abbreviations. TRIP_YEAR stamps the plan dates; the two maps fold month <-> label.
TRIP_YEAR = 2026
MONTH_NUMBERS = {"juil.": 7, "août": 8}          # sheet label (lower-cased) -> month
MONTH_ABBR = {7: "juil.", 8: "août"}             # month -> display abbreviation


def month_number(raw):
    """Map a French month abbreviation ('Juil.', 'Août') to its month number."""
    key = (raw or "").strip().lower()
    try:
        return MONTH_NUMBERS[key]
    except KeyError:
        raise ValueError(f"unknown month {raw!r}")


def trip_date(month_raw, day):
    """Assemble a plan date from the sheet's month label and day-of-month."""
    return date(TRIP_YEAR, month_number(month_raw), int(day))


def format_trip_date(d):
    """Render a plan date as a compact French label, e.g. '24 juil.'."""
    return f"{d.day} {MONTH_ABBR[d.month]}"


def parse_vids(raw):
    """Parse an itinerary vid cell into a set of voie ids.

    Cells are a single id ('39'), an inclusive range ('23 - 38', '71-74', '9 -10'),
    or blank (a rest day). Whitespace around the dash varies in the source.
    """
    text = (raw or "").strip()
    if not text:
        return frozenset()
    parts = [p.strip() for p in text.split("-")]
    if len(parts) > 2:
        raise ValueError(f"malformed vid range {raw!r}")
    nums = [int(p) for p in parts]
    if len(nums) == 1:
        return frozenset(nums)
    lo, hi = nums
    return frozenset(range(lo, hi + 1))
