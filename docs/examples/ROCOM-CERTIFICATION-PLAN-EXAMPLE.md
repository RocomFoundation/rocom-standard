# FILE: docs/examples/ROCOM-CERTIFICATION-PLAN-EXAMPLE.md
# Status: Informative example
# License: CC-BY 4.0
# Title: ROCOM Certification Plan — Example

This vendor-neutral example helps an implementer prepare evidence for ROCOM
conformance assessment and, where available, independent certification.
It is not an application, an approved certification programme or a certificate.
It adds no normative requirements and selects no provider, product,
programming language, compiler or security tool.

## 1. Define the assessment scope

Record the exact specification Edition, requirement set and deployment
profiles before testing. Distinguish coordination capability from applicable
security and data-governance obligations. Where level models are being
revised, document the reviewed requirement mapping rather than relabelling
existing levels.

Example deployment: three robot fleets, two building-management interfaces,
a task-source interface and a workforce interface. Identify each provider,
interface, site and workflow in the actual assessment. Two BMS interfaces
are not automatically interchangeable failover providers for the same
physical resource.

| Planning field | Value to supply for a real assessment |
|---|---|
| Implementer and product | Organisation, product and assessed build |
| Specification baseline | Edition, document versions and requirement identifiers |
| Claimed scope | Parts, interfaces, capabilities, workflows and applicable levels |
| Operational profiles | Timing, freshness, load, availability and recovery bounds |
| Authority | Resource owners, human decisions and delegated permissions |
| Assessor | Independent provider and documented scope, where appointed |
| Exclusions and deviations | Requirement ID, status, impact, rationale and planned resolution |

## 2. Prepare a requirement and evidence ledger

For every applicable requirement, record the source version, test ID,
expected behaviour, observed result, evidence reference and review status.
Keep separate states for pass, fail, not run, blocked and not applicable.
Missing evidence is not a pass; any not-applicable decision needs a rationale.

Retain full source revision, artifact digest, toolchain and dependency
versions, build command, migration/configuration versions, test environment,
timestamps, logs and test exit codes. Evidence should identify the artifact
actually executed, including the container image digest when applicable.
Protect credentials and personal data in the evidence store.

## 3. Example assessment work packages

| Work package | Example activities and evidence |
|---|---|
| Scope and provenance | Verify the declaration, applicable requirement set, assessed artifact and reproducible build evidence. |
| Identity and trust | Test distinct machine identities, onboarding/offboarding, certificate rotation, revocation, denied access and applicable transport protection. |
| Resource authority | Test grant expiry, renewal, explicit release, capacity, communication loss and recovery without assuming that expiry means physical vacancy. |
| Priority and human authority | Verify authorised priority changes, applicable preemption rules, human acceptance/refusal and protection against unauthorised escalation. |
| Interfaces and contracts | Exercise applicable service and transport contracts, including invalid input, retries, duplicates, stale state and incompatible versions. |
| Degradation and recovery | Disconnect one fleet or BMS interface, verify the affected workflow state, preserve independent work and reconcile state before new commitments. Test failover if it is claimed. |
| Data and audit | Verify permitted data flows, minimisation, retention, correlated decisions/outcomes and detection of corrupted evidence. |
| Operational changes | Test scoped administrative permissions, prevalidation, bounded rollout, recovery and emergency access using the selected deployment controls. |

Where failover is claimed, include a test in which the former active instance
returns after replacement. Verify that it cannot create conflicting effective
authority. Specify the expected result from the selected contract and local
profile before running the test.

## 4. Example control-plane audit

Use the applicable editions of CP-007 (agent identity), CP-008 (resource
authority), CP-009 (priority and preemption), Part 4 contracts and Part 5
bindings. Assess the interfaces actually claimed; do not infer conformance
from a demonstration of one endpoint or a successful build alone.

For a workflow involving a task, robot and lift, correlate submission,
acceptance, allocation, resource permission, execution, release and outcome.
Repeat with refusal, dependency loss and recovery. Report every failed or
unexecuted case, not just successful demonstrations.

## 5. Independent review and decision

Use Part 2, GOVERNANCE.md and Sup-005 for the applicable declaration,
provider-independence, assessment and decision procedures. Provider selection
and certification decisions remain with the roles defined there; this example
does not appoint a provider or amend certification criteria.

Independent assessment should inspect the declared deviations and run the
applicable tests against the submitted artifact. Record the outcome and its
scope without turning a partial result into a claim of full certification.
Self-declaration and independent certification remain distinct.

Toolchain qualification or an organisational security certificate does not
establish application-level ROCOM conformance. ROCOM certification does not
replace local risk assessment, regulatory obligations or deployment acceptance.

## 6. Completion and maintenance checklist

- [ ] Scope, Edition, profiles and requirement mapping reviewed.
- [ ] Executed artifact matches the submitted provenance.
- [ ] Each applicable requirement has a reviewed result and evidence reference.
- [ ] Failures, exclusions and unexecuted tests are explicitly reported.
- [ ] Claimed degraded-mode, recovery and failover behaviour has runtime evidence.
- [ ] Assessment decision records the actual scope and limitations.
- [ ] Applicable re-testing, expiry and change-triggered review are scheduled.
- [ ] Public summaries contain no credentials, personal data or private security details.

## Related guidance

- [Controlled Production Changes — Zero Trust and Zero Touch](../security-safety/CONTROLLED-PRODUCTION-CHANGES.md).
- Part 2 — Conformance and service-quality profiles.
- Part 6 — Identity & Trust; Part 7 — Data Governance.
- CP-007, CP-008 and CP-009; applicable service and transport contracts.
- GOVERNANCE.md and Sup-005 — certification governance and provider requirements.
