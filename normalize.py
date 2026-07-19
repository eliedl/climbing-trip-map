"""Normalisation concern: canonicalise region names."""

import math
import random

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
