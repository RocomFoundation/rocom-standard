# FILE: AGENTS.md
# Kvasir project instructions for rocom-standard

## Project Identity
**RoCom Standard** — Open, vendor-neutral specification for robot-enterprise integration.
Edition 2026a, 7 Parts, CC-BY 4.0. Owned by ROCOM (CVR 46774043).
NOT an implementation. NOT a product. A specification.

## Boundary Rules — Critical

| Boundary | Rule |
|----------|------|
| **RoCom Standard vs HRRM** | Standard = WHAT (specification). HRRM = HOW (implementation platform). Never conflate. |
| **Memory Project** | RoCom Standard artifacts use techhappens Memory (229d3378). HRRM uses the SAME Memory project but different EPF instances. |
| **EPF Instances** | RoCom Standard: `_instances/rocom-standard` (in epf-portfolio/techhappens). HRRM: `_instances/hrrm` (in health-robotics). Separate. |
| **Code** | RoCom Standard has NO implementation code. All Rust/Go/TypeScript lives in HRRM or other implementers. |
| **Capability Profiles** | New topics under `rocom/v0/*` require checking existing Part 2 §3.3 and Part 4 contracts first. |

## RoCom Standard Structure

```
rocom-standard/
├── spec/
│   ├── part-01-overview/     # Architecture, zone model, terminology
│   ├── part-02-conformance/  # L1-L3 levels, conformance statements
│   ├── part-03-information-model/  # Agent, task, capability types (YAML schema)
│   ├── part-04-services/     # Availability Provider, Task Source contracts
│   ├── part-05-transport/    # VDA 5050 binding, capability profiles
│   ├── part-06-security/     # Machine identity, mTLS, trust chain
│   ├── part-07-data-governance/  # Classification, egress, Art. 30
│   ├── cp-*.md               # Capability Profile proposals
│   └── supplements/          # Normative updates between editions
├── docs/                     # Informative guidance, examples
├── api/                      # API bindings (VDA 5050)
└── audit/                    # Certification artifacts
```

## Specification Parts — Dependency Order

Part N requires Parts 1 through N-1. Part 3 (Information Model) is foundation — Parts 4-7 reference its types verbatim.

| Part | Layer | Runtime? |
|------|-------|----------|
| 1 | Overview & Scope | No (meta-spec) |
| 2 | Conformance | No (meta-spec) |
| 3 | Information Model | Foundation |
| 4 | Service Contracts | Yes |
| 5 | Transport Profile | Yes |
| 6 | Security | Yes |
| 7 | Data Governance | Yes |

## IT/OT Zone Model

```
IT Zone ←→ Convergence Layer ←→ OT Zone
(HR, ERP, Tasks)  (mTLS, VDA 5050, Audit)  (Robot Fleet, BMS, Vendor)
```

All cross-zone data flow passes through Convergence Layer (Part 7, dg-p-001).

## Four Contract Planes

| Plane | Role | Part |
|-------|------|------|
| 1 | BMS Infrastructure (doors, elevators) | Part 5 |
| 2 | Robot Vendor (conformant platforms) | Part 5 |
| 3 | Availability Provider (HR/turnus) | Part 4 |
| 4 | Task Source (enterprise task gen) | Part 4 |

## Workforce — Existing Coverage

Workforce concepts are ALREADY covered by RoCom:
- **Part 2 §3.3**: Roles and availability at L1, allocation updates at L2, dynamic offer/accept/decline/reallocate at L3
- **Part 4**: Availability Provider Contract defines the interface

**Before proposing new `rocom/v0/workforce/*` topics:**
1. Check Part 2 §3.3 for existing coverage
2. Check Part 4 Availability Provider Contract
3. Only propose new topics if existing contracts cannot express the scenario

## Workforce Demo Scenario (per EG-001 feedback)

First demo should show HRRM offering task handoff to simulated receiving team:
1. Operator accepts → task completes
2. Repeat with decline or expired offer → HRRM escalates or replans
3. Tests all four planes: Robot, Infrastructure, Task, Workforce
4. L0-L3 level assessed per plane

## When Working in This Repo

1. **Never write implementation code** — this is a specification repo
2. **Spec changes follow supplement process** — normative content between editions goes through supplements
3. **Capability Profiles** — new profiles go through cp-registry process
4. **Conformance** — changes to L1-L3 levels require Part 2 review
5. **Cross-references** — Parts 4-7 reference Part 3 types verbatim; changes to Part 3 cascade

## Memory Graph — Relevant Entities

| Entity | Key | Role |
|--------|-----|------|
| Standard:rocom-standard | `rocom-standard` | The specification |
| Standard:rocom-conformance | `rocom-conformance` | Conformance test harness |
| ProjectStrategy:rocom-hrrm-strategy | `rocom-hrrm-strategy` | Implementation strategy (aligns_with Standard) |
| EPFInstance:rocom-epf | `rocom-epf` | HRRM's EPF instance (health-robotics) |
| EPFInstance:rocom-standard | `epf-rocom-standard` | RoCom Standard's EPF instance (strategy-server) |

Relationship: `rocom-hrrm-strategy aligns_with rocom-standard`

**Relasjonsemantikk:**
- `aligns_with` — strategi beskriver intensjon om å følge standarden (conformance_level: planned)
- `relates_to` — feature kobles til spec-seksjon (uten testbevis)
- `implements` — reservert for kode→krav med testbevis (krever: krav-ID, standard-revisjon, kodecommit, CI-resultat)
- `contributes_to` — feature bidrar til produkt (verdi/evne)
- `tests` — CI-bevis tester feature
- Vekt 0.95 = tillit til koblingen; testresultat viser hva som er verifisert

## Strategy Server

- Running on port 9094, PostgreSQL backend (shared with memory-db)

### Instances (parallel under techhappens)

| Instance | Instance ID | EPF Path |
|----------|-------------|----------|
| **RoCom Standard** | `320f5a31-f1aa-492f-a649-41dbe4ad621a` | `epf-portfolio/techhappens/_instances/rocom-standard/docs/EPF/_instances/rocom-standard` |
| **HRRM** | `f4b918cf-96d9-4602-9e09-def25b981160` | `epf-portfolio/techhappens/_instances/hrrm` |

**Relationship:** `ProjectStrategy:rocom-hrrm-strategy aligns_with Standard:rocom-standard`

**Boundary:** RoCom Standard defines WHAT (open spec). HRRM defines HOW (implementation platform). Never conflate.
`aligns_with` indicates strategic intent to conform. `implements` is reserved for code→requirement traceability with test evidence.
