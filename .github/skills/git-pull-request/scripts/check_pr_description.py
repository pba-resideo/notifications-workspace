#!/usr/bin/env python3
"""Pre-flight check for a PR title and description, mirroring what each repo's CI enforces.

ENFORCED rules fail the real PR checks (exit code 1 if any fail). RECOMMENDED rules are the
repo's template or this workspace's standard and only produce warnings.

Section content rule (resideo/beacon-build-support check-pr-template): after removing HTML comments,
empty bullets and links, a required section needs at least 10 letters (a-z only).

Usage:
    python3 check_pr_description.py --repo ds-notification-service --title "ANW-1: Add x" --body-file body.md
    python3 check_pr_description.py --repo integration-services --title "PCS-1: Add x" < body.md
"""
import argparse
import re
import sys

MIN_LETTERS = 10
KEY = r"[A-Z][A-Z0-9]*-[0-9]+"
STRICT_TITLE = re.compile(rf"^{KEY}: [A-Z].*[^.]$")
RIS_TITLE = re.compile(r"^([A-Z]{2,9}-[0-9]{1,6}|NO-TICKET): .*$")
RIS_JIRA_LINK = re.compile(r"https://resideo\.atlassian\.net/browse/[A-Z]{2,9}-[0-9]{1,6}")
ANY_JIRA_LINK = re.compile(r"https://resideo\.atlassian\.net/browse/" + KEY)

# (name, header pattern, enforced)
SECTIONS = {
    "ds-notification-service": [
        ("Related Jira tickets", r"###\s*Related\s+Jira\s+tickets", False),
        ("Motivation", r"###\s*Motivation", True),
        ("Changes", r"###\s*Changes", True),
        ("Preconditions, next steps, remaining questions", r"###\s*Preconditions", False),
    ],
    "ds-message-template-api": [
        ("Related Jira tickets", r"###\s*Related\s+Jira\s+tickets", False),
        ("Motivation", r"###\s*Motivation", True),
        ("Significant changes", r"###\s*Significant\s+changes", True),
        ("Preconditions, next steps, remaining questions", r"###\s*Preconditions", False),
    ],
    "notification-definitions": [
        ("Jira ticket", r"##\s*Jira\s+ticket", False),
        ("What changed", r"##\s*What\s+changed", False),
        ("Missing info / follow-up", r"##\s*Missing\s+info", False),
    ],
    "integration-services": [
        ("Originating Jira Item", r"##\s*Originating\s+Jira\s+Item", False),
        ("Motivation", r"##\s*Motivation", False),
    ],
    # No template or CI in this repo; the notification-service structure is the workspace standard.
    "ds-event-definitions": [
        ("Related Jira tickets", r"###\s*Related\s+Jira\s+tickets", False),
        ("Motivation", r"###\s*Motivation", False),
        ("Changes", r"###\s*Changes", False),
    ],
}


def strip_noise(text):
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"<!--[\s\S]*?-->", "", text)
    text = re.sub(r"^\[.*?\]:\s*#\s*\(.*?\)\s*$", "", text, flags=re.M)
    text = re.sub(r"^\[//\]:\s*#\s*\(.*?\)\s*$", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s*$", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s*$", "", text, flags=re.M)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"(https?|ftp)://[^\s<>()\[\]]+", "", text, flags=re.I)
    text = re.sub(r"www\.[^\s<>()\[\]]+", "", text, flags=re.I)
    return text


def section_letters(body, pattern):
    m = re.search(pattern, body, flags=re.I)
    if not m:
        return None
    rest = body[m.end():]
    nxt = re.search(r"^#+\s+", rest, flags=re.M)
    content = rest[: nxt.start()] if nxt else rest
    return len(re.findall(r"[a-zA-Z]", strip_noise(content)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, choices=sorted(SECTIONS))
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", help="read the description from this file instead of stdin")
    args = ap.parse_args()

    body = open(args.body_file, encoding="utf-8").read() if args.body_file else sys.stdin.read()
    results = []  # (status, enforced, message)

    def add(ok, enforced, msg):
        results.append(("PASS" if ok else ("FAIL" if enforced else "WARN"), enforced, msg))

    ris = args.repo == "integration-services"
    if ris:
        add(bool(RIS_TITLE.match(args.title)), True, "title matches ^(KEY|NO-TICKET): .* (pr-title-check.yaml)")
        if not args.title.startswith("NO-TICKET:"):
            add(bool(RIS_JIRA_LINK.search(body)), True,
                "description links https://resideo.atlassian.net/browse/<KEY> (pr-description-check.yaml)")
    add(bool(STRICT_TITLE.match(args.title)) or (ris and args.title.startswith("NO-TICKET: ")), False,
        "title is 'KEY: Capitalised description' without a trailing period (git-commit standard)")
    add(len(args.title) <= 72, False, f"title is at most 72 characters (is {len(args.title)})")
    add("(#" not in args.title, False, "title has no hand-typed (#NNNN) suffix")

    if not ris and not ANY_JIRA_LINK.search(body):
        add(False, False, "description links the Jira ticket (https://resideo.atlassian.net/browse/KEY)")

    for name, pattern, enforced in SECTIONS[args.repo]:
        n = section_letters(body, pattern)
        if "Jira" in name and n is not None:
            # A ticket section is link-only by design, so it is checked for the link, not for prose.
            add(bool(ANY_JIRA_LINK.search(body)), enforced, f"section '{name}' contains the Jira link")
        elif n is None:
            add(False, enforced, f"section '{name}' present (pattern: {pattern})")
        else:
            add(n >= MIN_LETTERS or name in ("Preconditions, next steps, remaining questions",
                                             "Missing info / follow-up"),
                enforced, f"section '{name}' has real content ({n} letters, needs {MIN_LETTERS})")

    for status, enforced, msg in results:
        print(f"{status:4} {'[CI] ' if enforced else '     '}{msg}")
    failed = [r for r in results if r[0] == "FAIL"]
    warned = [r for r in results if r[0] == "WARN"]
    print(f"\n{len(failed)} enforced failure(s), {len(warned)} warning(s).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
