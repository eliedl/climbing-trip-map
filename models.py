"""Semantic types: typed view-models built from raw spreadsheet rows.

Each model owns its own row->object mapping (`from_row`), so the orchestrator
stays a plain sequence of steps and the French column names live in one place.
Each parsed column goes through `_field`, which tags a bad cell with its column
name; the loader adds the sheet and row number, so a bad value surfaces as
sheet + row + column on the CLI rather than being skipped.
"""
import datetime
from dataclasses import dataclass, field

from normalize import (
    corrected_region,
    format_trip_date,
    parse_vids,
    resolve_orientation,
    trip_date,
)


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
        return cls(*resolve_orientation(raw))


@dataclass(frozen=True)
class Plan:
    """Whether a site is on the itinerary, and the day it's climbed.

    `label` is a field, not a property, so `dataclasses.asdict` serialises it into
    the map payload (asdict walks fields only). An unplanned site carries the
    empty default; `on` stamps a date and its French label.
    """
    planned: bool = False
    date: datetime.date | None = None
    label: str = ""

    @classmethod
    def on(cls, d):
        return cls(planned=True, date=d, label=format_trip_date(d))


@dataclass
class Site:
    """A climbing sector with a location and topo metadata."""
    sid: int
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
    plan: Plan = field(default_factory=Plan)  # filled in after the itinerary join

    @classmethod
    def from_row(cls, row):
        return cls(
            sid=_field("sid", int, row.get("sid")),
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


@dataclass(frozen=True)
class Voie:
    """A single climbing route, joined to its site by `sid`."""
    sid: int
    vid: int
    name: str
    number: int
    length: int
    grade: str

    @classmethod
    def from_row(cls, row):
        return cls(
            sid=_field("sid", int, row.get("sid")),
            vid=_field("vid", int, row.get("vid")),
            name=row.get("Voie", "").strip(),
            number=_field("Numéro", int, row.get("Numéro")),
            length=_field("Longueur (m)", int, row.get("Longueur (m)")),
            grade=row.get("Difficulté (max)", "").strip(),
        )


@dataclass(frozen=True)
class ItineraryDay:
    """One day of the trip: which voies are climbed (empty on a rest day)."""
    date: datetime.date
    kind: str            # 'G' (grimpe) or 'R' (repos)
    vids: frozenset
    notes: str

    @classmethod
    def from_row(cls, row):
        return cls(
            date=_field("Mois/Jour", trip_date, row.get("Mois"), row.get("Jour")),
            kind=row.get("Grimpe (G,R)", "").strip(),
            vids=_field("vid", parse_vids, row.get("vid")),
            notes=row.get("Notes", "").strip(),
        )
