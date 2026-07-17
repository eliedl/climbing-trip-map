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
