# Work Schedule Calendar

Public iCalendar (ICS) feed of my work schedule.

**ICS URL (after you push to GitHub):**
```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/public/calendar.ics
```

---

## How to update the schedule

1. Copy one or more HTML `<tr>` rows from the scheduling website.
2. Go to your GitHub repository → **Issues** → **New issue**.
3. Paste the HTML into the issue body (you can paste multiple months at once).
4. Title can be anything (e.g. `Update Schedule`).
5. Click **Submit new issue**.

The Action will:
- Extract all working shifts (`1`, `2`, `F12`, etc.)
- Ignore Pass Days
- **Completely replace** the schedule for the date range covered by the new data  
  (any old shifts inside that range that are no longer present get removed)
- Keep any shifts that fall outside the new date range
- Regenerate the calendar feed
- Close the issue with a success comment

This keeps the calendar current based on the most recently pasted data.

---

## Shift titles (all-day events)

| Code | Title on calendar              |
|------|--------------------------------|
| 1    | Connor 1 (7am–7pm)             |
| 2    | Connor 2 (7pm–7am)             |
| F12  | Connor F12 (12pm–12am)         |
| SA   | Connor SA (projected future)   |

---

## First-time setup

1. Upload the files from this folder to your GitHub repo.
2. Settings → Actions → General:
   - Allow all actions
   - Workflow permissions → **Read and write permissions**
3. Create a test Issue with some HTML to verify it works.
