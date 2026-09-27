# FILE: spec/supplements/Sup-003-BMS-Infrastructure-Contract.md
# Sup-003 — BMS Infrastructure Contract
# Status: PROPOSAL (2026-08-21)
# License: CC-BY 4.0
# Scope: Define the normative BMS infrastructure contract for robot
#        operations in healthcare buildings. Protocol-agnostic contract
#        + informative mappings to BACnet/KNX/OPC UA.
# NOTE:  Scope proposal. Phase 2 normative text produced in sup-003.md.

## 1. Purpose

Robot operations in healthcare buildings require interaction with
Building Management Systems (BMS) that control physical infrastructure:
doors, elevators, ventilation, and zone access. Currently, robot vendors
integrate with BMS through custom, vendor-specific methods that bypass
BMS oversight, creating safety risks and compliance gaps.

This supplement proposes a protocol-agnostic BMS infrastructure contract
that defines the normative request/response schemas for robot-BMS
interactions, with informative mappings to existing BMS protocols
(BACnet, KNX, OPC UA). The contract follows the same pattern as
Part 4 (Availability Provider Contract): open specification, pluggable
implementations per BMS vendor.

## 2. Precondition — VDA 5050 Version Pin

Before Sup-003 can be drafted as normative text, Part 5 §2 must pin
the VDA 5050 version. Proposed Correction Proposal:

- **CP-target:** Part 5 §2 — pin VDA 5050 version 2.1 as the profiled
  version, with change rule for future versions.
- **Rationale:** Sup-003 references VDA 5050 node/sequence semantics
  for robot navigation. Unpinned version = moving target.

This CP is a separate commit and is resolved before Phase 2 of Sup-003.

## 3. Contract Elements — Proposed Scope

Four contract elements are proposed. Each is a normative request/response
schema; protocol mappings are informative.

### 3.1. Door Access Request

Robot requests door access before entering a zone. BMS authorizes or
denies based on zone policy, time of day, and security level.

| Field | Type | Normative? | Description |
|-------|------|-----------|-------------|
| `request_id` | UUID | Yes | Correlates request to response |
| `agent_id` | UUID | Yes | Robot requesting access |
| `task_id` | UUID | Yes | Task authorizing the movement |
| `door_id` | string | Yes | BMS door identifier |
| `zone` | string | Yes | Ward/zone from Part 3 Location model |
| `access_type` | enum | Yes | `normal`, `emergency`, `restricted` |
| `time_window` | TimeWindow | Yes | Requested access period (reuse Part 3) |
| `audit_ref` | UUID | Yes | Links to orchestrator audit trail |
| `response_deadline` | duration | Yes | Max wait time (default: 2s) |

BMS response includes `authorization` (enum: `granted`, `denied`, `pending`),
`reason` (string, required on denial), and `valid_until` (datetime).

**Informative mapping:** BACnet `AccessDoor` object, KNX `Door Controller`
group objects. Mapping document shows how to translate the normative schema
to protocol-specific commands.

### 3.2. Elevator Dispatch

Robot requests elevator access with direction, priority, and boarding
status. BMS coordinates with human traffic and emergency operations.

| Field | Type | Normative? | Description |
|-------|------|-----------|-------------|
| `request_id` | UUID | Yes | Correlates request to response |
| `agent_id` | UUID | Yes | Robot requesting elevator |
| `task_id` | UUID | Yes | Task authorizing the movement |
| `elevator_id` | string | Yes | BMS elevator identifier |
| `floor_from` | string | Yes | Current floor (VDA 5050 building/floor) |
| `floor_to` | string | Yes | Target floor |
| `direction` | enum | Yes | `up`, `down`, `any` |
| `priority` | enum | Yes | `routine`, `urgent`, `emergency` |
| `boarding_status` | enum | Yes | `approaching`, `at_door`, `boarding`, `on_board`, `exiting` |
| `audit_ref` | UUID | Yes | Links to orchestrator audit trail |

BMS response includes `dispatch_status` (enum: `dispatched`, `queued`,
`denied`), `estimated_arrival` (datetime), and `elevator_car_id` (string).

**Note:** Elevator dispatch is NOT in standard VDA 5050. This is a
hospital-specific extension. The normative schema defines the contract;
the VDA 5050 roadmap is checked (see §6.1) to see if a future version
covers this, which would shrink our scope.

**Informative mapping:** OPC UA elevator companion spec (if exists),
BACnet `ElevatorGroup` object.

### 3.3. Zone Authorization

Robot requests authorization to operate in a specific zone. BMS
authorizes based on building security level, operational status, and
time-based policies.

| Field | Type | Normative? | Description |
|-------|------|-----------|-------------|
| `request_id` | UUID | Yes | Correlates request to response |
| `agent_id` | UUID | Yes | Robot requesting zone access |
| `task_id` | UUID | Yes | Task authorizing the operation |
| `zone` | string | Yes | Ward/zone from Part 3 Location model |
| `zone_type` | enum | Yes | `ward`, `corridor`, `restricted`, `maintenance`, `clinical` |
| `operation_type` | enum | Yes | `transit`, `stationary`, `delivery`, `cleaning` |
| `duration` | duration | Yes | Requested authorization period |
| `audit_ref` | UUID | Yes | Links to orchestrator audit trail |

BMS response includes `authorization` (enum: `granted`, `denied`,
`conditional`), `conditions` (array of strings, e.g., "max_speed_0.5m_s",
"no_stopping_allowed"), and `valid_until` (datetime).

### 3.4. Emergency Override

BMS issues emergency command to all robots. This is a BMS-initiated
command, not a robot request.

| Field | Type | Normative? | Description |
|-------|------|-----------|-------------|
| `command_id` | UUID | Yes | Unique emergency command identifier |
| `emergency_type` | enum | Yes | `fire_alarm`, `lockdown`, `evacuation`, `general_emergency` |
| `scope` | enum | Yes | `all_zones`, `zone_specific`, `floor_specific` |
| `zone` | string | No | Required if scope is `zone_specific` |
| `action` | enum | Yes | `suspend_all`, `suspend_non_essential`, `clear_path`, `return_to_base` |
| `timestamp` | datetime | Yes | Command issuance time |

Robot response includes `agent_id`, `acknowledged` (boolean),
`current_zone`, `action_taken`, and `acknowledged_at`.

**Critical requirement:** BMS maintains absolute override authority.
See §4.

## 4. Safety Clause — Normative

The following clause SHALL appear verbatim in the normative specification:

> Building safety systems remain authoritative at all times. This
> supplement never overrides fire, life-safety or access-control
> functions. On loss of BMS authorization the robot SHALL fail
> safe (stop/yield).

Additional safety requirements:
- Emergency override response time: BMS command SHALL be acknowledged
  by all robots within 1 second.
- Loss of BMS communication: Robot SHALL stop within 3 seconds and
  transition to ERROR state (VDA 5050 state update).
- BMS authorization expiry: Robot SHALL re-request authorization before
  `valid_until` and SHALL stop if re-request is denied.

## 5. Conformance

### 5.1. Test ID Reservation

Test ID series `BMS-xx` is reserved in the conformance test registry
schema (Part 2). No tests are written in this phase. Reservation ensures
test IDs are available when Phase 2 produces normative text.

Proposed test IDs:
| ID | Contract Element | Level |
|----|-----------------|-------|
| BMS-01 | Door access request/response | L1 |
| BMS-02 | Door access denial handling | L1 |
| BMS-03 | Elevator dispatch | L2 |
| BMS-04 | Elevator boarding status | L2 |
| BMS-05 | Zone authorization | L2 |
| BMS-06 | Zone authorization expiry | L2 |
| BMS-07 | Emergency override — fire alarm | L1 |
| BMS-08 | Emergency override — lockdown | L1 |
| BMS-09 | Loss of BMS communication — fail safe | L1 |
| BMS-10 | Audit correlation — all elements | L3 |

### 5.2. Conformance Levels

Follows existing L1–L3 model (Part 2). Does NOT introduce new vocabulary
(bronze/silver/gold rejected — inconsistent with Part 2).

| Level | Requirement |
|-------|-------------|
| L1 | Door access + emergency override. Minimum for safe robot operation. |
| L2 | L1 + elevator dispatch + zone authorization. Full production readiness. |
| L3 | L2 + audit correlation + multi-site federation. Regional operations. |

## 6. Out of Scope

The following are explicitly NOT included in Sup-003:

1. **BMS adapter implementations** (BACnet/KNX/OPC UA translators):
   These are open reference implementations delivered in a separate
   adapter working package. Sup-003 defines the contract; the adapters
   implement it.

2. **Vendor-specific BMS details:** Siemens Desigo CC, Johnson Controls
   Metasys, and Honeywell specifics are excluded. The contract is
   protocol-agnostic.

3. **IT-side allocation logic:** Cost models, collective agreement rules,
   and allocation decision logic remain in the closed management system repository.
   Sup-003 only defines the OT-side contract.

4. **VDA 5050 modifications:** This supplement does not modify standard
   VDA 5050 messages. Extensions live on `rocom/v0/` topics (see Part 5).

5. **BMS sensor data:** Temperature, humidity, occupancy sensor data
   from BMS is not part of this contract. Those belong in a potential
   sensor data governance supplement.

## 7. Relationship to Existing Specification

| Reference | Relationship |
|-----------|-------------|
| Part 1 §4 (IT/OT Zone Model) | BMS is in OT Zone; contract defines OT boundary |
| Part 1 §5 (Plane 1 — BMS) | This supplement implements Plane 1 |
| Part 2 (Conformance) | L1–L3 levels, BMS-xx test reservation |
| Part 3 (Information Model) | Reuses `Location` (ward_or_zone), `TimeWindow` |
| Part 4 (Service Contracts) | Same contract pattern: normative schema + events |
| Part 5 (Transport Profile) | VDA 5050 binding; `rocom/v0/` extension topics |
| Sup-001 (Orchestrator Service Interface) | IT-side contract; Sup-003 is OT-side counterpart |

## 8. Protocol-Agnostic Design — IHE Approach

Following the IHE (Integrating the Healthcare Enterprise) pattern:
the normative text defines the data model and interactions; informative
appendices show how to map to specific protocols. This means:

- The contract schema (request/response fields) is normative.
- BACnet object mappings are informative (Appendix A).
- KNX group address mappings are informative (Appendix B).
- OPC UA information model mappings are informative (Appendix C).

Implementers choose the protocol matching their BMS platform. The
reference adapters (separate WP) demonstrate each mapping.

## 9. Next Steps

1. This scope document is commited as PROPOSAL per CONTRIBUTING.md process.
2. Egil reviews and approves/rejects/modifies the scope.
3. Upon approval: Phase 2 produces normative spec text (no schema files
   in public repo — YAML schemas follow in Phase 3).
4. Research deliverables (§6) are completed and reported with sources.

## Appendix: Research Deliverables

### R1 — VDA 5050 / VDMA Roadmap

Check whether VDA 5050 future versions cover elevator dispatch or door
access semantics. If they do, Sup-003 scope shrinks — we reference the
standard instead of defining our own. Success criterion: find or don't
find the coverage.

### R2 — Part 3 CostModel — Tariff Leakage Audit

Review Part 3 `cost_model` fields for tariff/collective agreement
semantics that leak closed-source rules into the open standard.
Specifically: `overtime_multiplier` and `constraints` (collective
agreement rules) may need renaming or removal from the open schema.

### R3 — Sup-001 Endpoint Reconciliation

Sup-001 table says 13 standard endpoints. The Postman collection has
17 requests. The OpenAPI spec has 16 paths (PATCH /tasks/{id} covers
both update and cancel). Reconcile the numbers and report Sup-001's
actual approval status.

| Source | Count | Notes |
|--------|-------|-------|
| Postman collection | 17 | Includes "Cancel Task" as separate request |
| OpenAPI (management-system-api.yaml) | 16 paths | PATCH /tasks/{id} handles update + cancel |
| Sup-001 table | 13 standard + 3 product-specific = 16 | Excludes proposals from standard |

The discrepancy: Postman's "Cancel Task" is a PATCH /tasks/{id} with
`status: cancelled` — not a distinct endpoint. Sup-001's count of 13
standard endpoints is correct if proposals (3) are excluded from the
standard. The true count is **16 total endpoints** (13 standard + 3
product-specific).
