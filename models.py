"""Semantic types: typed view-models built from raw spreadsheet rows.

Each model owns its own row->object mapping (`from_row`), so the orchestrator
stays a plain sequence of steps and the French column names live in one place.
`from_row` returns None when the row lacks usable coordinates.
"""
from dataclasses import dataclass

from normalize import canonical_region, to_float


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
    altitude: str
    rock: str
    page: str
    stars_lolo: str
    stars_elie: str
    comment: str

    @classmethod
    def from_row(cls, row):
        lat, lon = to_float(row.get("Latitude")), to_float(row.get("Longitude"))
        if lat is None or lon is None:
            return None
        return cls(
            name=row.get("Secteur", ""),
            region=canonical_region(row.get("Région")),
            subregion=row.get("Sous-région", ""),
            lat=lat,
            lon=lon,
            type=row.get("Type", ""),
            face=row.get("Face", ""),
            length=row.get("Longueur (m)", ""),
            grade=row.get("Difficulté", ""),
            approach=row.get("Approche (min)", ""),
            altitude=row.get("Altitude (m)", ""),
            rock=row.get("Roche", ""),
            page=row.get("Page", ""),
            stars_lolo=row.get("Étoiles Lolo", ""),
            stars_elie=row.get("Étoiles Élie", ""),
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
        lat, lon = to_float(row.get("lat.")), to_float(row.get("long."))
        if lat is None or lon is None:
            return None
        return cls(
            name=row.get("nom du spot ", "").strip(),
            near=row.get("proche de quel endroit", ""),
            lat=lat,
            lon=lon,
            infos=row.get("infos", ""),
        )
