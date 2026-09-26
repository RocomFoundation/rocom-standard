# Changelog — Rocom Open Standard

All notable changes to the Rocom specification, structured by edition.
Format: [Keep a Changelog](https://keepachangelog.com/) adapted for standards.

---

### Added
- **Sup-005** Certification Provider Requirements — 28 krav (CP-REQ, OP-REQ, IND-REQ, INF-REQ) for certification provider operating on behalf of ROCOM

---

## [2026a-draft] — 2026-09-26

### Added
- **Sup-004** Governance Structure: Board and Working Groups — Board of Directors (5-9 members), 4 Working Groups (Robot, Infrastructure, Workforce, Task)

---

## [2026a-draft] — 2026-09-07

### Changed
- Governance: ROCOM association (CVR 46774043) established as independent owner
- Tech Happens Europe ApS transitioned to organizational member role
- Repository transferred to RocomFoundation GitHub organization

---

## [2026a-draft] — 2026-09-01

### Merged
- **CP-009** Priority and Preemption Model — 17 krav (PR-01 til PR-17). Priority tiers, preemption rules, escalation chain.
- **CP-008** Resource Authority Model — 29 krav (RA-01 til RA-29). Robot yield rules, authority delegation, stand-off behavior.
- **CP-007** Agent Identity Model — 9 krav (ID-01 til ID-09). Three-layer identity: access_key, device_identifier, production_identifier. UDI-aligned.
- **Sup-003** BMS Infrastructure Contract — 4 contract elements (door, elevator, zone auth, emergency override). 13 test IDs (BMS-01 to BMS-13). Protocol mappings: BACnet, KNX, OPC UA.

### Added
- `part-04-services/task_source_contract.yaml` — Task Source Interface (missing Part 4 companion to availability_provider_contract). Bronze/Silver/Gold conformance levels. AsyncAPI sketch.
- `spec/cp-007-agent-identity.md` (177 linjer)
- `spec/cp-008-resource-authority.md` (418 linjer)
- `spec/cp-009-priority-preemption.md` (207 linjer)
- `spec/supplements/sup-003.md` (336 linjer, normative)

### Changed
- CP registry: CP-007/008/009 status PROPOSAL → MERGED
- CP registry: CP-003 status confirmed MERGED (was incorrectly referenced as UTKAST in TOGAF v1.1)
- Sup registry: Sup-003 status DRAFT → MERGED
- `spec/supplements/sup-003.md`: status DRAFT → MERGED

### Fixed
- Part 4 completeness: task_source_contract.yaml now complements availability_provider_contract.yaml
- Agent types aligned: `human`, `robot`, `cockpit` (Part 3 Information Model)

---

## [2026a-draft] — 2026-08-22

### Merged
- **CP-006** CostModel generalization — `cost_factors` array in Part 3 Information Model

---

## [2026a-draft] — 2026-08-21

### Merged
- **CP-005** Pin VDA 5050 version to 2.1 — all references to "VDA 5050" now mean v2.1
- **Sup-003** BMS Infrastructure Contract — scope proposal

---

## [2026a-draft] — 2026-08-18

### Merged
- **Sup-002** Annex A — Engineering Practice Notes

---

## [2026a-draft] — 2026-08-12

### Added
- **Part 1** Overview and Scope — architecture, terminology, IT/OT zone model, partner planes
- **Part 2** Conformance — L1–L3 levels, conformance statement template, build provenance
- **Part 3** Information Model — agent, task, capability, cost_model, data_profile, compliance_event
- **Part 4** Service Contracts — availability_provider_contract.yaml
- **Part 5** Transport Profile — VDA 5050 binding, capability registry, conformance levels
- **Part 6** Security — identity-trust.yaml (4 principles)
- **Part 7** Data Governance — data_governance_module.yaml (4 principles)
- **Sup-001** Orchestrator Service Interface — 13 normative endpoints

### Merged
- **CP-001** Split architecture figure from Part map
- **CP-002** Remove FILE scaffolding from CONFORMANCE.md
- **CP-003** GOVERNANCE.md — funding, held-in-trust, Advisory Board

---

[2026a-draft]: https://github.com/RocomFoundation/rocom-standard/
