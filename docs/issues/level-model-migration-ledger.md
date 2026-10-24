# FILE: docs/issues/level-model-migration-ledger.md
# Status: DRAFT — under review
# License: CC-BY 4.0
# Title: Level-Model Migration Ledger (cpl-req-1002)
#
# Baseline: b7cc75f (Edition 2026a draft)
# Delivered: TBD
# Purpose: Requirement-by-requirement migration ledger per cpl-req-1002.
# Every existing level-tagged requirement in Parts 2–7 and affected Supplements
# is accounted for. No requirement is weakened, lost or reassigned solely by
# changing its numeric level label.

## 1. Scope and Methodology

This ledger covers:
- **SERVICE-LEVELS.md** (§2–§9): 43 cpl-req requirements (001–012, 101–103, 201–203, 301–303, 401–403, 501–504, 801–807, 901–904, 1001–1004)
- **Part 6 (identity-trust.yaml)**: 12 requirements (it-req-001–004, it-req-101–104, it-req-201–204)
- **Part 7 (data_governance_module.yaml)**: 12 requirements (dg-req-001–004, dg-req-101–104, dg-req-201–203, dg-req-020)
- **Part 5 (PROFILE.md)**: P-2.1.1–P-2.1.5 (L1), P-2.2.1–P-2.2.4 (L2), P-2.3.1–P-2.3.5 (L3)
- **Sup-003**: 13 BMS test cases (BMS-01–13) with level tags
- **CONFORMANCE.md**: legacy level definitions (L1=Pilot, L2=Single Site, L3=Multi-Site)
- **Overview/ARM**: informative level references

**Baseline:** `b7cc75fee9dbd2eaaf3226704875bfea163876ad` (Edition 2026a draft, pre-PR#10)
**Delivered:** Recorded at commit time

**Old model:** L1 = Pilot, L2 = Single Site, L3 = Multi-Site (deployment-scale axis)
**New model:** L0 = Manual, L1 = Static Integration, L2 = State-Aware, L3 = Fully Dynamic (coordination-capability axis)

The old model tied level to deployment scope. The new model separates coordination capability from deployment scope, stage, and assurance.

## 2. SERVICE-LEVELS.md — cpl-req Requirements

These requirements ARE the new model. They are ADOPTED (Edition 2026a) and do not need migration. They replace the legacy level definitions in CONFORMANCE.md §1–§1.1.

| ID | Level(s) | Semantic Change | Test Mapping |
|---|---|---|---|
| cpl-req-001 | All | NEW: per-plane declaration scope | CPL-T01 |
| cpl-req-002 | L1–L3 | NEW: cumulative levels | CPL-T02 |
| cpl-req-003 | L0 | NEW: manual participation | CPL-T01 |
| cpl-req-004 | All | NEW: target vs declared vs operational | CPL-T01 |
| cpl-req-005 | All | NEW: versioned context | CPL-T01 |
| cpl-req-006 | All | NEW: assurance not waived by level | CPL-T03 |
| cpl-req-007 | L3 | NEW: fully dynamic meaning | CPL-T04 |
| cpl-req-008 | L3 | NEW: authority preservation | CPL-T08 |
| cpl-req-009 | L1–L3 | NEW: correlation | CPL-T09 |
| cpl-req-010 | L2–L3 | NEW: freshness/recovery | CPL-T10 |
| cpl-req-011 | L3 | NEW: bounded resolution | CPL-T11 |
| cpl-req-012 | L1–L3 | NEW: auditable decisions | CPL-T12 |
| cpl-req-101–103 | L1–L3 | NEW: Robot plane requirements | CPL-T04 |
| cpl-req-201–203 | L1–L3 | NEW: Infrastructure plane requirements | CPL-T05 |
| cpl-req-301–303 | L1–L3 | NEW: Workforce plane requirements | CPL-T06 |
| cpl-req-401–403 | L1–L3 | NEW: Task plane requirements | CPL-T07 |
| cpl-req-501–504 | All/L3 | NEW: composition rules | CPL-T13–15 |
| cpl-req-801–807 | All | NEW: location model | CPL-T19–22 |
| cpl-req-901–904 | L1–L3 | NEW: service-quality profiles | CPL-T16–17 |
| cpl-req-1001–1004 | All | NEW: migration rules | CPL-T18 |

**Status:** All cpl-req requirements are new (ADOPTED). No legacy equivalent exists — they define the new model.

## 3. Part 6 — Identity & Trust (identity-trust.yaml)

Part 6 uses the OLD level labels in comments: "L1 = pilot / lab", "L2 = production, single site", "L3 = production, multi-site / regional". The requirements themselves are security/assurance requirements that apply at their respective coordination levels.

**Key observation:** Part 6's levels describe security maturity, NOT coordination capability. The new model separates coordination level from security level (cpl-req-006). These requirements MUST NOT be relabeled as coordination levels.

### 3.1 L1 Requirements

| Old ID | Old Level | Old Comment | New Applicability | Semantic Change | Test Mapping |
|---|---|---|---|---|---|
| it-req-001 | L1 | "pilot / lab" | All coordination levels (L0–L3) | NO CHANGE: fundamental identity requirement. Applies regardless of coordination level. | ID-01 |
| it-req-002 | L1 | "pilot / lab" | All coordination levels | NO CHANGE: certificate validity is an assurance requirement, not coordination. | Certificate inspection |
| it-req-003 | L1 | "pilot / lab" | All coordination levels | NO CHANGE: revocation is a baseline security requirement. | ID-02 |
| it-req-004 | L1 | "pilot / lab" | All coordination levels | NO CHANGE: audit logging applies at all levels. | Audit inspection |

### 3.2 Tier 2 — Production-grade security

| Old ID | Old Level | Old Comment | New Applicability | Semantic Change | Test Mapping |
|---|---|---|---|---|---|
| it-req-101 | L2 | "production, single site" | All production deployments (any coordination level) | NO CHANGE: rotation is a production-grade security requirement, independent of coordination level (cpl-req-006). | ID-10 |
| it-req-102 | L2 | "production, single site" | All production deployments | NO CHANGE: revocation propagation is an assurance requirement, not coordination-specific. | ID-11 |
| it-req-103 | L2 | "production, single site" | All production deployments | NO CHANGE: zone model is an architecture requirement. | ID-12 |
| it-req-104 | L2 | "production, single site" | All production deployments | NO CHANGE: CA policy conformance is deployment-profile specific. | Certificate inspection |

### 3.3 Tier 3 — Multi-site / regional security maturity

| Old ID | Old Level | Old Comment | New Applicability | Semantic Change | Test Mapping |
|---|---|---|---|---|---|
| it-req-201 | L3 | "multi-site / regional" | Multi-site deployments (any coordination level) | NO CHANGE: automated identity lifecycle is a deployment-scale security maturity gate, independent of coordination capability. | ID-20 |
| it-req-202 | L3 | "multi-site / regional" | Multi-site deployments | NO CHANGE: central revocation is a scale requirement, not a coordination requirement. | ID-21 |
| it-req-203 | L3 | "multi-site / regional" | Multi-site deployments | NO CHANGE: atomic lifecycle is a scale requirement. | ID-22 |
| it-req-204 | L3 | "multi-site / regional" | Multi-site deployments | NO CHANGE: compromise response is a maturity gate. | ID-23 |

**Important:** Security tier applicability is determined by deployment scope and stage (evaluation/production, single/multi-site), NOT by coordination level. An L0 manual interface in a multi-site production deployment still requires applicable security-tier obligations. See cpl-req-006.

### 3.4 Recommended Editorial Change

The section comments "L1 = pilot / lab", "L2 = production, single site", "L3 = production, multi-site / regional" should be updated to reflect that these are **security maturity tiers** independent of coordination level, per cpl-req-006. Proposed new comment headers:

- L1 → "Baseline security (all deployments)"
- L2 → "Production-grade security"
- L3 → "Multi-site / regional security maturity"

The `level` field values should be renamed to `security_tier` or similar to distinguish from `coordination_level`. This avoids confusion with the new coordination-level model.

## 4. Part 7 — Data Governance (data_governance_module.yaml)

Same pattern as Part 6: levels describe data-governance maturity, NOT coordination capability.

### 4.1 L1 Requirements

| Old ID | Old Level | Old Comment | New Applicability | Semantic Change | Test Mapping |
|---|---|---|---|---|---|
| dg-req-001 | L1 | "pilot / lab" | All coordination levels | NO CHANGE: data profiles are foundational. | DG-01 |
| dg-req-002 | L1 | "pilot / lab" | All coordination levels | NO CHANGE: connection data declarations are foundational. | DG-02 |
| dg-req-003 | L1 | "pilot / lab" | All coordination levels | NO CHANGE: sensor-payload boundary is a spec principle. | DG-03 |
| dg-req-004 | L1 | "pilot / lab" | All coordination levels | NO CHANGE: telemetry minimization is foundational. | DG-04 |

### 4.2 Tier 2 — Production-grade data governance

| Old ID | Old Level | Old Comment | New Applicability | Semantic Change | Test Mapping |
|---|---|---|---|---|---|
| dg-req-101 | L2 | "production, single site" | All production deployments (any coordination level) | NO CHANGE: egress control is a production data-governance requirement, independent of coordination level (cpl-req-006). | DG-10 |
| dg-req-102 | L2 | "production, single site" | All production deployments | NO CHANGE: third-country transfer governance. | Registry inspection |
| dg-req-103 | L2 | "production, single site" | All production deployments | NO CHANGE: flow attribution to identity. | DG-11 |
| dg-req-104 | L2 | "production, single site" | All production deployments | NO CHANGE: Article 30 export. | DG-12 |

### 4.3 Tier 3 — Multi-site / regional data governance maturity

| Old ID | Old Level | Old Comment | New Applicability | Semantic Change | Test Mapping |
|---|---|---|---|---|---|
| dg-req-201 | L3 | "multi-site / regional" | Multi-site deployments (any coordination level) | NO CHANGE: technical egress enforcement is a deployment-scale governance requirement, not coordination-specific. | DG-20 |
| dg-req-202 | L3 | "multi-site / regional" | Multi-site deployments | NO CHANGE: continuous verification. | DG-21 |
| dg-req-203 | L3 | "multi-site / regional" | Multi-site deployments | NO CHANGE: auditable transfer register. | DG-22 |
| dg-req-020 | L1+ | "all tiers where used" | All | NO CHANGE: teleoperation exception. | DG-30 |

**Important:** Data-governance tier applicability is determined by deployment scope and stage, NOT by coordination level. An L1 coordination interface in a multi-site production deployment still requires applicable dg_tier obligations. See cpl-req-006.

### 4.4 Recommended Editorial Change

Same as Part 6: rename `level` → `security_tier` (or `dg_tier`), update comment headers.

## 5. Sup-003 — BMS Infrastructure Contract

Sup-003 §8 contains BMS test cases with L1/L2/L3 tags. These describe
BMS integration maturity — minimum coordination level at which the test
applies. The level tags are unchanged from the original; they describe
the minimum coordination capability needed for the integration pattern.

| Old ID | Min. Level | New Applicability | Semantic Change | Notes |
|---|---|---|---|---|
| BMS-01 | L1 | All levels | NO CHANGE: door access is baseline | |
| BMS-02 | L1 | All levels | NO CHANGE: denial handling | |
| BMS-03 | L2 | L2–L3 | NO CHANGE: elevator dispatch | Min L2 |
| BMS-04 | L2 | L2–L3 | NO CHANGE: boarding status | Min L2 |
| BMS-05 | L2 | L2–L3 | NO CHANGE: zone authorization | Min L2 |
| BMS-06 | L2 | L2–L3 | NO CHANGE: zone expiry | Min L2 |
| BMS-07 | L1 | All levels | NO CHANGE: fire alarm override | |
| BMS-08 | L1 | All levels | NO CHANGE: lockdown override | |
| BMS-09 | L1 | All levels | NO CHANGE: fail-safe | |
| BMS-10 | L3 | L3 only | NO CHANGE: audit correlation | Min L3 |
| BMS-11 | L2 | L2–L3 | NO CHANGE: stand-off queuing | Min L2 |
| BMS-12 | L2 | L2–L3 | NO CHANGE: shared occupancy | Min L2 |
| BMS-13 | L2 | L2–L3 | NO CHANGE: expired trip re-request | Min L2 |

## 6. Part 5 — Transport Profile (PROFILE.md)

Part 5 P-2.* requirements use level labels for transport capability tiers.

| Old ID | Old Level | New Applicability | Semantic Change | Notes |
|---|---|---|---|---|
| P-2.1.1–P-2.1.5 | L1 | L1 (static integration) | NO CHANGE: VDA 5050 baseline | |
| P-2.2.1–P-2.2.4 | L2 | L2 (state-aware) | NO CHANGE: Rocom core extensions | |
| P-2.3.1–P-2.3.4 | Healthcare | All levels | NO CHANGE: Healthcare profile | |
| P-2.3.5 | L3 | L3 (fully dynamic) | NO CHANGE: federated connection state | |

## 6. CONFORMANCE.md — Legacy Level Definitions

CONFORMANCE.md §1–§1.1 defines:
- L1 = Pilot
- L2 = Single Site
- L3 = Multi-Site

These are **replaced** by SERVICE-LEVELS.md §2 (cpl-req-001–012). The old definitions remain for legacy declaration compatibility per cpl-req-1001.

| Old Definition | New Definition | Migration Rule |
|---|---|---|
| L1 = Pilot | L1 = Static Integration | cpl-req-1001: no automatic equivalence |
| L2 = Single Site | L2 = State-Aware Coordination | cpl-req-1002: ledger entry required |
| L3 = Multi-Site | L3 = Fully Dynamic Coordination | cpl-req-1004: new evidence required |

## 7. Part 5 (PROFILE.md) and Informative References

PROFILE.md §40: "Levels follow Part 2 (L1 = Pilot, L2 = Single Site, L3 = Multi-Site)."
**Action:** Update to reference SERVICE-LEVELS.md new definitions.

OVERVIEW.md §33–35, ARM.md §43, §58, §127: Informative references to L1–L3.
**Action:** Update terminology to new model.

## 8. Summary of Changes Required

| Document | Change Type | Affected Lines | Status |
|---|---|---|---|
| `CONFORMANCE.md` | Replace §1–§1.1 level definitions; new declaration template | Lines 7–82 | DONE |
| `identity-trust.yaml` | Rename `level` → `security_tier`; update comments | Lines 71–143 | DONE |
| `data_governance_module.yaml` | Rename `level` → `dg_tier`; update comments | Lines 70–165 | DONE |
| `PROFILE.md` | Update level reference text and section headers | Lines 38–62 | DONE |
| `OVERVIEW.md` | Update level terminology | Lines 33–35 | DONE |
| `ARM.md` | Update level terminology | Lines 43, 58, 127 | DONE |
| `sup-003.md` | Rename BMS table column to "Min. Coordination Level" | Lines 262–277 | DONE |
| `GOVERNANCE.md` | Update certification tier reference | Line 46 | DONE |
| `cp-001.md` | Update conformance reference | Line 47 | DONE |
| `build/build.sh` | Add migration ledger to link_map + build | — | DONE |

## 9. Open Decisions

1. **Field rename in Part 6/7 YAML:** `level` → `security_tier` / `dg_tier` — breaking change for consumers. Requires version bump.
2. **CONFORMANCE.md:** How much legacy text to preserve? Full §1–§1.1 replacement, or add deprecation notice + pointer to SERVICE-LEVELS.md?
3. **Part 5 PROFILE.md:** Does "Healthcare profile at L3-only" historical note need removal? (CONFORMANCE.md §32 already resolves this conflict.)
