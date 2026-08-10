#!/usr/bin/env python3
"""
Generate a public ICS calendar feed from data/schedule.csv

- All events are all-day (one calendar day only).
- Hours are shown in the title so the information is still visible.
- After the last known date, projects the 14-day pattern as "SA" for 12 months.

Titles:
  1   → Connor 1 (7am–7pm)
  2   → Connor 2 (7pm–7am)
  F12 → Connor F12 (12pm–12am)
  SA  → Connor SA

Usage:
  python scripts/generate_ics.py
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import csv
import uuid

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "schedule.csv"
OUT_PATH = ROOT / "public" / "calendar.ics"

CAL_NAME = "Work Schedule"
CAL_DESC = "NY State Trooper work schedule (public feed)"
PROD_ID = "-//Connor Gotham//Work Schedule//EN"

PROJECT_MONTHS = 12

# Short code → display title (all events are all-day)
SHIFT_TITLES = {
    "1":   "Connor 1 (7am–7pm)",
    "2":   "Connor 2 (7pm–7am)",
    "F12": "Connor F12 (12pm–12am)",
    "SA":  "Connor SA",
}

def parse_date(s: str) -> datetime:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {s}")

def make_uid(dt: datetime, shift: str) -> str:
    base = f"{dt.strftime('%Y%m%d')}-{shift}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base)) + "@work-schedule"

def generate_sa_projection(start_after: datetime, months: int = 12):
    cursor = start_after + timedelta(days=3)
    end_date = start_after + timedelta(days=months * 31)

    cycle = [
        (3, 2),
        (2, 3),
        (2, 2),
    ]

    sa_events = []
    cycle_idx = 0

    while cursor <= end_date:
        work_len, off_len = cycle[cycle_idx % len(cycle)]
        for i in range(work_len):
            day = cursor + timedelta(days=i)
            if day > end_date:
                break
            sa_events.append((day, "SA"))
        cursor = cursor + timedelta(days=work_len + off_len)
        cycle_idx += 1

    return sa_events

def main():
    events = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("Date") or not row.get("Shift"):
                continue
            dt = parse_date(row["Date"])
            shift = row["Shift"].strip().upper()
            if shift == "F12":
                shift = "F12"
            events.append((dt, shift))

    if not events:
        print("No events found in CSV")
        return

    events.sort(key=lambda x: x[0])
    last_known = events[-1][0]

    sa_events = generate_sa_projection(last_known, PROJECT_MONTHS)
    events.extend(sa_events)

    # CSV wins on conflicts
    seen = {}
    for dt, shift in events:
        if dt not in seen:
            seen[dt] = shift
    events = sorted(seen.items(), key=lambda x: x[0])

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{PROD_ID}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{CAL_NAME}",
        f"X-WR-CALDESC:{CAL_DESC}",
        "X-WR-TIMEZONE:America/New_York",
        "X-PUBLISHED-TTL:PT1H",
    ]

    for dt, shift in events:
        title = SHIFT_TITLES.get(shift, f"Connor {shift}")
        start = dt.strftime("%Y%m%d")
        end = (dt + timedelta(days=1)).strftime("%Y%m%d")
        uid = make_uid(dt, shift)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{start}",
            f"DTEND;VALUE=DATE:{end}",
            f"SUMMARY:{title}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")

    known_count = sum(1 for _, s in events if s != "SA")
    sa_count = sum(1 for _, s in events if s == "SA")
    print(f"Wrote {len(events)} total events → {OUT_PATH}")
    print(f"  Known shifts from CSV : {known_count}")
    print(f"  Projected SA days     : {sa_count}")

if __name__ == "__main__":
    main()
