---
name: git-commit
description: >
  Creates a commit in one of the notifications-workspace repos (ds-notification-service,
  ds-message-template-api, ds-event-definitions, notification-definitions, integration-services,
  or the workspace repo itself) using that repo's commit message standard. Use when asked to
  commit, "commit this", or /commit while working in this workspace. Takes precedence over a
  generic personal `commit` skill here.
---

## Message standard

```
<KEY>: <Imperative description>

<optional body: what and why, wrapped at 72 columns>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Derived from the last 200 non-merge commits of each repo plus the checks the repos enforce. Where the
history is mixed, this takes the stricter form.

### Subject rules

| Rule | Detail | Evidence |
|---|---|---|
| Ticket prefix | Jira key, uppercase, immediately followed by `: `. Example `ANW-2685: Set SensorOffline severity to Medium`. | `KEY: ` is the dominant keyed form in notification-service (63 colon vs 23 space), template-api (68 vs 36) and RIS (146 vs 26). ds-event-definitions is looser (29 colon, 73 space, plus `[TABASCO-16057]` and `TABASCO-16121 : `); use the strict form there too. |
| Key source | The key in the branch name (`bugfix/ANW-2685-...` gives `ANW-2685`, see the `git-branch` skill). Otherwise ask the user. | |
| Description | Starts with a capital letter, imperative mood (`Add`, `Remove`, `Fix`), no trailing period. | Imperative outnumbers past tense (`Added`) in every repo: about 3 to 1 in most, 39 to 24 in RIS. Lowercase descriptions are common in the two definitions repos (72 of 200 in notification-definitions) but capitalised is the majority everywhere. |
| Length | Whole subject at most 72 characters; aim for 64 or fewer. | GitHub appends ` (#NNNN)` to the subject when the PR merges. Average subject is 38 to 63 characters, but 6 to 28% of subjects exceed 72 once the PR suffix is counted. |
| No `(#NNNN)` | Never type the PR number. | It is added by GitHub: the last 100 first-parent subjects end with it in notification-service 100, template-api 100, RIS 98, notification-definitions 89 (ds-event-definitions 36). |
| No Conventional Commits | No `feat:`, `fix:`, `docs:`, scopes or `!`. | Human commits in all five repos use ticket keys. 46 of the 60 conventional-style subjects in notification-definitions come from `github-actions[bot]` (`docs: auto-update template overviews [skip ci]`). |
| One key | One key in the subject. List others in the body (`Related: ANW-2576, ANW-2570`). | RIS has `RO-289: RO-290: RO-291: ...` once; it passes the regex but is not the norm. |
| What it says | Say what changed in the repo and name the thing (event, template, endpoint). Do not paste the Jira title verbatim if it describes the symptom. | `ANW-2570: Severity bug fix and sync with ND` is the weak end; `ANW-2624: Add shutoff valve microleak test interrupted/rejected alerts` is the target. |

Validate before committing (a subject that fails this is wrong, not a style choice):

```
^([A-Z][A-Z0-9]*-[0-9]+): [A-Z].*[^.]$      # plus: length <= 72
```

In integration-services `NO-TICKET` is also valid in place of the key, and its `[A-Z]{2,9}-[0-9]{1,6}` key pattern (2 to 9 letters,
1 to 6 digits) is the enforced one. Only about a quarter to a third of existing subjects (11 to 89 of the last 200, by repo) pass
the strict form today, because history is loose; new commits should still meet it.

### Without a ticket

| Repo | Form |
|---|---|
| integration-services | `NO-TICKET: <Description>`. Required by the PR title check (below). 24 of the last 200 subjects use it. |
| notification-service, template-api, ds-event-definitions, notification-definitions | Ask the user for a ticket first. For chores with none (dependency bumps, tooling), a plain capitalised imperative subject with no prefix, e.g. `Update vulnerable packages`, `Upgrade tests to xUnit v3`. |
| notifications-workspace (the parent repo, no Jira work) | Plain capitalised imperative subject, e.g. `Add git-branch skill with branch naming standard`. |

### Body

- Blank line after the subject. Wrap at 72 columns.
- Explain **why** and the root cause for bugs, plus anything a reviewer cannot see in the diff (affected channels,
  cross-repo links, follow-ups). Do not restate the diff.
- Skip the body for trivial changes (typo, version bump, one-line config).
- Squash merges often copy branch commit messages into the final body, so keep bodies self-contained and free of "wip".

Real example (ds-message-template-api, `ANW-2624: Add shutoff valve microleak test interrupted/rejected alerts`):

```
Add ActivityFeed templates and declarative tests for the 4 new
shutoff valve microleak test alerts from notification-definitions
PR #218: ShutoffValveManualTestInterrupted, ShutoffValveManualTestRejected,
ShutoffValveScheduledTestInterrupted, ShutoffValveScheduledTestRejected.
All four are activity-feed-only (no push/email/sms).
```

## Repo-specific rules

- **integration-services.** `.github/workflows/pr-title-check.yaml` rejects PR titles that do not match
  `^([A-Z]{2,9}-[0-9]{1,6}|NO-TICKET): .*$`. Every commit subject must satisfy it, because a single-commit PR title comes
  from the commit. `pr-description-check.yaml` also requires the PR description to link
  `https://resideo.atlassian.net/browse/<KEY>` unless the title starts with `NO-TICKET:`.
  Revert subjects (`Revert "PCS-1: ..."`) are GitHub-generated; leave them as is.
- **ds-message-template-api.** Template changes need declarative tests (`.github/instructions/template-tests.instructions.md`).
  Commit the `.resx` change and its test update **together** in one commit.
- **notification-definitions.** If you change `.github/actions/<name>/src`, rebuild with `npm run build` and commit the updated
  `dist/index.js` in the same commit (CONTRIBUTING.md). The bot commits `docs: auto-update template overviews` and
  `chore: auto-update issue template categories`; never hand-write those.
- **ds-event-definitions.** A workflow increments `asyncapi.yaml` versions and commits them itself
  (`.github/workflows/README.md`); do not bump versions by hand.
- The PR template of every repo asks for the Jira ticket, so keep the key consistent between branch, commit and PR title.

## Steps

1. **Repo.** Run git inside the sub-repo that changed (`git -C <repo> ...`); the workspace root only tracks `.github/`, `scripts/` and `README.md`.
   Commit to the sub-repo's work branch, not `develop`/`main`. If it is on the base branch, stop and use the `git-branch`
   skill first (the workspace repo itself commits straight to `main`).
2. **Staged changes.** `git diff --staged --stat`. If nothing is staged, show `git status --short` and ask what to stage.
   Do not run `git add -A` without asking, and do not commit build output (`bin/`, `obj/`, `node_modules/`) or secrets.
3. **Key.** Parse it from `git branch --show-current` with `[A-Z][A-Z0-9]*-[0-9]+`. If absent, ask (or use the no-ticket forms above).
   Fetch the issue (Atlassian MCP `getJiraIssue`, cloudId `resideo.atlassian.net`) only if you need the summary to word the subject.
4. **Draft** the subject and body from the staged diff, check it against the regex and length limit, and show it to the user.
5. **Commit** with one `-m` per paragraph (no empty `-m ""`), trailer last:

   ```shell
   git commit -m "ANW-2685: Set SensorOffline severity to Medium" \
     -m "The base ActivityFeedTemplates.resx returned High for an active sensor, which RIS maps to Urgent. notification-definitions specifies Medium (RIS: Warning). Update the integration test expectation to match." \
     -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
   ```

6. **Confirm** with `git log -1 --format=%B`. Do not push unless asked.
