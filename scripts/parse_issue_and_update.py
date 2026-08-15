#!/usr/bin/env python3
"""
Parse HTML schedule rows from a GitHub Issue body and update data/schedule.csv.

Looks for title="... Date ... Shift: X" patterns.
Ignores "Pass Day".
Merges new dates into the existing CSV (overwrites if the date already exists).
"""

from datetime import datetime
from pathlib import Path
import csv
import os
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "schedule.csv"

# Matches the title attribute content that contains a date and "Shift: ..."
# Handles newlines inside the attribute value.
TITLE_PATTERN = re.compile(
    r'title\s*=\s*"([^"]*?)"',
    re.IGNORECASE | re.DOTALL
)

DATE_SHIFT_PATTERN = re.compile(
    r'(\d{1,2}/\d{1,2}/\d{4}).*?Shift:\s*([^\n\r"]+)',
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
    if s in ("PASS DAY", "PASS", "-", "OFF", ""):
        return None
    # Keep common codes as-is
    if s in ("1", "2", "F12", "SA"):
        return s
    # Allow other numeric or short codes
    if re.match(r'^[0-9A-Z]{1,6}$', s):
        return s
    return None

def extract_shifts(html: str) -> dict[str, str]:
    """Return {YYYY-MM-DD: shift_code} from the pasted HTML."""
    results = {}
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
    # Sort by date
    sorted_items = sorted(data.items(), key=lambda x: x[0])
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Shift"])
        for date, shift in sorted_items:
            writer.writerow([date, shift])

def main():
    # Issue body can come from env (GitHub Action) or stdin
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

    print(f"Found {len(new_shifts)} working shifts:")
    for d, s in sorted(new_shifts.items()):
        print(f"  {d} → {s}")

    existing = load_existing_csv()
    # New data overwrites existing dates
    existing.update(new_shifts)
    write_csv(existing)

    print(f"\nUpdated {CSV_PATH} — total entries: {len(existing)}")

if __name__ == "__main__":
    main()
