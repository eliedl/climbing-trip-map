"""Normalisation concern: canonicalise region names."""

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
