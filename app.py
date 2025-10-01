from flask import Flask, render_template, abort, request
from scrapers import scrape_events_list, scrape_event_details

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


@app.route("/")
def index():
    org_filter = request.args.get("org")  # ?org=UFC, PFL, ONE, etc.
    events = scrape_events_list()

    if org_filter:
        aliases = ORG_ALIASES.get(org_filter, [org_filter])
        events = [
            e for e in events
            if any(alias.lower() in e["organization"].lower() for alias in aliases)
        ]

    return render_template("index.html", events=events, org_filter=org_filter)


@app.route("/event/<event_id>")
def event_page(event_id):
    events = scrape_events_list()
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        abort(404)
    details = scrape_event_details(event["url"])
    return render_template("event.html", event=details)


if __name__ == "__main__":
    app.run(debug=True)
