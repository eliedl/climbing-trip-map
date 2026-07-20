"""Itinerary concern: stamp each site with the day its voies are climbed.

Voies join to sites by `sid`; the itinerary schedules voies by `vid`. We fold
those two hops into a sid -> date map, then assign it back onto each Site.
"""
from models import Plan


def plan_sites(sites, voies, days):
    """Set each site's `.plan` from the itinerary, in place."""
    sid_of = {v.vid: v.sid for v in voies}
    date_of = {sid_of[vid]: day.date for day in days for vid in day.vids}
    for site in sites:
        if site.sid in date_of:
            site.plan = Plan.on(date_of[site.sid])