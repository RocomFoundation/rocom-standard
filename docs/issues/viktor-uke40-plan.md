# Week 40 — Viktor Implementation Plan

**Created:** 2026-09-27
**Assignee:** Viktor
**Priority:** High
**Status:** Planning
**Baseline:** RocomFoundation/rocom-standard, commit `3a7091e`
**Source:** Egil

---

## Context

Week 39 delivered the DRAFT revision proposal for Part 2: Control-plane service levels L0–L3. The proposal is reviewed, pushed, and rendered on the spec site. Week 40 moves from specification to implementation scaffolding.

## Deliverables

### WP1 — Standards mapping (Day 1–2)

**Deliverable:** Requirement migration ledger.

1. Build a ledger that maps every existing L1/L2/L3-tagged requirement in Parts 2–7 and affected Supplements to the new cpl-req IDs.
2. Each entry: old ID, old text, old applicability, new cpl-req ID, semantic change, test mapping.
3. No requirement is weakened, lost, or reassigned solely by changing its level label.

**Reference:** cpl-req-1002 (Requirement migration ledger), §9 Migration.
**Proposal:** `spec/part-02-conformance/control-plane-service-levels-DRAFT.md`

**Definition of done:** Reviewers can see the semantic changes. Zero requirements without trace. No global search-and-replace of L1/L2/L3.

### WP2 — Declaration schemas (Day 2–3)

**Deliverable:** Versioned machine-readable schemas for declarations, plane capabilities, service-quality profiles, operational state, and location mappings.

1. Schema for the `coordination` object: plane interfaces, provision state, target/declared/verification levels, service-profile references.
2. Schema for location identity: `namespace`, `identifier`, `name`, `hierarchy`, `coordinates`, `state`.
3. Schema for cross-namespace location mappings: source/target namespace+ID, granularity, source attribution, validity.
4. Valid and invalid fixtures covering: target vs claim, L0 vs not_provided, evidence vs runtime condition, profile digests, `unknown` granularity mappings.
5. Validator that rejects: L0 automation claims, missing providers as L0, untested targets as conformant, missing timing values, infinite bounds, `unknown` mappings used for automated decisions.

**Reference:** cpl-req-001/003/004/005, cpl-req-801-807, §6 Declaration, §5 Location model.
**Tests:** CPL-T01, CPL-T02, CPL-T03, CPL-T16, CPL-T17, CPL-T18.

**Definition of done:** Schema validates all fixtures. Rejects every invalid case.

### WP3 — Registry and adapters (Day 3–4)

**Deliverable:** Provider/interface registration with version, capability support, per-plane status/freshness, and location mapping store.

1. Register all four adapter types (Robot, Infrastructure, Workforce, Task) with declared levels and capabilities.
2. Location mapping store: CRUD for cross-namespace mappings, granularity enforcement, source attribution, validity tracking.
3. Per-plane status/freshness: disconnected adapters must not appear available.
4. Two distinct units of the same robot type must remain distinguishable.

**Reference:** cpl-req-101/201/301/401, cpl-req-801-807.

**Definition of done:** All four adapter types exercise correctly. Location mappings are verifiable. Disconnected adapter disappears from availability.

### WP4 — Workflow admission (Day 4)

**Deliverable:** Dependency declaration, minimum-level/capability matching, location resolvability checks, assurance checks, rejection reasons.

1. Admit or reject workflows based on declared dependencies, minimum levels, capabilities, and location resolvability.
2. Location resolution: task destination must resolve through Infrastructure's resource model. `unknown` granularity → reject or escalate.
3. Incompatible contract/profile versions → reject end-to-end claim.
4. Explicit rejection reasons for every failure mode.

**Reference:** cpl-req-501/502/503, cpl-req-807.
**Tests:** CPL-T13, CPL-T14.

**Definition of done:** Mixed-level, absent-plane, incompatible-version, and unresolvable-location fixtures all behave as specified.

### WP5 — Dynamic coordination (Day 5)

**Deliverable:** State-driven replanning with commitment acknowledgements/refusals, bounded negotiation, retries, leases, release, reconciliation.

1. Replan when availability, capacity, or location state changes.
2. Commitment flows: accept, refuse, escalate within decision deadline.
3. Bounded retry/negotiation cycles — no oscillation or silent starvation.
4. Location state: access grants expire, occupancy changes, building mode restrictions — all reconciled before new commitments.

**Reference:** cpl-req-103/203/303/403, cpl-req-007-011, cpl-req-803/805.
**Tests:** CPL-T04 through CPL-T12, CPL-T15.

**Definition of done:** Per-plane tests pass. Integrated normal/degraded/recovery scenarios pass without manual reconfiguration.

### WP6 — Measurement and evidence (Day 5)

**Deliverable:** Service-profile enforcement, metrics, breach records, test evidence export.

1. Measure and enforce: acknowledgement time, state freshness, change visibility, reevaluation deadline, availability, state recovery, evidence visibility.
2. Report failed requests, timeouts, and breaches — not only completed successes.
3. Profile change handling: versioned, authorised, original measurement context preserved.

**Reference:** cpl-req-901-904 (§6 Measurable service-quality profiles).
**Tests:** CPL-T09-12, CPL-T15-17.

**Definition of done:** Metrics include unsuccessful work. Breaches are observable. Profile changes are versioned.

## Location model — cross-cutting

The new §5 (cpl-req-801 through cpl-req-807) applies across all work packages:

| WP | Location responsibility |
|---|---|
| WP2 | Schema for location identity, cross-namespace mappings, granularity enforcement |
| WP3 | Location mapping store with CRUD and validity tracking |
| WP4 | Location resolvability as admission gate; `unknown` granularity rejection |
| WP5 | Location state reconciliation before new commitments |

## Repository boundaries

- **`rocom-standard`:** Normative text, interoperable schemas, conformance fixtures, test definitions, source references.
- **HRRM implementation:** Product runtime logic, adapter implementations, live coordination engine.
- Use `coordination_level` in APIs — not ambiguous bare `level`.
- Align identities with CP-007, commitments with CP-008, priority with CP-009.

## Open decisions (from §11 of proposal)

1. Service-profile owners and concrete timing bounds for initial workflows.
2. Which workflows require human acceptance vs standing delegated authority.
3. Declaration/schema compatibility period and target Edition release.
4. Certification scope: plane interface vs combined workflow, production evidence expectations.

These do not block producing experimental schemas, simulator fixtures, or a reviewable implementation plan.

## Baseline commit

`3a7091e` — `spec/part-02-conformance/control-plane-service-levels-DRAFT.md` contains the complete proposal with location model.
