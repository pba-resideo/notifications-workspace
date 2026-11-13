# PT-790 – Pro PERKs: Connected Services Rewards

[Jira](https://resideo.atlassian.net/browse/PT-790) · Feature · PI 26-D · Status: Open

## Summary

The PERKS program rewards companies at the company level for spending and growing their hardware portfolio. There is no incentive for Pros tied to their software and services engagement. This feature adds a component to PERKS that rewards Pro companies for actions their technicians take in the Pro app. Earning and using points for commissioning and claiming devices is meant to drive service activations and offset Resideo's cloud costs.

Acceptance criteria:

1. Track the actions that earn installer points in the Pro app (claimed devices can already be tracked).
2. Pros can enroll in PERKS for Pro-IQ via the Pro app or Pro Portal, for their company in NA and EMEA.
3. Installers earn rewards for completed actions across device types (some actions don't apply to all devices):
   - Connect device to Wi-Fi (Resideo only gets paid for claimed devices that are online).
   - Invite the homeowner (claim the device) or commission the device (more claimed devices tied to RMR services).
   - Homeowner accepts Pro services, when the Pro is subscribed to a service.
4. Installers can view milestones and an activity log of their actions.
5. Pro Owners/Admins can view an activity log or report of installer points, the company's points and distance to the next milestone, and each team member's contribution.

Out of scope:

- Redeeming points (handled by PERKS' third-party vendor).
- Security and camera products.
- Rewards given to the installers themselves.
- Point values per action (defined by the PERKS team).

Data: track which Pros are enrolled and their points, and total points earned by action, company, region, etc.

Labels: `Consumer_Train`, `pi-26d-priority`

## Epics

- [PT-488](PT-488-proapp-installer-rewards/) – [ProApp] Installer Rewards
- PT-791 – [ProWeb] Service Professional: Company PERKs - Installer Rewards (no notes yet)

## Comment thread digest

Source: [Jira comments](https://resideo.atlassian.net/browse/PT-790). 1 comment. Last checked 2026-11-13.

A single comment from Anna Zahrbock (2025-03-05) with notes from a Pro Portal meeting with Adam and Ellen:

- Training incentives, e.g. show "Jim was your technician" on the customer account page.
- Business intelligence by crew, by individual, and success rates.
- Open question whether companies care about Wi-Fi. Wi-Fi has no record tied to a claim and couldn't be tracked on the T10. Possible alternative: whether the device was ever online, from the Wi-Fi success screen.
- Customer page > device table > "Installed by xxxx".
- Keep archived employees so their claim data isn't lost.
- Stephan noted the technician who claimed a device may already be known, so it might only need one more table field.

The detailed discussion is on the child epic, [PT-488](PT-488-proapp-installer-rewards/README.md).
