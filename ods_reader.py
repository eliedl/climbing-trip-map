"""I/O concern: read an OpenDocument spreadsheet into plain row dicts."""
import zipfile
import xml.etree.ElementTree as ET

_TABLE = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
_PARA = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"
_MAX_REPEAT = 50  # trailing empty cells repeat thousands of times; cap them


def _cell_text(cell):
    """Concatenate the text of every paragraph inside a cell."""
    return "".join(p.text or "" for p in cell.iter(_PARA))


def _row_cells(row):
    """Expand a row into a flat list of cell strings, honouring column repeats."""
    out = []
    for cell in row.findall(_TABLE + "table-cell"):
        repeat = int(cell.get(_TABLE + "number-columns-repeated", "1"))
        out.extend([_cell_text(cell)] * min(repeat, _MAX_REPEAT))
    return out


def read_sheet(path, sheet_name):
    """Return the named sheet as a list of dicts keyed by its header row."""
    root = ET.fromstring(zipfile.ZipFile(path).read("content.xml"))
    for table in root.iter(_TABLE + "table"):
        if table.get(_TABLE + "name") != sheet_name:
            continue
        rows = [_row_cells(r) for r in table.iter(_TABLE + "table-row")]
        header = rows[0]
        ncol = len([h for h in header if h.strip()])
        records = []
        for row in rows[1:]:
            if not any(c.strip() for c in row):
                continue
            records.append({header[i]: (row[i] if i < len(row) else "") for i in range(ncol)})
        return records
    raise KeyError(f"sheet {sheet_name!r} not found in {path}")
