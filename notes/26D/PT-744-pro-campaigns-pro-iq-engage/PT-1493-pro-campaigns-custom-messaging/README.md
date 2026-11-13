# PT-1493 – Pro Campaigns for Custom Messaging

[Jira](https://resideo.atlassian.net/browse/PT-1493) · Epic · PI 26-D · Status: Implementing

## Summary

Pros can currently send only one message to all customers. This epic adds campaign messaging to Pro Portal so Pro Owners/Admins can create campaigns and send them to all customers, selected audiences, or individual customers. Campaigns display in the Resideo Connect app. It uses the audiences built in [PT-1494](../PT-1494-campaign-audiences-custom-messaging/README.md).

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

Parent feature: [PT-744](../README.md). Sibling epic: PT-1494 (Campaign audiences for custom messaging).

## Comment thread digest

Source: [Jira comments](https://resideo.atlassian.net/browse/PT-1493). 2 comments so far. Last checked 2026-11-13.

Thread: Marla Foreman (FE) posted questions and an endpoint list on 2026-11-04. Travis Kragh (design/product) answered part of it on 2026-11-12. Stephan Schmidt is still looking into the technical details.

### Needs an answer

| # | Question | Asked of | Status |
|---|---|---|---|
| 1 | Which roles can access campaigns: Owners, Admins, Advanced Technicians? | Stephan, Grzegorz, Travis | Not answered in the thread (epic summary says Owners/Admins) |
| 2 | Is there a max number of active campaigns (per branch)? | Same | Not answered |
| 3 | What happens when an audience used by a campaign is deleted? Handled on the Audiences side? | Same | Not answered |
| 4 | Is a unique customer count across overlapping audiences feasible on the backend? | RIS (raised by Travis) | Open |
| 5 | Final MVP vs stretch scope (#6-7 below) | Stephan (technical details) | Open, waiting on Stephan |
| 6 | Endpoint questions for RIS (below) | RIS | None answered |

### Answered

| Question | Answer | By / date |
|---|---|---|
| Keep the default campaign? | Yes. One per branch, pinned last. It can't be deleted, archived or reordered. Its message comes from the branch's Brand Profile. | Travis, 11-12 |
| Are branches in scope? | Yes, in MVP. No "All Branches" option. The dropdown is hidden for single-branch companies. Designs are coming. All GET and create endpoints need to account for branches. | Travis, 11-12 |
| Can a campaign change branch? | No. Audiences are per branch too. | Travis, 11-12 |
| Max campaign name length? | 60 characters. The message stays at 40. | Travis, 11-12 |
| Unsaved-changes guard? | Yes. Leaving Create/Edit (nav link, Cancel, browser back) shows a "Changes Will Be Lost" modal with Go Back / Continue. [Figma](https://www.figma.com/design/hl0vnCbfWhdA4uB9JZN8Lc/Campaigns_SW-PRO?node-id=6243-6583) | Travis, 11-12 |

### Decisions and design notes from Travis

- **MVP scope:** Active and Archived, with Archive/Restore.
- **Stretch:** Expired, Reuse, and dates. Plan only for MVP for now.
- **Customer count:** Customers in several audiences count once, in the form banner and on each campaign row. It must be a unique count, not a sum.
- **Default campaign editing:** Proposed to happen in Brand Profile, via "Edit in Brand Profile" in the row menu.
- **Ranking:** Highest rank wins on overlap. A campaign with no message doesn't override lower-ranked ones. New campaigns go to the bottom, above the Default.

### Endpoint questions for RIS (all open)

| Screen | Endpoint | Question |
|---|---|---|
| Campaigns list | `GET campaigns` | Server-side filter for Active/Archived/Expired, or filter on the frontend? |
| Campaigns list | `GET campaigns` | Does it return customer count and audiences per campaign, or does the FE also call `GET audiences`? |
| Campaigns list | `PUT campaigns` | Reorder by sending the whole list in new order (like Alert Settings)? |
| Delete modal | `DELETE campaign/{id}` | Can the response return the deleted campaign's name for the success toast? |
| Archive / Restore | `PUT campaign/{id}` | Special archive endpoint, or the normal edit endpoint? |
| Reuse (stretch) | `PUT campaign/{id}` | Custom reuse endpoint that keeps the old record, or edit in place? |
| Create / Edit | `GET audiences` | Needs the customer count per audience for the banner. |
| Create / Edit | `POST campaign` | Max name length? (Answered: 60.) |
| Create / Edit | `PUT campaign/{id}` | Can the branch change? (Answered: no.) |

No API is needed for the empty state or the message preview. Set message uses `PUT campaign/{id}`.

### Conflicts to check against the epic summary

- The summary says archived campaigns can be republished. Travis lists Restore as MVP and Reuse as stretch, so confirm which applies.
- The summary doesn't mention branches, the default campaign being pinned last, or the 60-character name limit.
