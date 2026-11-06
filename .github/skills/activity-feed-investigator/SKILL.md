---
name: activity-feed-investigator
description: >
  Investigate bugs where an activity feed / notification item shows the wrong severity, title, body,
  alertName, or localized text (e.g. wrong alert background colour, "Urgent" instead of "Warning").
  Traces the Jira ticket through notification-definitions, ds-message-template-api resx templates,
  locale files, integration tests, and the RIS severity mapping. Use when given an ANW ticket about
  activity feed content, or when asked "why does this alert have the wrong severity/text".
---

## Goal

Find which layer disagrees with the source of truth, report it in a table, then (after the user
confirms) fix the resx and the test, and run the targeted tests.

## Layer map

| Layer | Location |
|---|---|
| Source of truth | `notification-definitions/templates/<DeviceFamily>/<eventtype>.json`: `Severity`, `ActivityFeed.AlertName`, `ShortText`, `LongText`. Translations in `<eventtype>.translations.json`. |
| Rendered values | `ds-message-template-api/src/DeviceServices.MessageTemplate.Api/Resources/ActivityFeed/ActivityFeedTemplates.resx`, keys `<Event>_AlertName`, `_Severity`, `_Title`, `_Body` (Liquid, e.g. `{{ if Status == "Active" }}Medium{{ else }}Low{{ end }}`). Some keys carry a prefix (`DeviceOffline_DeviceOffline_*`, `Panel.Sensor_*`). |
| Locales | `ActivityFeedTemplates.<locale>.resx` (de-DE, es-ES, es-MX, fr-BE, fr-CA, fr-FR, it-IT, nl-BE, nl-NL). Text only; severity lives only in the base file. Verify with `grep -c _Severity`. |
| Integration tests | `ds-message-template-api/tests/DeviceServices.MessageTemplate.IntegrationTests/Templates/<Event>/<Event>.cs`: `Alert(name, Severity)`, `Feed(locale, title, body)`. Tests can lock in a wrong value, so check them. |
| Severity enum | `MessageSeverity` = None/Low/Medium/High/Critical. |
| RIS mapping | `integration-services/src/IntegrationServices.BusinessLogic/Core/Helpers/DeviceAlertSeverityHelper.cs`: critical/high -> **Urgent**, medium -> **Warning**, low/none -> **Notice**. Used by `AccountsService` and `UsersService` when building the mobile `/notification` response. |

## Steps

1. **Ticket.** Fetch the Jira issue (Atlassian MCP `getJiraIssue`, cloudId `resideo.atlassian.net`). Extract the alert/event name, device type, and expected vs actual value. Translate mobile terms first: Urgent=High/Critical, Warning=Medium, Notice=Low.
2. **Audit script.** From the workspace root run
   `python3 .github/skills/activity-feed-investigator/scripts/audit_activity_feed.py --event <EventType> --all`
   It compares definition vs base resx for severity and alertName. Exit code 1 = mismatch.
   Matching is by EventType and key suffix, so entries for other device families sharing the event name (e.g. `Panel.Sensor_LowBattery_*`) can be false positives. Judge them against the ticket's device type. Without `--event` it audits everything; report unrelated findings to the user, do not fix them.
3. **Definition.** Read the definition JSON for the event (check every device-family folder: `find notification-definitions/templates -iname '<event>*.json'`).
4. **Resx.** Read the event's keys in the base resx, then check locale files for overrides of the same key.
5. **Tests.** Read `Templates/<Event>/<Event>.cs` and any `.json` fixture next to it. Also grep `AlertTemplateControllerTests.cs` and `ApiClient.Tests` for the event.
6. **Downstream.** If the template value is already right, the bug is downstream: check `DeviceAlertSeverityHelper` and its callers in integration-services, and NS use of `ComputeSeverityAsync` in `ds-notification-service`.
7. **Report.** One table: layer / expected / actual / match, plus the root cause in one sentence.
8. **Fix (confirm first).** Show the proposed resx and test edits and ask the user before editing. Then apply and run
   `dotnet test tests/DeviceServices.MessageTemplate.IntegrationTests --filter "FullyQualifiedName~<Event>"` from `ds-message-template-api`.
   Do not commit unless asked.

## Gotchas

- The `grep` tool skips the gitignored sub-repos in this workspace. Use bash:
  `grep -rIil '<term>' --exclude-dir={bin,obj,node_modules,.git} .`
- Each sub-repo is its own git repo; run git commands inside it.
- Edit resx files with targeted string edits. Do not re-serialize the XML (it reformats the file and adds BOM or whitespace churn).
- If the definition itself looks wrong (the product wants something else), stop and ask: notification-definitions is the source of truth, so changing it is a product decision.
