# FILE: spec/part-01-overview/OVERVIEW.md
# =====================================================================
# Rocom — Part 1: Overview and Scope
# Status: ADOPTED 1.0, Edition 2026a
# License: CC-BY 4.0 (see LICENSE-SPEC)
# =====================================================================

# 1. Purpose

Rocom is an open, vendor-neutral specification for integrating
heterogeneous robot fleets with enterprise orchestration systems. It
defines the protocol bindings, service contracts, security requirements,
and data governance controls that enable any conformant robot to
interoperate with any conformant orchestrator.

The target domain is healthcare logistics — but the architecture is
domain-agnostic.

# 2. Terminology

**orchestrator** — The system implementing the orchestration layer;
responsible for task allocation, the agent registry, and the audit
trail. This standard does not prescribe a specific orchestrator
implementation.

**agent** — Any entity that can be allocated tasks: human staff members,
robots, or human-in-the-loop operator stations (cockpit).

**convergence layer** — The IT/OT boundary crossing point where robot
fleet data (OT zone) meets enterprise systems (IT zone). All cross-zone
data flow passes through the convergence layer (see Part 7, dg-p-001).

**conformance level** — A tiered set of requirements (L1 through L3)
that allows incremental adoption. A system conforming to L2 satisfies
all L1 requirements.

# 3. Architecture — Specification Layers

The specification is structured as seven Parts, of which Parts 3 through
7 describe layered system architecture. Parts 1 and 2 are meta-specification
(overview, conformance rules) and do not correspond to runtime layers.

```
  Architecture layers (runtime):

    Part 7  Data Governance    — data classification, egress control
         |
    Part 6  Security           — machine identity, trust, mTLS
         |
    Part 5  Transport Profile  — VDA 5050 binding, capability registry
         |
    Part 4  Service Contracts  — availability provider, task source
         |
    Part 3  Information Model  — agent, task, data profile types
         |
          [ Robot Fleet / OT Zone ]

  Specification structure (all Parts):

    Part 1  Overview and Scope     — architecture, terminology, zone model
    Part 2  Conformance            — L1–L3 levels, conformance statement
    Parts 3–7  (architecture layers, shown above)
```

Parts are dependency-ordered: Part N requires Parts 1 through N-1.
Part 3 (Information Model) is a foundation — Parts 4 through 7 reference
its types verbatim.

# 4. IT/OT Zone Model

```
  +------------------+    +-------------------+    +------------------+
  |    IT Zone       |    |  Convergence      |    |    OT Zone       |
  |                  |    |  Layer            |    |                  |
  |  HR Systems      |◄──►|  Rocom Gateway    |◄──►|  Robot Fleet     |
  |  Turnus/Columna  |    |  (mTLS, VDA 5050) |    |  (VDA 5050      |
  |  Workday         |    |                   |    |   compliant)     |
  |  Task Sources    |    |  Audit Trail      |    |  Vendor Systems  |
  |  Enterprise ERP  |    |  Data Governance  |    |  BMS/Access Ctrl |
  +------------------+    +-------------------+    +------------------+
```

- **OT Zone:** Robot fleet, vendor systems, BMS, access control. Data
  generated here includes operational telemetry, diagnostics, and sensor
  payloads.
- **Convergence Layer:** The only sanctioned crossing point. Enforces
  protocol binding (Part 5), identity verification (Part 6), data
  classification (Part 7), and audit logging.
- **IT Zone:** Enterprise systems, HR platforms, task sources. Receives
  only operational telemetry and authorized data classes.

# 5. Partner Planes

The specification defines four contract planes:

| Plane | Role | Specification Part |
|-------|------|--------------------|
| 1 — BMS Infrastructure | Building Management Systems (access control, elevators) | Part 5 |
| 2 — Robot Vendor | Rocom-conformant robot platforms | Part 5 |
| 3 — Availability Provider | HR/turnus systems providing agent availability | Part 4 |
| 4 — Task Source | Enterprise systems generating tasks | Part 4 |

# 6. Specification Parts

| Part | Title | Scope |
|------|-------|-------|
| 1 | Overview and Scope | Architecture, terminology, zone model |
| 2 | Conformance | L1–L3 levels, conformance statement template |
| 3 | Information Model | Agent, task, capability, data profile types |
| 4 | Service Contracts | Availability provider, task source interfaces |
| 5 | Transport Profile & Bindings | VDA 5050 binding, capability registry |
| 6 | Security | Machine identity, trust, mTLS |
| 7 | Data Governance | Data classification, egress control, Art. 30 |

# 7. Cross-References

Parts 4 through 7 reference the types defined in Part 3 (Information
Model) verbatim. Conformance is declared per Part at L1, L2, or L3
(see Part 2). Formal certification is defined by the Rocom Certification
Program (see GOVERNANCE.md).
