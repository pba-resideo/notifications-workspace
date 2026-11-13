# PT-1493 – Pro Campaigns for Custom Messaging

[Jira](https://resideo.atlassian.net/browse/PT-1493) · Epic · PI 26-D · Status: Implementing

## Summary

Pros can currently send only one message to all customers. This epic adds campaign messaging to Pro Portal so Pro Owners/Admins can create campaigns and send them to all customers, selected audiences, or individual customers. Campaigns display in the Resideo Connect app. It uses the audiences built in [PT-1494](../PT-1494-campaign-audiences-custom-messaging/overview.md).

What it does:

- Adds a **Marketing** left-nav item containing Brand Profile, Audiences, and Campaigns.
- Create campaign messages, apply an audience, then save and publish. Campaigns go live on publish (no scheduling for MVO).
- Supports multiple campaign messages, ranked so a customer in several audiences sees the first-ranked one.
- Supports a default campaign (no audience) shown to customers who match no other campaign.
- Archive a campaign: stops it, keeps it for reference, and allows republishing.
- View a published or active campaign: name, number of customers, and message.
- Homeowner display is unchanged for MVO (40 character limit; existing FA app toggle).
- Access is limited to Pro Owners and Admins.

Future: scheduled or time-boxed messages and additional filters.

Parent feature: [PT-744](../overview.md). Sibling epic: PT-1494 (Campaign audiences for custom messaging).
