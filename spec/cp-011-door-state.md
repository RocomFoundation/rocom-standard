# CP-011 — BMS Door State Reporting

**Status:** MERGED (Edition 2026a)
**Target:** Part 4 — Service Contracts (Sup-003 BMS Infrastructure Contract extension)
**Also affects:** Part 5 (Transport Profile)
**Raised:** 19 November 2026
**Author:** Rocom Project

---

## 1. Problem

The Sup-003 door request/response flow provides a grant or denial but no continuous state. When a robot holds a door lease, the orchestrator has no visibility into the actual door state: whether the door opened, how long it remained open, or whether it closed as expected. Dead door detection (door reported open but physically stuck closed) requires manual investigation. Access audit trails are incomplete because they only record grant events, not state transitions.

## 2. Design basis

Building management systems report door state continuously through their own monitoring infrastructure. Exposing this state via a dedicated MQTT topic provides real-time visibility without polling the BMS. The topic publishes on state change, not at fixed intervals, reducing message volume while maintaining accuracy.

## 3. Normative requirements

**DS-10** — The BMS connector SHALL publish door state on `rocom/v0/bms/door/state/{door_id}` on every state transition.

**DS-11** — The door state payload SHALL contain `door_id`, `state` (`open`, `closed`, `fault`), `timestamp` (ISO 8601), and `trigger` (`bms_sensor`, `lease_expiry`, `manual_override`).

**DS-12** — The orchestrator SHALL correlate door state with active leases to detect dead doors: a door with an active lease reporting `closed` state for more than 30 seconds SHALL be flagged as `dead_door`.

**DS-13** — Door state messages SHALL be published at QoS 1 (at least once).

**DS-14** — A `fault` state SHALL trigger an alert to the orchestrator and SHALL mark the door as unavailable for allocation per CP-008 Resource Authority.

## 4. Topic specification

### Door State
- **Topic:** `rocom/v0/bms/door/state/{door_id}`
- **Direction:** BMS Connector → Orchestrator + Monitors
- **QoS:** 1
- **Payload:**
  ```json
  {
    "door_id": "door-floor2-zone-a",
    "state": "open",
    "timestamp": "2026-11-19T10:00:00Z",
    "trigger": "bms_sensor"
  }
  ```
- **States:** `open`, `closed`, `fault`
- **Triggers:** `bms_sensor`, `lease_expiry`, `manual_override`

## 5. Monitoring

Wildcard subscription `rocom/v0/bms/door/state/+` enables monitoring all door states. Combined with CP-010 liveness monitoring, door state anomalies can be distinguished from connector failures.

## 6. Relationship to existing control planes

Sup-003 defines door request (`rocom/v0/bms/door/request`) and response topics. CP-011 provides continuous state beyond the request/response lifecycle. CP-013 Early Lease Return updates door state when a robot releases a lease early. CP-008 Resource Authority uses door state to determine resource availability.
