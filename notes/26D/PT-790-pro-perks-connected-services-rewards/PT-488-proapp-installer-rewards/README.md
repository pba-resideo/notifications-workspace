# PT-488 – [ProApp] Installer Rewards

[Jira](https://resideo.atlassian.net/browse/PT-488) · Epic · PI 26-D · Status: Implementing · Label: ProApp

## Summary

As a Pro, I can receive company-level PERKS rewards when my installers complete actions in the Resideo Pro app while installing products. This is an addition to the existing PERKS program (confirmed by Brad Pierson, 05-27). Points are finalized with Finance.

Reward-eligible actions (not all apply to all devices):

1. Connect device to Wi-Fi.
2. Claimed devices. Triggers: homeowner invite (basic install) or commission (full install).
3. Homeowner acceptance of services. Triggers: implicit consent (complete setup/OK) if the Pro has Engage, or acceptance of data sharing if the Pro has Analyze.

Devices in scope for launch: T5/T6, T9/T10/T10+, FocusPRO, ElitePRO, L1/L2/L5/L7. Later comments narrow this: T6/T6R are out (EMEA products; launch is NA only), and T9/T10/T10+ have no Wi-Fi flow in the Pro app, so the Wi-Fi API doesn't apply to them.

Sync: events show instantly in the Pro app and Pro Portal. Points sync bi-monthly in PERKS/Salesforce. A daily sync between Informatica and RIS was accepted.

Links: [Figma (Pro Rewards)](https://www.figma.com/design/NtgfZQTtngVUfvLLV0BmUu/Pro-Rewards?node-id=17777-5187&t=f8AA17gHpo8zR44x-1), [Architecture: Pro Installer Rewards](https://resideo.atlassian.net/wiki/spaces/ARCH/pages/5130846853/Pro+Installer+Rewards), [latest GXD (Connected Device Activity)](https://www.figma.com/design/NtgfZQTtngVUfvLLV0BmUu/Connected-Device-Activity?node-id=18573-9730&t=jFtLENC5HMWgu74T-0).

Related: sibling epic PT-791 (ProWeb installer rewards); RIS tickets RES-3442 and RES-3367 (the RIS side), PCS-6319, PCS-6545 and PCS-7039 (Wi-Fi endpoint contract); PT-1350.

Parent feature: [PT-790](../README.md).

## Comment thread digest

Source: [Jira comments](https://resideo.atlassian.net/browse/PT-488). 81 comments, 2026-04-06 to 2026-11-03. Last checked 2026-11-13.

General read: product and design are settled on the Pro app side, but the RIS and Informatica data contract is still unfinished. The app work depends on RIS delivering to QA by 18 November (2 December at the latest). The target release is 26 January 2027.

### Timeline

- **April to June, planning:** An architecture workshop was held 04-21/22. On 05-27 Anna Zahrbock noted considerations: show progress toward the next milestone, dependency on backend services (Maritz), the PERKS enrollment process, and linking out to the PERKS dashboard as a first step. Current enrollment (05-29): the company applies through pro.resideo.com or the PERKS site, goes to Salesforce as pending, and is manually reviewed. On 06-17 the platform teams said they had no bandwidth because of Mako and Truman billing work. On 06-30 the billing and subscription dependency was judged possibly unnecessary.
- **July, design:** GXD was updated for PT-488 and PT-791 (07-07). John Murphy published the architecture page (07-14). Dipti Gadhia assumed no platform work, with any RIS work handled by RIS (07-16). Anna shared copy for screens explaining each action (07-16).
- **07-30/31, Wi-Fi reward design:** Agreed on a new RIS endpoint. The Pro app calls it after Wi-Fi setup, passing the device certificate and other details. Owner, Admin, Advanced Technician and Technician can all trigger rewards, but not Guest. The open question on how installations are counted for percentages was answered in Slack.
- **08-03 to 08-05, sync and triggers:** Nitin Nankani asked for the Informatica to RIS sync frequency, and Anna accepted daily. Stephan Schmidt noted that pre-registration workflows have no homeowner "accept" step, so pre-reg Pros wouldn't earn points on acceptance. He also explained that RIS calls Informatica in real time per action and stores nothing, so action counts must come from Informatica. RIS has no control over sync frequency. Anna added the triggers to the description.
- **09-09:** T6/T6R dropped from scope.
- **10-05, RIS status:** RIS work is tracked in RES-3442 and RES-3367. Only the Connect-to-Wi-Fi endpoint spec exists. The rewards-data schema from Informatica was not available.
- **10-06 to 10-15, GXD change:** The app team found the GXD had changed substantially. "Technical Stats" became "Customer Connections", showing the weekly count of customer invites accepted. Three stat categories were mapped: Wi-Fi setup, claimed devices (a tally of devices, not customers), and total Pro-IQ services accepted (Engage plus Analyze). Stephan pointed out that Informatica tracks Wi-Fi connected, device claimed, consented to Engage, and consented to Analyze. RIS can't know the denominators for the first two. Anna and GXD agreed to split Engage and Analyze tracking. Dark-mode icons were added.
- **10-14, endpoint shape:** The draft Wi-Fi contract (`POST .../proAccounts/{partnerAccountId}/locations/{partnerDeviceLocationId}/devices/{deviceId}/wifi`) required a location ID the app doesn't have at that point. RIS agreed to drop that validation (PCS-7039). Stephan warned the RIS design differs a lot from the architecture page.
- **10-22:** T9/T10/T10+ have no Wi-Fi flow, so the API doesn't apply to them.
- **10-26 to 10-27, offline gap and RIS commitment:** A new API will capture Wi-Fi connection through the Pro app. Offline devices can't be captured, so Anna will note it on the epic and create a phase 2 epic to send the event once the device is online. Informatica dedupes rewards for repeated online connections. Stephan said the Wi-Fi endpoint is already built and goes to Prod, behind a feature flag, in the next release. RIS had marked the epic Uncommitted because Informatica (PERKS) gave no QA timeline. Phaneendar Reddy Baddam answered: PERKS has only sandbox (for dev and QA) and production, events land in `dbo.PRODATA_PARTNERDB_INSTALLER_EVENTS_` (unique on ACTIVITY + DEVICE_ID + USER_ID + PARTNER_ACCOUNT_ID), and points start being awarded with the end-of-February 2027 release, counting events from 2027.
- **11-02 to 11-03, timeline:** RIS targets QA by the end of Sprint 1 (18 Nov), with 2 Dec (end of Sprint 2) at the latest. App integration is Sprint 3-4, the QA drop is Sprint 4, and the target release is 26 January 2027. Alexandra Emmons is working on the visual design, with a follow-up on 11/13. Testers must share account identifiers with Audra Bartell so she can confirm Perks eligibility.

### Key facts

- RIS is calling Informatica in real time and keeping no copy, so earned counts and points must be fetched from Informatica.
- The Wi-Fi endpoint exists behind a feature flag. The endpoints for fetching earned rewards have no contract yet.
- Points awarded from the end-of-February 2027 PERKS release, for 2027 events only.
- Rewards launch in NA only.

### Open threads

- Contract for fetching earned counts and points from Informatica (blocks the home screen and detail views).
- Scoring logic, text and conditions for the Stats Detail screen are not finalized (action on Anna and Michelle Banh).
- Whether Analyze tracking can be hidden for Pros subscribed only to Engage (asked 10-14, no answer seen).
- Offline Wi-Fi capture is deferred to a phase 2 epic.
- The visual design/wireframe for Pro Perks was due around 11/13.
- RIS QA delivery date (18 Nov, or 2 Dec latest) is the main schedule risk. Rewards is one of Dave's top 5 priorities.
