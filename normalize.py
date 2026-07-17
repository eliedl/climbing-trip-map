"""Normalisation concern: canonicalise region names and parse numbers."""

# Canonical region names keyed by lower-cased raw spelling. The source sheet mixes
# casing and typos (Valouise/Vallousie, "Tramouillonb"), which we fold here.
REGION_ALIASES = {
    "vallousie": "Valouise",
    "valouise": "Valouise",
    "vallée de la guisane": "Vallée de la Guisane",
    "vallée de la clarée et vallée étroite": "Clarée / Vallée Étroite",
    "vallée de la tramouillon champcella, saint-crépin": "Tramouillon / Champcella",
    "vallée de tramouillonb champcella": "Tramouillon / Champcella",
    "l'argentière-la bessée": "L'Argentière-la-Bessée",
    "la roche de rame": "La Roche-de-Rame",
}


def canonical_region(raw):
    """Map a raw region string to its canonical display name."""
    key = (raw or "").strip().lower()
    if key in REGION_ALIASES:
        return REGION_ALIASES[key]
    return key[:1].upper() + key[1:] if key else "Autre"


def to_float(value):
    """Parse a spreadsheet number (comma or dot decimal) or return None."""
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None
