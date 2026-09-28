# Security & Safety

ROCOM does not replace the safety systems, access control or clinical governance of a healthcare organisation. It makes the connections between those systems explicit, testable and traceable.

## What ROCOM adds to security and safety

When robots, building systems, workforce platforms and task systems interact, each system already has its own security and safety responsibilities. The gap is at the connections: who may request what, what data moves where, and how systems behave when a dependency fails.

ROCOM addresses that gap through declared interfaces and verifiable behaviour at the boundaries.

### Identified participants and controlled access

Every system that crosses the IT/OT boundary holds a verifiable machine identity. No anonymous participants. Identity events — issuance, rotation, revocation — are logged to an immutable audit trail.

**Specification:** Part 6 (Identity & Trust), requirements `it-req-001` through `it-req-204`.

### Declared data flows and traceable actions

Each agent and connection declares what data it generates, where that data goes, and the lawful basis for each destination. Data flows are attributable to machine identity and logged to the audit trail. Sensor payloads (video, audio, point clouds) do not cross the convergence layer by default.

**Specification:** Part 7 (Data Governance), requirements `dg-req-001` through `dg-req-203`.

### Behaviour when access is denied or dependencies fail

When a robot requests door access and the building system denies it, the robot stops. When the lift is unavailable, the robot waits or re-routes. When BMS communication is lost, the robot fails safe. These are not best-effort conventions — they are specified, testable requirements.

**Specification:** Sup-003 (BMS Infrastructure Contract), §3.1.3, §3.2.4, §4.2; Part 5 §6.1.

### Responsibilities retained by each system

ROCOM does not centralise authority. The building system remains authoritative for doors and lifts. The robot system remains authoritative for local collision avoidance and emergency stop. The workforce system remains authoritative for human allocation and competence. The task system remains authoritative for clinical priorities.

The standard defines who requests, who authorises, and what each system must do with the response.

### Conformance evidence

A conformance statement identifies which requirements an implementation claims to meet, at which service level, with what evidence. Self-declaration and independent certification are distinct. Neither automatically establishes regulatory compliance or deployment safety. Reusable evidence supports local risk assessment — it does not replace it.

**Specification:** Part 2 (Conformance), Part 2 (Service Levels L0–L3); Sup-005 (Certification Provider).

## What ROCOM does not do

- Does not execute safety-critical decisions on behalf of building or clinical systems.
- Does not claim that adopting the standard makes a deployment safe.
- Does not replace local risk assessment, organisational readiness reviews, or regulatory compliance processes.
- Does not define physical safety requirements for robots (covered by IEC 61508 / ISO 13482 / applicable medical-device regulation).

The standard provides the contracts and evidence that make the connections between existing systems auditable. Safety at the connections supports — but does not substitute for — the safety case of each participating system.

---

*This page provides guidance. Normative requirements are defined in the applicable ROCOM specification documents listed above.*
