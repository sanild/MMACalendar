# 🥊 MMA Calendar

**MMA Calendar** is a minimal web app that displays all upcoming MMA events in one place.  
It scrapes live event data from **[Sherdog](https://www.sherdog.com/events)** and presents it in a clean, responsive interface.  
The app allows users to browse upcoming fight cards, filter by organization (UFC, PFL, ONE, Cage Warriors, DWCS, Brave CF, Oktagon MMA), and view individual event details.

---

## 📸 Demo

![alt text](https://github.com/sanild/MMACalendar/blob/main/static/Screenshot.png?raw=true)


---

## ✨ Features

- 📅 **Upcoming Events** — displays all future MMA events with date/time.  
- 🌍 **Multiple Timezones** — event times are automatically shown in **EST** and **IST**.  
- 🥋 **Fight Cards** — see fighters, records, weight class, and images.  
- 🏷️ **Organization Filters** — quickly filter by UFC, PFL, ONE, Cage Warriors, DWCS, Brave CF, or Oktagon MMA.  
- 📱 **Responsive Design** — mobile-friendly with a hamburger menu overlay.  
- 🐈 **Fun Overlay** — includes a note from the author and an ASCII cat 🐾.  
- 🎨 **Custom Styling** — built with Bootstrap 5 and custom CSS for a minimal, modern look.  
- 🥐 **Favicon & Branding** — custom favicon (pain au chocolat 🥐) and logo in navbar.

---

## 🛠️ Technologies Used

- **Python 3.12+**  
- **Flask** — backend framework for serving pages  
- **BeautifulSoup4** — web scraping Sherdog event & fight data  
- **Requests** — HTTP requests to fetch event pages  
- **pytz** — timezone conversions (UTC → EST/IST)  
- **Bootstrap 5** — responsive UI framework  
- **Bootstrap Icons** — for the hamburger & GitHub icons  
- **Google Fonts** — Source Code Pro & Termina Test  

---

## ⚙️ Installation

Clone this repository, create a virtual environment, install dependencies, and run the app:

git clone https://github.com/sanild/mmacalendar.git <br />
cd mmacalendar

# Create and activate a virtual environment
python -m venv .venv<br />
source .venv/bin/activate   # macOS/Linux<br />
.venv\Scripts\activate      # Windows<br />

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
