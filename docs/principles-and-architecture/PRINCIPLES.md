# FILE: docs/principles-and-architecture/PRINCIPLES.md
# Rocom — Principles and Architecture
# Status: DRAFT 0.1 (2026-08-12) — Edition 2026a (draft)
# License: CC-BY 4.0 (see LICENSE-SPEC)
# Scope: Security-by-design, data governance, regulatory alignment.

## The Pattern: Open Protocol, Profile on Top

Rocom follows an architectural pattern proven in healthcare interoperability
since the 1980s: an open protocol establishes the transport and data model,
domain-specific profiles add constraints, and conformance testing validates
compliance mechanically.

| Domain | Open Protocol | Profile | Conformance |
|--------|--------------|---------|-------------|
| Medical imaging | DICOM (1993) | IHE profiles | IHE testing events |
| Clinical data | HL7 FHIR (2014, ISO 21772:2023) | IHE XCA, XDS | IHE testing events |
| Robot orchestration | VDA 5050 (2019) | Rocom (healthcare) | Rocom conformance (L1-L3) |

Rocom is the healthcare profile on VDA 5050 — analogous to how IHE profiles
sit on DICOM or HL7 FHIR. The standard VDA 5050 messages are never modified;
Rocom extensions live exclusively on `rocom/v0/` MQTT topics.

## Five-Layer Architecture

Rocom specifies five runtime layers, dependency-ordered from foundation to
enforcement:

```
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
```

Part 3 (Information Model) is the foundation — all upper layers reference
its types verbatim. Each layer adds conformance requirements at L1, L2, and
L3, forming a cumulative maturity ladder.

## IT/OT Convergence Model

Healthcare robot deployments span two security zones with fundamentally
different risk profiles:

```
  +------------------+     +------------------+     +------------------+
  |   IT ZONE        |     | CONVERGENCE      |     |   OT ZONE        |
  |                  |     | LAYER            |     |                  |
  | HR systems       |<--> | Rocom Gateway    |<--> | Robot fleet      |
  | ERP / WMS        |     | (mTLS, VDA 5050,|     | VDA 5050         |
  | Task sources     |     |  audit, gov.)   |     |                  |
  |                  |     +------------------+     | BMS / building   |
  +------------------+                               | vendor systems   |
```

The convergence layer is the **only sanctioned data crossing point** between
IT and OT zones. Four partner contract planes terminate at this boundary:

| Plane | Partner | Zone | Role |
|-------|---------|------|------|
| 1 | BMS Infrastructure | OT | Access control, elevators, environmental systems |
| 2 | Robot Vendor | OT | Rocom-conformant robot platforms |
| 3 | Availability Provider | IT | HR/turnus systems providing agent availability |
| 4 | Task Source | IT | Enterprise systems generating tasks |

## Security-by-Design Principles

Four principles govern machine identity at the IT/OT boundary:

| Principle | Statement |
|-----------|-----------|
| **it-p-001** | Every non-human agent (robot, adapter, provider, connector) MUST hold a verifiable machine identity. No anonymous participants at the IT/OT boundary. |
| **it-p-002** | Identity lifecycle is bound to agent lifecycle: onboarding implies identity issuance; offboarding implies revocation. |
| **it-p-003** | Open standard in specification, replaceable vendors in implementation. The spec references SPIFFE and X.509; it MUST NOT reference any CA vendor, IAM product, or national identity scheme normatively. |
| **it-p-004** | All identity events (issuance, rotation, revocation, failed authentication) MUST be written to the orchestrator's immutable audit trail. |

Machine identity uses SPIFFE-compatible URIs (`spiffe://<trust-domain>/agent/<type>/<id>`)
with X.509 SVID certificates. One trust domain per deployment.

### Transport Security Bindings

| Interface | Protocol | Minimum |
|-----------|----------|---------|
| Fleet binding (VDA 5050 / MQTT) | mTLS | 1.2+ |
| Orchestrator service interfaces (HTTP) | TLS | 1.2+ |
| Availability-provider / task-source contracts | mTLS | between connector and provider |

## Data Governance: Minimization by Protocol

Four principles govern data flows across the convergence layer:

| Principle | Statement |
|-----------|-----------|
| **dg-p-001** | The convergence layer is the only sanctioned data path across the IT/OT boundary. Direct cloud egress from robots or vendor fleet systems is out of policy. |
| **dg-p-002** | Data minimization by protocol: the boundary protocol carries state, orders, and operational telemetry only. Sensor payloads (video, audio, point clouds) do not cross the convergence layer. |
| **dg-p-003** | The spec provides the policy and verification surface, not physical prevention. Enforcement requires OT-zone network controls and contractual terms. |
| **dg-p-004** | Every declared data flow is attributable: flows are bound to the originating agent's machine identity and logged to the immutable audit trail. |

### Data Class Taxonomy

| Class | Content | Personal Data? |
|-------|---------|---------------|
| **Operational telemetry** | Position, battery, task state, error codes, availability | No (by design) |
| **Diagnostic** | Logs, firmware state, component wear, performance counters | Normally no; verified per vendor |
| **Sensor payload** | Video, audio, lidar/point clouds, images | Presumed yes (GDPR Art. 9) |
| **Personal data** | Staff scheduling, task metadata naming individuals | Yes |

### Teleoperation Exception

Sensor payloads MAY cross the boundary only as a declared, session-bound exception:
registered in the agent's data profile, time-limited, human-initiated, logged,
and auto-terminated at session end. Standing sensor streams are never an exception.

## Conformance Philosophy

Rocom conformance follows three rules:

1. **Cumulative levels**: A system at L2 satisfies all L1 requirements.
   L1 is pilot/lab, L2 is production single-site, L3 is multi-site/regional.

2. **Partial conformance with transparency**: Deviations are permitted but must
   be listed with rationale and planned resolution. Systems with more than three
   deviations at L2 or above are not eligible for Rocom Certified status.

3. **Voluntary certification**: Self-declaration is valid. Formal Rocom Certified
   status is awarded by the certification program upon successful test suite
   execution. The steward does not manufacture hardware — no conflict of interest.

## Regulatory Alignment

Rocom's architecture is designed to align with the regulatory landscape facing
healthcare robot deployments in Europe:

| Regulation | Rocom Alignment |
|------------|----------------|
| **EU Cyber Resilience Act** | Security-by-design for all products implementing the standard. Conformance levels map to CRA assurance requirements. |
| **GDPR (Art. 9, Art. 30)** | Data class taxonomy, lawful basis per destination, Article 30-compatible processing records exported on demand. |
| **IEC 62443** | Conformance levels map informatively to security levels: L1~SL1, L2~SL2, L3~SL3. IT/OT zone model is the structural hook. |
| **NIS2** | Zone model and egress control for critical-infrastructure operators. |
| **Schrems II** | Third-country transfer governance: declared basis per destination, auditable transfer register at L3. |
| **EHDS** | European data sovereignty: convergence layer keeps health-adjacent data in-region by default. |
| **Normen (NO)** | Norwegian deployment profile under definition. |

## What Rocom Does Not Do

Rocom addresses operational orchestration of robot fleets. It does not address:

- **Clinical data exchange** (patient records, lab results, prescriptions) — that is HL7 FHIR's domain
- **Medical device imaging** — that is DICOM's domain
- **Electronic health record integration** — a FHIR bridge layer is needed, tracked as a known gap (see Architecture Reference Model)

## References

- HL7 FHIR R4: <https://hl7.org/fhir/R4/>
- HL7 FHIR Architecture: <https://hl7.org/fhir/R4/architecture.html>
- DICOM Standard: <https://www.dicomstandard.org/>
- VDA 5050: <https://www.vda.de/en/vda-5050>
- IHE Radiology Technical Framework: <https://www.ihe.net/radiology/>
- Rocom Part 1 Overview: `spec/part-01-overview/OVERVIEW.md`
- Rocom Architecture Reference Model: `spec/part-01-overview/ARM.md`
