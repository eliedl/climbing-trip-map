"""Semantic types: typed view-models built from raw spreadsheet rows.

Each model owns its own row->object mapping (`from_row`), so the orchestrator
stays a plain sequence of steps and the French column names live in one place.
Each parsed column goes through `_field`, which tags a bad cell with its column
name; the loader adds the sheet and row number, so a bad value surfaces as
sheet + row + column on the CLI rather than being skipped.
"""
from dataclasses import dataclass

from normalize import corrected_region, ORIENTATION_ALIASES, ORIENTATION_DEGREES


def _field(column, parse, *values):
    """Parse a column's raw cell(s); tag failures with the column name for the loader."""
    try:
        return parse(*values)
    except (ValueError, TypeError) as e:
        raise ValueError(f"column {column!r}: {e}") from e


@dataclass(frozen=True)
class Stars:
    """Per-climber ratings and their mean.

    `int()` parses each cell with no guard: a blank or non-numeric rating raises
    and is surfaced (with its row) at the load boundary rather than defaulted.
    `mean` is a field, not a property, so `dataclasses.asdict` serialises it into
    the map payload — asdict walks fields only, a property would silently vanish.
    """
    lolo: int
    elie: int
    mean: float

    @classmethod
    def from_raw(cls, lolo, elie):
        lolo, elie = int(lolo), int(elie)
        return cls(lolo, elie, (lolo + elie) / 2)


@dataclass(frozen=True)
class Orientation:
    """A canonical compass code and its bearing; T / -9 means directionless."""
    label: str
    degree: int

    @classmethod
    def from_raw(cls, raw):
        label = ORIENTATION_ALIASES.get(raw.strip().lower())
        if label is None:
            raise ValueError(f"unknown orientation {raw!r}")
        return cls(label, ORIENTATION_DEGREES[label])


@dataclass
class Site:
    """A climbing sector with a location and topo metadata."""
    name: str
    region: str
    subregion: str
    lat: float
    lon: float
    type: str
    orientation: Orientation
    length: str
    grade: str
    approach: str
    altitude: float
    rock: str
    page: str
    stars: Stars
    comment: str

    @classmethod
    def from_row(cls, row):
        return cls(
            name=row.get("Secteur", ""),
            region=corrected_region(row.get("Région")),
            subregion=row.get("Sous-région", ""),
            lat=_field("Latitude", float, row.get("Latitude")),
            lon=_field("Longitude", float, row.get("Longitude")),
            type=row.get("Type", ""),
            orientation=_field("Orientation", Orientation.from_raw, row.get("Orientation")),
            length=row.get("Longueur (m)", ""),
            grade=row.get("Difficulté", ""),
            approach=row.get("Approche (min)", ""),
            altitude=_field("Altitude (m)", float, row.get("Altitude (m)")),
            rock=row.get("Roche", ""),
            page=row.get("Page", ""),
            stars=_field("Étoiles Lolo/Élie", Stars.from_raw,
                         row.get("Étoiles Lolo"), row.get("Étoiles Élie")),
            comment=row.get("Commentaires", ""),
        )


@dataclass
class Camp:
    """A bivouac / wild-camping spot."""
    name: str
    near: str
    lat: float
    lon: float
    infos: str

    @classmethod
    def from_row(cls, row):
        return cls(
            name=row.get("Nom", "").strip(),
            near=row.get("proche de quel endroit", ""),
            lat=float(row.get("lat.")),
            lon=float(row.get("long.")),
            infos=row.get("infos", ""),
        )
