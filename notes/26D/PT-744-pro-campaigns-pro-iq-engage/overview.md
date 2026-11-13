# PT-744 – Pro Campaigns for Pro-IQ Engage

[Jira](https://resideo.atlassian.net/browse/PT-744) · Feature · PI 26-D · Status: Open

## Summary

Today, Brand Profile messaging lets a Pro push only one custom message to **all** of their customers (in the app and on ElitePRO/ProSeries panels). This feature adds targeted marketing messaging in Pro Portal so Pros can send campaigns to all customers, groups of customers, or a single customer.

Why: the current approach doesn't support common use cases such as filter replacement reminders. It is blocking Pro-IQ Services adoption at Parker & Sons (2300+ ElitePROs, 50,000 service program members), who want targeted communications to customer segments.

Scope:

- Customer filtering within a customer branch.
- Extend the custom message flow to support multiple messages sent to one, many, or all customers.
- Keep the existing cobrand/company-wide message flow where appropriate.
- Display to homeowners is unchanged for MVO (40 character limit; the existing FA app toggle for pro messaging stays).

Success criteria: display a message to all, some, or a specific customer; save filtered customer groups; support multiple messages across segments; define which message wins when a customer is in multiple groups; show who sees which message (e.g. audit log); reduce spam and customer irritation.

Future scope: an inbox-style transactional messaging experience with sent/read/acknowledged/dismissed states.

## Epics

- [PT-1493](PT-1493-pro-campaigns-custom-messaging/) – Pro campaigns custom messaging
- [PT-1494](PT-1494-campaign-audiences-custom-messaging/) – Campaign audiences for custom messaging
