# Revision proposal — Part 2: Control-plane service levels L0–L3

**Status:** DRAFT PROPOSAL (v0.2) — for review; not an adopted ROCOM requirement.  
**Version:** 0.2-draft  
**Date:** 27 September 2026.  
**Requested by:** Egil Utheim.  
**Proposed implementation owner:** Viktor, following specification review.  
**Baseline:** RocomFoundation/rocom-standard, commit `2ad13a1`.  
**Primary target:** Part 2 — Conformance.  
**Also affects:** Parts 3–7, the four control-plane contracts, Sup-001, Sup-003 and certification guidance in Sup-005.  
**Change mechanism:** Full Part revision, with coordinated amendments to affected Parts. No CP or Supplement number is assigned by this draft.  
**Suggested repository location:** `spec/part-02-conformance/control-plane-service-levels-DRAFT.md`.

## Change log

| Version | Date | Changes |
|---|---|---|
| 0.1-draft | 27 Sept 2026 | Initial proposal: L0–L3 per plane, location model (§5), service quality (§6), tests CPL-T01–22 |
| 0.2-draft | 27 Sept 2026 | **Integrated specification.** Added: §13 L1 implementation profile with complete example, §14 L2/L3 progression, §15 Part 3/4 alignment notes. Versioned header throughout. |

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

## 5. Location model — system-agnostic — normative on adoption

All four planes must be able to refer to and exchange information about the same physical place. The systems involved may use different identifier schemes, different coordinate systems, and different naming conventions. This section provides a shared location model that is independent of any particular standard, vendor, or region.

### 5.1 Location identity

A location identity is the persistent statement "this is that place." It is separate from the place's name, its position in a floor plan, its coordinates in a robot map, and its transient state (occupied, accessible, under maintenance).

| Component | Meaning | Stability |
|---|---|---|
| **Namespace / identification system** | The system or registry that defines the identifier format and scope. | Stable — chosen by the deployment. |
| **Identifier** | The value that is unique within its namespace. | Stable — does not change with state or occupancy. |
| **Name** | Human-readable label(s). Locale-dependent. | Volatile — may change with reorganisation. |
| **Hierarchy / containment** | Parent, child, sibling relations (building → floor → ward → room → bay). | Stable — changes require explicit revision. |
| **Coordinates / spatial reference** | Position within a map, geodetic coordinates, or other spatial reference frame. | Semi-stable — map revisions create new coordinate sets. |
| **State** | Current availability, access permission, occupancy, capacity. | Dynamic — governed by service-quality profiles and L2/L3 rules. |

**cpl-req-801 — Namespace declaration.** Every location identifier used in a plane interface SHALL identify its namespace or identification system. A bare string without namespace context SHALL NOT be treated as globally unique. The namespace MAY be expressed as part of the identifier (for example, a GS1 GLN where the GS1 prefix carries namespace semantics), as a separate `namespace` field, or as a URI scheme. The standard does not mandate any particular identification system.

**cpl-req-802 — Cross-namespace linking.** Where a deployment uses different identifiers for the same physical place in different systems, the declaration SHALL provide explicit links between them. Each link SHALL identify both identifiers, the source of the mapping, its asserted validity period, and the granularity relationship (identical, contains, contained-in, or unknown). A link does not establish equivalence; it records an assertion that must be independently verified before automated decisions rely on it.

**cpl-req-803 — Identity versus state.** Location identity SHALL be carried separately from location state. A change in access permission, occupancy, or availability SHALL NOT create a new location identity or invalidate an existing identifier. Conversely, a new or updated identifier SHALL NOT silently change the reported state of the place it identifies.

**cpl-req-804 — Name and hierarchy are not identity.** Human-readable names, room numbers, and hierarchical parentage are informational attributes of a location. They SHALL NOT serve as the sole basis for automated identification. Two places with the same name in different namespaces are distinct until a verified link is established.

### 5.2 Location references in plane interfaces

Each plane interface uses location information differently. The model accommodates these differences without requiring a single global registry.

**Robot:** A robot map identifies waypoints, docking stations, no-go zones, and navigable areas by identifiers within that map's namespace. The map may cover a subset of the building. Map revisions create new coordinate sets; location identity is carried by the map's own identifiers.

**Infrastructure:** The BMS and access-control systems identify rooms, zones, doors, lifts, and docks using identifiers from the facility's space management system (for example, Uniclass, a local facility register, or an operator-defined scheme). These identifiers identify the place; access authority is determined by separate resource-grant and authorisation mechanisms (CP-008).

**Workforce:** Staffing and allocation systems identify departments, wards, teams, and duty stations. These identifiers are organisational rather than spatial; they map to physical places through the facility hierarchy.

**Task:** The task source identifies origin and destination locations for work. For workflows that depend on the Infrastructure plane (shared doors, lifts, docks, capacity), these references MUST be resolvable through the Infrastructure interface's resource model so that access, routing, and capacity decisions are based on the authoritative resource representation. Workflows that do not require shared infrastructure may use their own location references without cross-plane resolution.

Informative examples of identifier schemes in use (none mandatory for ROCOM conformance):

| Scheme | Namespace | Example identifier | Typical plane |
|---|---|---|---|
| GS1 GLN | GS1 (global, 13-digit, namespace must be declared) | `701234567890123` | Task, Workforce |
| URI (deployment-local) | Operator-defined | `urn:facility:st-olavs:room:3B-12` | Infrastructure |
| Robot map ID | Vendor map | `map-v3:waypoint:dock-3B` | Robot |
| Local register | Hospital ITSM | `FAC-ZONE-3B` | Infrastructure, Workforce |

### 5.3 Verifiable cross-system location mapping

When a workflow requires the same physical place to be identified across multiple plane interfaces, the mapping must be auditable.

| Mapping field | Required | Purpose |
|---|---|---|
| `source_namespace` | Yes | Namespace of the source identifier. |
| `source_id` | Yes | Identifier in the source system. |
| `target_namespace` | Yes | Namespace of the target identifier. |
| `target_id` | Yes | Identifier in the target system. |
| `granularity` | Yes | `identical`, `contains`, `contained_in`, or `unknown`. |
| `asserted_by` | Yes | Actor or system that created the mapping. |
| `asserted_at` | Yes | Timestamp of the mapping assertion. |
| `valid_until` | No | Expiry of the mapping assertion; absence means the deployment owner is responsible for timely review. |

**cpl-req-805 — Granularity and containment.** A mapping SHALL declare the granularity relationship between source and target. A robot waypoint may be `contained_in` a room; a zone may `contain` multiple docks. A task destination that refers to a ward is `contains` relative to a specific room within that ward. `identical` means the two identifiers are asserted to refer to the same place at the same granularity. `unknown` means the mapping exists but the spatial relationship is unverified; automated decisions SHALL NOT rely on `unknown` mappings without explicit escalation or reconfirmation.

**cpl-req-806 — Source attribution.** Every location mapping SHALL carry source attribution. A mapping created by an automated import SHALL identify the import process, its version, and the last verified timestamp. It SHALL NOT be treated as authoritative without human or procedural verification.

**cpl-req-807 — Missing or ambiguous mappings.** Where a required location reference cannot be resolved across the necessary plane interfaces, the coordinator SHALL treat the reference as unresolvable and SHALL NOT assume identity by name, partial identifier match, or proximity. The workflow SHALL be rejected, escalated, or entered into an explicitly approved alternative flow.

### 5.4 Four-plane location example — informative

A delivery task originates in the task system with destination `GLN:701234567890123` (the pharmacy receiving area). The following mappings exist:

| Mapping | Source | Target | Granularity | Verified |
|---|---|---|---|---|
| Task → Infrastructure | `GLN:701234567890123` | `urn:facility:pharmacy:receiving` | `identical` | Yes, 2026-09-15 |
| Infrastructure → Robot | `urn:facility:pharmacy:receiving` | `map-v3:waypoint:dock-pharmacy` | `contains` | Yes, 2026-09-15 |

The robot receives an order referencing `map-v3:waypoint:dock-pharmacy`. The Infrastructure plane verifies that the room `urn:facility:pharmacy:receiving` has active access authority (no building mode restriction). The Workforce plane confirms a qualified person is available to receive. The task completes with correlated evidence: task ID, robot identity, resource grant, workforce acceptance, and the location mappings used.

If the facility register is revised and the room identifier changes, the mappings are updated and reverified. The robot map waypoint may remain unchanged; the granularity relationship is preserved and reasserted.

## 6. Measurable service-quality profiles — normative on adoption

Coordination level expresses supported behaviour. Service-quality profiles express how reliably and how quickly the behaviour is delivered. A contractual SLA can refer to these profiles and add commercial terms; the level itself does not promise a universal response time or uptime percentage.

**cpl-req-901 — Profile definition.** Every L1–L3 claim SHALL reference a versioned, immutable service-quality profile. For each applicable metric, the profile SHALL define the bound, unit, observation points, measurement method, aggregation/window, load envelope, exclusions and breach action. Timing bounds SHALL be finite. Omitted values or unresolved placeholders SHALL block a conformant claim. Non-applicability requires a scope-specific justification and cannot waive a required behaviour. Existing applicable protocol deadlines and their defined override rules SHALL be preserved unless explicitly amended by the approved revision.

| Metric | Applies to | Required measurement definition |
|---|---|---|
| Request acknowledgement | L1–L3 | Time from request receipt at the declared interface to explicit acknowledgement or refusal; acknowledgement is not physical completion. |
| State age / freshness | L2–L3 | Maximum age and clock-uncertainty allowance for state used in a decision, including what happens when the limit is exceeded. |
| Change visibility | L2–L3 | Time from a change at the declared source observation point to its availability to authorised consumers. |
| Reevaluation / commitment decision | L3 | Time from receipt of a relevant change to a revised accepted commitment, refusal or escalation. |
| Availability | L1–L3 | Named operations measured, monitoring method, observation window, outage definition and permitted maintenance exclusions. |
| State recovery | L2–L3 | Time from restored communication to reconciled state that is eligible for new decisions. Reconnection alone is insufficient. |
| Evidence visibility | L1–L3 | Time from a decision/outcome to availability of its correlated audit evidence to authorised inspection. |

**cpl-req-902 — Measurement validity.** Implementations SHALL report the evidence needed to evaluate their bounds under the declared load envelope, including unsuccessful requests, timeouts and refused work. A profile SHALL specify percentile/maximum semantics where used, minimum sample rules and clock assumptions. It SHALL NOT hide unsuccessful work by measuring only completed successes.

**cpl-req-903 — Breach handling.** A bound violation SHALL create an observable service-state/evidence record and trigger the profile's defined action. The implementation SHALL distinguish a transient breach, an unavailable dependency and evidence that invalidates a longer-term conformance claim.

**cpl-req-904 — Profile changes.** Changes to timing, authority, accepted load or degraded-mode policies SHALL be versioned, authorised and associated with affected claims. An implementation SHALL NOT improve its apparent result by silently relaxing a bound during a measurement period.

No new universal numeric thresholds are introduced in this proposal. Existing contract defaults, such as Sup-003's door-response deadline and its request-level override mechanism, remain applicable until explicitly revised. The responsible profile owners must approve any additional concrete values for each workflow and deployment class before conformance testing. Missing values are implementation/review blockers, not zero, infinity or a default success.

## 7. Declaration and evidence model — normative on adoption

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

### 7.1 Illustrative target declaration — informative

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

## 8. Verification and acceptance — normative on adoption

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
| CPL-T16 | cpl-req-901, cpl-req-902 | Omit a timing value, use an infinite bound, exclude failed requests from measurement, or change the declared load. The relevant conformance assertion fails rather than returning success. |
| CPL-T17 | cpl-req-903, cpl-req-904 | Exceed a configured bound and attempt to relax it silently. Produce the breach and defined action; reject or version/authorise the profile change and retain the original measurement context. |
| CPL-T18 | cpl-req-1001, cpl-req-1002, cpl-req-1003, cpl-req-1004 | Import a legacy Multi-Site L3 claim. Preserve its original semantics; do not infer any new plane L3 claim. Confirm traceable assurance mapping, versioned publication and absence of a new certificate before the revision and evidence process support it. |
| CPL-T19 | cpl-req-801, cpl-req-804 | Register locations with and without explicit namespace. A bare string without namespace is rejected. Two places with the same name in different namespaces are treated as distinct. A GS1 GLN identifier without the namespace `GS1` declared is rejected even if the numeric value is well-formed. |
| CPL-T20 | cpl-req-802, cpl-req-805, cpl-req-806 | Create a `contains` mapping (room → waypoint), a `contained_in` reverse mapping, and an `identical` mapping. Change an `identical` mapping to `unknown` and verify that automated decisions stop relying on it. Remove the source attribution from a mapping and verify it is rejected. |
| CPL-T21 | cpl-req-803 | Change the access permission or occupancy state of a location. The location identity and identifier remain unchanged. Create a new identifier for the same physical place and verify the previous identifier's state is not silently transferred to the new one. |
| CPL-T22 | cpl-req-807 | Submit a task with a destination that cannot be resolved across the required plane interfaces. The workflow is rejected or escalated; it is not admitted based on name match, partial identifier match, or proximity. A workflow that does not depend on Infrastructure is admitted without cross-plane resolution. |

Required integrated demonstration: submit a healthcare transport task with a destination that maps across three namespaces (Task → Infrastructure → Robot); allocate an eligible robot and the required workforce interaction; request shared infrastructure; verify the location mappings carry granularity, source attribution, and validity. Make the intended lift unavailable; propose an allowed alternative; obtain revised commitments; complete or explicitly escalate; reconcile all resource releases and correlated task evidence. Repeat with connection loss, stale occupancy, a human refusal, a building safety override, and a location mapping degraded to `unknown`. Expected outcomes must be asserted from the approved workflow policy, not improvised by the demonstration.

## 9. Migration and publication — normative on adoption

**cpl-req-1001 — No automatic equivalence.** Legacy L1/Pilot, L2/Single Site and L3/Multi-Site SHALL NOT be converted mechanically into new coordination levels. Historical claims SHALL preserve their model, edition, build and scope. New coordination claims require the new declaration model and corresponding evidence.

**cpl-req-1002 — Requirement migration ledger.** The revision SHALL publish a ledger for existing level-tagged requirements in Parts 2–7 and affected Supplements. Each entry SHALL identify the old ID/text, old applicability, new applicability, justification and test mapping. No requirement SHALL be weakened, lost or reassigned solely by changing its numeric level label. Existing safety, security and domain obligations continue until an explicitly reviewed replacement is adopted.

**cpl-req-1003 — Versioned rollout.** Providers and consumers SHALL identify supported declaration/contract versions. A migration adapter MAY preserve compatibility, but SHALL NOT manufacture missing state, evidence or dynamic capability. The implementation SHALL maintain a clear distinction between legacy declarations and new coordination declarations throughout transition.

**cpl-req-1004 — Publication and claims.** Draft implementation and evaluation MAY proceed under this proposal with explicit draft labelling. Adopted normative requirements, public certification claims and website statements SHALL follow the approved edition/revision and evidence status. No draft or successful simulation alone establishes production conformance or certification.

### 9.1 Editorial adoption route — informative

The baseline `CONTRIBUTING.md` explicitly assigns new conformance levels to **Full Part Revisions**, requiring Editor approval, a `[Revision]` issue, a minimum 14-day discussion period, a draft within the Part directory and replacement on Edition release. This proposal follows that route. It is not a cosmetic CP and does not allocate CP-010 or the reserved Sup-006.

Use the draft above as the proposed replacement for Part 2 §1–§1.1 plus new service-level, composition, measurement and migration clauses. Integrate the declaration additions into Part 2's existing template, retaining provenance, deviations and independent certification requirements. The coordinated updates to other Parts must be included in the review, rather than treating Part 2 alone as sufficient.

## 10. Implementation brief for Viktor — informative

### Objective

Implement versioned, evidence-backed L0–L3 declarations per control-plane interface and enforce them when admitting and running workflows. Build reusable contracts so robot, building, workforce and task-system providers can participate at different verified levels.

### Work packages and definition of done

| Package | Deliverable | Acceptance |
|---|---|---|
| WP1 — Standards mapping | The requirement migration ledger, proposed Part 2 text and amendments to Parts 3–7/Sup-001/Sup-003/Sup-005. | Every affected legacy level-tagged requirement is accounted for; reviewers can see the semantic changes. No global search-and-replace of L1/L2/L3. |
| WP2 — Declaration schemas | Versioned machine-readable schemas for declarations, plane capabilities, service-quality profiles, operational state, and location mappings. Valid/invalid fixtures and a validator. | Target vs claim, L0 vs not-provided, evidence vs runtime condition, profile digests, provenance, namespace enforcement, and granularity are validated. Test CPL-T01–03, CPL-T16–22. |
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

## 11. Decisions to resolve during review — informative

1. Approve the new level semantics and their separation from deployment scope/stage and assurance.
2. Complete the per-requirement migration ledger, especially for existing L1–L3 security/data-governance requirements and transport bindings.
3. Assign service-profile owners and approve concrete timing, load, availability and recovery bounds for initial workflows.
4. Confirm which workflows require human acceptance and which actions can proceed under standing delegated authority.
5. Choose the declaration/schema compatibility period and the target Edition release. Do not infer either from this draft's date.
6. Confirm the certification scope for a plane interface versus a combined workflow, including production evidence expectations with the independent provider process.

These are explicit review decisions. They do not prevent producing an experimental schema, simulator fixtures or a reviewable implementation plan.

## 12. L1 implementation profile — normative on adoption

This section defines a concrete L1 starting point for any supplier who wants to deliver a single-plane integration against the specification. It draws requirements from this document, the Part 3 information model, and the Part 4 service contracts. An L1 implementation need not provide location mappings, runtime replanning, or cross-plane coordination — but it must establish identity, capability, explicit acceptance/refusal, and traceable evidence.

### 12.1 What L1 provides

An L1 integration supports **predefined exchanges** between a task source and the participating plane interface. The exchanges are static: identity, declared capabilities, configured availability, and explicit task acceptance or refusal. No runtime state observation, replanning, or dynamic reassignment is required.

### 12.2 Required elements per plane

The table below maps each plane's L1 requirement to the supporting data structures and contracts. A supplier implementing L1 for the Robot plane, for example, needs the agent identity model (CP-007), the task submission interface (CP-009), and the correlation lifecycle (cpl-req-009).

| Element | Robot (cpl-req-101) | Infrastructure (cpl-req-201) | Workforce (cpl-req-301) | Task (cpl-req-401) |
|---|---|---|---|---|
| **Identity** | `agent_identity` (CP-007): access_key, device_identifier, production_identifier | `resource_authority.resource_id`, `resource_type` | `agent_identity` (CP-007); `agent_type: human` or `cockpit` | `task.source_id`; `task.task_id` |
| **Capabilities** | `capability[]`: capability_id, name, level | `resource_authority.capacity` (configured maximum) | Declared roles/capabilities; allocation constraints | `task.required_capability`; task constraints |
| **Location references** | Robot map ID (namespace declared per cpl-req-801) | Facility identifier (namespace declared per cpl-req-801) | Organisational zone/ward (namespace declared per cpl-req-801) | Origin/destination identifiers; MUST be resolvable if workflow depends on Infrastructure |
| **Acceptance/Refusal** | Accept or refuse each task/order | Grant or refuse each access request (CP-008, Sup-003) | Accept or decline each allocation | Acknowledge task submission; explicit refusal of unhandled capability |
| **Priority** | Receives task priority from Task interface | Not directly applicable | Receives allocation priority | CP-009 values (`immediate`, `expedited`, `routine`, `deferred`); `priority_origin` |
| **Correlation** | cpl-req-009: task ID, agent identity, request ID | cpl-req-009: resource ID, request ID, grant ID | cpl-req-009: allocation ID, agent identity | cpl-req-009: task lifecycle states; distinct acceptance, execution, completion |
| **Evidence** | cpl-req-012: acceptance, result, refusal | cpl-req-012: grant, refusal, resource state | cpl-req-012: allocation, acceptance, decline | cpl-req-012: submission, lifecycle, outcome |
| **Service profile** | cpl-req-901: request acknowledgement, availability, evidence visibility | cpl-req-901: request acknowledgement, availability, evidence visibility | cpl-req-901: request acknowledgement, availability, evidence visibility | cpl-req-901: request acknowledgement, availability, evidence visibility |

### 12.3 Common L1 requirements

All L1 interfaces must additionally satisfy:

| Requirement | ID | Applicability |
|---|---|---|
| Declaration scope | cpl-req-001 | All planes |
| Cumulative levels | cpl-req-002 | N/A (L1 is base) |
| Versioned context | cpl-req-005 | All planes |
| Existing assurance | cpl-req-006 | All planes |
| Correlation and lifecycle | cpl-req-009 | All planes |
| Auditable decisions | cpl-req-012 | All planes |
| Namespace declaration (locations) | cpl-req-801 | All planes using location references |
| Service profile | cpl-req-901 | All planes |
| Measurement validity | cpl-req-902 | All planes |

### 12.4 Complete L1 example — Robot plane

The following is a complete, testable L1 integration scenario for the Robot plane. A supplier should be able to implement and test this against the specification.

**Scenario:** A hospital deploys a single robot type for meal transport. The robot fleet adapter provides L1 integration: identity, declared capabilities, task acceptance and results. Predefined assignment is used; no runtime state observation or replanning.

**Declaration:**

```yaml
schema_version: rocom-conformance/control-planes-0.2-draft
declaration_kind: implementation_target
specification:
  edition: 2026a-draft
  revision_status: proposed
implementer:
  organization: Example hospital
  product: Meal transport robot
context:
  deployment_stage: evaluation
  deployment_scope: single_site
  sites: [example-hospital]
  domain_profile: Healthcare
coordination:
  model: control-plane-levels-0.2-draft
  interfaces:
    - id: robot-adapter
      plane: robot
      provision: provided
      target_level: L1
      declared_level: L1
      verification_status: conformant
      service_profile_ref: urn:example:robot-l1-profile:0.1
      requirement_ids: [cpl-req-101, cpl-req-001, cpl-req-005, cpl-req-006, cpl-req-009, cpl-req-012, cpl-req-901, cpl-req-902]
      evidence_refs: [CPL-T04-L1, CPL-T09, CPL-T12, CPL-T16]
assurance:
  requirement_set_ref: urn:example:healthcare-l1-profile:0.1
  verification_status: conformant
  evidence_refs: [CPL-T03]
workflows:
  - id: meal-transport-l1
    requirements:
      - interface: robot-adapter
        minimum_level: L1
    target_end_to_end_level: L1
    verified_end_to_end_level: L1
    degraded_mode_policy_ref: urn:example:meal-fallback:0.1
    integration_evidence_refs: [CPL-T04-L1]
```

**Agent identity (CP-007):**

```yaml
agent_identity:
  access_key:
    issuing_entity: internal
    value: EVE-transport-2026
  device_identifier:
    issuing_entity: internal
    value: SN-2026-EVE-00142
    software_version: "2.1.0"
  production_identifier:
    serial_number: "EVE-00142"
agent_type: robot
provider_id: example-fleet-adapter
availability_status: available
```

**Capabilities:**

```yaml
capabilities:
  - capability_id: transport.meal
    name: Meal transport between wards
    level: basic
    certified: false
```

**Task submission (CP-009):**

```yaml
task_id: "550e8400-e29b-41d4-a716-446655440000"
description: Deliver lunch to Ward 3B, Room 12
required_capability: transport.meal
priority: routine
priority_origin: task-scheduling-system
source_id: hospital-task-system
status: pending
```

**Acceptance response:**

```yaml
task_id: "550e8400-e29b-41d4-a716-446655440000"
status: assigned
assigned_agent_id: "EVE-00142"
correlation_id: "req-001-accept"
timestamp: "2026-09-27T11:30:00Z"
```

**Result evidence:**

```yaml
task_id: "550e8400-e29b-41d4-a716-446655440000"
status: completed
completed_by: "EVE-00142"
completed_at: "2026-09-27T11:45:00Z"
correlation_id: "req-001-complete"
```

### 12.5 Testable acceptance criteria — L1

A supplier's L1 implementation is testable when the following conditions are met:

| Criterion | Test | Pass condition |
|---|---|---|
| Identity established | CPL-T04 (L1 subset) | Robot registers with three-layer identity; individual unit is distinguishable from same-type peers |
| Capability declared | CPL-T04 (L1 subset) | Declared capabilities match task requirements; unsupported capability is refused |
| Task accepted or refused | CPL-T09 | Each task produces at most one accepted assignment; retries do not create duplicates |
| Priority preserved | CPL-T07 (L1 subset) | Default `routine` priority applied; explicit priority from authorised origin preserved |
| Evidence traceable | CPL-T12 (L1 subset) | Request, acceptance, and outcome are correlated; evidence accessible to authorised inspection |
| Service profile met | CPL-T16 (L1 subset) | Request acknowledgement, availability, and evidence visibility bounds are measurable |
| Location namespace declared | CPL-T19 (L1 subset) | Any location reference used carries namespace; bare string is rejected |
| Assurance not waived | CPL-T03 | L1 coordination does not bypass applicable security or domain requirements |

## 13. L2 and L3 — what they add — informative

### 13.1 L2: State-aware coordination

L2 builds on L1 by introducing **observable state within declared bounds**. The interface reports and manages deviations from a plan, without requiring runtime replanning.

| What L2 adds | Robot (cpl-req-102) | Infrastructure (cpl-req-202) | Workforce (cpl-req-302) | Task (cpl-req-402) |
|---|---|---|---|---|
| **State reporting** | Execution state, availability changes, faults | Resource availability, occupancy, building modes | Availability, eligibility, workload changes | Task progress, amendments, cancellations |
| **Predefined responses** | Current state used for policy decisions | Access rules use grant expiry, occupancy | Allocation uses current availability | Responses use deadlines, readiness, dependencies |
| **Freshness** | cpl-req-010: source, time, version info | cpl-req-010: stale state exposed | cpl-req-010: stale state exposed | cpl-req-010: stale state exposed |
| **Tests added** | CPL-T04 (L2), CPL-T10 | CPL-T05 (L2), CPL-T10 | CPL-T06 (L2), CPL-T10 | CPL-T07 (L2), CPL-T10 |

**Key difference from L1:** The interface must report when state changes and ensure that those changes affect decisions. Missing state is not treated as availability. An unavailable participant cannot remain eligible solely because an earlier schedule lists them.

### 13.2 L3: Fully dynamic coordination

L3 builds on L2 by introducing **runtime adaptation without manual reconfiguration**. Participants can be added, removed, or reassigned during operation. The system handles routine in-scope changes dynamically, including replanning across planes.

| What L3 adds | Robot (cpl-req-103) | Infrastructure (cpl-req-203) | Workforce (cpl-req-303) | Task (cpl-req-403) |
|---|---|---|---|---|
| **Dynamic coordination** | Runtime proposals to allocate/revise/transfer/release | Runtime resource registration, renewal, amendment | Dynamic offers, acceptance, reassignment | Event-driven reevaluation, replanning |
| **Bounded resolution** | cpl-req-011: finite negotiation, no oscillation | cpl-req-011: bounded commitment decisions | cpl-req-011: bounded reassignment | cpl-req-011: bounded replanning |
| **Authority preservation** | Fleet retains local control | BMS/access-control authority preserved | Human decisions, consent, working-time constraints | Priority origin, preemption, chain-of-custody |
| **Tests added** | CPL-T04 (L3), CPL-T11, CPL-T15 | CPL-T05 (L3), CPL-T11, CPL-T15 | CPL-T06 (L3), CPL-T11, CPL-T15 | CPL-T07 (L3), CPL-T11, CPL-T15 |

**Key difference from L2:** The system must handle changes during operation — not just report them. A changed need triggers a new plan. A declined offer triggers reassignment. A degraded dependency triggers escalation. None of this requires manual reconfiguration for routine in-scope changes.

### 13.3 Composition at L3

End-to-end L3 requires every participating plane to reach L3 for the relevant operations. See cpl-req-503 for the composition rules. A mixed-level deployment (e.g., Robot L3 · Infrastructure L2 · Workforce L1 · Task L3) is a valid capability description but cannot claim end-to-end L3 for a workflow that uses all four planes.

## 14. Part 3 and Part 4 alignment — normative on adoption

This section documents the coordinated amendments required for Parts 3 and 4 when the DRAFT is adopted. These amendments are part of the revision, not standalone corrections.

### 14.1 Part 3 — Information Model: location extension

The existing `location` type in Part 3 is minimal (`ward_or_zone` string + optional coordinates). The location model defined in §5 of this document requires namespace, identifier, and hierarchical structure. The following extension preserves backward compatibility:

```yaml
# Part 3 amendment: location model extension
# Supersedes the flat location type while preserving ward_or_zone for backward compatibility

location:
  description: >
    Physical place within a deployment. The namespace/identifier pair
    provides stable identity (cpl-req-801, 803). The name, hierarchy,
    and coordinates are informational. State is carried separately.
  required_fields:
    - namespace
    - identifier
  fields:
    namespace:
      type: string
      description: >
        The identification system or registry that defines the
        identifier format and scope. Examples: GS1, internal,
        vda5050, uniclass, operator-defined.
      example: "GS1"
    identifier:
      type: string
      description: >
        The value unique within its namespace. Does not change
        with state or occupancy (cpl-req-803).
      example: "701234567890123"
    name:
      type: string
      description: >
        Human-readable label. Locale-dependent. SHALL NOT serve
        as the sole basis for automated identification (cpl-req-804).
      required: false
      example: "Pharmacy receiving area"
    parent:
      type: string
      description: >
        Reference to the containing location (namespace + identifier).
        Supports hierarchy: building → floor → ward → room.
      required: false
      format: "namespace:identifier"
      example: "internal:urn:facility:pharmacy"
    ward_or_zone:
      type: string
      description: >
        DEPRECATED. Preserved for backward compatibility with
        existing Part 4 contracts. New implementations SHALL use
        namespace and identifier.
      required: false
      example: "Ward 3B"
    coordinates:
      type: object
      required: false
      description: Position within a spatial reference frame.
      properties:
        x: { type: number }
        y: { type: number }
        map_id: { type: string }
```

The `ward_or_zone` field is deprecated but retained. Existing Part 4 contracts that reference `location.ward_or_zone` continue to function. New implementations must provide `namespace` and `identifier`.

### 14.2 Part 4 — Contract alignment

The availability provider and task source contracts use `agent_id` and define their own L1–L3 conformance levels. These must be aligned:

**Availability Provider Contract:**
- `agent_id` → reference `agent_identity.production_identifier.serial_number` (CP-007)
- `current_location` → reference extended `location` type (Part 3 amendment above)
- L1 conformance: add `agent_identity`, `location` (namespace-declared) to required fields
- L2 conformance: unchanged (availability_windows, capabilities already align)
- L3 conformance: unchanged (current_location, compliance_flags, push events already align)

**Task Source Contract:**
- `zone` → reference extended `location` type (Part 3 amendment above)
- L1 conformance: `zone` requires namespace declaration (cpl-req-801)
- L2 conformance: unchanged (zone, deadline, constraints already align)
- L3 conformance: unchanged (chain_of_custody, compliance_flags already align)

### 14.3 Versioning strategy

When adopted, the declaration schema version becomes `rocom-conformance/control-planes-1.0`. The Part 3 information model edition becomes `2026b`. The Part 4 contracts increment to `v0.2.0`.

Legacy declarations using schema version `rocom-conformance/control-planes-0.1-draft` remain valid during the compatibility period defined in cpl-req-1003. The migration adapter must not manufacture missing state or dynamic capability.

## 15. Start at L1 — supplier quick reference — informative

This section is designed for suppliers and integrators who want to begin implementation against a specific draft version. It summarises the minimum required elements, the test path, and the progression to L2 and L3.

### 15.1 What to implement first

1. **Identity model** — CP-007 three-layer identity for every agent. No flat `agent_id`.
2. **Location namespace** — Every location reference carries a namespace (cpl-req-801). Bare strings are rejected.
3. **Task/priority model** — CP-009 priority values; `priority_origin` for audit.
4. **Acceptance/refusal** — Every request produces an explicit outcome. Retries are idempotent (cpl-req-009).
5. **Evidence** — Correlated request, decision, and outcome. Accessible to authorised inspection (cpl-req-012).
6. **Service profile** — Measurable bounds for acknowledgement, availability, and evidence visibility (cpl-req-901).

### 15.2 Test path

| Phase | Tests | Description |
|---|---|---|
| **Identity** | CPL-T04 (L1), CPL-T19 | Register agent, declare capability, namespace locations |
| **Task flow** | CPL-T07 (L1), CPL-T09 | Submit task, accept/refuse, no duplicates |
| **Evidence** | CPL-T12 (L1), CPL-T16 (L1) | Correlate outcomes, measure service profile |
| **Assurance** | CPL-T03, CPL-T01 | Domain requirements not waived, declaration valid |
| **Integration** | CPL-T13 (L1) | Workflow admission with mixed levels |

### 15.3 Progression to L2

When L1 is stable:
- Add state reporting within declared bounds
- Implement freshness tracking (cpl-req-010)
- Add predefined policy responses to state changes
- Extend service profile with state age, change visibility, and recovery bounds

### 15.4 Progression to L3

When L2 is stable:
- Implement runtime coordination: proposals, renegotiation, reassignment
- Add bounded resolution (cpl-req-011): finite cycles, no oscillation
- Preserve authority: local control, human decisions, building safety
- Verify end-to-end with integration test across all participating planes (cpl-req-503)

### 15.5 Version pinning

This document is version `0.2-draft`. Implementation against this version should record the schema version in the declaration (`schema_version: rocom-conformance/control-planes-0.2-draft`). When the specification is adopted, the version will increment to `1.0`. The migration ledger (cpl-req-1002) will document any semantic changes between the draft and adopted version.

## 16. Source basis

Source links below are pinned to the current baseline. The proposal introduces new requirements; it does not claim that those requirements already exist in these sources.

- [Part 2 — Conformance](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/part-02-conformance/CONFORMANCE.md): current level definitions, profile, provenance, deviations and certification.
- [Part 3 — Information Model](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/part-03-information-model/INFORMATION-MODEL.yaml): core data types; location model extended by §14.1 of this document.
- [Part 4 — Service Contracts](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/part-04-services/): availability provider and task source contracts; alignment documented in §14.2.
- [Contributing](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/CONTRIBUTING.md): revision route for new conformance levels.
- [CP/Supplement registry](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/cp-registry.md): authoritative numbering and source status.
- [CP-007 — Agent identity](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/cp-007-agent-identity.md): type/configuration/individual identity and issuer handling.
- [CP-008 — Resource authority](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/cp-008-resource-authority.md): grants, expiry, release, delegated autonomy and commitments.
- [CP-009 — Priority and preemption](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/cp-009-priority-preemption.md): priority origin, limits, preemption and starvation reporting.
- [Sup-003 — BMS infrastructure](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/supplements/sup-003.md): infrastructure authority and safety boundary.
- [Sup-005 — Certification provider requirements](https://github.com/RocomFoundation/rocom-standard/blob/2ad13a1/spec/supplements/sup-005-certification-provider.md): draft provider/evidence framework; its draft status is preserved.

---

**Delivery status:** Review proposal, ready for editorial discussion and implementation planning. Adoption and public conformance claims follow the revision and evidence process described above.



