# CP-013 — BMS Early Lease Return (Door and Zone Release)

**Status:** MERGED (Edition 2026a)
**Target:** Part 4 — Service Contracts (Sup-003 BMS Infrastructure Contract extension)
**Also affects:** Part 5 (Transport Profile)
**Raised:** 19 November 2026
**Author:** Rocom Project

---

## 1. Problem

Sup-003 resource leases have a fixed expiry duration. When a robot completes its door-access or zone-occupancy task before lease expiry, the resource remains locked until the lease expires. This creates stale occupancy: doors and zones are unavailable for other robots despite the original task being complete. The orchestrator has no mechanism to receive early lease return, and robots have no topic to signal completion.

## 2. Design basis

Early lease return follows the same namespace pattern as Sup-003 request topics, using a `release` action. The robot publishes a release message when its task completes, the BMS connector acknowledges and updates the resource state, and the orchestrator's resource authority marks the resource as available. This reduces wait times for subsequent robots and prevents queue buildup at controlled access points.

## 3. Normative requirements

**LR-10** — A robot SHALL publish a release message on `rocom/v0/bms/door/release/{door_id}` or `rocom/v0/bms/zone/release/{zone}` when its task completes before lease expiry.

**LR-11** — The release payload SHALL contain `resource_id` (door_id or zone), `robot_id`, `lease_id`, `timestamp` (ISO 8601), and `reason` (`task_complete`, `task_cancelled`, `manual_release`).

**LR-12** — The BMS connector SHALL process a release message and update the resource state to `available` within 5 seconds.

**LR-13** — The orchestrator SHALL mark the resource as available for allocation within 10 seconds of processing the release.

**LR-14** — Release messages SHALL be published at QoS 1 (at least once).

**LR-15** — The BMS connector SHALL reject a release for a resource not held by the requesting robot (mismatched `robot_id` or `lease_id`) and SHALL publish the rejection to the orchestrator.

## 4. Topic specification

### Door Release
- **Topic:** `rocom/v0/bms/door/release/{door_id}`
- **Direction:** Robot → BMS Connector → Orchestrator
- **QoS:** 1
- **Payload:**
  ```json
  {
    "resource_id": "door-floor2-zone-a",
    "robot_id": "robot-hrrm-001",
    "lease_id": "lease-abc-123",
    "timestamp": "2026-11-19T10:00:00Z",
    "reason": "task_complete"
  }
  ```

### Zone Release
- **Topic:** `rocom/v0/bms/zone/release/{zone}`
- **Direction:** Robot → BMS Connector → Orchestrator
- **QoS:** 1
- **Payload:**
  ```json
  {
    "resource_id": "floor2-zone-a",
    "robot_id": "robot-hrrm-001",
    "lease_id": "lease-def-456",
    "timestamp": "2026-11-19T10:00:00Z",
    "reason": "task_complete"
  }
  ```
- **Reasons:** `task_complete`, `task_cancelled`, `manual_release`

## 5. Monitoring

Wildcard subscription `rocom/v0/bms/door/release/+` and `rocom/v0/bms/zone/release/+` enables monitoring all release events. Early release frequency per resource informs lease duration tuning: resources with high early-release rates benefit from shorter default lease durations.

## 6. Relationship to existing control planes

Sup-003 defines door request/grant and zone authorization flows with lease expiry. CP-013 provides early release, reducing the window between task completion and resource availability. CP-011 Door State updates when a released door transitions to `closed` state. CP-008 Resource Authority processes release messages to update resource availability.
