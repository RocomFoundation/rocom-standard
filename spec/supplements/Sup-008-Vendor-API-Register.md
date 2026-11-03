# Sup-008 — Informative Vendor / System / API Reference Register

**Status:** DRAFT
**Date:** 2026-11-03
**Scope:** Informative reference register for robot interaction with buildings — not a general BMS data catalog.
**Normative impact:** None. This document does not change ROCOM requirements.

## Purpose

Provide a short, sourced reference register that lists vendors, systems, documented APIs, access conditions, and source URLs for building-system interfaces relevant to robot-to-building integration. The register is **informational only** — it does not evaluate, certify, or recommend any vendor.

## Separation of Concerns

| Part | Content | Documentation |
|------|---------|---------------|
| ROCOM standard | Vendor-independent requirements and function profiles | Normative text and version |
| Reference register (this document) | Vendor, product, API, short descriptions, links | Source, documentation date, access conditions |
| Implementation and test evidence | Adapter, maintainer, test scope, results | Independent status fields, adapter version, test proof |
| Customer context | Installed equipment, local configuration, access agreements | Restricted per-site (e.g. Vestre Viken testbed) |

## Status Dimensions

Each entry tracks four independent dimensions. No automatic promotion between dimensions:

| Dimension | Values |
|-----------|--------|
| **Documentation** | primary_source_found, version_pinned, unknown |
| **Adapter Implementation** | not_assessed, in_progress, published |
| **Test Evidence** | not_assessed, simulated, production_tested |
| **ROCOM Conformance** | not_assessed, self_declared, certified |

## Governance Rules

1. A public API link does not confer ROCOM-compatible or certified status.
2. Status dimensions are recorded separately — documentation, implementation, testing, and conformance are distinct claims.
3. Use separate product entries when interfaces or license terms differ.
4. The vendor owns the API specification; ROCOM links to the original and maintains only short metadata.
5. Public registry contains generic product properties. Installed systems, local endpoints, and site configuration are kept in restricted customer context.
6. A test claim must state product/API version, adapter version, test environment, date, tested functions, and link to results.
7. Any ROCOM conformance declarations are a design proposal that must be adopted separately — this document introduces no certification scheme.
8. Candidates are accepted by the same criteria: relevant function and traceable documentation. The listing is not a vendor recommendation or ranking.
9. Use existing reviews and vendor notifications for updates — no new periodic automation is created.

## Core Fields

Minimum fields per entry: `supplier`, `product/system`, `product_and_api_version`, `domain`, `capabilities`, `official_documentation_url`, `source_owner`, `authentication_and_access_conditions`, `documentation_checked_on`, `adapter_reference_and_maintainer`, `test_evidence_reference_and_scope`.

## Industry Precedents

| Precedent | What They Do | Transfer to ROCOM |
|-----------|-------------|-------------------|
| [DICOM PS3.2 Annex N](https://dicom.nema.org/medical/dicom/current/output/chtml/part02/chapter_n.html) | Defines content and template for vendor Conformance Statements | Short, versioned declaration of which ROCOM functions a product or adapter supports |
| [HL7/FHIR CapabilityStatement](https://hl7.org/fhir/capabilitystatement.html) | Describes capabilities of software or a specific installation | Separate generic product functions from site-activated functions using structured metadata |
| [IHE Product Registry](https://www.ihe.net/testing/ihe_product_registry/) | Vendor Integration Statements; Connectathon results documented separately | Closest model: registry entry is not automatic approval |

---

## Register Entries

All entries as of 2026-11-03. Primary documentation found. Adapter status, test status, and ROCOM conformance not assessed in this review.

### Elevators

| ID | Vendor | System | Capabilities | Access Conditions | Documentation |
|----|--------|--------|-------------|-------------------|---------------|
| kone-service-robot | KONE | Service Robot API / connected elevators | WebSocket; elevator call, floor, direction, door status, call status | Agreement, compatibility, activation must be confirmed per installation | [KONE Service Robot API](https://dev.kone.com/api-portal/service-robot-api) |

### Access Control

| ID | Vendor | System | Capabilities | Access Conditions | Documentation |
|----|--------|--------|-------------|-------------------|---------------|
| shs-integra | SystemHouse Solutions | Integra / EasyConnect | SOAP/WebService (EasyConnect) for cards, rights, zones, status. REST in 8.80 described for booking; operational door control must be clarified separately | Product version, modules, and interfaces for robot use must be confirmed | [Integra overview](https://systemhousesolutions.com/integra/) · [EasyConnect SOAP](https://systemhousesolutions.com/wp-content/uploads/sites/2/2019/11/software-licence-integra-easyconnect.pdf) · [8.80 REST/Kepware](https://systemhousesolutions.com/news/integra-8-80-improved-functionality-and-integration/) |
| assa-incedo | ASSA ABLOY | Incedo Open / ARX–Multiaccess integration | Third-party API and integration with existing ARX/Multiaccess users | Scope, rights, and physical door automation must be confirmed separately | [Incedo Open](https://www.assaabloy.com/se/en/solutions/topics/access-control/incedo-open) |
| rco-m5 | RCO Security | R-CARD M5 User API / Admin API / OPC | User API for door control; Admin API for administration; OPC for higher-level systems | Integration agreement with RCO, license, and installer required | [RCO APIs](https://rco.se/integrationer/vara-integrationer) |
| acre-omnis | acre security | Omnis 7.5 REST API | Lists doors, reads status, offers open, pulse open, close | REST license, compatible version, and external web server required | [Omnis 7.5 REST API](https://ams.acresecurity.com/pln/2026-PR-A-105-EX) |
| salto-platform | Salto | Space / KS / Nebula | Developer portal with product-specific integration resources | Select product family before API specification; do not assume same functions across products | [Salto Developer](https://developer.saltosystems.com/) |
| unloc-platform | Unloc | Unloc API / Mobile Keys | Key and access management across supported lock types | Autonomous robot opening without human mobile user not confirmed | [Unloc Developer](https://developer.unloc.app/docs/getting-started-with-unloc) |

### Door Automation

| ID | Vendor | System | Capabilities | Access Conditions | Documentation |
|----|--------|--------|-------------|-------------------|---------------|
| dorma-doors | dormakaba | Door automation / exivo | Drammen reference for door automation and hardware. exivo is a separate product with API | exivo API does not document that installed doors have the same interface | [Drammen reference](https://www.dormakaba.com/no-no/bruk-tilfelle/hospital-in-drammen) · [exivo API](https://www.dormakaba.com/sg-en/offering/products/electronic-access-data/access-control-solutions-for-small-and-medium-enterprises/exivo--ka_500013) |

### Locks and Access

| ID | Vendor | System | Capabilities | Access Conditions | Documentation |
|----|--------|--------|-------------|-------------------|---------------|
| iloq-platform | iLOQ | iLOQ Platform / Mobile SDK | API for users, keys, log, events; documented KONE integration | Lock type and reader determine robot's practical passage | [iLOQ Ecosystem](https://www.iloq.com/en/ecosystem/) · [iLOQ/KONE integration](https://www.iloq.com/en/integration-partners/kone/) |

### Building Management (BMS)

| ID | Vendor | System | Capabilities | Access Conditions | Documentation |
|----|--------|--------|-------------|-------------------|---------------|
| schneider-buildings | Schneider Electric | EcoStruxure BO / SmartConnector / Building Data Platform | Official GitHub sources for servers, EWS integration, data platform access. Product families have different interfaces | Selected product, version, and modules must be confirmed per installation | [Schneider GitHub](https://github.com/SchneiderElectricBuildings) |
| jci-metasys | Johnson Controls | Metasys REST API | API documentation and C# client published by vendor | Server product, API version, rights, and license must be confirmed | [Metasys API](https://github.com/jci-metasys/api-landing) · [C# Client](https://github.com/jci-metasys/basic-services-dotnet) |
| distech-eclypse | Distech Controls | ECLYPSE / CloudRelay | Open CloudRelay code for REST access through Azure IoT Hub | Controllers, firmware, Azure, and required licenses must be confirmed | [CloudRelay](https://github.com/DistechControls/CloudRelay) |
| tridium-niagara | Tridium | Niagara Framework | Vendor examples for Baja, RPC, queries, and user interface | Example code without product support; no general ready-made REST integration claimed | [Code Samples](https://github.com/tridium/code-samples) |
| siemens-buildingx | Siemens | Building X | Public API documentation based on JSON:API | Product subscription and access must be confirmed. No official GitHub SDK confirmed | [Developer Docs](https://developer.siemens.com/building-x-openness/dev-guide/index.html) |

---

## Recommended Next Steps

1. Create the informative register with the entries above and identified candidates.
2. Prioritize version pinning and interface clarification for Integra, KONE, and Schneider at Drammen.
3. A formal scheme for conformance statements and tests can be considered once the first adapters have real test evidence.
