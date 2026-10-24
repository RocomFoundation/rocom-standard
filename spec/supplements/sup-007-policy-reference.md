# FILE: spec/supplements/sup-007-policy-reference.md
# Status: DRAFT — under review
# License: CC-BY 4.0 (see LICENSE-SPEC)
# Title: Versioned Policy References and Namespaced Extensions
# Registry: Sup-007 (next available per cp-registry.md)

This supplement defines the interoperable policy reference model used
throughout the specification. It extends the authority and audit
mechanisms already established in cpl-req-008 (authority and human
decisions), cpl-req-012 (auditable decisions), cpl-req-904 (profile
changes), CP-008 (resource authority) and CP-009 (priority and
preemption). It does not create a competing authority source.

## 1. Scope

The standard requires that coordination decisions reference applicable
policies: authorisation for dynamic coordination (cpl-req-008), audit
correlation (cpl-req-012), and versioned profile changes (cpl-req-904).
This supplement provides the minimum interoperable reference format so
that different implementations can identify, verify and audit the
same policy version without sharing policy content.

A policy reference is a pointer to a versioned policy document or
rule set. It does not carry the policy content. Content exchange
between authorised participants follows the applicable transport
profile and data-governance rules (Part 5, Part 7).

## 2. Policy Reference Envelope

Every policy reference carried in a ROCOM interface SHALL contain the
following fields. Extensions MAY add namespaced fields.

| Field | Type | Required | Description |
|---|---|---|---|
| `policy_id` | string | Yes | Stable identifier within its namespace. |
| `namespace` | string | Yes | The authority or registry that defines the identifier format. |
| `version` | string | Yes | Version string; format is namespace-defined. Consumers SHALL reject incompatible versions explicitly. |
| `digest` | string | Yes | Content integrity reference (e.g., `sha256:abcd...`). A digest alone does not prove permission. |
| `issuer` | string | Yes | The entity that created the policy. Must match a known identity (Part 6). |
| `approval_ref` | string | Yes | Reference to the authorisation that approved this version. A digest without approval is insufficient. |
| `valid_from` | datetime | Yes | ISO 8601 timestamp. The policy is not applicable before this time. |
| `valid_until` | datetime | No | ISO 8601 timestamp. Absence means the deployment owner is responsible for timely review and revocation. |
| `scope` | object | Yes | See §2.1. |
| `required_extensions` | string[] | No | Namespaced extension identifiers that MUST be supported by consumers. |
| `optional_extensions` | string[] | No | Namespaced extension identifiers that MAY be ignored by consumers that do not support them. |

### 2.1 Scope Object

| Field | Type | Description |
|---|---|---|
| `interfaces` | string[] | Applicable plane interfaces (e.g., `["robot", "infrastructure"]`). |
| `workflows` | string[] | Applicable workflow identifiers. |
| `operations` | string[] | Applicable operations within the scope. |
| `sites` | string[] | Applicable site identifiers. |
| `contract_versions` | string[] | Applicable service/transport contract versions. |

## 2.2 Behaviour for Missing or Invalid Policy

When a required policy reference is unknown, unavailable, expired,
revoked or incompatible, the consumer SHALL:

1. **Not silently accept** the request or produce a best-effort result.
2. Produce an explicit refusal or escalation, identifying the policy
   reference and the reason for rejection.
3. If a degraded-mode policy is approved, enter that mode explicitly
   and record the decision with the policy reference that triggered it.

## 3. Namespaced Extensions

Extensions follow a DICOM-inspired model (informative reference:
PS3.5 §7.8). Private/namespaced extensions:

- Use a `namespace:field` identifier format.
- MAY add fields to the policy reference envelope.
- SHALL NOT replace required public semantics.
- SHALL NOT change the meaning of required fields.
- SHALL NOT bypass authority checks (cpl-req-008) or audit
  requirements (cpl-req-012).

A consumer that encounters an unsupported identifier in
`required_extensions` SHALL refuse or escalate. An unsupported
identifier in `optional_extensions` MAY be ignored.

## 4. Authority Boundaries

- Binding safety, identity, audit, resource authority and reserved
  human decisions are outside negotiable policy weights.
- A local coordinating group may coordinate policy development, but
  cannot acquire clinical, employer, building or robot-safety
  authority merely by approving a document.
- Learning/AI systems may propose a policy change; they do not gain
  authority to approve or activate it. Activation follows authenticated,
  versioned approval and traceable change execution.
- Namespacing is not confidentiality or access control. Distinguish
  a public schema from deployment records exchanged only among
  authorised participants.

## 5. Illustrative Policy Reference — Informative

```yaml
policy_id: "hospital-lift-sharing-policy"
namespace: "urn:facility:st-olavs"
version: "2.1.0"
digest: "sha256:a1b2c3d4e5f6..."
issuer: "spiffe://st-olavs.hospital/authority/facilities"
approval_ref: "board-minutes-2026-09-15/item-7"
valid_from: "2026-10-01T00:00:00Z"
valid_until: "2027-03-31T23:59:59Z"
scope:
  interfaces: [infrastructure, robot]
  workflows: ["meal-transport", "linen-run"]
  operations: ["lift_request", "lift_release", "zone_authorization"]
  sites: ["st-olavs-main"]
  contract_versions: ["sup-003-v1.0"]
required_extensions: []
optional_extensions:
  - "local:priority-weighting-v1"
```

## 6. Verification Contract

Implementations that consume policy references SHALL implement the
following verification contract. The contract is ordered: each step
must succeed before the next is evaluated.

### 6.1. Structural Validity

The reference SHALL contain all required fields (§2). The `digest`
SHALL use the `sha256:` prefix. The `valid_from` and `valid_until`
SHALL be parseable ISO 8601 timestamps. `scope.interfaces` SHALL be
non-empty.

### 6.2. Temporal Validity

The current time SHALL be >= `valid_from`. If `valid_until` is present,
the current time SHALL be < `valid_until`. A policy with `valid_until`
in the past SHALL be treated as expired and SHALL NOT be used for
new coordination decisions. Existing trips may complete per Sup-003
§3.4 (trip expiry).

### 6.3. Identity Verification

The `issuer` SHALL be verifiable against Part 6 machine-identity
requirements. The `namespace` SHALL match the issuer's declared
authority scope. A policy from an unauthorised issuer SHALL be rejected.

### 6.4. Approval Binding

The `approval_ref` SHALL reference an identifiable approval artefact
(board minutes, committee resolution, automated approval pipeline).
A policy reference without a verifiable `approval_ref` SHALL be
rejected: content integrity alone (digest) does not establish
authorisation. The approval artefact SHALL be independently auditable.

### 6.5. Content Integrity

The `digest` SHALL be computed over the normative text of the policy
version. Implementations that have access to the policy content SHALL
verify the digest matches. A digest mismatch SHALL be treated as
content tampering and SHALL trigger rejection.

### 6.6. Revocation

The issuer MAY publish a revocation for a policy version. Consumers
SHALL check for revocation within the declared freshness interval
(default: 24 hours from last check). A revoked policy SHALL be
treated as invalid regardless of `valid_until`. Revocation is a
separate artefact from expiration: a policy may be revoked before
its `valid_until`.

### 6.7. Scope Applicability

The consumer SHALL verify that the policy `scope.interfaces` includes
at least one interface relevant to the coordination decision. A policy
whose scope does not cover the applicable interface SHALL be treated
as not applicable, not as invalid.

### 6.8. Version Compatibility

The consumer SHALL verify it supports the policy `version`. If the
consumer only supports earlier versions, it SHALL refuse or escalate
— not silently apply an older interpretation. The version comparison
semantics are namespace-defined; consumers SHALL NOT assume
backward compatibility of major versions.

### 6.9. Extension Handling

- `required_extensions`: The consumer SHALL support every listed
  extension. If any required extension is unsupported, the consumer
  SHALL refuse the policy reference.
- `optional_extensions`: The consumer MAY ignore unsupported optional
  extensions. Optional extensions SHALL NOT override required field
  semantics.
- Extensions SHALL NOT modify the meaning of `digest`, `issuer`,
  `approval_ref`, `valid_from`, `valid_until`, or `scope`.

## 7. Test Cases

| Test | Requirements | Stimulus | Pass Condition |
|---|---|---|---|
| POL-T01 | §2, §6.1 | Valid policy reference with all required fields | Accepted and correlated to decision evidence |
| POL-T02 | §6.4 | Missing `approval_ref` | Rejected: digest alone is insufficient |
| POL-T03 | §6.2 | Expired policy (`valid_until` in past) | Explicit refusal; degraded mode not assumed |
| POL-T04 | §6.6 | Revoked policy (issuer publishes revocation) | Explicit refusal within declared freshness |
| POL-T05 | §6.3 | Unknown/unauthorised issuer | Explicit refusal; no best-effort guess |
| POL-T06 | §6.8 | Version incompatibility (consumer supports v1, policy is v3) | Explicit refusal or escalation |
| POL-T07 | §6.9 | Unsupported required extension | Explicit refusal |
| POL-T08 | §6.9 | Unsupported optional extension | Accepted; extension ignored |
| POL-T09 | §6.9 | Extension attempts to override required field | Rejected; standard semantics preserved |
| POL-T10 | §6.5, cpl-req-012 | Decision evidence records exact `policy_id` + `version` + `digest` | Auditable trace from decision to policy version |

## 8. Registry Update

This document is assigned **Sup-007** from the CP/Supplement registry
(cp-registry.md). The registry is updated in the same commit.

## 9. Relation to the Specification

This supplement extends:
- **cpl-req-008**: Policy references provide the verifiable authorisation
  that dynamic coordination operates within.
- **cpl-req-012**: Decision evidence now carries structured policy references.
- **cpl-req-904**: Profile changes use the policy reference envelope for
  versioned, authorised changes.
- **CP-008**: Resource authority grants reference applicable policies.
- **Part 6**: `issuer` identity follows Part 6 machine-identity requirements.
- **Part 7**: Policy content exchange follows data-governance rules.

No normative requirements in Parts 1–7 are weakened or replaced.

## 10. Schema Validation

The policy reference schema is validated by `build/test_policy_reference.py`.
The coordination declaration schema is validated by
`build/test_coordination_declaration.py`. Both suites are wired into
the site build process.
