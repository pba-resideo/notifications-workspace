# PT-1309 – [ProApp] Full Service Flow for Pro Portal Pre-Registered Devices

[Jira](https://resideo.atlassian.net/browse/PT-1309) · Epic · PI 26-D · Status: Ready for PI

## Summary

A device can be pre-registered in Pro Portal before it is used in the Pro app, but the Pro app flow wasn't accounted for when Pro Portal made updates. For both L-series devices and thermostats, Pros hit errors in the Pro app after pre-registering a device in Pro Portal and then connecting to it in the app to finish setup. This epic improves that flow and makes the handoff to the Pro app and FA app clearer and more reliable.

In scope:

- Update the Pro app flow after a device is pre-registered in Pro Portal.
- Drop the user into the full service flow (instead of choosing basic vs install).
- Show the customer account already pre-registered to the device.
- **Phase 1 (26D scope): thermostats only** (Denali, FocusPRO, T5/T6, T9/T10).

Out of scope (tracked elsewhere):

- Resideo Connect device card update for the homeowner if the device was never put online.
- Pro Portal pre-registration changes: "Send Invite Later" as the first option when adding a device, and clearer messaging about when the customer gets the email.

Success criteria: the Pro app flow is clearer after pre-registration in Pro Portal.

Risks and dependencies: implementation dependencies between Pro Portal, Pro app, FA app and backend.

References: [Figma (Add Device)](https://www.figma.com/design/TIYdtcSoW8OtO2Hxkp9eth/Add-Device?node-id=1292-13492&t=zVlCEbX41P3gvDOg-11), [PI 26-C Pro priorities](https://resideo.atlassian.net/wiki/spaces/CE/pages/4751917233/PI+26-C+Pro+priorities), [Feature Flags for Pro Portal EPICs](https://resideo.atlassian.net/wiki/spaces/TAB/pages/5349802030/Feature+Flags+for+Pro+Portal+EPIC+s), [PI 26 C Pro Dependencies / Risk Register](https://resideo.atlassian.net/wiki/spaces/CE/pages/5209653261/PI+26+C+Pro+Dependencies+Risk+Register).

Parent feature: [RIQ-202](../README.md).

## Comment thread digest

Source: [Jira comments](https://resideo.atlassian.net/browse/PT-1309). 19 comments, 2026-09-21 to 2026-11-03. Last checked 2026-11-13.

General read: the thread has settled on a design and a RIS dependency. The remaining open point is how Pros who start from the main screen get guided to the new flow.

### Timeline

- **09-21, Naveen Kumar K N:** Raised the L1/L2 problem. Pre-registering in Pro Portal generates a Device ID. The Pro app then shows "Device Already Registered" and says to commission, but the device still needs the Device ID set over BLE, Wi-Fi setup and cloud provisioning. Pros who skip that exit to the Basic flow and the device gets stuck in "Sync" in the FA app. He proposed that the `/info` response return the Device ID, and that this be discussed with RIS.
- **10-01 to 10-02, design debate:** Atul Kumar proposed (from Garett's suggestion) that installers start from Customer List > Add Device > Setup Products. The app then reads device state: Not Registered keeps the current flow, Pre-Registration goes to Full Service. Anna Zahrbock and Jaymeson Tucker objected that Pros will also start from the main screen. Atul said the cloud/RIS device-to-customer association can't support that today, so the main screen behaves as it does now. He suggested updating the Install-type text for "Send Later" Pros and covering the flow in Pro training. Anna wants to correct the existing flow, since that is what installers are used to, and took it to grooming.
- **10-13, Naveen:** Posted the device state matrix, with API statuses:

  | Device state | API status | Flow |
  |---|---|---|
  | Registered, same partner | `ALREADY_REGISTERED_TO_SAME_USER` | Basic Install |
  | Registered, different partner (different `locationId`) | `409 ALREADY_REGISTERED` | Basic Install |
  | Not registered | `UNREGISTERED` | Existing flow (Full Service or Basic Install) |
  | Pre-registration | `DEVICE_IS_IN_PREREGISTRATION` | New Full Service flow |

- **10-19 to 10-20, scope:** Atul raised [PCS-7093](https://resideo.atlassian.net/browse/PCS-7093) for the RIS change. The scope was narrowed to Phase 1 thermostats only, and Anna added the Out of Scope section. Michelle Banh posted the [Figma for the new Invite option](https://www.figma.com/design/5BInLJzDXir4FYTeO1RGeZ/Customer-Invite--Pre-Reg-?node-id=12995-8459).
- **10-26, capacity:** David Quam asked why this isn't O&M capacity, since it looks like a bug fix. Atul argued it is a new capability: the Pro Portal and Pro app pre-registration paths were never designed to connect. He proposed the title now on the epic.
- **10-29 to 11-03, RIS commitment:** Manikandan KV (RIS) agreed to do PCS-7093 in Sprint 1 of PI 26-D. The deploy plan is QA on 11/18/2026, Stage in the first week of December, and Prod in the second or third week of December.

### Key facts

- **RIS dependency:** [PCS-7093](https://resideo.atlassian.net/browse/PCS-7093) makes `/info` return the Device ID generated at pre-registration. Pro app needs it to set the ID on the device over BLE before provisioning.
- **Scope:** Phase 1 covers thermostats only. The L1/L2 issue that started the thread is not in the 26D scope.
- **Dates:** QA 11/18, Stage early December, Prod mid-to-late December. The epic's commitment depends on the QA date.

### Open threads

- Main-screen entry: Anna and Jaymeson want that flow fixed. The agreed approach adds a Customer List entry path and leaves the main screen unchanged, with updated text and training. This was never explicitly closed.
- Whether L1/L2 devices get a follow-up epic or are folded into the thermostat work. Atul scheduled a call to combine the thermostat flows into one 26D epic (related PT-233).
