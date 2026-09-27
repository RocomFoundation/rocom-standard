# CP-008 — Resource Authority Model

**Status:** MERGED (Edition 2026a)
**Target:** Part 4 — Service Contracts
**Also affects:** Part 3 (Information Model), Part 5 (Transport Profile),
Sup-003 (BMS Infrastructure Contract)
**Raised:** 30 August 2026
**Author:** Rocom Project
**Depends on:** CP-007 (agent identity), Sup-003 (BMS contract)

---

## 1. Problem

Rocom currently has no explicit model of the shared resources agents
compete for. Space, doors, lifts, docks and tasks are all contended, but
the standard treats access to them as an implicit property of movement.
Four consequences follow, all observed in implementation:

1. **Grants have no lifetime.** A door is "granted" with no endpoint and
   no expiry, so no implementation can tell whether a grant is still
   valid.
2. **Release is implicit.** An agent that has passed a door never states
   that it has released it. Nobody can determine who currently holds
   what.
3. **Capacity is not expressible.** A door is exclusive; a lift carries
   several agents. The model has no way to say so, so lift capacity
   lives in vendor code.
4. **No behaviour is defined for communication loss.** An agent that
   loses contact with the orchestrator has no specified obligation
   regarding resources it holds.

A robot from another supplier cannot behave correctly in a shared
building without this model. It is therefore a contract between
independent parties, and belongs in the open standard.

## 2. Design basis (informative)

Two mature domains solve the same problem, and this proposal adopts
their vocabulary where it fits.

**Railway signalling (ETCS/ERTMS).** A train does not receive a
permission to move in general; it receives a *movement authority* with a
defined end point and validity, and must brake if it expires or cannot
be renewed. Sections are released explicitly behind the train, and loss
of radio contact with the block centre causes a safe stop.

**Air traffic control.** Short-term conflict alert (STCA) and
medium-term conflict detection (MTCD) compare predicted trajectories and
raise a warning before separation is lost. Arrival managers (AMAN)
sequence traffic through a single constrained resource — a runway —
rather than serving first-come-first-served.

**Airspace block reservation (military air operations).** A volume of
airspace is reserved for a using unit over a stated time window. Within
that block, the unit manoeuvres freely and does not clear each movement
individually; outside it, or after it expires, the unit has no standing
permission. Deconfliction happens once, when the block is allocated —
not continuously, movement by movement. Blocks may be released early when
no longer needed, and the airspace returns to the pool.

Two properties are worth adopting directly. First, **deconfliction is
front-loaded**: the cost of coordination is paid once per block rather
than once per movement, which is what makes the model scale. Second,
**freedom inside the block is total and freedom outside it is nil** —
there is no gradient, and therefore no ambiguity about what is permitted.

**Multi-fleet robotics (Open-RMF).** Open-RMF maintains a central
Traffic Schedule Database holding the *intended* trajectories of every
participating fleet. Its job is to identify conflicts in those intentions
and notify the fleets; when a conflict is found, a negotiation begins
between the fleet adapters, each proposing itineraries that can
accommodate the others, with defined rejection and forfeit paths.
Resolution proposes alternatives — slow down, pause, reroute — rather
than simply assigning right of way. Integration is offered at several
levels, with a defined message set per level, so a vendor fleet manager
can participate without surrendering control. In deployments pairing RMF
with Nav2, RMF keeps schedule control while the local stack handles path
planning and obstacle avoidance.

Rocom differs from RMF on one deliberate point, stated in §5: RMF
schedules *trajectories*; Rocom schedules *commitments*. The reason is
given there.

**What a mobile robot actually is.** Topologically it is a train: it
traverses an ordered sequence of resources, and the sequence is what
matters. Kinematically it is neither train nor aircraft. A train has no
lateral freedom — the rail is the route. An aircraft moves freely in
three dimensions and rotates about all three axes. A mobile robot keeps
lateral freedom within a tolerance band around its route, and
unconstrained rotation about its vertical axis.

Rocom therefore grants **authority over resources, not over
trajectories.**

**Boundary, normative in effect.** Rocom borrows these *concepts*, not
their safety integrity. ETCS and ATC systems are certified to defined
safety-integrity levels; Rocom is not a safety system. As stated in
Sup-003, the building's own safety systems remain authoritative at all
times, and no requirement in this proposal may be read as a safety
function. An implementation SHALL fail safe by yielding, never by
overriding a building system.

## 3. Normative requirements

### 3.1 Resource model

**RA-01** — A contended resource SHALL be declared with a `resource_type`
and a `capacity`. `capacity` is 1 for exclusive resources and n > 1 for
capacity-limited resources.

**RA-02** — The following resource types are defined: `space` (a cell or
zone), `passage` (door, gate), `transport` (lift, conveyor), `dock`
(charging or rest position) and `task`. Implementations MAY define
additional types; they SHALL NOT redefine these.

**RA-03** — An agent SHALL hold a valid authority for a resource before
entering or occupying it. An implementation SHALL NOT rely on movement
itself as an implicit claim.

### 3.2 Authority

**RA-04** — An authority SHALL carry: the resource, the holding agent
(identified per CP-007), an end point, a validity expiry, and an issue
timestamp.

**RA-05** — An authority SHALL expire. An implementation SHALL NOT issue
an authority without an expiry.

**RA-06** — An agent whose authority has expired and cannot be renewed
SHALL stop before the resource and SHALL NOT enter it.

**RA-07** — An authority MAY be renewed before expiry. Renewal SHALL be
an explicit exchange, not an assumption.

### 3.3 Release

**RA-08** — An agent SHALL release a resource explicitly when it no
longer occupies it. Release SHALL be an event, observable in the audit
chain.

**RA-09** — An implementation SHALL be able to report, at any time,
which agent holds which resource and until when.

### 3.4 Lateral freedom and local avoidance

**RA-15** — An authority for a `space` resource SHALL state a **lateral
tolerance**: the band around the planned route within which the agent may
deviate without a new authority.

**RA-16** — Rotation about the agent's vertical axis SHALL NOT require
authority. Rotation is not a change of resource.

**RA-17** — An agent SHALL remain within its lateral tolerance. A
deviation that would take the agent into a different resource requires a
new authority before the movement is executed.

**RA-18** — Local avoidance of unregistered obstacles — people,
equipment, temporary objects — is the agent's own responsibility and
SHALL NOT require orchestrator approval while the agent stays within its
lateral tolerance. The agent SHALL report the avoidance as an event.

RA-18 is deliberate: requiring an orchestrator round trip before yielding
to a person would be both technically wrong and, in a hospital,
indefensible. The robot yields first and reports afterwards.

### 3.5 Block reservation

**RA-19** — An implementation MAY grant authority over a **block**: a set
of resources reserved together for one holder over one interval, rather
than granting each resource separately.

**RA-20** — Within a granted block, the holder SHALL move freely between
the included resources without requesting further authority. Outside the
block, or after its expiry, the holder has no authority whatsoever.

**RA-21** — A block SHALL be deconflicted once, at grant time, against
all other held blocks and authorities. An implementation SHALL NOT
require per-movement deconfliction within a granted block.

**RA-22** — A holder SHALL release a block, in whole or in part, as soon
as it is no longer needed. Released resources return to the pool
immediately and SHALL NOT wait for the block's expiry.

Block reservation is the mechanism that makes coordination scale: the
cost of deconfliction is paid once per block rather than once per
movement. It is particularly suited to a fleet operating a defined ward
or corridor section for a shift, and to any participant that wants to
plan internally without a round trip per step. Note that the freedom is
binary by design — total inside the block, none outside — so that no
implementation has to reason about a gradient.

### 3.6 Communication loss

**RA-10** — An agent that loses contact with the orchestrator SHALL stop
safely at the earliest safe position and SHALL NOT continue executing a
previously issued plan beyond its current authority.

**RA-11** — Authorities held by an agent that has lost contact SHALL be
released on expiry and SHALL NOT be extended automatically.

### 3.7 Conflict detection

**RA-12** — Where an implementation holds both a planned agent
trajectory and a scheduled resource reservation (for example a lift
reserved for bed transport), it SHALL compare them over a defined
look-ahead window and SHALL emit a `resource.conflict_predicted` event
when they overlap.

**RA-13** — The conflict event SHALL identify the resource, the two
claims, and the tick at which the overlap occurs. It SHALL NOT prescribe
the resolution.

**RA-14** — Resolution — which claim yields, whether the agent waits or
reroutes, how urgency is weighed — is implementation-defined and outside
this standard. Only detection and reporting are normative.

## 4. Delegated autonomy

A local fleet manager knows things Rocom does not and should not: battery
state, wear, maintenance windows, charging strategy, its own cost model.
It must be able to optimise on them. At the same time, several
participants each holding their own view of the next hundred ticks
produces several truths about the future.

### 4.1 The principle: standardise the commitment, not the plan

**RA-23** — A predicted trajectory is private. It MAY change at any time
and SHALL NOT be relied upon by other participants.

**RA-24** — A **commitment** is public and binding: a statement that an
agent will hold a named resource over a stated interval, or complete a
named task by a stated time. Conflict detection under RA-12 SHALL operate
on commitments, never on predictions.

This is the deliberate divergence from Open-RMF noted in §2. RMF
schedules intended trajectories and resolves conflicts between them,
which requires every participant to publish and mirror a living
trajectory database. Committing to resources and deadlines instead keeps
the shared surface small, lets each fleet keep its planning private, and
removes the many-truths problem: there is only one truth about what has
been *promised*, however many plans lie behind it.

### 4.2 Local replanning

Block reservation (§3.5) is the natural unit here: a fleet that holds a
block can replan inside it without any exchange at all, which is the
cheapest possible form of delegated autonomy.


**RA-25** — A local fleet manager MAY replan freely within its own domain
without orchestrator approval, provided every commitment it has made is
still met.

**RA-26** — A local fleet manager SHALL subscribe to resource and
commitment events for the resources it uses. Whether it optimises against
the wider picture is its own choice.

### 4.3 Bidding

**RA-27** — Where an implementation allocates a task by bidding, the bid
SHALL carry a cost and the commitments the bidder is willing to make. The
**composition** of that cost is outside this standard: battery, wear,
maintenance, crew or commercial factors are the bidder's own business and
SHALL NOT be required to be disclosed.

The format of the bid and the commitment is open; what goes into the bid
is closed — for us and for every other fleet vendor. That is what makes
participation safe for a vendor with a proprietary cost model.

This mirrors collaborative decision making in air traffic management,
where the authority allocates capacity in the form of slots while
operators reallocate among their own flights on criteria — crew hours,
connections, aircraft rotation — the authority neither sees nor needs.
The same division exists in rail: the infrastructure manager allocates
paths, the operators optimise their own rolling stock within them.

### 4.4 Breaking a commitment

**RA-28** — A participant that can no longer meet a commitment SHALL emit
`commitment.broken` as early as it knows, naming the commitment, the
reason and the earliest revised time. Silence is not an acceptable
failure mode.

**RA-29** — On receiving `commitment.broken`, an implementation SHALL
re-evaluate dependent commitments. What it does about them is
implementation-defined.

### 4.5 Levels of participation (informative)

Following Open-RMF's approach of defining integration levels rather than
one all-or-nothing interface, a fleet may participate at:

- **Observing** — subscribes to events, makes no commitments. Useful for
  monitoring and evidence only.
- **Committing** — makes and honours resource and task commitments.
  Minimum for shared operation.
- **Negotiating** — additionally responds to conflict notices with
  alternative commitments.

A conformance profile SHOULD state which level it claims.

## 5. Schema (illustrative)

```yaml
resource:
  resource_id: string
  resource_type: space | passage | transport | dock | task
  capacity: integer          # 1 = exclusive

authority:
  authority_id: string
  resource_id: string
  holder: <agent_identity.access_key or serial_number>
  end_point: string          # where the authority ends
  issued_at: timestamp
  expires_at: timestamp
  renewable: boolean

authority:
  lateral_tolerance_m: number   # band around route, RA-15

block:
  block_id: string
  resources: [resource_id]      # reserved together, RA-19
  holder: <agent or fleet identity>
  from: timestamp
  until: timestamp

commitment:
  commitment_id: string
  kind: resource | task
  subject: string               # resource_id or task_id
  holder: <agent or fleet identity>
  from: timestamp
  until: timestamp

events:
  resource.authority_granted
  resource.authority_renewed
  resource.authority_expired
  resource.released
  resource.conflict_predicted
  resource.local_avoidance          # RA-18
  resource.block_granted
  resource.block_released       # whole or partial, RA-22
  commitment.made
  commitment.broken                 # RA-24
```

## 6. Relationship to Sup-003

Sup-003 specifies the BMS boundary — how a door or lift is requested and
how the building responds. CP-008 specifies what a granted request *is*:
an authority with an end point and an expiry, held by an identified
agent, released explicitly. The two are complementary; Sup-003 governs
the exchange, CP-008 governs the object exchanged.

Where Sup-003 and CP-008 appear to conflict, Sup-003's safety clause
prevails.

## 7. Conformance tests

**CT-01** — A resource declared with capacity 3 accepts three
simultaneous holders and rejects the fourth.
**CT-02** — An authority issued without an expiry is rejected.
**CT-03** — An agent whose authority has expired is refused entry to the
resource.
**CT-04** — After an agent releases a resource, a query reports the
resource as unheld.
**CT-05** — An agent that stops reporting has its authorities released at
expiry, not extended.
**CT-06** — Two overlapping claims on one resource within the look-ahead
window produce exactly one `resource.conflict_predicted` event naming
both claims and the overlap tick.
**CT-07** — An agent that deviates within its stated lateral tolerance is
not refused and requires no new authority; a deviation crossing into
another resource is refused without one.
**CT-08** — Rotation in place produces no authority request.
**CT-09** — Local avoidance of an unregistered obstacle within tolerance
completes without orchestrator approval and emits
`resource.local_avoidance`.
**CT-10** — A conflict raised against a changed *prediction*, with all
commitments intact, produces no conflict event.
**CT-11** — A participant that cannot meet a commitment emits
`commitment.broken` with reason and revised time before the original
`until`.
**CT-12** — A holder of a granted block moves between resources inside
the block without issuing further authority requests.
**CT-13** — The same holder is refused entry to a resource outside its
block without a separate authority.
**CT-14** — A partial release of a block returns exactly the released
resources to the pool and leaves the remainder held.

## 8. Migration

Implementations that today treat grants as boolean remain conformant
until Edition 2026b, provided they can report holders (RA-09). From
2026b, authorities without expiry SHOULD be rejected.

## 9. References

- Sup-003 — BMS Infrastructure Contract (safety clause)
- CP-007 — Agent Identity Model
- ERTMS/ETCS System Requirements Specification — movement authority,
  release, safe reaction to communication loss *(informative)*
- ICAO / EUROCONTROL practice — STCA, MTCD, arrival sequencing, and
  collaborative decision making (slot allocation by the authority, slot
  reallocation by operators) *(informative)*
- Open-RMF — Traffic Schedule Database, fleet adapters, conflict notice
  and negotiation with rejection and forfeit paths, tiered integration
  levels *(informative)*
- Airspace block reservation in military air operations — a volume
  reserved for a using unit over a time window, with free manoeuvre
  inside, no standing permission outside, deconfliction at grant time,
  and early release back to the pool *(informative)*
- Railway capacity allocation — infrastructure manager allocates paths,
  operators optimise rolling stock within them *(informative)*
