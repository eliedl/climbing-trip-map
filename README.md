# climbing-trip-map

Build tool that bakes a climbing spreadsheet into a single self-contained `.html` map
for a France trip (Écrins & Queyras). The output is one static file — Leaflet with
OpenTopoMap online tiles — that you open directly on your phone. No server, no
deployment.

## What it does

Reads a climbing `.ods` spreadsheet and produces an interactive map with:

- 73 climbing sectors, coloured by region (10 regions)
- A toggleable ⛺ bivouac layer (11 spots)
- Per-region legend toggles and a collapsible side panel
- Tap-for-details popups per sector

## Running it

```bash
cd code
python3 build_map.py
```

Paths resolve relative to the script. Pure standard library — no `pandas`; parsing uses
`zipfile` + `xml.etree.ElementTree`.

- **Input:** `../france/data_ecrins.ods` (not tracked in this repo — see below)
- **Output:** `../france/carte_ecrins.html`

## Data source

The spreadsheet lives outside this repo at `../france/data_ecrins.ods`. Relevant sheets:

- `sites` — climbing sectors (Région, Sous-région, Secteur, Face, Longueur, Difficulté,
  Approche, Altitude, Type, Roche, Longitude, Latitude, per-climber star ratings,
  Commentaires)
- `campings` — bivouac spots (nom, proche de, lat., long., infos)
- `voies` — routes

## Module layout

Concern-separated, one responsibility per module:

| File              | Responsibility                                                        |
|-------------------|-----------------------------------------------------------------------|
| `ods_reader.py`   | Parse ODS → row dicts                                                  |
| `normalize.py`    | Region typo correction + `to_float`                                  |
| `models.py`       | `Site` / `Camp` dataclasses with `from_row`                           |
| `display.py`      | Region → colour lookup table                                          |
| `template.html`   | Leaflet/CSS/JS shell with placeholders                                 |
| `html_builder.py` | Inject JSON into the template                                         |
| `build_map.py`    | Orchestrator                                                          |

`template.html` placeholders filled at build time: `__SITES__`, `__CAMPS__`,
`__COLORS__`, `__NSITES__`, `__NCAMPS__`.

## Notes

- **Offline tiles were deliberately skipped** — this is a planning tool and signal is
  assumed at use time.
- Coordinates are read directly from the `Latitude` / `Longitude` headers; the source
  spreadsheet had those two headers swapped originally, now corrected at source.

## Future features
 
 - Add a "chosen" column to the ods and change strokeColor to black for these Sites