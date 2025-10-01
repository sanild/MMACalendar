import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

BASE_URL = "https://www.sherdog.com"
EVENTS_URL = "https://www.sherdog.com/events"

# Timezones
UTC = pytz.utc
EST = pytz.timezone("US/Eastern")
IST = pytz.timezone("Asia/Kolkata")


def format_date(date_str: str) -> str:
    """Convert ISO date string to EST and IST friendly format."""
    dt_utc = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    dt_utc = dt_utc.astimezone(UTC)

    # Convert to EST and IST
    dt_est = dt_utc.astimezone(EST)
    dt_ist = dt_utc.astimezone(IST)

    # Format with day suffix
    def pretty_format(dt):
        day = dt.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return dt.strftime(f"%-d{suffix} %B %Y, %-I:%M %p")

    return f"{pretty_format(dt_est)} EST | {pretty_format(dt_ist)} IST", dt_ist


def scrape_events_list():
    response = requests.get(EVENTS_URL, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    now_ist = datetime.now(IST)

    events = []
    rows = soup.select("tr[itemtype='http://schema.org/Event']")
    for row in rows:
        date_raw = row.select_one("meta[itemprop='startDate']")["content"]
        date_str, dt_ist = format_date(date_raw)

        # Cutoff = midnight (00:00) IST on event date
        cutoff = dt_ist.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        # Skip if current IST is past cutoff
        if now_ist > cutoff:
            continue

        raw_name = row.select_one("meta[itemprop='name']").get("content")
        org = row.select_one("td:nth-of-type(2) a").get_text(strip=True)

        # Clean duplication
        if org.lower() in raw_name.lower():
            name = raw_name
        else:
            name = f"{raw_name} ({org})"

        url_path = row.select_one("a[itemprop='url']")["href"]
        event_url = BASE_URL + url_path
        location = row.select_one("span[itemprop='location']").get_text(strip=True)
        event_id = url_path.split("-")[-1]

        events.append({
            "id": event_id,
            "name": name,
            "organization": org,
            "date": date_str,
            "location": location,
            "url": event_url
        })
    return events


def scrape_event_details(event_url):
    response = requests.get(event_url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    event_name = soup.select_one("h1 span[itemprop='name']").get_text(strip=True)
    date_raw = soup.select_one("div.info span meta[itemprop='startDate']")["content"]
    date_str, _ = format_date(date_raw)
    location = soup.select_one("div.info span span[itemprop='location']").get_text(strip=True)

    fights = []

    # --- Main event fight cards ---
    fight_cards = soup.select("div.fight_card")
    for fight in fight_cards:
        left_name = fight.select_one(".fighter.left_side span[itemprop='name']").get_text(strip=True)
        left_record = fight.select_one(".fighter.left_side .record").get_text(strip=True)
        left_img = fight.select_one(".fighter.left_side img[itemprop='image']")["src"]

        right_name = fight.select_one(".fighter.right_side span[itemprop='name']").get_text(strip=True)
        right_record = fight.select_one(".fighter.right_side .record").get_text(strip=True)
        right_img = fight.select_one(".fighter.right_side img[itemprop='image']")["src"]

        weight_class = fight.select_one(".versus .weight_class").get_text(strip=True)

        fights.append({
            "fighter_left": {
                "name": left_name,
                "record": left_record,
                "image": BASE_URL + left_img if left_img.startswith("/") else left_img
            },
            "fighter_right": {
                "name": right_name,
                "record": right_record,
                "image": BASE_URL + right_img if right_img.startswith("/") else right_img
            },
            "weight_class": weight_class
        })

    # --- Undercard fights ---
    subevents = soup.select("tr[itemprop='subEvent']")
    for row in subevents:
        left_name = row.select_one("td.text_right span[itemprop='name']").get_text(" ", strip=True)
        left_record = row.select_one("td.text_right span.record em").get_text(strip=True)
        left_img = row.select_one("td.text_right img")["src"]

        right_name = row.select_one("td.text_left span[itemprop='name']").get_text(" ", strip=True)
        right_record = row.select_one("td.text_left span.record em").get_text(strip=True)
        right_img = row.select_one("td.text_left img")["src"]

        weight_class = row.select_one("td.text_center .weight_class").get_text(strip=True)

        fights.append({
            "fighter_left": {
                "name": left_name,
                "record": left_record,
                "image": BASE_URL + left_img if left_img.startswith("/") else left_img
            },
            "fighter_right": {
                "name": right_name,
                "record": right_record,
                "image": BASE_URL + right_img if right_img.startswith("/") else right_img
            },
            "weight_class": weight_class
        })

    return {
        "name": event_name,
        "date": date_str,
        "location": location,
        "fights": fights
    }
