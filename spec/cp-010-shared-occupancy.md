# CP-010 — Shared Occupancy and Physical State Authority

**Status:** PROPOSAL
**Target:** Sup-003 — BMS Infrastructure Contract
**Also affects:** Part 3 (Information Model)
**Raised:** 17 September 2026
**Author:** Rocom Project
**Depends on:** CP-008 (resource authority), CP-009 (priority and
preemption). Both are PROPOSAL at the time of writing; this proposal
cross-references them and does not restate their requirements.

---

## 1. Problem

Sup-003 defines door access and elevator dispatch as an exchange between a
robot and a building management system. The exchange is complete on its own
terms: a request is made, an authorization is granted or denied, the robot
proceeds.

It is incomplete against the building. Corridors, doorways and elevator cars
are occupied by staff, patients and visitors who are not Rocom agents, are not
in any agent registry, and never will be. Sup-003 currently says nothing about
them, which leaves three failures available to a conformant implementation:

1. **Authorization read as physical state.** `authorization: granted` says the
   robot is permitted to pass. It does not say the door is open. An
   implementation that treats the grant as the state will drive at a closed
   door.

2. **Registry read as occupancy.** An orchestrator that knows every agent may
   conclude that a resource with no agent in it is free. An elevator car with
   four people and no robot is not free.

3. **Queued read as dispatched.** `dispatch_status: queued` produces an
   `estimated_arrival` and a car assignment. Nothing states that the robot must
   remain clear of the doors until the car is actually its own.

Each failure is a robot occupying space a person is using. That is a contract
between independent parties in a shared building, and it belongs in the open
standard.

## 2. Design basis (informative)

**Physical state over declared state.** The principle is already present in
Sup-003 §4.1: the building's safety systems are authoritative. This proposal
extends the same precedence to ordinary operation. Where a declared
authorization and a reported physical state disagree, the physical state
governs.

**The registry is not a census.** Rocom's agent registry enumerates
participants in the protocol. It is not, and must not become, an enumeration of
people in a building. Part 7 forbids the latter on data-governance grounds;
this proposal states the operational consequence — occupancy must be read from
building sensors, never inferred from the registry.

**Stand-off distance.** Industrial and service robot practice distinguishes
waiting *near* a resource from waiting *in* it. The distinction is cheap to
specify and is what keeps a queued robot out of a doorway that people are
using.

## 3. Normative requirements

### 3.1 Physical state governs

**SO-01** — Where the BMS reports a physical state for a resource, the robot
SHALL act on the reported state and not on the authorization alone. An
`authorization` is permission to use a resource in the state the building
reports it to be in.

**SO-02** — A robot holding `authorization: granted` for a door SHALL proceed
only where the BMS-reported door state is `open`, in deployments where the BMS
exposes door state. A grant is not permission to force, push or otherwise act
upon a closed door.

**SO-03** — Where the BMS does not expose door state, the implementation SHALL
declare this in its conformance statement. The absence of reported state is not
equivalent to a reported open state.

### 3.2 Occupants outside the registry

**SO-04** — Building occupants who are not Rocom agents MAY occupy doorways,
door openings and elevator cars. They SHALL NOT be registered as Rocom agents
and SHALL NOT appear in the agent registry.

**SO-05** — An implementation SHALL NOT infer that a resource is unoccupied
from the absence of an agent holding it. BMS-reported occupancy and physical
state are the authority on whether a resource is free; the agent registry is
not.

**SO-06** — A robot waiting for a door SHALL wait on BMS-reported door state,
not on an agent registry event.

### 3.3 Elevator occupancy

**SO-07** — The elevator dispatch response MAY carry `occupancy` and
`capacity`. Where carried, `occupancy` SHALL count all occupants of the car,
not only robots.

**SO-08** — Where the BMS reports both `occupancy` and `capacity`, the robot
SHALL NOT board a car reported at capacity, regardless of its dispatch status
or task priority.

**SO-09** — The elevator dispatch response MAY carry `queue_position` where
`dispatch_status` is `queued`.

### 3.4 Stand-off and queue

**SO-10** — While `dispatch_status` is `queued`, the robot SHALL remain at a
stand-off position clear of the car doors and SHALL NOT enter the car.

**SO-11** — The robot MAY enter the car only once `dispatch_status` is
`dispatched` and `boarding_status` is `boarding`.

**SO-12** — While queued, the robot MAY cancel the request and issue a new
request naming a different car the BMS reports idle. Where the implementation
models the car as a held resource, the cancellation and the new request are
subject to CP-008.

**SO-13** — If a trip completes and the car returns to idle without the robot
having reached `on_board`, the robot SHALL treat the request as expired and MAY
issue a new request. The robot SHALL NOT remain blocked on a completed trip.

### 3.5 Precedence

**SO-14** — Sup-003 §4.1 prevails over this proposal in all cases. Nothing here
authorises a robot to enter a car, hold a door, or remain in a doorway on the
basis of an authorization where BMS-reported physical state contradicts it.

**SO-15** — Priority does not relax any requirement in this proposal. The
ordering of competing requests and the semantics of preemption are specified in
CP-009 and are not restated here. CP-009 PR-10 — a resource occupied by a
person SHALL NOT be preempted — is absolute and applies to every resource
governed by Sup-003.

## 4. Changes to Sup-003

### 4.1 §3.1.3 — Door Access, Behavior

Replace the `granted` bullet with:

> - If `authorization` is `granted`, the robot SHALL proceed only when the
>   BMS-reported door state is `open`, where the BMS exposes door state. A
>   `granted` authorization is permission to pass through an open door. It is
>   not permission to force, push or otherwise act upon a closed door.
> - The robot SHALL re-request before `valid_until`.
> - Building occupants who are not Rocom agents — staff, patients, visitors —
>   MAY hold a door open or closed. They are not Rocom agents and SHALL NOT be
>   registered as such. The robot SHALL wait on BMS-reported door state, not on
>   an agent registry event.

### 4.2 §3.2.2 — Elevator Dispatch, Response Schema

Add three rows:

> | `queue_position` | Integer | 1..1 if `queued`; 0..1 otherwise | 1-based position in the dispatch queue |
> | `occupancy` | Integer | 0..1 | Occupants currently in the assigned car, counting all occupants, not only robots |
> | `capacity` | Integer | 0..1 | Car capacity as reported by the BMS |

### 4.3 §3.2.4 — new subsection

Insert after §3.2.3:

> #### 3.2.4. Shared occupancy and wait
>
> Elevators and doors are shared building resources. A Rocom agent is one
> participant among building occupants who are not, and cannot be, represented
> in the agent registry.
>
> - Building occupants who are not Rocom agents MAY occupy elevator cars and
>   door openings. They SHALL NOT appear in the agent registry. BMS-reported
>   occupancy, car state and door state are the authority on whether a resource
>   is free; the agent registry is not.
> - `occupancy` SHALL count all occupants of the car, not only robots. Where
>   the BMS reports both `occupancy` and `capacity`, the robot SHALL NOT board
>   a car reported at capacity.
> - While `dispatch_status` is `queued`, the robot SHALL remain at a stand-off
>   position clear of the car doors and SHALL NOT enter the car. The robot MAY
>   enter only once `dispatch_status` is `dispatched` and `boarding_status` is
>   `boarding`.
> - While queued, the robot MAY cancel the request and issue a new request
>   naming a different car that the BMS reports idle. Where an implementation
>   models the car as a held resource, the cancellation and the new request are
>   subject to CP-008.
> - If a trip completes and the car returns to idle without the robot having
>   reached `on_board`, the robot SHALL treat the request as expired and MAY
>   issue a new request. The robot SHALL NOT remain blocked on a completed
>   trip.
> - Human traffic and emergency operations preempt robot requests. The ordering
>   of competing requests and the semantics of preemption are specified in
>   CP-009 and are not restated here.
>
> The safety clause of §4.1 prevails over this subsection in all cases.

## 5. Relationship to other proposals

**CP-008 (Resource Authority Model)** governs the authority object — its
holder, its expiry, its release. CP-010 governs whether the physical resource
that authority refers to may actually be entered. An expired authority and an
occupied car are different refusals, and an implementation needs both.

**CP-009 (Priority and Preemption Model)** governs which of several contending
claims is served first. CP-010 governs what a robot does while it is not being
served. PR-09 already states that priority does not bypass authority; SO-15
adds that priority does not bypass physical state either.

Where CP-010 and CP-009 appear to conflict, Sup-003's safety clause prevails,
consistent with CP-009 PR-11.

## 6. Conformance tests

Test identifiers are reserved in Sup-003 §5.1, the existing BMS series, rather
than introduced here. This keeps one test series per specification document.

**BMS-14** — A robot issued `dispatch_status: dispatched` for a car the BMS
reports at capacity does not board, and either waits or re-requests.

**BMS-15** — A robot holding `authorization: granted` for a door the BMS
reports as closed does not attempt passage, and does not report an error before
`response_deadline` elapses.

**BMS-16** — A robot queued for a car that completes a trip without the robot
boarding treats the request as expired rather than remaining blocked.

**BMS-17** — A robot with `dispatch_status: queued` remains clear of the car
doors and does not enter the car.

**BMS-18** — An orchestrator does not report a resource as free on the basis of
an empty agent registry where the BMS reports the resource occupied.

## 7. Migration

Implementations that today act on authorization alone remain conformant until
Edition 2026b, provided they can report whether the BMS exposes door state and
car occupancy (SO-03). From 2026b, an implementation that boards a car reported
at capacity is not conformant.

`occupancy`, `capacity` and `queue_position` are optional fields. A BMS that
cannot report them does not become non-conformant; the robot's obligations
under SO-08 apply only where the values are reported.

## 8. References

- Sup-003 — BMS Infrastructure Contract (safety clause, §4.1)
- CP-008 — Resource Authority Model
- CP-009 — Priority and Preemption Model
- Part 7 — Data Governance (agent registry scope)
- Service robot practice on stand-off distance from shared resources
  *(informative)*
