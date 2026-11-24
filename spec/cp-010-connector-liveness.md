# CP-010 — BMS Connector Liveness (heartbeat + LWT)

**Status:** MERGED (Edition 2026a)
**Target:** Part 4 — Service Contracts (Sup-003 BMS Infrastructure Contract extension)
**Also affects:** Part 5 (Transport Profile — MQTT QoS requirements)
**Raised:** 19 November 2026
**Author:** Rocom Project

---

## 1. Problem

BMS connectors mediate between the orchestrator and facility infrastructure: doors, elevators, zone access control. When a connector loses connectivity, the orchestrator has no visibility into the failure until a robot task fails at the affected resource. Request-response patterns only reveal problems reactively. There is no mechanism to detect connector disconnection before it impacts robot operations.

## 2. Design basis

MQTT provides two mechanisms for connection monitoring: periodic heartbeat publications and Last-Will and Testament (LWT). The LWT message is published by the broker when the client disconnects abnormally, providing immediate failure notification without requiring the subscriber to implement timeout logic. The heartbeat topic provides continuous health indicators with metadata (timestamp, uptime, resource count).

## 3. Normative requirements

**LV-10** — Every BMS connector SHALL publish a heartbeat message on `rocom/v0/bms/liveness/heartbeat/{connector_id}` at configurable intervals (default 30 s).

**LV-11** — Every BMS connector SHALL register an LWT on topic `rocom/v0/bms/liveness/lwt/{connector_id}` with `{"status": "offline", "connector_id": "<id>", "timestamp": "<iso8601>"}` at connection time.

**LV-12** — The heartbeat payload SHALL contain `connector_id`, `status` (`online`), `timestamp` (ISO 8601), `uptime_seconds` (integer), and `active_resources` (integer count of currently managed resources).

**LV-13** — The orchestrator SHALL subscribe to LWT topics for all registered BMS connectors and SHALL mark affected resources as unavailable within 10 seconds of LWT delivery.

**LV-14** — Heartbeat and LWT messages SHALL be published at QoS 1 (at least once) per Part 5 Transport Profile.

## 4. Topic specification

### Heartbeat
- **Topic:** `rocom/v0/bms/liveness/heartbeat/{connector_id}`
- **Direction:** Connector → Orchestrator + Monitors
- **QoS:** 1
- **Payload:**
  ```json
  {
    "connector_id": "bms-main-building",
    "status": "online",
    "timestamp": "2026-11-19T10:00:00Z",
    "uptime_seconds": 3600,
    "active_resources": 12
  }
  ```
- **Interval:** Configurable, default 30 s

### Last-Will
- **Topic:** `rocom/v0/bms/liveness/lwt/{connector_id}`
- **Direction:** Broker → Orchestrator + Monitors (on abnormal disconnect)
- **QoS:** 1
- **Payload:**
  ```json
  {
    "status": "offline",
    "connector_id": "bms-main-building",
    "timestamp": "2026-11-19T10:05:00Z"
  }
  ```

## 5. Monitoring

Wildcard subscription `rocom/v0/bms/liveness/heartbeat/+` enables monitoring all connector heartbeats from a single subscription. LWT topics require per-connector subscriptions or `rocom/v0/bms/liveness/lwt/+` wildcard.

## 6. Relationship to existing control planes

Sup-003 BMS Infrastructure Contract defines door request/response, elevator dispatch, and zone authorization flows. CP-010 extends Sup-003 with liveness monitoring, independent of the request-response patterns. CP-008 Resource Authority uses liveness state to determine resource availability.
