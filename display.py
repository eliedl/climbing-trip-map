"""Display LUT concern: map regions to marker colours.

A region gets a colour by its position in a fixed, high-contrast palette. Adding a
region needs no code change here — it just consumes the next palette entry.
"""

# Distinct, colour-blind-tolerant qualitative palette (wraps if regions exceed it).
PALETTE = [
    "#e6194B", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#469990", "#9A6324",
    "#800000", "#000075", "#808000", "#e6beff", "#a9a9a9",
]


def region_colors(regions):
    """Return an ordered {region: hex_colour} map for the given regions."""
    ordered = sorted(regions)
    return {region: PALETTE[i % len(PALETTE)] for i, region in enumerate(ordered)}


# --- marker alpha from mean star rating ---
MIN_OPACITY, MAX_OPACITY = 0.4, 1.0
MIN_STARS, MAX_STARS = 1, 3  # rating-scale bounds; the mean maps across [MIN, MAX]


def opacity(mean):
    """Map a mean star rating (MIN_STARS..MAX_STARS) to a marker alpha in [MIN, MAX]."""
    frac = (mean - MIN_STARS) / (MAX_STARS - MIN_STARS)
    return MIN_OPACITY + frac * (MAX_OPACITY - MIN_OPACITY)


# --- marker radius from altitude ---
MIN_RADIUS, MAX_RADIUS = 5, 14  # px
MIN_ALT_M, MAX_ALT_M = 900, 3200  # altitude scale (m); encompasses the data


def radius(altitude):
    """Map an altitude (MIN_ALT_M..MAX_ALT_M metres) to a marker radius in px."""
    frac = (altitude - MIN_ALT_M) / (MAX_ALT_M - MIN_ALT_M)
    return MIN_RADIUS + frac * (MAX_RADIUS - MIN_RADIUS)


def marker_style(site):
    """Per-marker style derived from site data (grows with later passes)."""
    alpha  = opacity(site.stars.mean)
    size = radius(site.altitude)
    
    return {"fillOpacity": alpha, "opacity": alpha, "radius": size}
