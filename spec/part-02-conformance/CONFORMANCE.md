# =====================================================================
# Rocom — Part 2: Conformance
# Status: DRAFT 0.1 (2026-08-12) — Edition 2026a (draft)
# License: CC-BY 4.0 (see LICENSE-SPEC)
# =====================================================================

# 1. Conformance Levels

A system claiming Rocom conformance declares a level per Part. Levels
are cumulative: a system at L2 satisfies all L1 requirements of that
Part. Healthcare-specific requirements (chain of custody, restricted
zone enforcement) may apply at any level — they are a profile
dimension, not a level dimension.

| Level | Name | Scope |
|-------|------|-------|
| L1 | Pilot | Minimal conformance for proof-of-concept and controlled evaluation. |
| L2 | Single Site | Full production readiness for a single deployment (hospital or municipality). |
| L3 | Multi-Site | Federated operations across multiple deployments; automatic lifecycle management. |

## 1.1 Dimensions

Conformance has two independent dimensions:

1. **Level** (L1–L3): scope of operational complexity — from pilot to
   multi-site federated operations.
2. **Profile** (General / Healthcare): domain-specific requirements.
   The Healthcare profile adds chain-of-custody, restricted zone
   enforcement, and compliance event reporting. These requirements may
   be declared at any level.

A system declaring the Healthcare profile at L1 satisfies all L1
General requirements plus the Healthcare profile additions. This avoids
the previous conflict where Part 5 treated Healthcare as L3-only.

# 2. Conformance Declaration

A conformant implementation MUST produce a Conformance Statement
following the template below. The statement is a public document
published by the implementer. The `build_provenance` section is
mandatory: conformance claims must be reproducible against an
identifiable build artifact, not against source code alone.

# 3. Conformance Statement Template

```yaml
# =====================================================================
# Rocom Conformance Statement
# =====================================================================

# Implementer
implementer:
  organization: "TODO — organization name"
  product: "TODO — product name and version"
  contact: "TODO — email or URL for conformance inquiries"
  statement_date: "TODO — YYYY-MM-DD"

# Scope
conformance_scope:
  parts_declared:
    - part: 1
      level: L1   # or L2, L3
      status: conformant   # conformant / partial / not-tested
    - part: 2
      level: L1
      status: conformant
    - part: 3
      level: L1
      status: conformant
    - part: 4
      level: L1
      status: conformant
    - part: 5
      level: L1
      status: conformant
    - part: 6
      level: L1
      status: conformant
    - part: 7
      level: L1
      status: conformant

  # For each Part with status "partial", list non-conforming requirements:
  deviations:
    - part: 5
      requirement: "p-req-201"
      status: not-implemented
      rationale: "TODO — explanation"
      planned_resolution: "TODO — target date or edition"

# Build Provenance
# Conformance claims must be tied to an identifiable build. Source code
# alone does not constitute evidence: the compiled artifact, toolchain,
# and build environment must be reproducible for audit.
build_provenance:
  toolchain: "TODO — compiler/runtime and version (e.g., 'Ferrocene 26.02.0', 'rustc 1.75.0')"
  target: "TODO — compilation target triple (e.g., 'x86_64-unknown-linux-gnu')"
  build_command: "TODO — reproducible build command (e.g., 'cargo build --release')"
  artifact_hash: "TODO — SHA-256 of the compiled binary or test artifact"
  build_log_reference: "TODO — URL or path to the build log"

# Test Evidence
test_evidence:
  conformance_tests_executed:
    - test_id: "TODO — e.g., DG-01, ID-01"
      result: pass   # pass / fail / not-applicable
      notes: "TODO — test date, environment, any conditions"

# Certification (optional)
certification:
  certified_by: "TODO — certification body, or 'self-declared'"
  certificate_id: "TODO — certificate reference"
  valid_until: "TODO — YYYY-MM-DD"
```

# 4. Partial Conformance

Partial conformance is permitted. An implementer declaring partial
conformance MUST:

1. List every non-conforming requirement in the `deviations` section.
2. Provide a rationale for each deviation.
3. Indicate a planned resolution date or target edition.

Systems with more than three deviations at L2 or above are not
eligible for Rocom Certified status.

# 5. Formal Certification

Formal Rocom Certified status is awarded by the Rocom Certification
Program upon successful execution of the full conformance test suite
at the declared level. The certification program is defined separately
and maintained by the specification steward (see GOVERNANCE.md).
