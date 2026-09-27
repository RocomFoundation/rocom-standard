# Revision proposal — Part 2: Control-plane service levels L0–L3

**Status:** DRAFT PROPOSAL — for review; not an adopted ROCOM requirement.  
**Date:** 27 September 2026.  
**Requested by:** Egil Utheim.  
**Proposed implementation owner:** Viktor, following specification review.  
**Baseline:** RocomFoundation/rocom-standard, commit `ff6803dd9176d9875511cbf5134bdcf6b704f0e6`.  
**Primary target:** Part 2 — Conformance.  
**Also affects:** Parts 3–7, the four control-plane contracts, Sup-001, Sup-003 and certification guidance in Sup-005.  
**Change mechanism:** Full Part revision, with coordinated amendments to affected Parts. No CP or Supplement number is assigned by this draft.  
**Suggested repository location:** `spec/part-02-conformance/control-plane-service-levels-DRAFT.md`.

## Executive decision

Introduce independently declared service levels **L0, L1, L2 and L3 for each of Robot, Infrastructure, Workforce and Task**.

**L3 means fully dynamic coordination during operation, within declared capabilities, authorisations and operating constraints.** It does not mean that an orchestrator takes over a robot's local motion control, the building's safety functions, or decisions reserved to a person.

Keep deployment scope, deployment stage, domain profile and measurable service-quality targets as explicit, separate dimensions. A single hospital can operate at L3. A multi-site deployment can contain lower-level integrations.

The current Part 2 level names — Pilot, Single Site and Multi-Site — cannot be silently relabelled. Historical declarations retain their original meaning; new claims require a versioned declaration and new evidence.

This document contains proposed normative text, a declaration model, migration rules and an implementation brief. The requirement identifiers below are proposed identifiers and are not reserved until the revision is registered and reviewed.

## 1. Rationale and scope — informative

The four planes provide different contributions to the same workflow:

- **Robot:** robot identity, capabilities, accepted work and execution state, usually through a fleet system or adapter.
- **Infrastructure:** access to shared resources such as doors, lifts, spaces and docks, through the responsible building and resource systems.
- **Workforce:** availability, competence and allocation of people and robot capacity, through the responsible staffing and availability systems.
- **Task:** the originating need, its authorised priority, constraints, lifecycle and evidence of completion.

Today, Part 2 describes levels in terms of deployment scale, while the availability and task contracts describe increasing integration and allocation capability. Those meanings are not equivalent. This revision provides one shared meaning for the level axis and separate declarations for operational context.

The standard defines externally observable contracts and outcomes. Vendor planning algorithms, commercial models, local fleet optimisation and staffing policies remain implementation-defined, subject to the declared contracts and existing requirements.

## 2. Proposed replacement for Part 2 §1–§1.1 — normative on adoption

### 2.1 Dimensions

| Dimension | Declaration | Meaning |
|---|---|---|
| Coordination service level | L0–L3 per plane | The degree of machine integration, state awareness and dynamic coordination supported by a specific plane interface. |
| Deployment scope | `single_site` / `multi_site` | The deployment topology covered by the claim. |
| Deployment stage | `evaluation` / `production` | The operational setting in which the implementation is evaluated or used. |
| Domain profile | Existing `General` / `Healthcare` | The applicable domain requirements. |
| Service-quality profile | Versioned profile reference and digest | The measurable timing, freshness, availability and recovery commitments. |
| Verification state | `not_tested` / `partial` / `conformant` | Whether evidence supports the declared coordination level for the specified build and scope. |

**cpl-req-001 — Declaration scope.** An implementation SHALL declare its coordination service level separately for each implemented plane interface. The scope SHALL identify the provider, interface version, site or sites, workflow/resource coverage and build provenance. A product-level statement SHALL NOT imply that every deployment or adapter has the same level.

**cpl-req-002 — Cumulative levels.** L1–L3 SHALL be cumulative within a plane. A declaration at L3 SHALL satisfy L1 and L2 requirements for that plane and every applicable common requirement. Features MAY exceed the declared level without increasing the claim automatically.

**cpl-req-003 — L0 and absence.** L0 SHALL mean documented manual participation with no claim of machine-coordinated interoperability. L0 SHALL identify the responsible operator, handoff, limitations and escalation procedure. An interface not supplied by the product SHALL be marked `not_provided`; it SHALL NOT be represented as L0 or as a tested interface. L0 SHALL NOT be advertised as automated or dynamically conformant.

**cpl-req-004 — Declared, targeted and operational capability.** Target level, evidence-backed declared level and current operational state SHALL be distinct values. Runtime state SHALL include at least `normal`, `degraded` and `unavailable`. A transient loss of connectivity SHALL NOT silently change a certification claim or be interpreted as a new level of conformance.

**cpl-req-005 — Versioned context.** Every claim SHALL identify the level-model version, domain profile and service-quality profile. Site count and evaluation/production stage SHALL NOT determine the coordination level by themselves.

**cpl-req-006 — Existing assurance requirements.** A coordination level SHALL NOT waive any applicable identity, security, data-governance, resource-authority or Healthcare-profile requirement. Low coordination capability SHALL NOT be used to justify pilot-only assurance in production. The declaration SHALL identify the applicable assurance requirement set and its evidence independently of the coordination level.

### 2.2 Shared meaning of L0–L3

| Level | Name | Observable boundary |
|---|---|---|
| L0 | Manual participation | The operational handoff depends on a person; there is no machine-coordination claim. |
| L1 | Static integration | Machine-readable identity, capabilities and contracts support predefined exchanges and allocations. Runtime adaptation is not required. |
| L2 | State-aware coordination | Changes in state are observed within declared bounds and affect decisions through predefined policies. The interface reports and manages deviations from a plan. |
| L3 | Fully dynamic coordination | Relevant participants, availability, capacity, commitments and permitted allocations can be updated and coordinated during operation, including replanning across participating planes, without manual reconfiguration for routine in-scope changes. |

**cpl-req-007 — Meaning of fully dynamic.** An L3 implementation SHALL support runtime updates to applicable availability, capacity, declared capability state, commitments and allocation outcomes within its declared operating envelope. An in-scope change SHALL trigger bounded reevaluation or an explicit refusal/escalation. A restart, deployment or manual configuration change SHALL NOT be required for routine in-scope changes. Introduction of an unsupported protocol, new physical capability or unapproved policy is outside this guarantee.

**cpl-req-008 — Authority and human decisions.** Dynamic coordination SHALL operate within authenticated, versioned authorisations and policies. Human acceptance or approval explicitly required by the workflow SHALL remain a first-class outcome. The system SHALL NOT fabricate that approval, change clinical priority on its own authority or modify labour constraints in order to maintain an L3 claim. Local robot and building safety behaviour remains authoritative.

**cpl-req-009 — Correlation and lifecycle, L1–L3.** An integrated interface SHALL correlate requests, acknowledgements, refusals and outcomes to the relevant task, resource, agent and request identifiers. Retries SHALL NOT create duplicate accepted work or duplicate effective resource grants. Partial failure SHALL be observable.

**cpl-req-010 — Freshness and recovery, L2–L3.** State used for coordination SHALL carry enough source, time and version/sequence information to detect stale, duplicate and out-of-order updates. The interface SHALL expose unknown state explicitly, apply its declared freshness limits and reconcile state after reconnection before using it for new commitments. Receipt of an old event SHALL NOT make its underlying state fresh.

**cpl-req-011 — Bounded resolution, L3.** An L3 coordinator SHALL reach an accepted revised commitment, an explicit refusal, or a defined escalation within the profile's decision deadline. It SHALL bound retry/negotiation cycles and prevent uncontrolled oscillation or silent starvation. The standard does not prescribe an optimisation algorithm.

**cpl-req-012 — Auditable decisions, L1–L3.** Evidence SHALL connect requests, relevant observations, applicable policy versions, decisions, acknowledgements and final outcomes. It SHALL distinguish simulation/test evidence from production evidence and apply Part 7's data minimisation and access controls. An integration layer does not gain authority to collect additional personal data merely because its coordination level increases.

## 3. Requirements per control plane — normative on adoption

L0 uses the common declaration and manual-handoff requirements. The following rows define the minimum additional capability at each integrated level. Each row applies in addition to the lower-level rows for the same plane.

### 3.1 Robot

| ID | Level | Required behaviour |
|---|---|---|
| cpl-req-101 | L1 | The Robot interface SHALL expose identity consistent with CP-007, declared capabilities, and a task/order acceptance and result interface. It SHALL support predefined assignment to eligible robots and explicitly refuse unsupported work. Individual robots of the same type SHALL remain distinguishable. |
| cpl-req-102 | L2 | The interface SHALL report relevant execution state, availability, capability changes and faults within its service-quality bounds. Loss of eligibility or ability to fulfil an accepted task SHALL produce an observable exception. Predefined policies SHALL respond using current state, without treating missing state as availability. |
| cpl-req-103 | L3 | The interface SHALL accept and respond to runtime proposals to allocate, revise, transfer or release work within its delegated authority. Inability to fulfil a commitment SHALL trigger a correlated renegotiation/refusal flow. The fleet retains local planning and motion control; routine changes to eligible robot participation SHALL not require manual interface reconfiguration. |

### 3.2 Infrastructure

| ID | Level | Required behaviour |
|---|---|---|
| cpl-req-201 | L1 | The Infrastructure interface SHALL identify resources, responsible authorities, supported operations and configured capacity. Access requests SHALL receive explicit grants or refusals consistent with CP-008 and Sup-003. A static integration SHALL NOT treat an unconfirmed door or lift request as permission to enter. |
| cpl-req-202 | L2 | The interface SHALL report current resource availability, occupancy/capacity constraints, active authorities and building modes within its service-quality bounds. Predefined access rules SHALL use this state, including grant expiry and explicit release. Unknown occupancy or connectivity SHALL NOT imply free capacity. |
| cpl-req-203 | L3 | The interface SHALL support runtime resource registration within approved scope and bounded request, renewal, amendment and release of resource commitments. Capacity/mode changes SHALL trigger reevaluation and notification of affected participants. It SHALL coordinate commitments through the responsible BMS/access-control systems and preserve their authority, physical occupancy constraints and safety modes. |

Lease expiry is not proof that a physical resource is empty. The resulting availability decision must reconcile authority records with the applicable occupancy and building-state evidence.

### 3.3 Workforce

| ID | Level | Required behaviour |
|---|---|---|
| cpl-req-301 | L1 | The Workforce interface SHALL expose declared roles/capabilities, configured availability and allocation constraints for its scope. A predefined allocation SHALL identify the responsible team, person or robot capacity through authorised identifiers. Shared contracts SHALL preserve differences between human and robotic participation. |
| cpl-req-302 | L2 | Changes in availability, eligibility, acceptance and permitted workload indicators SHALL be reflected within service-quality bounds. Predefined allocation policies SHALL use these changes. An unavailable participant SHALL not remain eligible merely because an earlier schedule lists them as available. |
| cpl-req-303 | L3 | The interface SHALL support dynamic offers, acceptance/refusal, release and reassignment of capacity across eligible human teams and robots. It SHALL respect declared competence, working-time constraints, consent/acceptance requirements, supervision and reserved human decisions. A person may decline; L3 requires the system to handle that outcome dynamically, not to bypass it. |

### 3.4 Task

| ID | Level | Required behaviour |
|---|---|---|
| cpl-req-401 | L1 | The Task interface SHALL accept and correlate standardised task submissions, required capabilities, constraints and lifecycle outcomes. Priority SHALL use CP-009's values and authorised origin, including the default `routine`. Predefined assignment rules MAY be used. |
| cpl-req-402 | L2 | The interface SHALL publish task progress, authorised amendments, cancellations and exceptions within service-quality bounds. Predefined responses SHALL account for deadlines, readiness, dependencies and applicable evidence requirements. Acceptance, execution and completion SHALL remain distinct states. |
| cpl-req-403 | L3 | The interface SHALL support event-driven reevaluation and coordinated reassignment/replanning when needs or dependencies change. It SHALL preserve CP-009's priority origin and preemption restrictions, CP-008's resource authority and applicable chain-of-custody. A changed need may trigger a new plan; it SHALL NOT authorise a participant to silently increase priority. |

## 4. Composition across planes — normative on adoption

**cpl-req-501 — Explicit dependencies.** Each workflow profile SHALL declare the plane interfaces on which it depends, their minimum levels, required capabilities, authority boundaries and applicable service-quality profiles. A plane may be omitted only where it is genuinely outside that workflow; the omission and rationale SHALL be recorded.

**cpl-req-502 — Admission.** Before automated execution, the coordinator SHALL check that every required interface is present, supports the required contract/capabilities, meets the declared minimum level and has usable operational state. Insufficient or unknown support SHALL cause rejection, escalation or entry into an explicitly approved alternative workflow.

**cpl-req-503 — End-to-end L3.** A workflow SHALL be described as fully dynamic end-to-end only where every required participating plane interface meets L3 for the relevant operations and an integration test demonstrates their joint behaviour. Four separate vendor L3 declarations alone SHALL NOT establish end-to-end conformance. No average or maximum of plane levels may be advertised as a system-wide level.

**cpl-req-504 — Degradation.** If a required dependency degrades, the coordinator SHALL expose the affected workflows and follow the approved degraded-mode policy. It SHALL preserve existing authority and safety obligations, avoid new unverified commitments and reconcile state before resuming normal operation. Degraded execution SHALL not continue to be reported as normal end-to-end L3 operation.

Example: `Robot L3 · Infrastructure L2 · Workforce L1 · Task L3` is a valid capability description. A workflow using all four planes cannot claim end-to-end L3. A different workflow may have a different set of dependencies, but must declare and test that set explicitly.

## 5. Measurable service-quality profiles — normative on adoption

Coordination level expresses supported behaviour. Service-quality profiles express how reliably and how quickly the behaviour is delivered. A contractual SLA can refer to these profiles and add commercial terms; the level itself does not promise a universal response time or uptime percentage.

**cpl-req-601 — Profile definition.** Every L1–L3 claim SHALL reference a versioned, immutable service-quality profile. For each applicable metric, the profile SHALL define the bound, unit, observation points, measurement method, aggregation/window, load envelope, exclusions and breach action. Timing bounds SHALL be finite. Omitted values or unresolved placeholders SHALL block a conformant claim. Non-applicability requires a scope-specific justification and cannot waive a required behaviour. Existing applicable protocol deadlines and their defined override rules SHALL be preserved unless explicitly amended by the approved revision.

| Metric | Applies to | Required measurement definition |
|---|---|---|
| Request acknowledgement | L1–L3 | Time from request receipt at the declared interface to explicit acknowledgement or refusal; acknowledgement is not physical completion. |
| State age / freshness | L2–L3 | Maximum age and clock-uncertainty allowance for state used in a decision, including what happens when the limit is exceeded. |
| Change visibility | L2–L3 | Time from a change at the declared source observation point to its availability to authorised consumers. |
| Reevaluation / commitment decision | L3 | Time from receipt of a relevant change to a revised accepted commitment, refusal or escalation. |
| Availability | L1–L3 | Named operations measured, monitoring method, observation window, outage definition and permitted maintenance exclusions. |
| State recovery | L2–L3 | Time from restored communication to reconciled state that is eligible for new decisions. Reconnection alone is insufficient. |
| Evidence visibility | L1–L3 | Time from a decision/outcome to availability of its correlated audit evidence to authorised inspection. |

**cpl-req-602 — Measurement validity.** Implementations SHALL report the evidence needed to evaluate their bounds under the declared load envelope, including unsuccessful requests, timeouts and refused work. A profile SHALL specify percentile/maximum semantics where used, minimum sample rules and clock assumptions. It SHALL NOT hide unsuccessful work by measuring only completed successes.

**cpl-req-603 — Breach handling.** A bound violation SHALL create an observable service-state/evidence record and trigger the profile's defined action. The implementation SHALL distinguish a transient breach, an unavailable dependency and evidence that invalidates a longer-term conformance claim.

**cpl-req-604 — Profile changes.** Changes to timing, authority, accepted load or degraded-mode policies SHALL be versioned, authorised and associated with affected claims. An implementation SHALL NOT improve its apparent result by silently relaxing a bound during a measurement period.

No new universal numeric thresholds are introduced in this proposal. Existing contract defaults, such as Sup-003's door-response deadline and its request-level override mechanism, remain applicable until explicitly revised. The responsible profile owners must approve any additional concrete values for each workflow and deployment class before conformance testing. Missing values are implementation/review blockers, not zero, infinity or a default success.

## 6. Declaration and evidence model — normative on adoption

The next declaration version SHALL add an explicit `coordination` object. The current legacy `parts_declared[].level` field must retain its historical meaning while old declarations remain in circulation.

Minimum information:

| Object | Required information |
|---|---|
| Declaration | Schema/model version; declaration identifier/date; implementer/product; specification edition/revision; build provenance. |
| Context | Deployment stage, deployment scope, covered sites and domain profile. |
| Plane interface | Plane; provision state; provider/interface/version; covered operations/resources; target level; declared level; verification state; service-profile reference/digest; applicable requirement IDs and evidence references. |
| Assurance | Applicable requirement-set reference/digest, domain requirements and independent evidence status. Existing Part 2 provenance/deviation requirements remain applicable. |
| Workflow | Required interfaces, minimum levels, capabilities, policy references, degraded-mode behaviour and integration-test evidence. |
| Runtime state | Separate operational records identifying interface, observation time, state version, condition, affected workflows, reason and recovery evidence. |

For an intended but untested integration, `target_level` MAY be L3 while `declared_level` is null and `verification_status` is `not_tested`. A target is not a capability claim. A `partial` declaration SHALL enumerate deviations using Part 2's applicable rules and SHALL NOT satisfy workflow admission as if it were conformant.

### 6.1 Illustrative target declaration — informative

The example below deliberately contains **no conformance or certification claim**. The `example` references identify documents to be supplied; they are not operational endpoints or evidence. Viktor should implement the versioned schema and validation before populating evidence-backed declarations.

```yaml
schema_version: rocom-conformance/control-planes-0.1-draft
declaration_kind: implementation_target
specification:
  edition: 2026a-draft
  revision_status: proposed
implementer:
  organization: Example integrator
  product: Example deployment
context:
  deployment_stage: evaluation
  deployment_scope: single_site
  sites: [example-hospital]
  domain_profile: Healthcare
coordination:
  model: control-plane-levels-0.1-draft
  interfaces:
    - id: robot-adapter
      plane: robot
      provision: planned
      target_level: L3
      declared_level: null
      verification_status: not_tested
      service_profile_ref: urn:example:robot-service-profile:0.1-draft
      evidence_refs: []
    - id: building-adapter
      plane: infrastructure
      provision: planned
      target_level: L3
      declared_level: null
      verification_status: not_tested
      service_profile_ref: urn:example:infrastructure-service-profile:0.1-draft
      evidence_refs: []
    - id: workforce-provider
      plane: workforce
      provision: planned
      target_level: L3
      declared_level: null
      verification_status: not_tested
      service_profile_ref: urn:example:workforce-service-profile:0.1-draft
      evidence_refs: []
    - id: task-source
      plane: task
      provision: planned
      target_level: L3
      declared_level: null
      verification_status: not_tested
      service_profile_ref: urn:example:task-service-profile:0.1-draft
      evidence_refs: []
assurance:
  requirement_set_ref: urn:example:healthcare-assurance-profile:0.1-draft
  verification_status: not_tested
  evidence_refs: []
workflows:
  - id: hospital-transport
    requirements:
      - interface: robot-adapter
        minimum_level: L3
      - interface: building-adapter
        minimum_level: L3
      - interface: workforce-provider
        minimum_level: L3
      - interface: task-source
        minimum_level: L3
    target_end_to_end_level: L3
    verified_end_to_end_level: null
    degraded_mode_policy_ref: urn:example:hospital-transport-fallback:0.1-draft
    integration_evidence_refs: []
```

The proposed schema shall enumerate provision states `planned`, `provided` and `not_provided`. A conformant L1–L3 claim requires `provided`, complete context/build/profile data and supporting evidence. The abbreviated target example omits those claim-only fields intentionally. Runtime condition is carried separately; it does not rewrite this target declaration.

## 7. Verification and acceptance — normative on adoption

Test identifiers below are proposed. Each evidence record must identify the build, profiles, configuration, fixture, stimulus, timestamps and assertions. Simulation can demonstrate contract behaviour; physical deployment claims additionally require evidence for the real interfaces and environment covered by the claim.

| Test | Requirements | Stimulus and pass condition |
|---|---|---|
| CPL-T01 | cpl-req-001, cpl-req-003, cpl-req-004, cpl-req-005 | Validate a mixed-plane declaration. Preserve separate levels/context; reject an L0 automation claim, a missing provider represented as L0, and an untested target represented as conformant. A degraded runtime record must not overwrite the evidence-backed level. |
| CPL-T02 | cpl-req-002 | Remove evidence for a mandatory lower-level requirement from an L3 declaration. L3 verification fails and identifies the missing requirement. |
| CPL-T03 | cpl-req-006 | Use an L1 coordination interface in a production Healthcare workflow with an unmet applicable security/domain requirement. Admission fails independently of coordination capability. |
| CPL-T04 | cpl-req-007, cpl-req-101, cpl-req-102, cpl-req-103 | Register two eligible robots of the same type and distinguish their individual identities. Accept supported work, refuse unsupported work, then change availability/capability state and make the selected robot unable to meet its commitment. L2 reports/responds by policy; L3 resolves or explicitly escalates without restart or manual reconfiguration. |
| CPL-T05 | cpl-req-201, cpl-req-202, cpl-req-203 | Exercise a confirmed resource grant/refusal, capacity reduction, occupancy uncertainty, expiry, renewal and release. No double allocation above capacity; no assumption that expired authority means empty space. L3 notifies affected commitments and resolves changes during operation. |
| CPL-T06 | cpl-req-301, cpl-req-302, cpl-req-303 | Change a qualified participant's availability; then decline an offered task and remove eligibility. The interface uses current state, preserves required acceptance and constraints, and at L3 offers/reassigns or escalates dynamically. No allocation is reported as accepted before required acceptance. |
| CPL-T07 | cpl-req-401, cpl-req-402, cpl-req-403 | Submit a task without explicit priority, amend it through an authorised source, cancel another and inject a dependency delay. Preserve default priority/origin, distinguish lifecycle stages, and at L3 produce a coordinated revised outcome. Reject unauthorised priority escalation and prohibited preemption. |
| CPL-T08 | cpl-req-008 | Inject building safety mode, a resource occupied by a person and a workflow requiring human approval. Dynamic coordination yields to the relevant authority; it never invents approval or overrides the applicable prohibition. |
| CPL-T09 | cpl-req-009 | Duplicate a request and retry after an acknowledgement is lost. At most one effective accepted task/grant results; all outcomes remain correlated. |
| CPL-T10 | cpl-req-010 | Deliver stale, reordered and duplicated events, then disconnect and reconnect. The receiver does not roll state backward or make stale state fresh, and does not issue new commitments before reconciliation. |
| CPL-T11 | cpl-req-011 | Cause repeatedly conflicting replans or unavailable capacity. A finite bounded attempt produces acceptance, refusal or escalation; no oscillating commitments or silent starvation. |
| CPL-T12 | cpl-req-012 | Trace one successful task and one failed/replanned task from request to final outcome. Policy/build provenance and correlated evidence are present, with access controls and minimised personal data. |
| CPL-T13 | cpl-req-501, cpl-req-502 | Omit a required interface, lower its supported level, or remove a required capability. The workflow is not admitted under its original claim; only an explicitly approved alternative may proceed. |
| CPL-T14 | cpl-req-503 | Combine four individually verified L3 adapters that disagree on a contract/profile version. Reject the end-to-end L3 claim until compatibility and the combined scenario are demonstrated. A mixed L3/L2/L1/L3 workflow is not averaged into L3. |
| CPL-T15 | cpl-req-504 | Degrade a required plane during a running workflow. Affected workflows and their degraded state are visible; outstanding grants are handled according to authority rules; recovery requires state reconciliation. |
| CPL-T16 | cpl-req-601, cpl-req-602 | Omit a timing value, use an infinite bound, exclude failed requests from measurement, or change the declared load. The relevant conformance assertion fails rather than returning success. |
| CPL-T17 | cpl-req-603, cpl-req-604 | Exceed a configured bound and attempt to relax it silently. Produce the breach and defined action; reject or version/authorise the profile change and retain the original measurement context. |
| CPL-T18 | cpl-req-701, cpl-req-702, cpl-req-703, cpl-req-704 | Import a legacy Multi-Site L3 claim. Preserve its original semantics; do not infer any new plane L3 claim. Confirm traceable assurance mapping, versioned publication and absence of a new certificate before the revision and evidence process support it. |

Required integrated demonstration: submit a healthcare transport task; allocate an eligible robot and the required workforce interaction; request shared infrastructure; make the intended lift unavailable; propose an allowed alternative; obtain revised commitments; complete or explicitly escalate; reconcile all resource releases and correlated task evidence. Repeat with connection loss, stale occupancy, a human refusal and a building safety override. Expected outcomes must be asserted from the approved workflow policy, not improvised by the demonstration.

## 8. Migration and publication — normative on adoption

**cpl-req-701 — No automatic equivalence.** Legacy L1/Pilot, L2/Single Site and L3/Multi-Site SHALL NOT be converted mechanically into new coordination levels. Historical claims SHALL preserve their model, edition, build and scope. New coordination claims require the new declaration model and corresponding evidence.

**cpl-req-702 — Requirement migration ledger.** The revision SHALL publish a ledger for existing level-tagged requirements in Parts 2–7 and affected Supplements. Each entry SHALL identify the old ID/text, old applicability, new applicability, justification and test mapping. No requirement SHALL be weakened, lost or reassigned solely by changing its numeric level label. Existing safety, security and domain obligations continue until an explicitly reviewed replacement is adopted.

**cpl-req-703 — Versioned rollout.** Providers and consumers SHALL identify supported declaration/contract versions. A migration adapter MAY preserve compatibility, but SHALL NOT manufacture missing state, evidence or dynamic capability. The implementation SHALL maintain a clear distinction between legacy declarations and new coordination declarations throughout transition.

**cpl-req-704 — Publication and claims.** Draft implementation and evaluation MAY proceed under this proposal with explicit draft labelling. Adopted normative requirements, public certification claims and website statements SHALL follow the approved edition/revision and evidence status. No draft or successful simulation alone establishes production conformance or certification.

### 8.1 Editorial adoption route — informative

The baseline `CONTRIBUTING.md` explicitly assigns new conformance levels to **Full Part Revisions**, requiring Editor approval, a `[Revision]` issue, a minimum 14-day discussion period, a draft within the Part directory and replacement on Edition release. This proposal follows that route. It is not a cosmetic CP and does not allocate CP-010 or the reserved Sup-006.

Use the draft above as the proposed replacement for Part 2 §1–§1.1 plus new service-level, composition, measurement and migration clauses. Integrate the declaration additions into Part 2's existing template, retaining provenance, deviations and independent certification requirements. The coordinated updates to other Parts must be included in the review, rather than treating Part 2 alone as sufficient.

## 9. Implementation brief for Viktor — informative

### Objective

Implement versioned, evidence-backed L0–L3 declarations per control-plane interface and enforce them when admitting and running workflows. Build reusable contracts so robot, building, workforce and task-system providers can participate at different verified levels.

### Work packages and definition of done

| Package | Deliverable | Acceptance |
|---|---|---|
| WP1 — Standards mapping | The requirement migration ledger, proposed Part 2 text and amendments to Parts 3–7/Sup-001/Sup-003/Sup-005. | Every affected legacy level-tagged requirement is accounted for; reviewers can see the semantic changes. No global search-and-replace of L1/L2/L3. |
| WP2 — Declaration schemas | Versioned machine-readable schemas for declarations, plane capabilities, service-quality profiles and operational state. Valid/invalid fixtures and a validator. | Target vs claim, L0 vs not-provided, evidence vs runtime condition, profile digests and provenance are validated. Test CPL-T01–03 and CPL-T16–18. |
| WP3 — Registry and adapters | Provider/interface registration; version/capability support; stable agent/resource references; per-plane status/freshness. | Exercise all four adapter types and preserve two distinct units of the same robot type. A disconnected adapter does not appear available. |
| WP4 — Workflow admission | Dependency declaration, minimum-level/capability matching, assurance checks and explicit reasons for rejection or alternative flow. | Mixed-level, absent-plane and incompatible-version fixtures behave as CPL-T13–14 require. |
| WP5 — Dynamic coordination | State-driven replanning, commitment acknowledgements/refusals, bounded negotiation, retries, leases, release and reconciliation. | Pass per-plane tests and integrated normal/degraded/recovery scenarios without requiring routine manual reconfiguration. No prescribed vendor planning algorithm. |
| WP6 — Measurement and evidence | Service-profile enforcement, metrics, breach records, reproducible test evidence and export by build/profile/interface/workflow. | Report failed requests and breaches as well as successes; satisfy CPL-T09–12 and CPL-T15–17. |
| WP7 — Presentation and release | Per-plane capability view, separate runtime health, workflow compatibility and draft/evidence status; rendered standard pages and migration notes. | UI/API do not show one misleading global L3 badge. Documentation and schemas use the same model version. Live pages and source agree on status. |

Suggested order: WP1 and WP2 establish the model; WP3 enables realistic fixtures; WP4 establishes admission; WP5 and WP6 implement dynamic operation and evidence; WP7 publishes the reviewed results. Viktor can start the schema and simulator work while the revision is under review, with the model explicitly marked experimental.

### Repository boundaries

In `rocom-standard`, keep normative text, interoperable schemas, conformance fixtures, test definitions, source references and rendering changes. Keep HRRM or other product runtime logic in the corresponding implementation repository. Viktor should identify the relevant implementation branches and components in the work-package plan.

Use concrete model fields such as `coordination_level` in product APIs; avoid an ambiguous bare `level` that could refer to legacy conformance, priority or robot proficiency. Align identities with CP-007 and commitments with CP-008. Retain CP-009's existing priority and preemption semantics.

### Handoff checklist

- Submit separate reviewable changes for the standard revision, interoperability schemas/tests and product implementation.
- Include the exact baseline and proposed model version in each change.
- Demonstrate one mixed-level deployment and one fully dynamic four-plane workflow.
- Include disconnection, stale state, duplicate requests, capacity contention, refusal, override and recovery in evidence.
- Document unresolved decisions instead of filling them with implementation assumptions.
- Do not publish L3 conformance or certification before the relevant evidence and approval process support it.

## 10. Decisions to resolve during review — informative

1. Approve the new level semantics and their separation from deployment scope/stage and assurance.
2. Complete the per-requirement migration ledger, especially for existing L1–L3 security/data-governance requirements and transport bindings.
3. Assign service-profile owners and approve concrete timing, load, availability and recovery bounds for initial workflows.
4. Confirm which workflows require human acceptance and which actions can proceed under standing delegated authority.
5. Choose the declaration/schema compatibility period and the target Edition release. Do not infer either from this draft's date.
6. Confirm the certification scope for a plane interface versus a combined workflow, including production evidence expectations with the independent provider process.

These are explicit review decisions. They do not prevent producing an experimental schema, simulator fixtures or a reviewable implementation plan.

## 11. Source basis

Source links below are pinned to the reviewed baseline. The proposal introduces new requirements; it does not claim that those requirements already exist in these sources.

- [Part 2 — Conformance](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/part-02-conformance/CONFORMANCE.md): current level definitions, profile, provenance, deviations and certification.
- [Contributing](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/CONTRIBUTING.md): revision route for new conformance levels.
- [CP/Supplement registry](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/cp-registry.md): authoritative numbering and source status.
- [CP-007 — Agent identity](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/cp-007-agent-identity.md): type/configuration/individual identity and issuer handling.
- [CP-008 — Resource authority](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/cp-008-resource-authority.md): grants, expiry, release, delegated autonomy and commitments.
- [CP-009 — Priority and preemption](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/cp-009-priority-preemption.md): priority origin, limits, preemption and starvation reporting.
- [Availability provider contract](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/part-04-services/availability_provider_contract.yaml) and [Task source contract](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/part-04-services/task_source_contract.yaml): existing interface-specific L1–L3 structures.
- [Sup-003 — BMS infrastructure](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/supplements/sup-003.md): infrastructure authority and safety boundary.
- [Sup-005 — Certification provider requirements](https://github.com/RocomFoundation/rocom-standard/blob/ff6803dd9176d9875511cbf5134bdcf6b704f0e6/spec/supplements/sup-005-certification-provider.md): draft provider/evidence framework; its draft status is preserved.

---

**Delivery status:** Review proposal, ready for editorial discussion and implementation planning. Adoption and public conformance claims follow the revision and evidence process described above.



