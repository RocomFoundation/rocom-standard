# FILE: spec/part-01-overview/ARM.md
# ARM — Architecture Reference Model
# Status: ADOPTED 1.0, Edition 2026a
# License: CC-BY 4.0
# Scope: Position Rocom against HL7 FHIR, IHE, and VDA 5050.
# NOTE:  Positioning document. No normative requirements.

## Purpose

Rocom occupies a specific position in healthcare interoperability:
**operational orchestration of heterogeneous robot fleets**. This document
maps that position against established reference models to clarify what
Rocom is, what it is not, and where it connects to adjacent standards.

## Reference Model Mapping

The table below maps Rocom's five specification layers (Parts 3--7) against
the HL7 FHIR architecture, which serves as the healthcare interoperability
reference model. Both follow the same pattern:

```
  Terminology / Vocabulary
       |
  Information / Resource Model
       |
  Operations / Service Contracts
       |
  Transport Binding
       |
  Security & Governance
       |
  Implementation Profiles / Conformance
```

| Layer | HL7 FHIR (clinical data) | Rocom (robot orchestration) | VDA 5050 (transport substrate) |
|-------|--------------------------|-----------------------------|--------------------------------|
| **Vocabulary** | CodeSystem, ValueSet (SNOMED CT, LOINC, ICC) | Capability registry (key-value definitions) | Message type registry |
| **Information Model** | Patient, Device, Observation, CarePlan, Location | Agent, Task, Data Profile, Capability | Agent state, Order, Factsheet |
| **Service Contracts** | REST operations (`$everything`, `$search`, conditional create) | Availability Provider, Task Source, Fleet Binding | State updates, Order accept/reject |
| **Transport** | HTTP/JSON (primary), MQTT, WebSocket bindings | MQTT on `rocom/v0/` topics (VDA 5050 baseline) | MQTT 3.1.1/5.0, JSON encoding |
| **Security** | SMART on FHIR, OAuth 2.0, OpenID Connect | mTLS, X.509 machine identity | TLS (recommended by VDA) |
| **Audit** | AuditEvent (RFC 3634 / DICOM conformance) | Compliance events with `auditCorrelationId` | — |
| **Conformance** | ImplementationGuides (IHE profiles), SUSHI/GENESIS | Conformance levels L1--L3, conformance statements | VDA 5050 certification |

## The Pattern: Open Protocol, Profile on Top

Both HL7 FHIR and Rocom follow the same architectural pattern that has
proven successful in healthcare interoperability:

1. **Open protocol** defines the base transport and data model
2. **Implementation profiles** add domain-specific constraints
3. **Conformance testing** validates compliance mechanically

| Domain | Open Protocol | Profile | Conformance |
|--------|--------------|---------|-------------|
| Medical imaging | DICOM | IHE profiles | IHE testing events |
| Clinical data | HL7 FHIR | IHE XCA, XDS | IHE testing events |
| Robot orchestration | VDA 5050 | Rocom (healthcare profile) | Rocom conformance (L1--L3) |

Rocom is the **healthcare profile on VDA 5050**, analogous to how IHE
profiles sit on DICOM or HL7 FHIR.

## What Rocom Does Not Do

Rocom does not address:

- **Clinical data exchange** (patient records, lab results, prescriptions) — that is HL7 FHIR's domain
- **Medical device imaging** — that is DICOM's domain
- **Electronic health record (EHR) integration** — that requires a FHIR bridge layer

Rocom models logistics agents (robots, human staff, cockpits) and their
operational tasks (transport, delivery, patrol). It does not model
patients, diagnoses, treatments, or clinical observations.

## The FHIR Bridge Gap

A future integration point exists between Rocom and HL7 FHIR:

```
  [ EHR: Epic, Cerner ] -- FHIR -- [ FHIR Bridge ] -- Rocom -- [ Robot Fleet ]
                                    ^
                                    |
                          Maps Rocom Agent -> FHIR Device
                          Maps Rocom Task   -> FHIR CarePlan/ServiceRequest
                          Maps Rocom Task status -> FHIR Observation
```

This bridge layer would enable:

- Robot agents appearing as FHIR `Device` resources in the EHR
- Task execution status visible as FHIR `Observation` or `Procedure`
- Clinical workflows triggering robot tasks via FHIR `ServiceRequest`

This is **out of scope for Rocom** but is a natural integration point for
healthcare deployments that require EHR-level visibility into robot
operations.

## Spatial Architecture: IT/OT Zones

Rocom's five specification layers map to a three-zone spatial architecture:

```
  +------------------+     +------------------+     +------------------+
  |   IT ZONE        |     | CONVERGENCE      |     |   OT ZONE        |
  |                  |     | LAYER            |     |                  |
  | HR systems       |<--> | Rocom Part 4     |<--> | Robot fleet      |
  | ERP / WMS        |     | (service        |     | VDA 5050         |
  | Columna Flow     |     |  contracts)     |     |                  |
  | Task sources     |     +------------------+     | BMS / Siemens    |
  |                  |           |                  | Vendor systems   |
  +------------------+     +------------------+     +------------------+
                           |
                     Rocom Part 3  Rocom Part 5  Rocom Part 6  Rocom Part 7
                    (information  (transport    (security     (data
                     model)        profile)      mTLS)        governance)
```

The convergence layer is the **only sanctioned data crossing point** between
IT and OT zones. All four partner contract planes (BMS, Robot Vendor,
Availability Provider, Task Source) terminate at this boundary.

## Why This Matters

Understanding Rocom's position in the interoperability landscape is not
academic. It determines:

1. **Procurement language** — "Rocom L2 conformance" means something
   specific and testable, not "we integrate with robots"
2. **Security architecture** — the IT/OT boundary is where data governance
   (Part 7) and security (Part 6) are material concerns
3. **EHR integration strategy** — Rocom handles the logistics layer; a
   FHIR bridge handles the clinical layer. They are complementary, not
   competitive.
4. **Regulatory positioning** — like DICOM and HL7 FHIR, Rocom is a
   voluntary open standard, not a regulatory mandate

## References

- HL7 FHIR R4: <https://hl7.org/fhir/R4/>
- HL7 FHIR Architecture: <https://hl7.org/fhir/R4/architecture.html>
- IHE Radiology Technical Framework: <https://www.ihe.net/radiology/>
- VDA 5050: <https://www.vda.de/en/vda-5050>
- Rocom Part 1 Overview: `spec/part-01-overview/OVERVIEW.md`
