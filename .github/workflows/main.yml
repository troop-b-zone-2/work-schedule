#!/usr/bin/env python3
"""
Generate a public ICS calendar feed from data/schedule.csv

- Includes every date/shift from the CSV exactly as written.
- After the last known date, automatically projects the repeating
  14-day work pattern for the next 12 months using the title "SA".

Shift mapping:
  1   → "Connor 1"     07:00 – 19:00 (same day)
  2   → "Connor 2"     19:00 – 07:00 (overnight)
  F12 → "Connor F12"   12:00 – 00:00 (overnight)
  SA  → "Connor SA"    all-day

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
TZID = "America/New_York"

# How far to project SA events after the last known date
PROJECT_MONTHS = 12

# Mapping from short code in CSV → (display title, start_hour, start_min, end_hour, end_min, is_all_day)
# For overnight shifts the end time is on the following day.
SHIFT_MAP = {
    "1":   ("Connor 1",   7,  0, 19, 0, False),
    "2":   ("Connor 2",  19,  0,  7, 0, False),  # overnight
    "F12": ("Connor F12",12,  0,  0, 0, False),  # overnight (ends at midnight)
    "SA":  ("Connor SA",  0,  0,  0, 0, True),   # all-day
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
    """
    Generate future SA work days using the 14-day repeating block pattern.

    Pattern: 3 work → 2 off → 2 work → 3 off → 2 work → 2 off → (repeat)
    """
    cursor = start_after + timedelta(days=3)  # first day of next 3-work block
    end_date = start_after + timedelta(days=months * 31)

    cycle = [
        (3, 2),  # 3 work, 2 off
        (2, 3),  # 2 work, 3 off
        (2, 2),  # 2 work, 2 off
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

def format_event(dt: datetime, shift_code: str) -> list:
    """Return the VEVENT lines for one shift."""
    if shift_code not in SHIFT_MAP:
        # Fallback – treat unknown codes as all-day with the raw code as title
        title = f"Connor {shift_code}"
        is_all_day = True
        start_h = start_m = end_h = end_m = 0
    else:
        title, start_h, start_m, end_h, end_m, is_all_day = SHIFT_MAP[shift_code]

    uid = make_uid(dt, shift_code)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{stamp}",
        f"SUMMARY:{title}",
        "TRANSP:TRANSPARENT",
    ]

    if is_all_day:
        start = dt.strftime("%Y%m%d")
        end = (dt + timedelta(days=1)).strftime("%Y%m%d")
        lines.append(f"DTSTART;VALUE=DATE:{start}")
        lines.append(f"DTEND;VALUE=DATE:{end}")
    else:
        # Timed event – use floating time with TZID (America/New_York)
        start_dt = dt.replace(hour=start_h, minute=start_m, second=0)
        end_dt = dt.replace(hour=end_h, minute=end_m, second=0)

        # Overnight: end is next calendar day
        if (end_h, end_m) <= (start_h, start_m):
            end_dt += timedelta(days=1)

        lines.append(f"DTSTART;TZID={TZID}:{start_dt.strftime('%Y%m%dT%H%M%S')}")
        lines.append(f"DTEND;TZID={TZID}:{end_dt.strftime('%Y%m%dT%H%M%S')}")

    lines.append("END:VEVENT")
    return lines

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

    # Project SA days
    sa_events = generate_sa_projection(last_known, PROJECT_MONTHS)
    events.extend(sa_events)

    # Deduplicate – CSV wins
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
        f"X-WR-TIMEZONE:{TZID}",
        "X-PUBLISHED-TTL:PT1H",
    ]

    for dt, shift in events:
        lines.extend(format_event(dt, shift))

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
