# ROCOM Standard — CH Audit Report v0.8.3

**Date:** 2026-11-19
**Auditor:** Kvasir (CH v0.8.3, deterministic templates)
**Scope:** ROCOM Standard normative specification (Parts 1–7, Supplements 1–8, CP Registry through CP-013)
**Branch:** `cp-remove-internal-brief-20261030` at `8e4e1a0`
**Base commit:** `33d60c3` (Edition 2026a published)

---

## Executive Summary

The ROCOM Standard Edition 2026a is a well-structured specification for robot-human coordination in healthcare environments. The normative core (Parts 1–5) is internally consistent. Parts 6–7 (Security, Data Governance) introduce deployment-profile dependencies that defer verification to external configuration. CP-010–013 (BMS extensions) are MERGED status but untracked in git — normative weight rests solely on `cp-registry.md`.

**Overall warrant status:** PARTIALLY WARRANTED — normative claims are internally consistent but lack independent verification (conformance test results, deployment-profile parameters unresolved).

### Key Findings

| # | Severity | Area | Finding |
|---|----------|------|---------|
| 1 | High | CP-010–013 | Spec files exist on disk but are untracked in git. Normative authority only via cp-registry.md (blob `c49d5ab5...`). |
| 2 | High | Parts 6–7 | 20 requirements reference `PENDING-DEPLOYMENT-PROFILE` parameters (12 i Part 6, 8 i Part 7). Cannot verify conformance until deployment profiles are defined. |
| 3 | Medium | Part 2 | Service levels L0–L3 are cumulative per plane but cross-plane interactions undefined. A system at L2 Robot + L1 Infrastructure has undefined coordination semantics. |
| 4 | Medium | Part 4 | Availability provider contract defines `response_deadline` field but no normative requirement on how robots must respond to deadline expiry. |
| 5 | Medium | Part 5 | VDA 5050 v2.1.0 pinned (CP-005) but Part 5 transport profile does not specify which VDA 5050 message types are in scope. |
| 6 | Low | Part 3 | Information model YAML uses `oneOf` for action types but no conformance test references the discriminator. |
| 7 | Low | Sup-003 | BMS contract defines 4 elements but does not define error response schema for malformed requests. |
| 8 | Low | CP-011 | DS-12 dead-door detection requires orchestrator to correlate leases with door state — orchestrator-side requirement not in Part 1 architecture. |
| 9 | Low | CP-012 | EB-13 requires reassignment within 30 seconds — orchestrator-side SLA, not BMS connector requirement. |
| 10 | Informational | Part 6 | Security tier mapping to IEC 62443 is informative, not certifiable. Stated explicitly — acceptable. |

---

## Normative Consistency Analysis

### Internal Consistency

**PASS** — No contradictory requirements found across Parts 1–5. The specification maintains consistent terminology:
- "orchestrator" consistently refers to the coordination layer (Part 1 definition)
- "connector" consistently refers to protocol adapters at the IT/OT boundary
- Service level progression (L0→L1→L2→L3) is cumulative and monotonic

**FLAG** — Parts 6–7 introduce requirements that reference Part 4 contract fields (`data_classes_delivered`, `declared_destinations`) not present in the current Part 4 YAML. This is a forward-reference pattern: Part 7 requires Part 4 extension. **Not a contradiction, but a dependency ordering risk.**

### Normative vs Informative Separation

**PASS** — The specification clearly marks informative sections:
- Part 2 regulatory mapping: "informative (not certifiable)" for IEC 62443
- Part 6 deployment profiles: `PENDING-DEPLOYMENT-PROFILE` markers explicit
- CP-010–013 §6 "Relationship to existing control planes": informative cross-references

**FLAG** — CP-010–013 problem statements (§1) and design basis (§2) are normative files containing informative content. This is acceptable for design documents but blurs the normative boundary. The normative requirements are clearly marked (§3, requirement IDs LV-10 through LR-15).

### Ambiguity Assessment

**Low ambiguity** — Requirement IDs (LV-10, DS-10, EB-10, LR-10) provide unambiguous cross-references. Quantitative thresholds specified (10 s LWT response, 30 s dead-door detection, 5 s release processing, 30 s reassignment).

**Minor ambiguity** — "Configurable intervals (default 30 s)" in LV-10: no range or minimum specified. Implementation may use 1 s or 300 s without violating the spec.

---

## Conformance Test Coverage

| Spec Element | Conformance Tests Referenced | Tests Defined | Gap |
|---|---|---|---|
| Part 1 (Overview) | None | 0 | Architecture descriptions, no tests |
| Part 2 (Conformance) | References test IDs | 0 | Framework only |
| Part 3 (Info Model) | DG-01, DG-04 | 0 | Schema review tests pending |
| Part 4 (Services) | CT-ID-10/11/12 | 0 | Contract-level tests pending |
| Part 5 (Transport) | None explicit | 0 | VDA 5050 profile tests pending |
| Part 6 (Security) | ID-01, ID-02, CT-ID-10/11/12, ID-20-23 | 0 | 11 test IDs referenced, none defined |
| Part 7 (Data Gov) | DG-01-04, DG-10-12, DG-20-22, DG-30 | 0 | 13 test IDs referenced, none defined |
| CP-010–013 | None | 0 | New requirements, no test IDs |

**CRITICAL:** The specification references 24+ conformance test IDs but does not contain test definitions. This is acceptable for a specification (tests typically in separate repository), but it means no normative claim can be verified as `warranted` without access to the test suite.

---

## Evidence Provenance

| Artifact | Blob SHA | Git Status | Normative Weight |
|---|---|---|---|
| `cp-registry.md` | `c49d5ab59c3e9e230004298e05a25a9eb3fb5f40` | Committed | Full — committed normative registry |
| `cp-010-connector-liveness.md` | `179ac2f9a49d473a29da184d653bee399b525b63` | Untracked | Partial — detailed spec, but git authority via cp-registry only |
| `cp-011-door-state.md` | `a618174d2cbcafe65dc14eaa398b7d7a793140be` | Untracked | Partial — same as above |
| `cp-012-elevator-boarding.md` | `4efc3e94eb0c1812db519a48dd400422111f14ca` | Untracked | Partial — same as above |
| `cp-013-lease-return.md` | `55aeaa8369e0dbabe9994f65caa06449b0f181ee` | Untracked | Partial — same as above |
| `SERVICE-LEVELS.md` | `faf5c89a44149f4d99364ded27bc916e2086d949` | Committed | Full |
| `PROFILE.md` | `f08786427f91e03381d01edf2d4ebc102a37f4ac` | Committed | Full |
| `sup-003.md` | `3ba9c3e6f4788423c06e6ccd197f3c1b1ee6cb42` | Committed | Full |
| `identity-trust.yaml` | `55f92b2930ae8c32e50ea7f649c3bfeb0b295815` | Committed | Full |
| `data_governance_module.yaml` | `6169524507d48c9f5f7f0da1d843dcc9dfd74d8d` | Committed | Full |

---

## Warrant Assessment (CH Framework)

Using Superretometer v0.8.3 deterministic templates:

| Claim Category | Evidence Tier | Warrant Status | Justification |
|---|---|---|---|
| Architecture (Part 1) | Documented | PARTIALLY WARRANTED | Internally consistent, no independent deployment evidence |
| Service Levels (Part 2) | Documented | PARTIALLY WARRANTED | Cumulative model sound, cross-plane interactions undefined |
| Information Model (Part 3) | Schema YAML | PARTIALLY WARRANTED | Valid YAML, no conformance test execution |
| Service Contracts (Part 4) | YAML contracts | PARTIALLY WARRANTED | Well-formed, but Part 7 forward-refs not yet in Part 4 |
| Transport Profile (Part 5) | Documented | PARTIALLY WARRANTED | VDA 5050 v2.1.0 pinned, message type scope unclear |
| Security (Part 6) | Documented | UNWARRANTED | 12 of 16 requirements depend on PENDING-DEPLOYMENT-PROFILE |
| Data Governance (Part 7) | Documented | UNWARRANTED | 8 of 13 requirements depend on PENDING-DEPLOYMENT-PROFILE |
| CP-010–013 (BMS) | Documented | UNWARRANTED | Spec exists, implementation exists, no CI verification, untracked in git |

---

## Recommendations

1. **Track CP-010–013 in git** — commit to `main` or merge branch to establish normative provenance.
2. **Define deployment-profile parameters** — Parts 6–7 cannot be verified until `PENDING-DEPLOYMENT-PROFILE` markers are resolved.
3. **Publish conformance test definitions** — 24+ test IDs referenced but no test suite found in spec repo.
4. **Add LV-10 minimum heartbeat interval** — prevent pathological implementations.
5. **Extend Part 4 contracts** — add `data_classes_delivered` and `declared_destinations` fields required by Part 7.
