#!/usr/bin/env python3
"""
Parse HTML schedule rows from a GitHub Issue body and update data/schedule.csv.

- You can paste multiple <tr> rows at once (multiple months is fine).
- Pass Days are ignored.
- The newest paste completely replaces the schedule for the date range it covers.
  Any previous entries that fall inside that range but are missing from the new
  data are removed. Entries outside the range are kept.
"""

from datetime import datetime
from pathlib import Path
import csv
import os
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "schedule.csv"

TITLE_PATTERN = re.compile(
    r'title\s*=\s*"([^"]*?)"',
    re.IGNORECASE | re.DOTALL
)

DATE_SHIFT_PATTERN = re.compile(
    r'(\d{1,2}/\d{1,2}/\d{4}).*?Shift:\s*([^\n\r"]+)',
    re.IGNORECASE | re.DOTALL
)

# Catch SA cells even when title says "Pass Day" + "On Special Assignment"
SA_CELL_PATTERN = re.compile(
    r'title="[^"]*?(\d{1,2}/\d{1,2}/\d{4})[^"]*?(?:On Special Assignment|Special Assignment)[^"]*?"[^>]*>\s*SA\s*</a>',
    re.IGNORECASE | re.DOTALL
)

def parse_date(s: str) -> datetime:
    s = s.strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date: {s}")

def normalize_shift(raw: str) -> str | None:
    """Return normalized shift code or None if it should be ignored."""
    s = raw.strip().upper()

    # SA indicators (handles "Pass Day\nOn Special Assignment" and "1-6\nOn Special Assignment")
    if "SPECIAL ASSIGNMENT" in s or s == "SA":
        return "SA"

    if s in ("PASS DAY", "PASS", "-", "OFF", ""):
        return None

    if s in ("1", "2", "F12", "SA"):
        return s

    # Allow simple codes like 1-6, F12, etc.
    if re.match(r'^[0-9A-Z\-]{1,8}$', s):
        return s

    return None

def extract_shifts(html: str) -> dict[str, str]:
    """Return {YYYY-MM-DD: shift_code} from the pasted HTML."""
    results = {}

    # Primary: parse every title attribute
    for title_match in TITLE_PATTERN.finditer(html):
        title_content = title_match.group(1)
        for m in DATE_SHIFT_PATTERN.finditer(title_content):
            date_str, shift_raw = m.group(1), m.group(2)
            try:
                dt = parse_date(date_str)
                shift = normalize_shift(shift_raw)
                if shift:
                    iso = dt.strftime("%Y-%m-%d")
                    results[iso] = shift
            except ValueError:
                continue

    # Secondary: catch SA cells that the title parser missed
    for m in SA_CELL_PATTERN.finditer(html):
        date_str = m.group(1)
        try:
            dt = parse_date(date_str)
            iso = dt.strftime("%Y-%m-%d")
            results[iso] = "SA"          # force SA
        except ValueError:
            continue

    return results

def load_existing_csv() -> dict[str, str]:
    existing = {}
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Date") and row.get("Shift"):
                    existing[row["Date"].strip()] = row["Shift"].strip().upper()
    return existing

def write_csv(data: dict[str, str]):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    sorted_items = sorted(data.items(), key=lambda x: x[0])
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Shift"])
        for date, shift in sorted_items:
            writer.writerow([date, shift])

def main():
    body = os.environ.get("ISSUE_BODY", "")
    if not body and not sys.stdin.isatty():
        body = sys.stdin.read()

    if not body.strip():
        print("No issue body provided.")
        sys.exit(1)

    new_shifts = extract_shifts(body)
    if not new_shifts:
        print("No valid shifts found in the issue body (Pass Days are ignored).")
        sys.exit(2)

    print(f"Found {len(new_shifts)} working shifts in the new data:")
    for d, s in sorted(new_shifts.items()):
        print(f"  {d} → {s}")

    # Determine the date range covered by this paste
    dates = sorted(new_shifts.keys())
    range_start = dates[0]
    range_end = dates[-1]
    print(f"\nDate range of this update: {range_start} → {range_end}")

    existing = load_existing_csv()

    # Keep only entries that are OUTSIDE the new range
    kept = {
        d: s for d, s in existing.items()
        if d < range_start or d > range_end
    }

    removed_count = len(existing) - len(kept)
    if removed_count > 0:
        print(f"Removed {removed_count} previous entries that fell inside this range.")

    # Add the new shifts (this fully replaces the range)
    kept.update(new_shifts)
    write_csv(kept)

    print(f"\nUpdated {CSV_PATH}")
    print(f"  Total entries now: {len(kept)}")
    print(f"  Kept outside range: {len(kept) - len(new_shifts)}")
    print(f"  New/updated in range: {len(new_shifts)}")

if __name__ == "__main__":
    main()
