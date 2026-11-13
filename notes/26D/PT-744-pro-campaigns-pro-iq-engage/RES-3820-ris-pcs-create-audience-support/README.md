# RES-3820 – RIS/PCS Pro Campaign: Create Audience Support

[Jira](https://resideo.atlassian.net/browse/RES-3820) · Epic · PI 26-D · Status: Ready for PI

## Summary

Platform (RIS/PCS) backend counterpart to the Pro Portal audiences epic [PT-1494](../PT-1494-campaign-audiences-custom-messaging/README.md). It delivers together with [RES-3783](../RES-3783-ris-pcs-create-campaign-support/README.md) as part of [PT-744](../README.md).

Pros today have a single custom message (40 characters) tied to branding, so they can't target customer subsets. This epic covers the audience creation workflow: a reusable, named group of customers that can be attached to multiple campaigns.

What it does:

- Select filters (location, device type, other audience attributes), and combine multiple filters.
- Return the list of matching audience members for review before saving.
- Remove individuals from the list without changing the filter criteria.
- Save the audience under a unique name, and retrieve it later during campaign creation.
- Reusable across campaigns.
- Creation limited to Owner, Admin and Advance Technician roles.

Assumptions: targeting is the Pro's relationship to a customer location, not individual user accounts; GXD designs must be available before development.

Dependencies: Pro Portal, FA, RIS backend. Architecture draft: "PT-744 Pro Messaging on Notification Center" (Confluence).
