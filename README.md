# Work Schedule Calendar

Public iCalendar (ICS) feed of my work schedule for easy subscription in Apple Calendar, Google Calendar, Outlook, etc.

## Subscribe

**Direct ICS URL:**

```
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/public/calendar.ics
```

### Apple Calendar (iPhone / iPad)
Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar → paste the URL

### Apple Calendar (Mac)
Calendar → File → New Calendar Subscription… → paste the URL → set Location to **iCloud**

---

## Shift titles (all events are all-day)

| Code in CSV | Title shown on calendar          |
|-------------|----------------------------------|
| 1           | Connor 1 (7am–7pm)               |
| 2           | Connor 2 (7pm–7am)               |
| F12         | Connor F12 (12pm–12am)           |
| SA          | Connor SA                        |

Each shift appears on **one single day** only. The hours are included in the title so the information is still visible without the event spanning two days.

---

## How the schedule is built

1. Known shifts come from `data/schedule.csv`
2. After the last date in the CSV the script automatically continues the 14-day pattern for the next 12 months as `SA`

Pattern used for projection:
```
3 work → 2 off → 2 work → 3 off → 2 work → 2 off → (repeat)
```

---

## How to update

1. Edit `data/schedule.csv`
2. Push the change
3. The GitHub Action automatically regenerates `public/calendar.ics`

You can also run it manually:
```bash
python scripts/generate_ics.py
```
