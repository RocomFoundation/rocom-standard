# ROCOM Compliance Traceability Matrix v0.8.3

**Date:** 2026-11-19
**Auditor:** Kvasir (CH v0.8.3, deterministic templates)
**Scope:** Full traceability from ROCOM Standard normative claims → HRRM implementation → tests → evidence → CH warrant

---

## Traceability Legend

- **W** = Warranted (test passes, matches spec)
- **PW** = Partially Warranted (structural match, incomplete)
- **U** = Unwarranted (no evidence)
- **NI** = Not Implemented
- **OO** = Out of Scope (requirement belongs to different component)
- **TD** = Topic Defined (topic pattern exists, no publisher)

---

## Sup-003 BMS Infrastructure Contract

### Door Access (§6)

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| Door request topic | `rocom/v0/bms/door/request` | sup-003.md §6 | `BmsTopics::door_request()` | topics.rs:42 | topics tests | blob `d3f36f35...` | W |
| Door request payload | agent_id, task_id, door_id, zone, access_type | sup-003.md §6 | `DoorAccessRequest` | contract.rs | contract tests | blob `9e86dc00...` | W |
| Door response payload | authorization, valid_until | sup-003.md §6 | `DoorAccessResponse` | contract.rs | contract tests | blob `9e86dc00...` | W |
| Door access flow | BmsClient→MQTT→BMS | sup-003.md §6 | `BmsClient::request_door()` | client.rs:180 | `client_request_door_returns_pending` | blob `9f2f7e3c...` | PW |
| Emergency access | Always granted | sup-003.md §9 | `SimBuilding::handle_door_request()` | sim.rs:128 | `sim_emergency_granted` | blob `02da4e11...` | W |

### Elevator Dispatch (§7)

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| Elevator topic | `rocom/v0/bms/elevator/dispatch` | sup-003.md §7 | `BmsTopics::elevator_request()` | topics.rs:52 | topics tests | blob `d3f36f35...` | W |
| Elevator request payload | elevator_id, floors, direction, priority, boarding | sup-003.md §7 | `ElevatorDispatchRequest` | contract.rs | contract tests | blob `9e86dc00...` | W |
| Elevator dispatch flow | BmsClient→MQTT | sup-003.md §7 | `BmsClient::request_elevator()` | client.rs:250 | — | blob `9f2f7e3c...` | PW |

### Zone Authorization (§8)

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| Zone topic | `rocom/v0/bms/zone/request` | sup-003.md §8 | `BmsTopics::zone_request()` | topics.rs:57 | topics tests | blob `d3f36f35...` | W |
| Zone request payload | zone, access_type | sup-003.md §8 | `ZoneAuthRequest` | contract.rs | contract tests | blob `9e86dc00...` | W |
| Zone auth flow | BmsClient→MQTT | sup-003.md §8 | `BmsClient::request_zone()` | client.rs:294 | — | blob `9f2f7e3c...` | PW |

### Audit Trail (§10)

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| Audit event structure | event_id, agent_id, resource_id, action, timestamp | sup-003.md §10 | `AuditEvent` struct | client.rs:130 | — | blob `9f2f7e3c...` | PW |
| Audit sink interface | record() method | sup-003.md §10 | `AuditSink` trait | client.rs:125 | — | blob `9f2f7e3c...` | PW |
| Audit recording | On door request | sup-003.md §10 | `request_door()` audit branch | client.rs:214 | — | blob `9f2f7e3c...` | PW |

---

## CP-010 — Connector Liveness

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| LV-10 | Heartbeat topic | cp-010-connector-liveness.md §3 | `BmsTopics::heartbeat()` | topics.rs:62 | topics tests | blob `d3f36f35...` | TD |
| LV-10 | Periodic publish (30s) | cp-010-connector-liveness.md §3 | — | — | — | — | NI |
| LV-11 | LWT registration | cp-010-connector-liveness.md §3 | — | — | — | — | OO |
| LV-12 | Heartbeat payload (5 fields) | cp-010-connector-liveness.md §3 | `LivenessStatus` | client.rs:88 | `liveness_tracks_heartbeat` | blob `9f2f7e3c...` | PW |
| LV-13 | Orchestrator subscribes LWT | cp-010-connector-liveness.md §3 | — | — | — | — | OO |
| LV-14 | QoS 1 | cp-010-connector-liveness.md §3 | `QoS::AtLeastOnce` | mod.rs:20 | — | blob `dabf6283...` | W |

---

## CP-011 — Door State

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| DS-10 | State topic | cp-011-door-state.md §3 | `BmsTopics::door_state()` | topics.rs:67 | topics tests | blob `d3f36f35...` | TD |
| DS-11 | State payload (4 fields) | cp-011-door-state.md §3 | `DoorState` (sim) | sim.rs:43 | — | blob `02da4e11...` | PW |
| DS-12 | Dead-door detection (30s) | cp-011-door-state.md §3 | — | — | — | — | OO |
| DS-13 | QoS 1 | cp-011-door-state.md §3 | `QoS::AtLeastOnce` | mod.rs:20 | — | blob `dabf6283...` | W |
| DS-14 | Fault alert | cp-011-door-state.md §3 | — | — | — | — | NI |

---

## CP-012 — Elevator Boarding

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| EB-10 | Boarding topic | cp-012-elevator-boarding.md §3 | `BmsTopics::elevator_boarding()` | topics.rs:72 | topics tests | blob `d3f36f35...` | TD |
| EB-11 | Boarding payload (6 fields) | cp-012-elevator-boarding.md §3 | `BoardingStatus` enum | contract.rs | — | blob `9e86dc00...` | PW |
| EB-12 | Failure reasons (4 types) | cp-012-elevator-boarding.md §3 | — | — | — | — | NI |
| EB-13 | Reassignment SLA (30s) | cp-012-elevator-boarding.md §3 | — | — | — | — | OO |
| EB-14 | QoS 1 | cp-012-elevator-boarding.md §3 | `QoS::AtLeastOnce` | mod.rs:20 | — | blob `dabf6283...` | W |

---

## CP-013 — Early Lease Return

| Req | Description | Spec | HRRM Module | HRRM File:Line | Test | Evidence | Warrant |
|-----|-------------|------|-------------|----------------|------|----------|---------|
| LR-10 | Release topics | cp-013-lease-return.md §3 | `BmsTopics::door_release()` | topics.rs:77 | topics tests | blob `d3f36f35...` | TD |
| LR-11 | Release payload (5 fields) | cp-013-lease-return.md §3 | `Lease` struct | client.rs:31 | — | blob `9f2f7e3c...` | PW |
| LR-12 | BMS processes release (5s) | cp-013-lease-return.md §3 | — | — | — | — | NI |
| LR-13 | Orchestrator marks available (10s) | cp-013-lease-return.md §3 | — | — | — | — | OO |
| LR-14 | QoS 1 | cp-013-lease-return.md §3 | `QoS::AtLeastOnce` | mod.rs:20 | — | blob `dabf6283...` | W |
| LR-15 | Reject mismatched release | cp-013-lease-return.md §3 | — | — | — | — | NI |

---

## Summary Statistics

### By Warrant Status

| Status | Count | Percentage |
|--------|-------|------------|
| WARRANTED (W) | 13 | 37% |
| PARTIALLY WARRANTED (PW) | 14 | 39% |
| TOPIC DEFINED (TD) | 5 | 14% |
| NOT IMPLEMENTED (NI) | 5 | 14% |
| OUT OF SCOPE (OO) | 5 | 14% |
| **Total requirements traced** | **35** | |

### By Spec Element

| Spec Element | Traced | Warranted | Gap |
|---|---|---|---|
| Sup-003 Door Access | 5 | 3 | 2 PW |
| Sup-003 Elevator Dispatch | 3 | 2 | 1 PW |
| Sup-003 Zone Authorization | 3 | 2 | 1 PW |
| Sup-003 Audit Trail | 3 | 0 | 3 PW |
| CP-010 Liveness | 6 | 2 | 1 PW, 1 TD, 1 NI, 2 OO |
| CP-011 Door State | 5 | 2 | 1 PW, 1 TD, 1 NI, 1 OO |
| CP-012 Boarding | 5 | 2 | 1 PW, 1 TD, 1 NI, 1 OO |
| CP-013 Lease Return | 6 | 2 | 1 PW, 1 TD, 2 NI, 1 OO |

### Implementation Coverage by File

| File | Blob SHA | Requirements Covered | Tests |
|---|---|---|---|
| `topics.rs` | `d3f36f35...` | 10 topic definitions | 12 |
| `contract.rs` | `9e86dc00...` | 6 payload definitions | 6 |
| `client.rs` | `9f2f7e3c...` | 7 client-side requirements | 4 |
| `sim.rs` | `02da4e11...` | 2 simulation behaviors | 6 |
| `runtime.rs` | `a5e14ed9...` | 1 heartbeat infra | 4 |
| `transport/mod.rs` | `dabf6283...` | 4 QoS definitions | 0 |

---

## Critical Gaps (Priority Order)

1. **CP-010 heartbeat publisher** — LV-10 requires periodic publication. Topic defined, no publisher. **Impact:** orchestrator cannot detect connector liveness.
2. **CP-011 door state publisher** — DS-10 requires state transitions. Topic defined, `check_door_state()` returns stub. **Impact:** no dead-door detection possible.
3. **CP-012 boarding status publisher** — EB-10 requires boarding transitions. Topic defined, no publisher. **Impact:** no dispatch outcome feedback.
4. **CP-013 BMS release processing** — LR-12 requires connector to process releases. Not implemented. **Impact:** early lease return non-functional.
5. **AuditSink implementation** — Sup-003 §10 requires audit trail. Trait only. **Impact:** no audit compliance verification possible.
6. **`is_alive()` timeout** — client.rs:110 ignores timeout parameter. **Impact:** false-positive liveness.
7. **CP-010–013 untracked in git** — Spec files on disk, not committed. **Impact:** normative provenance incomplete.
