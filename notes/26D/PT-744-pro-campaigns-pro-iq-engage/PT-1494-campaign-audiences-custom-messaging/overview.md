# PT-1494 – Campaign Audiences for Custom Messaging

[Jira](https://resideo.atlassian.net/browse/PT-1494) · Epic · PI 26-D · Status: Implementing

## Summary

Today, Brand Profile messaging in the Resideo Connect app lets a Pro send only one message to **all** of their customers. This epic adds **audiences** to Pro Portal: named groups of customers that Pro Owners/Admins can build and then target with campaigns, so messages can go to all customers, a subset, or an individual customer.

What it does:

- Create and name an audience (customer group).
- Add customers manually, or with filters ("Smart Audience", stretch; MVP filters are city/state and device type).
- Review an audience and remove individual customers before saving.
- Sync Now: manually re-run a smart audience's filters to pick up newly matching customers.
- View saved audiences: members, applied filters, created date, and customer count.
- A customer can belong to multiple audiences.
- Access is limited to Pro Owners and Admins (Audiences, Brand Profile, Campaigns).

Out of scope for MVP: CSV upload of CRM customers into an audience.

Parent feature: [PT-744](../overview.md). Sibling epic: PT-1493 (Pro campaigns custom messaging).
