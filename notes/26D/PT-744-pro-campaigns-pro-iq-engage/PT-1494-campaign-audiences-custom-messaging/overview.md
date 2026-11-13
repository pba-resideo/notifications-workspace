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

## Comment thread digest

Source: [Jira comments](https://resideo.atlassian.net/browse/PT-1494). 11 comments, 2026-11-03 to 2026-11-10. Last checked 2026-11-13.

Thread: Aliaksandra Nasevich (FE) posted the endpoint list and questions. Stephan Schmidt and Grzegorz Konieczny (RIS) answered. Anna Zahrbock, Travis Kragh and Ellen Bensman are the product/design contacts.

### Needs an answer

| # | Question | Asked of | Status |
|---|---|---|---|
| 1 | Can an audience be deleted while a campaign uses it? Options from Anna: (a) block it and tell the user to delete the campaign first (suggested for MVO), or (b) delete it and remove it from the active campaign with a warning. | Anna, Travis | Open. Anna leans to (a), no decision. Same question is open on [PT-1493](../PT-1493-pro-campaigns-custom-messaging/overview.md). |
| 2 | Sync Now: synchronous request or async job? | RIS | Not answered |
| 3 | Smart audience POST: send filters plus excluded customer IDs? | RIS | Not answered (Stephan said "mostly correct") |
| 4 | CSV upload: how does it work when RIS needs customer IDs but the CSV only has emails? | RIS, GXD | Open. Out of MVP per the epic summary, but the workflow is undefined. |
| 5 | City/State filter: free text, Google API, or values from existing customer data? | GXD, FE | Open. Needs refinement with GXD. |
| 6 | Manual audience with thousands of customers: how does the FE select across pages? | FE, RIS | Open. Grzegorz says the customers endpoint is paginated, so the FE must keep selected IDs across pages. Discussion continues on PCS-7239 (Grzegorz replied 11-09; content not in this thread). |

### Answered

| Question | Answer | By / date |
|---|---|---|
| Which smart audience filters are in MVO? | City/State or ZIP, and Age of Equipment. (Device type/model are "future".) | Aliaksandra, 11-10 |
| Need a name-uniqueness endpoint? | No. POST and PUT return a validation error if the name exists. | Stephan, 11-03 |
| Need a "filter options" endpoint? | No. Filters are dynamic: the user supplies values, and RIS takes plain-text fields (city = X, state = Y). | Stephan, 11-03 |
| Separate "preview count" endpoint? | No. The performance gain is insignificant; use the filtered customers endpoint and count the results. | Stephan, 11-03 |
| Separate customers endpoint for manual vs smart? | No. One endpoint serves both. A smart audience just has its filters stored in RIS so they can be re-applied (synced). | Stephan, 11-03 |
| Filter by device type / device model? | RIS can't support device type and has no concept of device model. Remove from the design and requirements. | Stephan, 11-03 |
| Can the FE parse the CSV and load all customers? | Not recommended. Some Pros have a few thousand customers, so older computers would slow down. | Stephan, 11-04 |

### Endpoints agreed so far

| Endpoint | Notes |
|---|---|
| `GET audiences` | List, with search by name |
| `POST audiences` | Create. Smart: filters (excluded IDs unconfirmed). Manual: selected customer IDs. Returns a validation error on a duplicate name. |
| `GET audience/{id}` | Load for editing |
| `PUT audience` | Update. Same name validation. |
| `DELETE audience/{id}` | Behaviour when a campaign uses it is undecided (open #1) |
| Sync audience | Re-applies the stored filters. Sync vs async undecided (open #2). |
| `GET customers` (existing) | Paginated, filterable by the user-supplied values. Serves both manual and smart audiences. |

### Conflicts to check against the epic summary

- The summary lists "device type" as an MVP filter. The thread says device type and model are not supported by RIS and should be removed; MVO filters are City/State or ZIP, and Age of Equipment.
- The summary says CSV upload is out of scope for MVP. The thread still debates how to build it, and PCS-7243 (CSV upload) exists under RES-3820.
