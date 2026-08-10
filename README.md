# Work Schedule Calendar

Public iCalendar (ICS) feed of my work schedule for easy subscription in Apple Calendar, Google Calendar, Outlook, etc.

## Subscribe

**Direct ICS URL (recommended for Apple Calendar):**

```
https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/public/calendar.ics
```

Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME` with your actual values after you push this repo.

### Apple Calendar (iPhone / iPad)
1. Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar
2. Paste the URL above
3. Tap Next → Save
4. (Optional) Set a custom name/color and choose Refresh frequency

Or in the Calendar app (newer iOS): Calendars → Add Calendar → Add Subscription Calendar.

### Apple Calendar (Mac)
1. Calendar app → File → New Calendar Subscription…
2. Paste the URL → Subscribe
3. Set name, color, Location = **iCloud** (so it appears on all your devices)
4. Choose Auto-refresh (Hourly is usually good)

### Google Calendar / others
Add by URL using the same link.

---

## How the schedule is built

1. **Known shifts** come from `data/schedule.csv` (exactly as you write them).
2. **Future projection** — after the last date in the CSV the script automatically continues the observed 14-day repeating pattern for the next 12 months and labels those days `SA`.

The repeating pattern used for projection is:

```
3 work days → 2 off → 2 work days → 3 off → 2 work days → 2 off → (repeat)
```

When you later learn the real shift for a projected day, just add (or edit) the row in the CSV with the correct title. The generator prefers the CSV value over the automatic `SA`.

---

## Shift titles & times

| Code in CSV | Title shown     | Time                          |
|-------------|-----------------|-------------------------------|
| 1           | Connor 1        | 7:00 AM – 7:00 PM             |
| 2           | Connor 2        | 7:00 PM – 7:00 AM (overnight) |
| F12         | Connor F12      | 12:00 PM – 12:00 AM (overnight) |
| SA          | Connor SA       | All-day                       |

---

## How to update the schedule

1. Edit `data/schedule.csv`  
   Format is simple:
   ```csv
   Date,Shift
   2026-08-11,1
   2026-10-25,2
   2026-11-03,1
   ```
   - Date: `YYYY-MM-DD` (preferred) or `MM/DD/YYYY`
   - Shift: `1`, `2`, `F12`, or `SA`

2. Run the generator (locally or via GitHub Actions):
   ```bash
   python scripts/generate_ics.py
   ```

3. Commit and push both the CSV and the updated `public/calendar.ics`.

Subscribers will pick up the changes on their next refresh.

---

## Notes

- The feed is public. Anyone with the URL can view it.
- The automatic projection can be adjusted in `scripts/generate_ics.py`.

Generated with a simple Python script so you stay in full control.
