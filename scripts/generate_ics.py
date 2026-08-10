#!/usr/bin/env python3
"""
Generate a public ICS calendar feed from data/schedule.csv

- Includes every date/shift from the CSV exactly as written.
- After the last known date, automatically projects the repeating
  14-day work pattern for the next 12 months using the title "SA".

The observed repeating pattern (after the early transition days) is:

  3 work days  →  2 off  →  2 work days  →  3 off  →  2 work days  →  2 off  →  (repeat)

This produces a clean 14-day cycle. The script continues from the
correct phase after the final known work day.

Usage:
  python scripts/generate_ics.py

Outputs: public/calendar.ics
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

# How far to project SA events after the last known date
PROJECT_MONTHS = 12

def parse_date(s: str) -> datetime:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {s}")

def make_uid(dt: datetime, shift: str) -> str:
    # Stable UID so re-generating the same data produces the same UIDs
    base = f"{dt.strftime('%Y%m%d')}-{shift}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base)) + "@work-schedule"

def generate_sa_projection(start_after: datetime, months: int = 12):
    """
    Generate future SA work days using the 14-day repeating block pattern.

    Pattern of consecutive days (work/off lengths):
        3 work, 2 off, 2 work, 3 off, 2 work, 2 off   → 14 days total

    We begin the projection in the correct phase after the last known
    work day (which ended a 2-work block). Therefore the next block
    is a 3-work block starting 3 days later (2 offs in between).
    """
    # After a final 2-day work block the next action is 2 offs then a 3-day work block.
    # last_known + 3 days lands on the start of the next 3-day block.
    cursor = start_after + timedelta(days=3)  # first day of next 3-work block

    end_date = start_after + timedelta(days=months * 31)  # rough upper bound

    # The repeating sequence of (work_length, off_length) pairs
    # After the initial alignment we cycle through these forever.
    cycle = [
        (3, 2),  # 3 work, 2 off
        (2, 3),  # 2 work, 3 off
        (2, 2),  # 2 work, 2 off
    ]

    sa_events = []
    cycle_idx = 0

    while cursor <= end_date:
        work_len, off_len = cycle[cycle_idx % len(cycle)]

        # Emit the work days
        for i in range(work_len):
            day = cursor + timedelta(days=i)
            if day > end_date:
                break
            sa_events.append((day, "SA"))

        # Advance past the work block + the following off block
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
            shift = row["Shift"].strip()
            events.append((dt, shift))

    if not events:
        print("No events found in CSV")
        return

    events.sort(key=lambda x: x[0])
    last_known = events[-1][0]

    # Project SA days for the next N months after the last known date
    sa_events = generate_sa_projection(last_known, PROJECT_MONTHS)
    events.extend(sa_events)

    # Remove any accidental duplicates (keep the CSV version if conflict)
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
        start = dt.strftime("%Y%m%d")
        end = (dt + timedelta(days=1)).strftime("%Y%m%d")
        uid = make_uid(dt, shift)
        title = shift

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
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
    print(f"  Projection starts after: {last_known.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
