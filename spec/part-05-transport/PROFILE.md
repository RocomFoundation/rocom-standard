# FILE: specs/rocom-profile/PROFILE.md
# Rocom Healthcare Profile — Normative Specification v0.1

## 1. Scope

This profile defines the requirements a robot system MUST satisfy to be
considered Rocom-conformant. It extends the VDA 5050 standard by adding
healthcare-specific capability declarations, compliance event reporting,
and chain-of-custody tracking on `rocom/v0/` extension topics.

Rocom extensions use the separate `rocom/v0/` namespace and never
modify standard VDA 5050 messages.

## 1.1 Normative References

This profile is based on **VDA 5050 version 2.1.0** (VDA 5050-2,
published January 2025). All references to "VDA 5050" in this profile
refer to this specific version unless explicitly stated otherwise.

VDA 5050 3.0 was published in April 2026 and introduces zones, movement
rules, and areas requiring explicit permission. Rocom has reviewed these
changes. Version 2.1.0 is retained as the normative baseline because it
provides sufficient coverage for current deployments and is widely
implemented. Overlap with 3.0 features (notably zone semantics) is
addressed through Rocom's own zone model (Part 1) and the Healthcare
profile, rather than by depending on a newer VDA release.

The VDA 5050 specification and MQTT topic structure are publicly available:
https://github.com/VDA5050/VDA5050

Topic namespace: `vda5050/`. Messages follow the VDA 5050 factsheet
schema. Cancellation uses `instantActions` — the orchestrator publishes
`{"action": "cancelOrder", "order": {"serialNumber": "..."}}` to
`vda5050/instantActions/<serialNumber>`. Rocom extensions use the
separate `rocom/v0/` namespace and never modify standard VDA 5050
messages.

## 2. Conformance Levels

Levels follow Part 2 (L1 = Pilot, L2 = Single Site, L3 = Multi-Site).
The Healthcare profile adds domain-specific requirements at every level.

### Level 1 — VDA 5050 Baseline
The system SHALL:
- [P-2.1.1] Publish a valid factsheet on `vda5050/factsheet` on connection.
- [P-2.1.2] Publish periodic state updates on `vda5050/state/<serialNumber>`.
- [P-2.1.3] Accept orders on `vda5050/order/<serialNumber>` and execute node sequences.
- [P-2.1.4] Publish connection state on `vda5050/connection/<serialNumber>`.
- [P-2.1.5] Support order cancellation via `instantActions` with `cancelOrder`
  as defined in VDA 5050 2.1 (topic: `vda5050/instantActions/<serialNumber>`).

### Level 2 — Rocom Core
The system SHALL additionally:
- [P-2.2.1] Publish compliance events on `rocom/v0/compliance/event` on every zone transition.
- [P-2.2.2] Each compliance event MUST include `auditCorrelationId` referencing the orchestrator AuditEvent.
- [P-2.2.3] Declare Rocom-profile capabilities on `rocom/v0/capability/declare` using keys from the capability registry.
- [P-2.2.4] Report `complianceStatus` as `passed`, `failed`, or `exception` for each zone transition.

### Level 3 — Multi-Site Transport
The system SHALL additionally:
- [P-2.3.5] Support federated connection state: publish `rocom/v0/connection/federated`
  with cross-site routing information when operating across multiple deployment sites.

### Healthcare Profile (any level)
When the Healthcare profile is declared, the system SHALL additionally:
- [P-2.3.1] Publish chain-of-custody events on `rocom/v0/chainOfCustody/event` for tasks requiring chain-of-custody (`chainOfCustody: true` in capability params).
- [P-2.3.2] Enforce restricted-zone access: robot MUST publish a `restricted_zone_check` compliance event before entering a restricted zone, and SHALL NOT proceed if `complianceStatus` is `failed`.
- [P-2.3.3] Ensure chain-of-custody event completeness: every `picked_up` action MUST have a corresponding `delivered` or `handed_off` action within the task lifetime.
- [P-2.3.4] Capability declarations MUST match a key defined in `capability-registry.yaml`. Undeclared keys SHALL cause a conformance test failure.

## 3. Capability Declaration

Every conformant robot SHALL publish a capability declaration containing:
- `key`: one of the keys defined in the capability registry
- `level`: `basic`, `advanced`, or `certified`
- `certified`: boolean indicating whether the capability has passed certification testing

## 4. Audit Correlation

Every compliance and chain-of-custody event MUST carry an `auditCorrelationId`
that references the corresponding orchestrator `AuditEvent.eventId`. This ensures
the end-to-end audit trail from allocation decision through physical execution.

## 5. Restricted Zone Enforcement

When a task requires capability with `restricted_zones: true`:
1. The orchestrator SHALL include zone restriction constraints in the allocation proposal.
2. The gateway SHALL verify zone access before dispatching the order.
3. The robot SHALL publish a `restricted_zone_check` compliance event upon zone boundary crossing.
4. If access is denied, the robot SHALL NOT enter and SHALL transition to ERROR state.

## 6. Error Handling

- [P-6.1] A robot detecting a compliance failure SHALL publish a state update with `state: ERROR` and the corresponding compliance event with `complianceStatus: failed`.
- [P-6.2] The gateway SHALL notify the orchestrator of the compliance failure via the `/agents/{agentId}` PATCH endpoint.
- [P-6.3] The orchestrator SHALL record the failure in the audit trail and mark the task as `cancelled`.
