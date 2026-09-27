# CP-009 — Priority and Preemption Model

**Status:** MERGED (Edition 2026a draft)
**Target:** Part 4 — Service Contracts
**Also affects:** Part 3 (Information Model), Part 7 (Data Governance),
Sup-003 (BMS Infrastructure Contract)
**Raised:** 31 August 2026
**Author:** Rocom Project
**Depends on:** CP-008 (resource authority)

---

## 1. Problem

Implementations already distinguish urgent from routine work — lift calls
are dispatched as `routine` or `urgent`, and urgency is a term in
allocation scoring. The standard says nothing about it.

That is tolerable in a single-vendor deployment and untenable in a shared
building. When a vendor fleet and a Rocom orchestrator both request the
same lift and both call their request urgent, the word carries no shared
meaning. Four failures follow:

1. **No shared scale.** "Urgent" is whatever each implementation decided.
2. **No declared origin.** Nothing says who is entitled to set priority,
   so every participant can raise its own.
3. **No preemption rules.** Nothing states what may never be interrupted
   — including a lift occupied by a patient.
4. **No protection against inflation.** A scale on which everything is
   urgent is not a scale.

This is a contract between independent parties and belongs in the open
standard. How priority is *weighed against other factors* is not, and
remains implementation-defined (CP-008 RA-14, same principle).

## 2. Design basis (informative)

**Clinical ordering vocabulary.** Hospitals already run on a priority
scale: orders are placed as stat, asap, routine or timed/deferred, and
staff know what each means without training. Rocom SHOULD NOT invent a
competing vocabulary. Aligning with the language the task system already
uses is worth more than a theoretically cleaner scale.

**Lift and building safety modes.** Building lift standards define
firefighter and evacuation modes that override all normal traffic and are
controlled by the building, not by its users. *(EN 81-72 and EN 81-73 are
believed to be the relevant designations; verify before publication.)*
Rocom must treat these as absolute and outside its own scale.

**Air traffic and rail.** As in CP-008: the authority allocates capacity;
operators prioritise within it. Priority is declared at the point where
the need arises, not by the vehicle carrying out the work.

## 3. Normative requirements

### 3.1 The scale

**PR-01** — Every task SHALL carry a `priority` from the following
enumeration:

| Value | Meaning |
|---|---|
| `immediate` | Clinical or safety need now. Delay causes harm. |
| `expedited` | Needed as soon as capacity allows, ahead of routine work. |
| `routine` | Normal operational work. The default. |
| `deferred` | May be scheduled to a stated window or quiet period. |

**PR-02** — `routine` SHALL be the default where no priority is stated.
An implementation SHALL NOT default to a higher value.

**PR-03** — A task MAY additionally carry `not_before` and `due_by`.
These express scheduling, not priority, and SHALL NOT be substituted for
it.

### 3.2 Who may declare priority

**PR-04** — Priority SHALL be declared by the task's originating system
or role, recorded in `priority_origin`. It is a property of the need,
not of the agent that will carry out the work.

**PR-05** — An agent or fleet manager SHALL NOT raise the priority of a
task assigned to it. It MAY decline, report inability, or return the task
(CP-008 RA-24).

**PR-06** — A change of priority after a task is created SHALL be an
explicit `task.priority_changed` event carrying the new value, the
originator and a reason. Silent escalation is not conformant.

PR-04 and PR-05 exist because a scale on which any participant may
promote its own work collapses within weeks. Every widely deployed
priority field that omitted this rule has ended with everything marked
urgent.

### 3.3 From task priority to resource priority

**PR-07** — Where several claims contend for one resource, the ordering
SHALL be monotonic in task priority: a claim derived from a higher
priority task SHALL NOT be served after one derived from a lower priority
task, all else equal.

**PR-08** — How priority is weighed against distance, capability, battery
state, wear or cost is implementation-defined and outside this standard.
Only monotonicity is normative.

**PR-09** — Priority SHALL NOT bypass authority. An agent still requires
a valid authority under CP-008 before entering a resource, regardless of
its task priority.

### 3.4 Preemption

**PR-10** — A resource occupied by a person SHALL NOT be preempted. This
is absolute and admits no priority override.

**PR-11** — A building safety mode — fire, evacuation, or any mode the
building declares — SHALL override every Rocom priority. On entering such
a mode, agents SHALL release held resources and move to a safe position
as instructed by the building. Sup-003's safety clause prevails.

**PR-12** — Preemption of a task in progress SHALL be permitted only for
`immediate` priority, and only where the preempted task can be resumed or
reassigned. An implementation SHALL NOT preempt a task it cannot restore.

**PR-13** — Every preemption SHALL emit `task.preempted` naming the
preempting task, the preempted task, the resource and the reason.

**PR-14** — A task that cannot be preempted, but whose completion would
delay an `immediate` task beyond acceptable limits, SHALL raise
`priority.conflict_unresolved` rather than being silently deferred.

### 3.5 Starvation and inflation

**PR-15** — An implementation SHALL bound the waiting time of `routine`
and `deferred` tasks, or SHALL report them as starved once a stated
threshold is exceeded. Indefinite deferral without report is not
conformant.

**PR-16** — An implementation SHALL be able to report the distribution of
declared priorities per originating system over a stated period. This
makes inflation visible without prescribing a remedy.

**PR-17** — Priority distribution reporting SHALL be aggregated per
originating system or role. It SHALL NOT be reported per named
individual. Part 7 applies unchanged.

## 4. Schema (illustrative)

```yaml
task:
  priority: immediate | expedited | routine | deferred
  priority_origin: string        # originating system or role, PR-04
  not_before: timestamp          # optional, PR-03
  due_by: timestamp              # optional, PR-03

events:
  task.priority_changed          # PR-06
  task.preempted                 # PR-13
  priority.conflict_unresolved   # PR-14
  task.starved                   # PR-15
```

## 5. Relationship to other parts

**CP-008.** Priority orders contending claims; it does not create a right
to enter a resource. Authority remains mandatory (PR-09).

**Sup-003.** Building safety modes sit above the entire scale (PR-11).
Where this proposal and Sup-003 appear to conflict, Sup-003 prevails.

**Part 7.** Priority inflation reporting is aggregated, never
individual (PR-17). Nothing in this proposal permits measuring a named
person's response to a priority.

## 6. Conformance tests

**PR-01** — A task created without a stated priority is stored as
`routine`.
**PR-02** — A priority raised by the assigned agent is rejected.
**PR-03** — A priority change from the originating system produces
`task.priority_changed` with originator and reason.
**PR-04** — Two contending claims of different priority are served in
priority order.
**PR-05** — A preemption attempt against a resource occupied by a person
is refused, at any priority.
**PR-06** — A declared building safety mode causes held resources to be
released and produces no further authority requests.
**PR-07** — A preemption of a non-restorable task is refused.
**PR-08** — A `routine` task held beyond the stated threshold produces
`task.starved`.
**PR-09** — Priority distribution can be reported per originating system
and cannot be reported per individual.

## 7. Migration

Implementations that today use two levels (routine/urgent) map `urgent`
to `expedited` and `routine` to `routine`. `immediate` SHOULD be
introduced only together with the preemption rules in §3.4, since it is
the only value that permits preemption.

## 8. References

- CP-008 — Resource Authority Model
- Sup-003 — BMS Infrastructure Contract (safety clause)
- Part 7 — Data Governance
- Clinical ordering priority vocabulary (stat / asap / routine / timed)
  *(informative)*
- Lift safety standards governing firefighter and evacuation modes
  *(informative — verify designation before publication)*
