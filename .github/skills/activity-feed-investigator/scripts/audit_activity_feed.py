#!/usr/bin/env python3
"""Read-only audit: notification-definitions vs ds-message-template-api ActivityFeedTemplates.resx.

For every definition with an ActivityFeed block, finds the matching `*_Severity` / `*_AlertName`
resx keys and flags values that the definition does not allow. Resx values are Liquid expressions,
so literals are extracted from all branches (e.g. `{{ if Status == "Active" }}Medium{{ else }}Low{{ end }}`).

Usage (from the workspace root):
    python3 .github/skills/activity-feed-investigator/scripts/audit_activity_feed.py [--event SensorOffline] [--all]
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SEVERITIES = {"None", "Low", "Medium", "High", "Critical"}
RESX = Path("ds-message-template-api/src/DeviceServices.MessageTemplate.Api/Resources/ActivityFeed/ActivityFeedTemplates.resx")
DEFINITIONS = Path("notification-definitions/templates")
LIQUID_TAG = re.compile(r"\{\{.*?\}\}", re.DOTALL)


def load_resx(path):
    return {d.get("name"): (d.findtext("value") or "") for d in ET.parse(path).getroot().iter("data")}


def literals(expr):
    """Literal text left after stripping Liquid tags, one entry per branch."""
    parts = [p.strip() for p in LIQUID_TAG.split(expr)]
    return {p for p in parts if p}


def find_keys(resx, event, suffix):
    exact = f"{event}_{suffix}"
    return [k for k in resx if k == exact or k.endswith(f"_{exact}")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", help="only audit this EventType (case-insensitive)")
    ap.add_argument("--all", action="store_true", help="also list events that match")
    args = ap.parse_args()

    root = Path.cwd()
    if not (root / RESX).exists() or not (root / DEFINITIONS).exists():
        sys.exit("Run from the notifications-workspace root (resx or definitions not found).")

    resx = load_resx(root / RESX)
    rows, missing = [], []

    for path in sorted((root / DEFINITIONS).rglob("*.json")):
        if path.name.endswith(".translations.json"):
            continue
        try:
            d = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            continue
        if not isinstance(d, dict) or "ActivityFeed" not in d:
            continue
        events = d.get("EventType") or ""
        events = events if isinstance(events, list) else [events]
        if args.event:
            events = [e for e in events if e.lower() == args.event.lower()]
        if not events:
            continue

        feed_alert = (d["ActivityFeed"] or {}).get("AlertName")
        want_sev = d.get("Severity")
        rel = path.relative_to(root)

        for event in events:
            audit_event(resx, event, want_sev, feed_alert, rel, args, rows, missing)

    for r in rows:
        print(" | ".join(r))
    mism = sum(1 for r in rows if r[0] != "ok")
    print(f"\n{mism} mismatch(es); {len(missing)} definition(s) with no matching resx severity key (informational).")
    if args.event:
        for m in missing:
            print("missing:", " | ".join(m))
    return 1 if mism else 0


def audit_event(resx, event, want_sev, feed_alert, rel, args, rows, missing):
    sev_keys = find_keys(resx, event, "Severity")
    if not sev_keys:
        missing.append((event, str(rel), "no *_Severity key in resx"))
    for k in sev_keys:
        found = literals(resx[k]) & SEVERITIES
        if want_sev and want_sev not in found:
            rows.append(("SEVERITY", event, k, f"definition={want_sev}", f"resx={sorted(found)}", str(rel)))
        elif args.all:
            rows.append(("ok", event, k, f"definition={want_sev}", f"resx={sorted(found)}", str(rel)))

    for k in find_keys(resx, event, "AlertName"):
        found = literals(resx[k])
        if feed_alert and feed_alert not in found:
            rows.append(("ALERTNAME", event, k, f"definition={feed_alert}", f"resx={sorted(found)}", str(rel)))
        elif args.all:
            rows.append(("ok", event, k, f"definition={feed_alert}", f"resx={sorted(found)}", str(rel)))


if __name__ == "__main__":
    sys.exit(main())
