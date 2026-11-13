# RES-3783 – RIS/PCS Pro Campaign: Create Campaign Support

[Jira](https://resideo.atlassian.net/browse/RES-3783) · Epic · PI 26-D · Status: Ready for PI

## Summary

Platform (RIS/PCS) backend counterpart to the Pro Portal campaigns epic [PT-1493](../PT-1493-pro-campaigns-custom-messaging/overview.md). It delivers together with [RES-3820](../RES-3820-ris-pcs-create-audience-support/overview.md) as part of [PT-744](../overview.md).

Today a Pro's custom message (40 characters) is a single field coupled to branding. This epic gives RIS a separate communication channel for promotional/campaign messages, which frontends render with their own logic (IAM, email, push, etc.).

What it does:

- Campaign messages go through the existing **Notification Center** delivery path; no separate consumer messaging architecture.
- Branding with its custom message keeps the existing flow to Pro Portal, FA and Resideo Pro App.
- Messages target the Pro's relationship to a customer location (one or multiple locations), applied to all users of those locations, not to individual accounts.
- Provides or reuses an API to receive campaign messages from an authorized Pro-facing consumer. It validates message and targeting info and rejects unauthorized callers.
- Message length is configurable (default 40 characters).
- Notification Center logs sender and message, keeps history, and renders the latest message on request (max retention 3 years; a latest message older than that is still persisted and rendered).
- The data model must not block future targeting of one, many or all users within or across locations (depends on GXD).

Out of scope: device-level and user/account-level messaging; how each UI renders the message.

Dependencies: Pro Portal, FA. Architecture draft: "PT-744 Pro Messaging on Notification Center" (Confluence).
