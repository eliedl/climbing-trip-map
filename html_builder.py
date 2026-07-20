"""Export concern: inject the data payload into the static HTML template."""
import json
from dataclasses import asdict

from display import marker_style


def _json(obj):
    """Compact, embed-safe JSON (</script> can't appear in the payload)."""
    return json.dumps(obj, ensure_ascii=False, default=str).replace("</", "<\\/")


def build_html(template, sites, camps, colors):
    """Return the template with data placeholders substituted."""
    replacements = {
        "__SITES__": _json([{**asdict(s), **marker_style(s)} for s in sites]),
        "__CAMPS__": _json([asdict(c) for c in camps]),
        "__COLORS__": _json(colors),
        "__NSITES__": str(len(sites)),
        "__NCAMPS__": str(len(camps)),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template
