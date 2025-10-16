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
    from datetime import timezone, timedelta

    with open("events.json", "r") as f:
        data = json.load(f)

        # Case 1: your current format → [ { "events": [ ... ] } ]
        if isinstance(data, list) and len(data) > 0 and "events" in data[0]:
            events = data[0]["events"]
        # Case 2: dict with "events"
        elif isinstance(data, dict) and "events" in data:
            events = data["events"]
        # Case 3: already just a list of events
        elif isinstance(data, list):
            events = data
        else:
            events = []

    # Filter out past events by IST cutoff
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    valid_events = []
    for e in events:
        date_str = e.get("date")
        if not date_str:
            continue
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            dt_ist = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
            cutoff = dt_ist.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            if now_ist <= cutoff:
                valid_events.append(e)
        except Exception:
            valid_events.append(e)  # fallback if parsing fails

    return valid_events

@app.template_filter("pretty_date")
def pretty_date_filter(date_str):
    """Format ISO date into EST and IST friendly format with weekday"""
    from datetime import timezone, timedelta

    try:
        # Parse the ISO datetime
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

        # Define offsets for EST and IST
        EST = timezone(timedelta(hours=-5))
        IST = timezone(timedelta(hours=5, minutes=30))

        dt_est = dt.astimezone(EST)
        dt_ist = dt.astimezone(IST)

        def pretty_format(dt):
            day = dt.day
            suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            # Add weekday (%A)
            return dt.strftime(f"%A, %-d{suffix} %B %Y, %-I:%M %p")

        return f"{pretty_format(dt_est)} EST | {pretty_format(dt_ist)} IST"
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
