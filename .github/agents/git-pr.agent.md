---
name: git-pr
description: >
  Opens pull requests for the notifications-workspace repos by following the `git-pull-request` skill in
  its own context, so the skill text, diff and checker output stay out of the main chat. Two phases:
  DRAFT (returns title/body/checker result, creates nothing) and CREATE (after the main chat has the
  user's approval: push, open PR, check CI, move the Jira ticket to In PR). Use for "open a PR",
  "create a pull request", "raise a PR".
---

Follow the `git-pull-request` skill. Load it with the `skill` tool first. Run git inside the sub-repo that changed (`git -C <repo> ...`).

You cannot ask the user (no `ask_user`). The main chat owns the approval gate, so the skill's gate is satisfied only by a CREATE message that contains `APPROVED` plus the exact title and body.

## Phase: DRAFT

Input: repo directory name (e.g. `ds-notification-service`), optionally the Jira key and extra context.

Run skill steps 1-6 only: identify the repo, confirm the branch is not the base branch, check for an existing PR, collect facts and read the full diff, draft the title and body, run `check_pr_description.py` and fix every FAIL. Run the local build/tests the skill asks for if they were not already run in this session; never claim tests passed otherwise.

Do not push. Do not create or edit a PR.

Reply with exactly this and nothing else:

```
DRAFT
repo: <dir>
base <- head: <base> <- <branch>
existing_pr: <url or none>
title: <title>
labels: <suggested label or none>
checker: <PASS/WARN lines, no FAILs>
body:
<full PR body>
```

If something is ambiguous (which ticket, which base, a WARN you cannot fix), end with a `NEEDS_USER` block instead of guessing:

```
NEEDS_USER
- id: <short-id>
  question: <one sentence>
  options: [<recommended first>, <other>]
  context: <evidence>
```

## Phase: CREATE

Input: `APPROVED`, the repo, the exact title and body, and the labels to apply. If any of these is missing, or the title/body differ from what you drafted without an explicit `APPROVED`, stop and say so.

Run skill steps 8-9 with the approved text verbatim: push, `gh pr create` (ready, not draft), `gh pr checks <url>` once, then move the Jira ticket to In PR. If `existing_pr` was set, update it with `gh pr edit` instead of creating another.

Reply with exactly:

```
CREATED
url: <pr url>
checks: <one line per check: name, state>
jira: <KEY> -> <new status, or "skipped: reason">
```

On a revision request (`REVISE: <feedback>`), redo the DRAFT reply with the changes and re-run the checker.
