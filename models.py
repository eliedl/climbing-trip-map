"""Semantic types: typed view-models built from raw spreadsheet rows.

Each model owns its own row->object mapping (`from_row`), so the orchestrator
stays a plain sequence of steps and the French column names live in one place.
Coordinates are parsed with a bare `float`: a non-numeric cell (e.g. a comma
decimal or a blank) raises and surfaces on the CLI rather than being skipped.
"""
from dataclasses import dataclass

from normalize import corrected_region


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


@dataclass
class Site:
    """A climbing sector with a location and topo metadata."""
    name: str
    region: str
    subregion: str
    lat: float
    lon: float
    type: str
    face: str
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
            lat=float(row.get("Latitude")),
            lon=float(row.get("Longitude")),
            type=row.get("Type", ""),
            face=row.get("Orientation", ""),
            length=row.get("Longueur (m)", ""),
            grade=row.get("Difficulté", ""),
            approach=row.get("Approche (min)", ""),
            altitude=float(row.get("Altitude (m)")),
            rock=row.get("Roche", ""),
            page=row.get("Page", ""),
            stars=Stars.from_raw(row.get("Étoiles Lolo"), row.get("Étoiles Élie")),
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
            name=row.get("nom du spot ", "").strip(),
            near=row.get("proche de quel endroit", ""),
            lat=float(row.get("lat.")),
            lon=float(row.get("long.")),
            infos=row.get("infos", ""),
        )
