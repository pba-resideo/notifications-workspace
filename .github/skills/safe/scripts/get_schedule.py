#!/usr/bin/env python3
"""
get_schedule.py — Fetch and display the ART schedule for a year from Confluence.

The schedule page is found by title per year ("PI <year> Schedule" in space CE),
so the script works for any year without editing page IDs. The current PI is
derived from the calendar (the entry containing today), never hardcoded.

HTTP and credentials come from the atlassian skill (stdlib only, no pip deps).
"""
import argparse
import json
import os
import sys
from datetime import datetime, date, timezone
from html.parser import HTMLParser
from pathlib import Path

# The atlassian skill is a sibling of this skill, wherever they are installed.
SKILL_DIR = Path(__file__).resolve().parent.parent
ATLASSIAN_SCRIPTS = SKILL_DIR.parent / "atlassian" / "scripts"
sys.path.insert(0, str(ATLASSIAN_SCRIPTS))

import api
from dotenv import load_dotenv

load_dotenv(ATLASSIAN_SCRIPTS.parent / ".env")
BASE_URL = os.getenv("JIRA_BASE_URL")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")
AUTH = (EMAIL, TOKEN)

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_MAX_AGE_HOURS = 24


# ---------------------------------------------------------------------------
# HTML table parser (stdlib only)
# ---------------------------------------------------------------------------
class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell_text = []
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._in_cell = True
            self._cell_text = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._in_cell:
            self._row.append(" ".join(self._cell_text).strip())
            self._in_cell = False
            self._cell_text = []
        elif tag == "tr" and self._row is not None:
            if any(c.strip() for c in self._row):
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._in_cell:
            text = data.strip()
            if text:
                self._cell_text.append(text)

    def handle_entityref(self, name):
        _entities = {"rsquo": "'", "lsquo": "'", "rdquo": '"', "ldquo": '"',
                     "copy": "©", "nbsp": " ", "amp": "&", "lt": "<", "gt": ">",
                     "mdash": "—", "ndash": "–", "rarr": "→"}
        if self._in_cell:
            self._cell_text.append(_entities.get(name, ""))

    def handle_charref(self, name):
        if self._in_cell:
            try:
                char = chr(int(name[1:], 16) if name.startswith("x") else int(name))
                self._cell_text.append(char)
            except (ValueError, OverflowError):
                pass


def _parse_html_table(html: str) -> list[dict]:
    """Return schedule entries parsed from Confluence storage HTML."""
    parser = _TableParser()
    parser.feed(html)
    entries = []
    for row in parser.rows:
        if not row or "PIs and Sprints" in row[0]:
            continue
        label = row[0].strip()
        if not label:
            continue
        entries.append({
            "label": label,
            "start": row[1].strip() if len(row) > 1 else "",
            "finish": row[2].strip() if len(row) > 2 else "",
            "holidays_us": row[3].strip() if len(row) > 3 else "",
            "holidays_india": row[4].strip() if len(row) > 4 else "",
            "holidays_ch": row[5].strip() if len(row) > 5 else "",
            "holidays_uk": row[6].strip() if len(row) > 6 else "",
            "is_planning": "PI Planning" in label,
        })
    return entries


# ---------------------------------------------------------------------------
# Fetch / cache
# ---------------------------------------------------------------------------
def _find_page(year: int) -> dict:
    """Locate the 'PI <year> Schedule' page in space CE via CQL search."""
    cql = f'space = CE AND type = page AND title ~ "PI {year} Schedule"'
    resp = api.get(
        f"{BASE_URL}/wiki/rest/api/content/search",
        auth=AUTH,
        params={"cql": cql, "limit": 10, "expand": "space"},
        headers={"Accept": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    exact = [r for r in results if r["title"].strip().startswith(f"PI {year} Schedule")]
    if not exact:
        raise RuntimeError(
            f"No page titled 'PI {year} Schedule' found in space CE. "
            f"Search matched: {[r['title'] for r in results]}"
        )
    page = exact[0]
    return {
        "id": page["id"],
        "title": page["title"],
        "url": page.get("_links", {}).get("webui",
              f"{BASE_URL}/wiki/spaces/CE/pages/{page['id']}"),
    }


def _fetch_live(year: int) -> dict:
    page = _find_page(year)
    print(f"Found page: {page['title']} ({page['id']})\n"
          f"Fetching schedule from Confluence...", file=sys.stderr)
    resp = api.get(
        f"{BASE_URL}/wiki/rest/api/content/{page['id']}",
        auth=AUTH,
        headers={"Accept": "application/json"},
        params={"expand": "body.storage"},
        timeout=30,
    )
    resp.raise_for_status()
    html = resp.json()["body"]["storage"]["value"]
    cache = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "year": year,
        "page_id": page["id"],
        "source_url": page["url"],
        "entries": _parse_html_table(html),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / f"schedule_{year}.json").write_text(json.dumps(cache, indent=2))
    return cache


def _load_cache(year: int) -> dict | None:
    cache_file = DATA_DIR / f"schedule_{year}.json"
    if not cache_file.exists():
        return None
    try:
        cache = json.loads(cache_file.read_text())
        fetched = datetime.fromisoformat(cache["fetched_at"])
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - fetched).total_seconds() / 3600
        return cache if age_h < CACHE_MAX_AGE_HOURS else None
    except Exception:
        return None


def _get_schedule(year: int, refresh: bool = False) -> dict:
    cache = None if refresh else _load_cache(year)
    if cache is None:
        cache = _fetch_live(year)
    return cache


# ---------------------------------------------------------------------------
# Date / PI helpers
# ---------------------------------------------------------------------------
def _parse_date(s: str) -> date | None:
    """Parse 'Mon-Feb 02, 26' → date(2026, 2, 2)."""
    if not s:
        return None
    if "-" in s and s[:3].isalpha():
        s = s.split("-", 1)[1]
    for fmt in ("%b %d, %y", "%b %d, %Y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _pi_prefix(label: str) -> str:
    """Extract PI identifier: '26-B.3' → '26-B', 'PI Planning - 26-B' → '26-B'."""
    label = label.replace("PI Planning - ", "").replace("PI Planning – ", "").strip()
    if "." in label:
        return label.rsplit(".", 1)[0]
    return label


def _current_pi_id(entries: list[dict]) -> str | None:
    """PI id of the entry containing today, else the most recent past PI."""
    today = date.today()
    past_pi = None
    for e in entries:
        s, f = _parse_date(e["start"]), _parse_date(e["finish"])
        if not (s and f):
            continue
        if s <= today <= f:
            return _pi_prefix(e["label"])
        if f < today:
            past_pi = _pi_prefix(e["label"])
    return past_pi


def _find_active_entry(entries: list[dict]) -> dict | None:
    today = date.today()
    for e in entries:
        s, f = _parse_date(e["start"]), _parse_date(e["finish"])
        if s and f and s <= today <= f:
            return e
    return None


def _entries_for_pi(entries: list[dict], pi_id: str) -> list[dict]:
    pi_id = pi_id.upper()
    return [e for e in entries if pi_id in e["label"].upper()]


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------
def _format_table(entries: list[dict], holidays: str | None = None) -> str:
    today = date.today()
    lines = []
    col_map = {"us": "holidays_us", "india": "holidays_india",
               "ch": "holidays_ch", "uk": "holidays_uk"}
    hol_key = col_map.get((holidays or "").lower())
    hdr = f"{'Sprint / PI':<34} {'Start':<20} {'Finish':<20}"
    if hol_key:
        hdr += f" Holidays ({holidays.upper()})"
    lines.append(hdr)
    lines.append("─" * (74 + (30 if hol_key else 0)))

    for e in entries:
        s, f = _parse_date(e["start"]), _parse_date(e["finish"])
        active = "▶ " if (s and f and s <= today <= f) else "  "
        bold = "★ " if e["is_planning"] else "  "
        line = f"{active}{bold}{e['label']:<30} {e['start']:<20} {e['finish']:<20}"
        if hol_key and e.get(hol_key):
            line += f" {e[hol_key]}"
        lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Fetch and display the ART calendar for a year from Confluence.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full schedule for the current year
  python3 get_schedule.py

  # Show only what is active today
  python3 get_schedule.py --current

  # Just the current PI id (e.g. 26-B), for scripting
  python3 get_schedule.py --current-pi

  # A specific PI (the year is read from the id)
  python3 get_schedule.py --pi 26-C --holidays india

  # A different year, force refresh, JSON output
  python3 get_schedule.py --year 2027 --refresh --format json
""",
    )
    ap.add_argument("--pi", metavar="ID",
                    help="Filter to a specific PI, e.g. 26-A. The year is read from the id.")
    ap.add_argument("--year", type=int, metavar="YEAR",
                    help="Schedule year to fetch (default: current calendar year)")
    ap.add_argument("--current", action="store_true",
                    help="Show the currently active sprint/planning event and its full PI context")
    ap.add_argument("--current-pi", action="store_true",
                    help="Print only the current PI id (e.g. 26-B) and exit")
    ap.add_argument("--refresh", action="store_true",
                    help="Force re-fetch from Confluence (ignore cache)")
    ap.add_argument("--holidays", metavar="REGION",
                    help="Include holidays for region: us | india | ch | uk")
    ap.add_argument("--format", choices=["table", "json"], default="table",
                    help="Output format (default: table)")
    args = ap.parse_args()

    if args.pi:
        pi_id = args.pi.upper()
        first = pi_id.split(".")[0]  # "26-B" or "26-B.3" → "26-B"
        try:
            year = 2000 + int(first.split("-")[0])
        except ValueError:
            print(f"Cannot read a year from PI id '{args.pi}'. Expected format like 26-B.",
                  file=sys.stderr)
            sys.exit(1)
    else:
        year = args.year or date.today().year

    cache = _get_schedule(year, args.refresh)
    entries = cache["entries"]
    cached_ts = cache.get("fetched_at", "")[:16]

    if args.current_pi:
        pi_id = _current_pi_id(entries)
        if not pi_id:
            print("Could not determine the current PI from the schedule.", file=sys.stderr)
            sys.exit(1)
        print(pi_id)
        return

    if args.current:
        active = _find_active_entry(entries)
        if not active:
            print(f"No active sprint found for today ({date.today()}). "
                  f"We are in a gap between PIs.", file=sys.stderr)
            sys.exit(0)
        pi_id = _pi_prefix(active["label"])
        pi_entries = _entries_for_pi(entries, pi_id)
        print(f"Today: {date.today()}  |  Cached: {cached_ts} UTC")
        print(f"Active: {active['label']}  ({active['start']} → {active['finish']})")
        if active.get("holidays_us"):
            print(f"US Holidays this sprint: {active['holidays_us']}")
        print(f"\nFull PI {pi_id}:")
        if args.format == "json":
            print(json.dumps(pi_entries, indent=2))
        else:
            print(_format_table(pi_entries, args.holidays))
        return

    if args.pi:
        entries = _entries_for_pi(entries, args.pi)
        if not entries:
            print(f"No schedule entries found for PI '{args.pi.upper()}' in {year}.",
                  file=sys.stderr)
            sys.exit(1)

    if args.format == "json":
        print(json.dumps({"fetched_at": cache["fetched_at"],
                          "year": year,
                          "entries": entries}, indent=2))
    else:
        print(f"PI {year} ART Schedule  (cached: {cached_ts} UTC)\n")
        print(_format_table(entries, args.holidays))


if __name__ == "__main__":
    main()
