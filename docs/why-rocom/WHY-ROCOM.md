# FILE: docs/why-rocom/WHY-ROCOM.md
# Title: Why ROCOM

Healthcare operations involve robots, building systems, staffing platforms and clinical task systems — built by different suppliers, managed by different teams, governed by different regulations. Connecting them requires more than adapters. It requires clear responsibilities and testable interfaces at every boundary.

ROCOM is an open standard that defines how those systems interact, where authority sits, and what evidence supports their declared capabilities.

## What ROCOM enables

Four connected areas, each with distinct expertise, working together through open interfaces:

- **Robot** — delivery, transport and support capabilities, with fleet-management systems that retain specialist control.
- **Infrastructure** — doors, lifts and shared building resources, coordinated through responsible building and access-control systems.
- **Workforce** — staffing, skills and availability, coordinating human teams and robot capacity with respect for distinct responsibilities.
- **Task** — clinical and operational needs, priorities and progress, shared across participating systems with traceability.

The value comes from applying these capabilities to a defined operational need — not from the connections alone.

## One practical example

A hospital needs to deliver supplies from a central store to a ward on another floor. A delivery robot is assigned the task by the hospital's task system. Before leaving, the robot requests door access from the building management system — and receives authorisation for a defined time window.

The robot reaches the lift. It sends a dispatch request to the BMS. The lift is currently serving human traffic, so the BMS returns a queued response with an estimated arrival. The robot waits at a safe stand-off distance.

The lift becomes available. The BMS dispatches it. The robot boards, rides to the target floor, and exits. At the ward entrance, the robot re-requests zone authorisation because the previous door access has expired. The BMS grants it, and the robot proceeds to the delivery point.

At each step, the robot system executes the movement, the BMS controls building resources, and the task system tracks progress. No single system takes over the others' authority.

*This is an illustrative workflow. ROCOM specifies the interfaces and responsibilities — it does not execute them. Local robot safety, building systems and required human decisions remain authoritative.*

## Why an open standard matters

### For healthcare organisations

Adoption begins with an agreed operating model. Responsibilities may be shared with service providers, but they should be explicit. ROCOM helps organisations understand what to ask for, assess and verify — before a single robot arrives on site.

### For technology providers

Shared interfaces reduce integration friction. Conformance evidence — self-declared or independently verified — makes it possible to compare capabilities across suppliers without proprietary lock-in.

### For security and assurance professionals

Identified participants, declared data flows and specified failure behaviour turn integration assumptions into auditable claims. Version-specific conformance evidence and disclosed deviations support local risk assessment.

## What ROCOM does not do

- Replace the safety systems, access control or clinical governance of a healthcare organisation.
- Require a particular orchestration or management product.
- Define physical safety requirements for robots (covered by IEC 61508 / ISO 13482 / applicable medical-device regulation).
- Claim that adopting the standard makes a deployment safe.

The standard provides the contracts and evidence that make the connections between existing systems auditable. Each participating system retains its own responsibilities.

---

*This page provides guidance. Normative requirements are defined in the applicable ROCOM specification documents.*
