---
author: Dominik von Burg <dominik.vonburg@resideo.com>
description: SAFe domain knowledge for Resideo trains (Consumer, Pro, Platform) plus the ART calendar script. Use when asking about the current PI or sprint, PI schedules and holidays, risk registers, team rosters, priorities, CCRB change requests, epic health checks, or any PI planning question.
metadata:
    github-path: skills/engineering/safe
    github-ref: refs/heads/main
    github-repo: https://github.com/resideo/skills
    github-tree-sha: f93eabc08005dad818bc3020dfce97a0c718853f
name: safe
tags:
    - safe
    - agile
    - pi
    - planning
    - consumer-train
    - jira
    - confluence
version: 1.0.0
---
# SAFe at Resideo

Domain knowledge for Resideo's SAFe setup (Consumer, Pro, and Platform trains), plus one script for the ART calendar. All data fetching goes through the atlassian skill. This skill has no credentials, no HTTP code, and no pip dependencies of its own.

All script paths are relative to this skill's directory (the folder containing this SKILL.md). Atlassian scripts live in the sibling skill directory, referenced as `../atlassian/scripts/`.

## Fetching data

Every Jira and Confluence operation uses the atlassian skill's scripts:

```bash
# Read a Confluence page (storage HTML body)
python3 ../atlassian/scripts/get_page.py <page_id> --body

# List child pages of a page or folder
python3 ../atlassian/scripts/get_page_children.py <parent_id>

# List child folders of a page or folder (Confluence folders are a separate content type)
python3 ../atlassian/scripts/get_folder_children.py <folder_id>

# JQL search
python3 ../atlassian/scripts/search_issues.py "<jql>" --all
```

Credentials live in the atlassian skill's `.env` (`../atlassian/.env`). Pages come back as Confluence storage HTML. Parse the tables in them directly; no helper is needed.

## PI naming and the current PI

- PI format is `PI YY-X`. YY is the two-digit year, X is A, B, C, or D. Every year has exactly four PIs in that order.
- Sprint format is `YY-X.1` through `YY-X.5`, then `YY-X.6 (IP)` for Innovation & Planning. Example: `26-C.1`, `26-C.6 (IP)`.
- Never assume the current PI. Derive it from the calendar:

```bash
python3 scripts/get_schedule.py --current-pi
# → 26-C
```

## Schedule script

`scripts/get_schedule.py` fetches the "PI <year> Schedule" page from space CE. It finds the page by title search, so it works for any year without editing the script. It caches per year for 24 hours in this skill's `data/` directory.

```bash
python3 scripts/get_schedule.py [options]
```

| Option | Description |
|---|---|
| `--pi ID` | Filter to one PI, e.g. `26-C`. The year is read from the id. |
| `--year YEAR` | Fetch another year's schedule (default: current calendar year) |
| `--current` | The sprint or event active today, plus the full PI context |
| `--current-pi` | Print only the current PI id (e.g. `26-C`) and exit |
| `--holidays REGION` | Include the holiday column: `us` · `india` · `ch` · `uk` |
| `--refresh` | Bypass the 24h cache |
| `--format table\|json` | Output format (default: `table`) |

Table legend: `▶` marks the entry active today, `★` marks PI Planning events.

```bash
# What sprint are we in right now?
python3 scripts/get_schedule.py --current

# Just PI 26-C with India holidays
python3 scripts/get_schedule.py --pi 26-C --holidays india

# Next year's calendar as JSON
python3 scripts/get_schedule.py --year 2027 --format json
```

## Confluence sources

| Source | Space | What it contains | How to find it |
|---|---|---|---|
| PI schedule | CE | Full ART calendar: all PIs, sprints, IP sprints, PI Planning, per-region holidays | `scripts/get_schedule.py` finds it by title per year |
| Process docs | SAAR | Framework overview, glossary, work item type definitions | Page ids below |
| PI risk register | CE | Per-PI risks: description, impact, owner, category, probability, latest notes | PI folder tree, see below |
| PI team roster | CE | Per-PI Consumer Train roster: role, location, name, email by sub-team | PI folder tree, see below |
| PI priorities, planning prep, carry-over epics, bug bash, RCA | CE | The rest of the per-PI Consumer Train working pages | PI folder tree, see below |
| CCRB change requests | CE | Consumer Change Request Board submissions per train and PI | CCRB subfolder in the train folder, see below |

### Process docs (SAAR space)

General process documentation lives in the SAAR space. The homepage is `3910140761` (Scaled Agile at Resideo). Other pages:

| Key | Title | Page id |
|---|---|---|
| Glossary | Glossary | `3927408818` |
| Work items | Work Item Types | `3926884592` |

```bash
# Read a page
python3 ../atlassian/scripts/get_page.py 3927408818 --body

# Discover more pages under the homepage
python3 ../atlassian/scripts/get_page_children.py 3910140761
```

### Per-PI content (CE space folder tree)

Everything related to a specific PI lives in one folder tree in space CE. The root folder is `3522400355`. The structure is always the same, so it works for any year and any PI without hardcoded page ids:

| Level | Example | Listing command |
|---|---|---|
| Root folder | `3522400355` | start here |
| Year folder | `2026` | `get_folder_children.py 3522400355` |
| PI folder | `PI 26-B` | `get_folder_children.py <year_folder_id>` |
| Train folder | `PI 26-C - Consumer Train` | `get_folder_children.py <pi_folder_id>` |
| Pages | Risk Register, Roster, Priorities, ... | `get_page_children.py <train_folder_id>` |

```bash
# Walk to the Consumer Train pages of PI 26-C (ids from the previous step's output)
python3 ../atlassian/scripts/get_folder_children.py 3522400355
python3 ../atlassian/scripts/get_folder_children.py 4039573507
python3 ../atlassian/scripts/get_folder_children.py 4751851688
python3 ../atlassian/scripts/get_page_children.py 4907368753
python3 ../atlassian/scripts/get_page.py 5230133284 --body
```

The year folder is named with the four-digit year and the PI folder with `PI YY-X`, so the current PI is identifiable by name once you reach that level. The train folders are named `PI YY-X <Train> Train`, e.g. `PI 26-C - Consumer Train`, `PI 26-C Pro Train`, `PI 26-C - Platform Train`.

The PI folder also holds PI-level pages directly (agenda, PI Planning navigation, solution sync board, shared roster). List them with `get_page_children.py <pi_folder_id>`.

Consumer Train pages typically include: Risk Register, Roster, Priorities, PI Prep Kanban, Planning Preparation, Carry Over Epics, Bug Bash, Planning RCA.

Risk register columns: description, impact, owner, category, probability, latest notes. Categories are Resolved, Owned, Accepted, Mitigated. Probability is H, M, or L.

Roster columns: role, location, name, email. Filter by location, team, or name after parsing.

### CCRB change requests

Each train has a CCRB subfolder inside its train folder in the PI folder tree. The names vary a bit, e.g. `Consumer Train PI 26-B - CCRB` or `Platform CCRBs - PI 26-C`. Not every train has one in every PI.

```bash
# Find the CCRB folder inside a train folder
python3 ../atlassian/scripts/get_folder_children.py <train_folder_id>

# List the CR pages in it
python3 ../atlassian/scripts/get_page_children.py <ccrb_folder_id>

# Read one CR
python3 ../atlassian/scripts/get_page.py <page_id> --body
```

Rule: always read all existing CRs before creating a new one. List the children, fetch every CR body, and match their structure, headings, table layout, and macros exactly. This keeps new CRs consistent with the existing set.

## Jira

### Project mapping

| Jira project | Train | Example key |
|---|---|---|
| `MW` | Consumer Train | `MW-xxxxx` |
| `PT` | Pro Train | `PT-xxxxx` |
| `RES` | Platform Train | `RES-xxxxx` |

### Querying items for a PI

Jira items are linked to a PI through the fix version. The version name is the PI id, e.g. `PI 26-C`. The pattern is `project = <train> AND fixVersion in ("PI YY-X")`:

```bash
# All epics on the Consumer Train for PI 26-C
python3 ../atlassian/scripts/search_issues.py 'project = MW AND fixVersion in ("PI 26-C") AND issuetype = Epic' --all --fields summary,status

# Committed epics only
python3 ../atlassian/scripts/search_issues.py 'project = MW AND fixVersion in ("PI 26-C") AND issuetype = Epic AND customfield_10540 = "Committed"' --all

# All work in a PI, any type
python3 ../atlassian/scripts/search_issues.py 'project = MW AND fixVersion in ("PI 26-C")' --all
```

Get the current PI id first with `python3 scripts/get_schedule.py --current-pi`, then plug it into the JQL. Use `--all` whenever you need the complete list, since the search endpoint does not return a total count.

To get the child stories of one epic, query by parent:

```bash
python3 ../atlassian/scripts/search_issues.py 'parent = MW-32581' --all --fields summary,issuetype,customfield_10021
```

This is the entry point for health checks: the sprint of each child story (`customfield_10021`) drives the start, due, and PI iteration derivations below.

### Issue hierarchy

- Feature (Jira type "Feature", hierarchyLevel 2): top-level grouping, not used for sprint planning.
- Epic (Jira type "Epic"): used as the SAFe Feature. All PI planning happens at this level.
- Story / Task / Bug: children of epics, planned in sprints.

Dev vs testing stories:

- `MW-` / `PT-` / `RES-` stories are owned by the dev team. These are what matter for sprint planning and health checks.
- `SYSTEST-xxxxx` stories are owned by the QA team. Ignore them in health checks and sprint alignment.

Sprint naming examples:

- `Core Sprint 26-B.1`: Consumer App Core team, PI 26-B, sprint 1.
- `FA_NPITeam_PI26B.1_05/07-05/20`: Consumer App NPI team, PI 26-B, sprint 1.

### Custom fields on epics

| Field | Jira id | Notes |
|---|---|---|
| Story Points | `customfield_10023` | The real SP estimate. Use this one. |
| Story point estimate | `customfield_10016` | A different field. Do not use it for health checks. |
| PI Iteration | `customfield_11286` | Sprint in which the epic completes |
| Start date | `customfield_10015` | Epic start date |
| Due date | `duedate` | Epic due date |
| Commitment | `customfield_10540` | SAFe commitment status, see below |
| Developer | `customfield_10371` | Owner field, used instead of assignee |
| Team | `customfield_10001` | e.g. Consumer App Core / Consumer App NPI |
| PMO Category | `PMO Category` | Priority grouping, see below |
| Sprint (on stories) | `customfield_10021` | Sprint assigned to a child story or task |

### PMO Category

Epics are grouped into PMO Categories, and the category is prioritized as a group rather than each epic individually. Priority 0 is highest (the O&M bucket), then 1-32 in ascending order. This lets product set priority on the group.

### SAFe Commitment field (`customfield_10540`)

| Value | Meaning |
|---|---|
| `Committed` | Planned and firmly committed for this PI |
| `Uncommitted` | Planned but not firmly committed (stretch or open-ended) |
| `null` / empty | Not planned for this PI. Skip all health checks. |

Health checks apply only to planned epics (Committed or Uncommitted).

### Health check rules (planned epics only)

1. Story points: set, and <= 30 (`customfield_10023`).
2. PI iteration: assigned (`customfield_11286`). This is the last sprint in which the epic's stories land.
3. Start date: set (`customfield_10015`). Derive it from the earliest current-PI sprint among the epic's dev stories.
4. Due date: set (`duedate`) if all dev stories have sprint assignments. Leave it empty if any story has no sprint yet.
5. Has stories: at least one child dev story or task. SYSTEST stories do not count.
6. Story sprint alignment: dev stories are assigned to sprints in the current PI (sprint names contain the current PI id, e.g. `26-C`).

Auto-derivation from sprint data:

- Fetch all dev child stories for the epic.
- Map sprint names to dates with `scripts/get_schedule.py`.
- Start date = start of the earliest current-PI sprint used by any story.
- Due date = end of the latest current-PI sprint used, only if all stories have a sprint.
- PI iteration = `PI YY-X.N` where N is the last sprint number used.

### Dependency links

Link type: "is dependency of". If Epic A "is dependency of" Epic B, then Epic A must be delivered (due date) before Epic B starts (start date).

## Common use cases

| Question | Command |
|---|---|
| What sprint are we in? | `python3 scripts/get_schedule.py --current` |
| What is the current PI id? | `python3 scripts/get_schedule.py --current-pi` |
| When does the next PI Planning start? | `python3 scripts/get_schedule.py`, then find the next `★` row after today |
| Dates for PI 26-C | `python3 scripts/get_schedule.py --pi 26-C` |
| US holidays in 26-D.2 | `python3 scripts/get_schedule.py --pi 26-D --holidays us` |
| What is a ROAM board? | `python3 ../atlassian/scripts/get_page.py 3927408818 --body` (glossary), search for the term |
| How is an Epic defined? | `python3 ../atlassian/scripts/get_page.py 3926884592 --body` (work items) |
| Where are the CRs for this PI? | Walk the tree to the train folder, find the CCRB subfolder, then `get_page_children.py <ccrb_folder_id>` |
| Risks for the current PI | Walk the CE folder tree to the Consumer Train folder, find the Risk Register page, then `python3 ../atlassian/scripts/get_page.py <id> --body` |
| Who is on the Consumer Train? | Walk the CE folder tree to the Consumer Train folder, find the Roster page, then `python3 ../atlassian/scripts/get_page.py <id> --body` |
