# ROCOM-HRRM Implementation — CH Audit Report v0.8.3

**Date:** 2026-11-19
**Auditor:** Kvasir (CH v0.8.3, deterministic templates)
**Scope:** ROCOM-HRRM `rocom-connectors` crate — BMS connector implementation
**Commit:** `a27635cbaee1796ec66f0d21cdd68305e502179e` (main)
**Tests:** 32 passed, 0 failed (`cargo test --package rocom-connectors`)

---

## Executive Summary

The `rocom-connectors` crate implements the BMS infrastructure contract (Sup-003) with CP-010–013 extensions. The implementation covers all 4 contract elements (door, elevator, zone, emergency) and provides liveness tracking, lease management, and audit logging. Test coverage is functional but incomplete: fault injection exists but several CP requirements lack test coverage.

**Overall warrant status:** PARTIALLY WARRANTED — implementation matches specification structurally, but test coverage gaps prevent full warrant.

### Key Findings

| # | Severity | Area | Finding |
|---|----------|------|---------|
| 1 | High | CP-010 | Liveness: heartbeat topic generated in `topics.rs` but no periodic heartbeat publisher in `runtime.rs`. LWT not implemented (MQTT client-level feature, not in crate scope). |
| 2 | High | CP-011 | Door state: topic pattern exists (`door_state()`) but no state transition publisher. `check_door_state()` returns `"unknown"` stub. |
| 3 | High | CP-012 | Elevator boarding: topic pattern exists but no boarding status publisher. |
| 4 | Medium | CP-013 | Early lease return: `release_door()` implemented in `BmsClient`, but no release topic publisher for BMS connector side. |
| 5 | Medium | Liveness | `is_alive()` check in `client.rs:110-117` is simplified — only checks `!last.is_empty()`, not actual timeout. |
| 6 | Medium | Audit | `AuditSink` is a trait only — no implementation in this crate. Dependency on `rocom-hrrm-core` or external. |
| 7 | Low | Client | `request_door()` returns `Authorization::Pending` immediately — actual response handled by message loop (not tested). |
| 8 | Low | Simulation | `SimBuilding` grants all zone requests regardless of zone configuration — no zone access control logic. |
| 9 | Informational | Transport | `MqttTransport` trait abstracts MQTT — `mqtt.rs` implementation uses rumqttc. |
| 10 | Informational | Topics | All topic patterns follow `rocom/v0/bms/{resource}/{action}/{id}` convention consistently. |

---

## Spec-to-Implementation Traceability

### Sup-003 Contract Elements

| Contract Element | Spec Reference | Implementation | Test | Status |
|---|---|---|---|---|
| Door Access Request | Sup-003 §6 | `BmsClient::request_door()` (`client.rs:180`) | `client_request_door_returns_pending` | IMPLEMENTED (stub) |
| Door Access Response | Sup-003 §6 | `DoorAccessResponse` struct (`contract.rs`) | — in sim tests | DEFINED |
| Elevator Dispatch | Sup-003 §7 | `BmsClient::request_elevator()` (`client.rs:250`) | — | IMPLEMENTED (stub) |
| Elevator Response | Sup-003 §7 | `ElevatorDispatchResponse` (`contract.rs`) | — in sim tests | DEFINED |
| Zone Authorization | Sup-003 §8 | `BmsClient::request_zone()` (`client.rs:294`) | — | IMPLEMENTED (stub) |
| Emergency Override | Sup-003 §9 | `SimBuilding::handle_door_request()` emergency branch (`sim.rs:128`) | `sim_emergency_granted` | IMPLEMENTED |
| Audit Trail | Sup-003 §10 | `AuditSink` trait + `AuditEvent` struct (`client.rs:125-140`) | — | PARTIAL (trait only) |

### CP-010 — Connector Liveness

| Requirement | Spec | Implementation | Test | Status |
|---|---|---|---|---|
| LV-10: Heartbeat topic | `rocom/v0/bms/liveness/heartbeat/{id}` | `BmsTopics::heartbeat()` (`topics.rs`) | — | TOPIC DEFINED |
| LV-10: Periodic publish | Every 30 s | Not in `runtime.rs` | — | NOT IMPLEMENTED |
| LV-11: LWT registration | At connection | Not in crate (MQTT client feature) | — | OUT OF SCOPE |
| LV-12: Heartbeat payload | 5 fields | `LivenessStatus` struct (`client.rs:88`) | — | PARTIAL (3/5 fields) |
| LV-13: Orchestrator subscribes | 10 s response | Not in this crate | — | OUT OF SCOPE |
| LV-14: QoS 1 | At least once | `QoS` enum in transport (`mod.rs:18`) | — | DEFINED |

### CP-011 — Door State

| Requirement | Spec | Implementation | Test | Status |
|---|---|---|---|---|
| DS-10: State topic | `rocom/v0/bms/door/state/{id}` | `BmsTopics::door_state()` (`topics.rs`) | — | TOPIC DEFINED |
| DS-11: State payload | 4 fields | `DoorState` in sim (`sim.rs:43-46`) | — | PARTIAL (3 fields, no trigger) |
| DS-12: Dead-door detection | 30 s correlation | Not implemented | — | NOT IMPLEMENTED |
| DS-13: QoS 1 | At least once | Transport layer | — | DEFINED |
| DS-14: Fault alert | Alert + unavailable | `DoorState.fault` not in sim | — | NOT IMPLEMENTED |

### CP-012 — Elevator Boarding

| Requirement | Spec | Implementation | Test | Status |
|---|---|---|---|---|
| EB-10: Boarding topic | `rocom/v0/bms/elevator/boarding/{id}` | `BmsTopics::elevator_boarding()` (`topics.rs`) | — | TOPIC DEFINED |
| EB-11: Boarding payload | 6 fields | `BoardingStatus` enum (`contract.rs`) | — | PARTIAL |
| EB-12: Failure reasons | 4 reasons | Not in `contract.rs` | — | NOT IMPLEMENTED |
| EB-13: Reassignment SLA | 30 s | Not in this crate | — | OUT OF SCOPE |
| EB-14: QoS 1 | At least once | Transport layer | — | DEFINED |

### CP-013 — Early Lease Return

| Requirement | Spec | Implementation | Test | Status |
|---|---|---|---|---|
| LR-10: Release topic | `rocom/v0/bms/{resource}/release/{id}` | `BmsTopics::door_release()` (`topics.rs`) | — | TOPIC DEFINED |
| LR-11: Release payload | 5 fields | `Lease` struct (`client.rs:31-37`) | — | PARTIAL (4/5 fields) |
| LR-12: BMS processes release | 5 s | Not in connector side | — | NOT IMPLEMENTED |
| LR-13: Orchestrator marks available | 10 s | Not in this crate | — | OUT OF SCOPE |
| LR-14: QoS 1 | At least once | Transport layer | — | DEFINED |
| LR-15: Reject mismatched release | Error | Not implemented | — | NOT IMPLEMENTED |

---

## Test Coverage Analysis

### Test Inventory (32 tests)

| Module | Tests | Coverage |
|---|---|---|
| `topics.rs` | 12 | Topic pattern generation, all paths covered |
| `contract.rs` | 6 | Serialization/deserialization, enum variants |
| `runtime.rs` | 4 | Heartbeat loop, config |
| `client.rs` | 4 | Lease table, liveness, door request |
| `sim.rs` | 6 | Door/elevator/zone handling, fault injection |

### Coverage Gaps

1. **No integration tests** — all tests are unit-level. No end-to-end MQTT flow tested.
2. **Elevator dispatch not tested** — `request_elevator()` has no dedicated test.
3. **Zone authorization not tested** — `request_zone()` has no dedicated test in `client.rs`.
4. **AuditSink not tested** — trait only, no mock implementation exercised.
5. **LWT not tested** — MQTT client feature, outside crate scope.
6. **Door state transitions not tested** — `check_door_state()` always returns `"unknown"`.
7. **Lease expiry not tested** — `get_active()` expiry logic tested implicitly but not with time-travel.

---

## Architectural Risk Assessment

### Risk 1: Client-side vs Connector-side split
The `BmsClient` implements robot-facing operations (request door, check state, release). The `Runtime` implements connector-facing operations (heartbeat, MQTT transport). The spec's CP-010–013 requirements span both sides, but the crate only implements the client-side stubs and connector-side infrastructure. **Risk:** orchestrator-side requirements (LV-13, DS-12, EB-13, LR-13) cannot be verified in this crate.

### Risk 2: AuditSink trait without implementation
`AuditSink` is defined but not implemented. The audit trail requirement (Sup-003 §10) depends on an external implementation. **Risk:** audit compliance cannot be verified without the consuming crate.

### Risk 3: Simplified liveness check
`LivenessStatus::is_alive()` only checks if the heartbeat string is non-empty. The timeout parameter is ignored. **Risk:** false-positive liveness in production.

---

## Evidence Provenance

| File | Blob SHA | Lines | Purpose |
|---|---|---|---|
| `topics.rs` | `d3f36f357ecce79c47448c28cbc2f9df40294395` | 174 | MQTT topic builder, all CP-010-013 topic patterns |
| `contract.rs` | `9e86dc00dfe27cfb2677064f9a2ea3000458d305` | 318 | BMS contract types (requests, responses, enums) |
| `runtime.rs` | `a5e14ed9a1477cccd64d9b8147c6f53c988a8c6f` | 312 | Connector runtime, MQTT transport, heartbeat |
| `client.rs` | `9f2f7e3c6c4ac4a1ffd41dcb8c8828813633f2cf` | 428 | BmsClient, LeaseTable, LivenessStatus, AuditSink |
| `sim.rs` | `02da4e119e8e0bdaf5d6768c5b8b75ad5f494134` | 286 | SimBuilding, fault injection |
| `transport/mod.rs` | `dabf6283e7ce8201d4a0a8e49cf06ab707b3c593` | 45 | MqttTransport trait, QoS enum |

---

## Warrant Assessment

| Component | Evidence | Warrant Status | Justification |
|---|---|---|---|
| Topic patterns | 12 tests pass | WARRANTED | All CP-010-013 topic patterns generate correctly |
| Contract types | 6 tests pass | WARRANTED | Serialization/deserialization verified |
| Lease management | 2 tests pass | PARTIALLY WARRANTED | Insert/get/release tested, expiry logic partial |
| Liveness tracking | 1 test pass | PARTIALLY WARRANTED | `on_heartbeat` tested, `is_alive` simplified |
| Door access client | 1 test pass | PARTIALLY WARRANTED | Returns Pending, actual response path not tested |
| Emergency override | 1 test pass | WARRANTED | Sim grants emergency access correctly |
| Fault injection | 1 test pass | PARTIALLY WARRANTED | Door denial tested, elevator partial |
| Heartbeat publisher | — | NOT IMPLEMENTED | Topic exists, no periodic publisher |
| Door state publisher | — | NOT IMPLEMENTED | Topic exists, `check_door_state()` stub |
| Boarding status | — | NOT IMPLEMENTED | Topic exists, no publisher |
| Audit trail | — | PARTIAL | Trait defined, no implementation |

---

## Recommendations

1. **Implement periodic heartbeat publisher** in `Runtime` — LV-10 requires 30 s interval publication.
2. **Fix `is_alive()` timeout logic** — use actual time delta, not string emptiness check.
3. **Implement door state transitions** — replace `check_door_state()` stub with BMS state reader.
4. **Add boarding status publisher** — CP-012 EB-10/EB-11 require state transition messages.
5. **Implement AuditSink mock** for testing — at minimum, an in-memory collector for unit tests.
6. **Add integration tests** — test full request→response flow through simulated MQTT transport.
7. **Add elevator/zone client tests** — `request_elevator()` and `request_zone()` untested.
