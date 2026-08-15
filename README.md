# Work Schedule Calendar

Public iCalendar (ICS) feed of my work schedule.

**ICS URL (after you push to GitHub):**
```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/public/calendar.ics
```

---

## How to update the schedule (easiest method)

1. Copy the HTML row(s) from the scheduling website (the ones that look like `<tr groupid=...>` with the `title="GOTHAM, CONNOR B ... Shift: X"` attributes).
2. Go to your GitHub repository → **Issues** → **New issue**.
3. Paste the HTML into the issue body.
4. Title can be anything (e.g. `Update Schedule`).
5. Click **Submit new issue**.

The Action will automatically:
- Extract all working shifts (`1`, `2`, `F12`, etc.)
- Ignore Pass Days
- Update `data/schedule.csv`
- Regenerate `public/calendar.ics`
- Commit the changes
- Close the issue and leave a success comment

That’s it. Subscribers will see the new shifts on their next calendar refresh.

---

## Shift titles (all-day events)

| Code | Title on calendar              |
|------|--------------------------------|
| 1    | Connor 1 (7am–7pm)             |
| 2    | Connor 2 (7pm–7am)             |
| F12  | Connor F12 (12pm–12am)         |
| SA   | Connor SA (projected future)   |

---

## Manual methods (if needed)

### Edit the CSV directly
Edit `data/schedule.csv` and push. The original “Generate ICS” workflow will rebuild the calendar.

### Run locally
```bash
python scripts/parse_issue_and_update.py   # if you have HTML
python scripts/generate_ics.py
```

---

## Files

- `data/schedule.csv` – source of truth
- `public/calendar.ics` – the public feed
- `scripts/generate_ics.py` – builds the ICS (includes 12-month SA projection)
- `scripts/parse_issue_and_update.py` – parses the HTML from Issues
- `.github/workflows/update-from-issue.yml` – the automatic Issue → calendar workflow
- `.github/workflows/generate-ics.yml` – rebuilds ICS when the CSV changes

---

## First-time setup reminders

1. Make sure **Actions** are enabled (Settings → Actions → General → Allow all actions).
2. Set **Workflow permissions** to **Read and write permissions**.
3. The first time you open an Issue with schedule HTML, the workflow should appear in the Actions tab.
