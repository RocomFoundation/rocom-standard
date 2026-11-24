# CP-012 — BMS Elevator Boarding Status

**Status:** MERGED (Edition 2026a)
**Target:** Part 4 — Service Contracts (Sup-003 BMS Infrastructure Contract extension)
**Also affects:** Part 5 (Transport Profile)
**Raised:** 19 November 2026
**Author:** Rocom Project

---

## 1. Problem

The Sup-003 elevator dispatch flow sends a dispatch command but provides no feedback on boarding outcome. When an elevator dispatch fails — door closes before robot arrives, capacity exceeded, elevator malfunction — the orchestrator has no visibility. The robot remains assigned to a failed elevator, the task is delayed, and the facility has no record of the failure for capacity planning.

## 2. Design basis

Elevator control systems report boarding state through their monitoring infrastructure. Exposing this state via a dedicated MQTT topic provides real-time visibility into dispatch outcomes. The topic publishes boarding status transitions: dispatched, boarding, boarded, failed.

## 3. Normative requirements

**EB-10** — The BMS connector SHALL publish elevator boarding status on `rocom/v0/bms/elevator/boarding/{elevator_id}` on every status transition.

**EB-11** — The boarding status payload SHALL contain `elevator_id`, `robot_id`, `status` (`dispatched`, `boarding`, `boarded`, `failed`), `timestamp` (ISO 8601), and `floor_from` / `floor_to`.

**EB-12** — A `failed` status SHALL include a `failure_reason` field: `door_timeout`, `capacity_exceeded`, `elevator_fault`, `robot_no_show`.

**EB-13** — The orchestrator SHALL reassign a robot receiving `failed` status within 30 seconds, either to the next available elevator or by dispatching a different robot from the waiting queue.

**EB-14** — Boarding status messages SHALL be published at QoS 1 (at least once).

## 4. Topic specification

### Elevator Boarding Status
- **Topic:** `rocom/v0/bms/elevator/boarding/{elevator_id}`
- **Direction:** BMS Connector → Orchestrator + Monitors
- **QoS:** 1
- **Payload (successful boarding):**
  ```json
  {
    "elevator_id": "elevator-shaft-a",
    "robot_id": "robot-hrrm-001",
    "status": "boarded",
    "timestamp": "2026-11-19T10:00:00Z",
    "floor_from": 1,
    "floor_to": 3
  }
  ```
- **Payload (failed boarding):**
  ```json
  {
    "elevator_id": "elevator-shaft-a",
    "robot_id": "robot-hrrm-001",
    "status": "failed",
    "failure_reason": "door_timeout",
    "timestamp": "2026-11-19T10:00:00Z",
    "floor_from": 1,
    "floor_to": 3
  }
  ```
- **Statuses:** `dispatched`, `boarding`, `boarded`, `failed`
- **Failure reasons:** `door_timeout`, `capacity_exceeded`, `elevator_fault`, `robot_no_show`

## 5. Monitoring

Wildcard subscription `rocom/v0/bms/elevator/boarding/+` enables monitoring all elevator boarding events. Aggregated boarding failure rates per elevator inform capacity planning and maintenance scheduling.

## 6. Relationship to existing control planes

Sup-003 defines elevator dispatch (`rocom/v0/bms/elevator/dispatch`). CP-012 provides boarding outcome feedback beyond the dispatch command. CP-010 liveness monitoring distinguishes elevator failures from connector failures. CP-008 Resource Authority uses boarding status to manage elevator resource allocation.
