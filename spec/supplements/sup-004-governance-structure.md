# Sup-004 — Governance Structure: Board and Working Groups

| Field | Value |
|-------|-------|
| **Supplement** | Sup-004 |
| **Title** | Governance Structure: Board and Working Groups |
| **Status** | DRAFT |
| **Edition** | 2026a |
| **Depends On** | GOVERNANCE.md (ownership, stewardship) |
| **License** | CC-BY 4.0 |

## 1. Scope

This supplement defines the organizational governance structure of the
ROCOM association (CVR 46774043). It specifies the composition and
responsibilities of the Board of Directors and the Working Groups
that develop and maintain the Rocom specification.

The model follows established practice from DICOM and HL7 standards
organizations, adapted for the scope and size of Rocom.

## 2. Reference Models

| Organization | Board | Working Groups |
|---|---|---|
| **DICOM** | Board of Directors — appointed from radiology/medtech leadership | Functional Groups — each maintains a PS3.x part |
| **HL7** | Board of Directors — CEO-level from medtech and health organizations | Work Groups — chaired by board-appointed experts |

ROCOM adopts the two-tier model: a Board provides strategic direction
and appoints Working Group leadership; Working Groups execute
specification development through the CP/Supplement process.

## 3. Board of Directors

### 3.1. Composition

The Board consists of **5 to 9 members**, recruited from leading
positions in:

- Robotics and autonomous systems
- Healthcare IT and hospital operations
- Standards organizations (e.g., ISO, IEC, CEN, HL7, DICOM)
- Building management systems and infrastructure

### 3.2. Appointment

Board members are recruited and confirmed by the ROCOM association
in accordance with its articles of association. The Board is
responsible for its own succession planning.

### 3.3. Responsibilities

The Board is responsible for:

1. **Strategic direction.** Setting the scope, roadmap, and Edition
   timeline for the Rocom specification.
2. **Edition approval.** Formal approval of Editions before publication.
3. **Working Group leadership.** Appointing a Chair and Vice-Chair
   for each Working Group.
4. **Conflict resolution.** Resolving disputes between Working Groups
   or on cross-cutting specification matters.
5. **Representation.** Public representation of the ROCOM association
   and the Rocom standard.
6. **Oversight.** Ensuring vendor neutrality and adherence to the
   stewardship principles defined in GOVERNANCE.md.

### 3.4. Meetings

The Board meets at least quarterly. Meetings may be in person or
remote. Decisions are made by majority vote. The Board may delegate
operational authority to the Specification Steward (Tech Happens
Europe ApS) for day-to-day management.

## 4. Working Groups

Working Groups are the primary bodies for specification development.
Each Working Group is responsible for one of the four partner contract
planes defined in Part 1, Section 5.

### 4.1. Structure

| WG | Name | Contract Plane | Specification Scope |
|----|------|----------------|---------------------|
| **WG-1** | Robot | Robot Vendor | Part 5: Transport Profile, VDA 5050 binding, capability registry, robot conformance |
| **WG-2** | Infrastructure | BMS Infrastructure | Part 5: BMS protocols, access control, elevators, zone authorization |
| **WG-3** | Workforce | Availability Provider | Part 4: Availability Provider Interface, HR/turnus integration. The workforce includes both humans and robots as agents. |
| **WG-4** | Task | Task Source | Part 4: Task Source Interface, task generation, prioritization, enterprise system integration |

### 4.2. Leadership

Each Working Group has:

- **Chair** — appointed by the Board; responsible for WG direction,
  meeting facilitation, and liaison to the Board.
- **Vice-Chair** — appointed by the Board; assumes Chair duties
  in their absence; supports Chair on cross-WG coordination.

### 4.3. Membership

Working Group membership is open to any individual or organization
with interest in the WG's scope. Participants contribute through:

- Correction Proposals (CP) and Supplement proposals
- Review of proposals from other members
- Implementation experience and testing
- Participation in WG meetings and discussions

The Chair and Vice-Chair do not veto proposals — they facilitate
consensus and escalate unresolved matters to the Board.

### 4.4. Cross-WG Coordination

When a proposal affects multiple Working Groups:

1. The originating WG identifies the affected WGs.
2. Chairs of affected WGs are consulted before the proposal advances
   to PROPOSAL status.
3. If consensus cannot be reached between WG Chairs, the matter is
   escalated to the Board.

## 5. Relationship to Specification Steward

The Specification Steward (Tech Happens Europe ApS) handles
day-to-day operations:

- Repository maintenance and CI/CD
- Processing CP and Supplement submissions
- Running the Rocom Certification Program
- Organizing WG meetings and maintaining minutes

The Steward does not set specification direction — that authority
resides with the Board and Working Groups.

## 6. Current Status

As of this supplement, the Board is not yet constituted. The first
Board will be recruited and appointed by the ROCOM association in
accordance with its articles. The Specification Steward (Tech Happens
Europe ApS) provides interim stewardship until the Board is operational.

## 7. Cross-References

- GOVERNANCE.md — ownership, stewardship principles, certification
- Part 1, Section 5 — partner contract planes
- CONTRIBUTING.md — CP and Supplement process
- CP-003 — initial governance principles (funding, held-in-trust, Advisory Board)
