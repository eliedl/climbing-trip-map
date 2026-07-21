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


def attach_voies(sites, voies):
    """Group each site's routes onto it by `sid`, in place."""
    by_sid = {}
    for v in voies:
        by_sid.setdefault(v.sid, []).append(v)
    for site in sites:
        site.voies = sorted(by_sid.get(site.sid, []), key=lambda v: v.number)