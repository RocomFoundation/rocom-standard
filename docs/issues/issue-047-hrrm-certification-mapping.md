# Issue #47: Map HRRM Against Rocom Certification Program

**Created:** 2026-09-26
**Assignee:** Daniel (Tech Happens / HRRM)
**Priority:** Critical
**Status:** Open
**EPF Reference:** fd-004-rocom-certification-and-ros (HRRM EPF instance)
**Source:** Egil
**Scope:** ROCOM Foundation — certification program execution against first implementation (HRRM)

---

## Background

ROCOM is established as an independent association (CVR 46774043) with certification program (Sup-005). The first step toward hospital acceptance is certifying a real implementation — HRRM — against the full stack.

Hospitals and municipalities do NOT accept vendor ROS-analyses. They require independent certification from ICT providers with ISO 27001 competence and code-level testing.

## Why Control Plane Audit Is Critical

Three autonomous service providers operate simultaneously in the same hospital area. Each optimizes its own operations, but shares bottlenecks: doors, lifts, charging docks, corridors.

Decisions good for one provider create problems for the other two. Without CP-008 and CP-009:
- Provider A holds a lift indefinitely — grant never expires
- Provider B sends its robot through a door Provider C just closed
- "Urgent" means something different to each provider — and everything becomes urgent

Control plane audit ensures every implementation respects the shared rules that allow three independent actors to share infrastructure safely.

---

## Certification Providers (Approved by ROCOM Board)

| Role | Provider | Country | Scope |
|------|----------|---------|-------|
| Regional CP | **Secura** | Denmark | ISO 27001 audit, ROS-analyses, formal certification |
| Regional CP | **Cybercom** | Norway | Code hardening, ISO 27001, ROS for Norwegian municipalities |
| Security Platform | **Aikido Security** | Belgium | Automated Rust code analysis, dependencies, containers |
| Toolchain | **Ferrous Systems / Ferrocene** | Germany | Ferrocene compiler, Supply Chain (libraries, vulnerabilities, air-gapped) |
| API Testing | **Escape** | France | Language-agnostic API and application testing |

**Snyk excluded** — Boston HQ, fails European requirement (Sup-005 IND-REQ-03).

---

## Tasks for HRRM Implementation (11 total)

### Codebase and Toolchain

- [ ] **t01:** Audit HRRM Rust codebase against Ferrocene requirements
  - All Rust must compile with Ferrocene (not rustc)
  - Identify unsafe blocks, FFI boundaries, async patterns
  - Map dependencies to Ferrocene Supply Chain

- [ ] **t02:** Map HRRM against Rocom test suite
  - Run Rocom conformance test suite
  - Identify gaps in Part 4 (Service Contracts) and Part 5 (Transport Profile)

- [ ] **t03:** Demo: Aikido Security on HRRM Rust code
  - Run Aikido on HRRM codebase
  - Verify detection of: unsafe, FFI, vulnerable dependencies, missing access control
  - Results exported with requirement-ID, code version, artifact hash

- [ ] **t04:** Evaluate Ferrocene Supply Chain for HRRM dependencies
  - Set up Ferrocene Supply Chain for Cargo.toml
  - Verify: component overview, vulnerability monitoring, air-gapped mode

- [ ] **t05:** Map HRRM against ISO 27001 requirements
  - Access control, audit logging, data classification, incident response
  - Coordinate pre-audit with Secura/Cybercom

- [ ] **t06:** Integrate Escape API testing into CI/CD
  - API endpoint testing, access control verification

### Control Plane API Audit (Endpoint-by-Endpoint)

- [ ] **t07:** **CP-007 Agent Identity** — Audit all `/agents` endpoints
  - UDI alignment (Unique Device Identification for medical devices)
  - Issuer-agnostic identity
  - Type / configuration / unit distinction (model vs. instance)
  - Regulatory identity fields

- [ ] **t08:** **CP-008 Resource Authority** — Audit resource connectors
  - Grant lifetime with expiry (doors, lifts, docks)
  - Explicit release signaling (not implicit)
  - Capacity modeling: exclusive (doors) vs. shared (lifts)
  - Behavior on communication loss

- [ ] **t09:** **CP-009 Priority and Preemption** — Audit task allocation
  - Shared priority scale (not vendor-specific semantics)
  - Only authorized entities can set priority
  - Preemption rules: patient transport MUST NEVER be interrupted
  - Inflation protection (not everything can be "urgent")

- [ ] **t10:** **CP-006 CostModel + Sup-001 Orchestrator API**
  - CostModel: `cost_factors` array — no collective agreement leakage in public API
  - Sup-001: All normative endpoints implemented:
    - `/agents`: 7 endpoints
    - `/tasks`: 4 endpoints
    - `/audit`: 2 endpoints
  - Product-specific endpoints separated from normative

- [ ] **t11:** Build ROS-analyse template for certified deployments
  - Standardized template aligned with Norwegian/Danish requirements
  - Populated from automated results: Aikido, Ferrocene Supply Chain, CP audit matrix, conformance tests

---

## Demo Requirements Before Provider Contract (Aikido + Ferrous)

1. Real HRRM Rust code: macros, async, unsafe, C/C++ FFI
2. Known test bugs: missing access control, dangerous input, vulnerable libraries
3. Automatic fix suggestions + regression tests with locked Ferrocene
4. Results with requirement-ID, code version, artifact hash

---

## Done Criteria

- [ ] All 11 tasks complete with documented results
- [ ] Pass/fail matrix per endpoint per control plane (CP-006 through CP-009 + Sup-001)
- [ ] Ferrocene pipeline operational (all builds with Ferrocene, not rustc)
- [ ] Aikido integrated in CI/CD with result export
- [ ] First pre-audit with Secura or Cybercom completed
- [ ] ROS-analyse template ready — first hospital accepts without additional review

## Governance Notes

- HRRM (Tech Happens) CANNOT self-certify. Certification comes from independent ICT providers under ROCOM Board oversight (Sup-005 IND-REQ-01, IND-REQ-02).
- Ferrocene qualification covers toolchain scope only — does NOT grant application-level security approval.
- This issue tracks the first certification execution. Results inform future provider onboarding for other implementations.

## Related Files

- EPF: `health-robotics/_instances/hrrm/FIRE/definitions/product/fd-004-rocom-certification-and-ros.yaml`
- Sup-005: `spec/supplements/sup-005-certification-provider.md`
- CP-007: `spec/cp-007-agent-identity.md`
- CP-008: `spec/cp-008-resource-authority.md`
- CP-009: `spec/cp-009-priority-preemption.md`
- CP-006: `spec/cp-006-proposal.md`
- Sup-001: `spec/supplements/Sup-001-Orchestrator-Service-Interface.md`
