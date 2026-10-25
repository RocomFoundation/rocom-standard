# =====================================================================
# Rocom — Part 2: Conformance
# Status: ADOPTED 1.0, Edition 2026a
# License: CC-BY 4.0 (see LICENSE-SPEC)
# =====================================================================

# 1. Conformance Dimensions

A system claiming Rocom conformance declares a coordination service level
per control-plane interface (SERVICE-LEVELS.md §2). Coordination level
expresses the degree of machine integration, state awareness and dynamic
coordination supported by a specific plane interface. It is separate from
deployment scope, deployment stage, security maturity and certification
scope.

Coordination levels L1–L3 are cumulative within a plane: a declaration at
L3 satisfies all L1 and L2 requirements for that plane. See
[SERVICE-LEVELS.md](SERVICE-LEVELS.md) for the full model, per-plane
requirements and composition rules.

Security, identity-trust and data-governance requirements carry their own
maturity tiers (e.g., `security_tier` in Part 6, `dg_tier` in Part 7). A
coordination level SHALL NOT waive any applicable assurance requirement
(cpl-req-006).

## 1.1 Dimensions

Conformance has independent dimensions:

1. **Coordination service level** (L0–L3 per plane): the degree of machine
   integration, state awareness and dynamic coordination. Defined in
   [SERVICE-LEVELS.md](SERVICE-LEVELS.md).
2. **Deployment scope** (`single_site` / `multi_site`): the deployment
   topology covered by the claim.
3. **Profile** (General / Healthcare): domain-specific requirements.
   The Healthcare profile adds chain-of-custody, restricted zone
   enforcement, and compliance event reporting. These requirements may
   be declared at any coordination level.
4. **Security / data-governance maturity**: tiered requirements in Part 6
   and Part 7 independent of coordination level.
5. **Service-quality profile**: versioned, measurable timing, freshness,
   availability and recovery commitments.

A system declaring the Healthcare profile at L1 coordination satisfies all
L1 coordination requirements plus the Healthcare profile additions.

## 1.2 Legacy Level Definitions

Historical declarations used L1 = Pilot, L2 = Single Site, L3 = Multi-Site.
These labels referred to deployment scale, not coordination capability.
They SHALL NOT be mechanically converted into new coordination levels
(cpl-req-1001). Historical claims retain their original meaning; new
claims require the new declaration model and evidence (SERVICE-LEVELS.md
§9).

| Legacy | Meaning | Migration |
|--------|---------|-----------|
| L1 / Pilot | Proof-of-concept evaluation | Requires new per-plane declaration |
| L2 / Single Site | Single deployment production | Requires new per-plane declaration |
| L3 / Multi-Site | Multi-deployment federated | Requires new per-plane declaration |

The [migration ledger](../../docs/issues/level-model-migration-ledger.md)
documents every affected requirement.

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
# Schema version identifies the declaration format (rocom-conformance/control-planes-1.0)
# =====================================================================

schema_version: "rocom-conformance/control-planes-1.0"

# Specification edition this declaration targets
specification:
  edition: "2026a"     # e.g. "2025d", "2026a"
  supplements_in_scope: ["sup-003", "sup-007"]  # supplements that apply

# Implementer
implementer:
  organization: "TODO — organization name"
  product: "TODO — product name and version"
  contact: "TODO — email or URL for conformance inquiries"
  statement_date: "TODO — YYYY-MM-DD"

# Deployment context
context:
  profile: "General"   # or "Healthcare"
  deployment_scope: "single_site"   # or "multi_site"
  deployment_stage: "production"    # or "evaluation"
  sites:
    - name: "site-alpha"
      location: "TODO — facility identifier"

# ── Coordination Interfaces ──
# Each interface declares: target level (what the workflow requires),
# declared level (what the implementer claims), and provision state
# (whether the interface is actually provided).
coordination:
  model_version: "control-plane-levels-1.0"
  interfaces:
    - id: "robot-adapter"           # unique identifier
      plane: robot                  # robot | infrastructure | workforce | task
      provision: provided           # provided | planned | not_provided
      declared_level: L1            # L0, L1, L2, or L3
      target_level: L1              # level required by workflow
      verification_status: conformant   # conformant / partial / not_tested
      requirement_ids: ["cpl-req-101", "cpl-req-102"]  # for L3: all applicable requirements
    - id: "infra-adapter"
      plane: infrastructure
      provision: provided
      declared_level: L1
      target_level: L1
      verification_status: conformant
    - id: "workforce-prov"
      plane: workforce
      provision: planned            # L0 manual handoff is permitted
      declared_level: L0
      target_level: L0
      verification_status: not_tested
    - id: "task-source"
      plane: task
      provision: provided
      declared_level: L1
      target_level: L1
      verification_status: conformant

# ── Workflow Verification ──
# End-to-end level is determined by the lowest coordinating interface.
# cpl-req-503: end-to-end L3 requires every necessary interface at L3.
workflows:
  - id: "meal-transport"
    description: "Meal tray delivery via robot + task source"
    participating_interfaces: ["robot-adapter", "task-source"]
    requirements:
      - interface: "robot-adapter"
        minimum_level: L1
      - interface: "task-source"
        minimum_level: L1
    target_end_to_end_level: L1
    verified_end_to_end_level: L1

# ── Scope Tiers (independent of coordination level, per cpl-req-006) ──
scope_tiers:
  security_tier: 1   # Part 6: 1=evaluation, 2=production, 3=multi-site
  dg_tier: 1         # Part 7: 1=evaluation, 2=production, 3=multi-site

# ── Legacy Parts Declaration (backward compatibility) ──
# Implementers targeting pre-2026a editions may use parts_declared.
# New declarations SHOULD use coordination.interfaces + scope_tiers above.
parts_declared:
  - part: 1
    level: L1   # legacy — see §1.2
    status: conformant
  - part: 2
    level: L1
    status: conformant
  - part: 5
    level: L1
    status: conformant
  - part: 6
    security_tier: 1
    status: conformant
  - part: 7
    dg_tier: 1
    status: conformant

# ── Deviations ──
# For each interface with verification_status=partial, or Part with status=partial:
deviations:
  - interface: "robot-adapter"  # or part: 5
    requirement: "cpl-req-102"
    status: not-implemented
    severity: minor   # critical / major / minor
    rationale: "TODO — explanation"
    planned_resolution: "TODO — target date or edition"

# ── Policy References (Sup-007) ──
# Facility- or site-specific policy references that govern this deployment.
policy_references:
  - policy_id: "facility-transport-policy-v1"
    namespace: "urn:example:facility:transport"
    version: "1.0.0"
    digest: "sha256:..."
    issuer: "spiffe://example.local/authority/policy"
    approval_ref: "board-minutes-2026-10-01/item-3"
    valid_from: "2026-10-01T00:00:00Z"
    scope:
      interfaces: ["robot", "infrastructure"]
      workflows: ["meal-transport"]

# ── Build Provenance ──
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
    - test_id: "TODO — e.g., DG-01, ID-01, cpl-test-101"
      result: pass   # pass / fail / not-applicable
      policy_version: "TODO — policy version applied, if any (Sup-007)"
      notes: "TODO — test date, environment, any conditions"

# Certification (optional)
certification:
  certified_by: "TODO — certification body, or 'self-declared'"
  certificate_id: "TODO — certificate reference"
  scope_tier: "TODO — security_tier or dg_tier certified"
  coordination_levels_covered: ["L1"]  # legacy: was 'level'
  valid_until: "TODO — YYYY-MM-DD"
```

# 4. Partial Conformance

Partial conformance is permitted. An implementer declaring partial
conformance MUST:

1. List every non-conforming requirement in the `deviations` section.
2. Provide a rationale for each deviation.
3. Classify each deviation severity (critical, major, minor).
4. Indicate a planned resolution date or target edition.

Systems with more than three deviations at coordination levels L2 or above,
or at security_tier ≥ 2, or dg_tier ≥ 2 are not eligible for Rocom Certified
status. See Sup-005 CP-REQ-10.

# 5. Formal Certification

Formal Rocom Certified status is awarded by independent Certification
Providers under ROCOM Board oversight upon successful execution of the
full conformance test suite at the declared coordination level, profile,
and applicable scope tiers. The Certification Program is defined in
Sup-005 (Certification Provider Requirements). During the transition
period before providers are appointed, self-declaration of conformance
remains available.

**Three distinct conformance outcomes:**
1. **Self-declaration:** The implementer declares conformance against the
   specification. No independent verification required.
2. **Validator/portal validation:** An automated tool or portal runs the
   conformance test suite and produces a report. This is a validation aid,
   NOT formal certification. The portal operator is not the certification
   authority.
3. **Formal Rocom Certified:** Awarded by an independent Certification
   Provider (Sup-005, IND-REQ-02: not under same corporate ownership as
   the implementer). Only this outcome may use the "Rocom Certified" mark.

## 5.2 Legacy certification — no automatic translation

A legacy certificate (pre-Edition 2026a) with `level: L3` or `level: multi-site`
does NOT automatically imply coordination level L3 under the new model.
Coordination capability must be demonstrated per interface under the new
declaration model (§3). Legacy certificates remain valid for their original
scope until expiration but SHALL NOT be used to claim end-to-end L3
coordination without the corresponding per-interface evidence.

## 5.3 Deviation Severity

Declarations of partial conformance must classify each deviation:

| Severity | Definition | Certification impact |
|----------|-----------|---------------------|
| **Critical** | Security vulnerability, safety hazard, or data integrity failure | Certification blocked. Must be resolved before certification. |
| **Major** | Missing normative requirement that affects interoperability | Maximum 1 major deviation permitted. |
| **Minor** | Implementation difference that does not affect interoperability | Maximum 2 minor deviations permitted. |

Systems with more than three deviations total (any severity) at coordination
levels L2 or above, or at security_tier ≥ 2, or dg_tier ≥ 2 are not eligible
for Rocom Certified status. One or more Critical deviations block certification
regardless of level or tier.
