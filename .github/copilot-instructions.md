# Notifications Workspace

This repo is a parent workspace. Each directory below is an independent git repo (gitignored here, managed by `scripts/sync_repos.py`). Run git commands inside the relevant repo.

## Nicknames

- **NS** = Notification Service = `ds-notification-service`
- **RIS** = Resideo Integration Services = `integration-services`

## Repositories

- **ds-notification-service** (.NET): Core Device Services notification service. A Consumer reads events from EventHub, enriches them via external API, and forwards them to channel-specific EventHubs; the service then delivers via push (NotificationHub), email, SMS, and SignalR.
- **ds-message-template-api** (.NET): REST API that renders localized, templated messages for each notification channel; the central template/i18n store.
- **ds-event-definitions** (JSON/AsyncAPI): Definitions of raw and templated events published by Device Services, organized by device type and domain; generates AsyncAPI specs.
- **notification-definitions** (JSON/Node): Source of truth for First Alert mobile app notification specs (templates, device families, schema, translations), replacing the old alerts Excel file.
- **integration-services** (.NET): Resideo Integration Services platform (auth, event consumer, saga processor, master data, localization, APIM config, migrations, etc.) supporting the mobile app.

## NS Consumer -> RIS enrichment

NS Consumer (`ds-notification-service/src/DeviceServices.NotificationService.Consumer`) enriches events by calling RIS `CoreController` (`integration-services/src/IntegrationServices.Api/Controllers/CoreController.cs`, route `api/v1/core`).

| NS Consumer caller | NS HTTP client (`DeviceServices.IntegrationServices.Client/Api/IntegrationServicesEnrichmentApi.cs`) | RIS endpoint (`CoreController`) |
|---|---|---|
| `Enrichers/RisDeviceContextEnricher.EnrichAsync` (`RisEnrichmentType.Complete`) | `GetDeviceInfo` | `GET devices/{macAddress}/info?partitionId=` -> `GetDeviceInfo` |
| `Enrichers/RisDeviceContextEnricher.EnrichAsync` (`RisEnrichmentType.Minimal`) | `GetDeviceUserInfo` | `GET devices/{macAddress}/userInfo` -> `GetDeviceUserInfo` |
| `Enrichers/RisLocationContextEnricher.EnrichAsync` | `GetLocationInfo` | `GET locations/{consumerDeviceLocationId}/info` -> `GetLocationInfo` |

The enrichers are invoked from `Processing/Pipelines/EventEnrichingProcessor.cs` (~lines 270-274). The client interface is `IIntegrationServicesEnrichmentApi`.

## Activity feed investigations

For bugs about wrong activity feed severity/title/body/alertName, use the `activity-feed-investigator` skill (`.github/skills/activity-feed-investigator/`). It traces notification-definitions -> template API resx -> tests -> RIS severity mapping (`DeviceAlertSeverityHelper`: High/Critical=Urgent, Medium=Warning, Low=Notice).

## Opening PRs

For "open a PR" requests, do not load the `git-pull-request` skill in the main chat. Delegate to the `git-pr` agent (`.github/agents/git-pr.agent.md`): run it for the DRAFT phase, show the user the returned title and body, get explicit approval with `ask_user`, then send the same agent `APPROVED` with the exact title and body for the CREATE phase (it also moves the Jira ticket to In PR). On a no, send `REVISE: <feedback>`.

## Merging PRs

- **ds-message-template-api**: squash merges are the norm (`gh pr merge <n> --squash --delete-branch`; history on `develop` is single-parent commits titled `... (#N)`).
- Other repos: merge convention not yet verified; check `git log --first-parent origin/develop` before choosing a method.

## Notes hierarchy

Epic/ticket notes live in `notes/<PI>/<TICKET>-<brief-title>/`, e.g. `notes/26D/PT-1493-pro-campaigns-custom-messaging/`.

- `<PI>` is the Program Increment (e.g. `26D`). Determine it from the epic's Fix Version field in Jira; the folder drops the space and hyphen (Fix Version `PI 26-D` -> `26D`).
- The folder name is the Jira key plus a short kebab-case title taken from the Jira summary (drop prefixes like `[Resideo One]`).
- Epics normally sit directly under `<PI>/`. Only when an epic belongs to a Jira Feature that is being tracked, nest the epic folders under a feature folder: `notes/<PI>/<FEATURE-KEY>-<brief-title>/<EPIC-KEY>-<brief-title>/`, e.g. `notes/26D/PT-744-pro-campaigns-pro-iq-engage/PT-1494-campaign-audiences-custom-messaging/`.
- Each feature and epic folder gets a `README.md` (Jira link, type, PI, status, summary; features list their epics).
- Look up the title in Jira (cloud `resideo.atlassian.net`) when creating a new folder.
