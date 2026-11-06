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
