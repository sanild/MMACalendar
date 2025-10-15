from flask import Flask, render_template, abort, request
import json
from datetime import datetime

app = Flask(__name__)

# Map friendly filter names → all known variations/abbreviations Sherdog may use
ORG_ALIASES = {
    "UFC": [
        "Ultimate Fighting Championship",
        "UFC"
    ],
    "PFL": [
        "Professional Fighters League",
        "PFL"
    ],
    "ONE": [
        "ONE Championship",
        "ONE",
        "One"
    ],
    "Cage Warriors": [
        "Cage Warriors",
        "CW"
    ],
    "DWCS": [
        "Dana White's Contender Series",
        "DWCS",
        "Contender Series"
    ],
    "Brave CF": [
        "Brave CF",
        "Brave Combat Federation",
        "BFC"
    ],
    "Oktagon MMA": [
        "Oktagon MMA",
        "OKTAGON",
        "OKMMA"
    ]
}


def load_events():
    with open("events.json", "r") as f:
        data = json.load(f)

        # Case 1: your current format → [ { "events": [ ... ] } ]
        if isinstance(data, list) and len(data) > 0 and "events" in data[0]:
            return data[0]["events"]

        # Case 2: dict with "events"
        if isinstance(data, dict) and "events" in data:
            return data["events"]

        # Case 3: already just a list of events
        if isinstance(data, list):
            return data

        return []


@app.template_filter("pretty_date")
def pretty_date_filter(date_str):
    """Format ISO date into readable form"""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        suffix = "th" if 11 <= dt.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(dt.day % 10, "th")
        return dt.strftime(f"%-d{suffix} %B %Y, %-I:%M %p")
    except Exception:
        return date_str


@app.route("/")
def index():
    org_filter = request.args.get("org")  # ?org=UFC, PFL, ONE, etc.
    events = load_events()

    if org_filter and org_filter != "ALL":
        aliases = ORG_ALIASES.get(org_filter, [org_filter])
        events = [
            e for e in events
            if any(alias.lower() in e.get("name", "").lower() or alias.lower() in e.get("organization", "").lower()
                   for alias in aliases)
        ]

    return render_template("index.html", events=events, org_filter=org_filter)


@app.route("/event/<event_id>")
def event_page(event_id):
    events = load_events()
    event = next((e for e in events if e.get("id") == event_id), None)
    if not event:
        abort(404)

    # Right now n8n only saves high-level info; if you want details,
    # you’ll need to also save fight cards for chosen orgs in events.json.
    return render_template("event.html", event=event)


if __name__ == "__main__":
    app.run(debug=True)
