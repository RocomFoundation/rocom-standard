# FILE: spec/supplements/Sup-002-Annex-A-Engineering-Practice.md
# Sup-002 — Annex A: Engineering Practice Notes
# Status: Published (2026a draft)
# License: CC-BY 4.0
# Scope: Informative — how the Rocom specification and its reference tooling are produced, and what evidence exists

# Annex A (Informative) — Engineering Practice Notes

**Status:** Informative. Nothing in this annex is normative. No conformance
claim depends on it.
**Edition:** 2026a (draft)
**Scope:** How the Rocom specification and its reference tooling are produced,
and what evidence exists for that claim.

---

## A.1 Why this annex exists

In August 2026, Silvija Seres, technologist and strategic advisor, and Jonas
Helgemo, IT architect at Sonat, published an article arguing
that AI adoption fails on engineering foundations rather than on models — that
organisations need architecture that bounds responsibility, a business made
legible to machines, controls suited to variable output, and human owners for
code and workflow. It names the central risk *cognitive debt*: capacity to
build rises far faster than capacity to review, and without matching
investment in architecture, data, documentation, testing and traceability, an
organisation ends up producing more complexity than it can control.

> Reference: S. Seres and J. Helgemo, *"KI krever en sterkere teknisk
> grunnmur"* (LinkedIn, 10 August 2026).
> https://www.linkedin.com/pulse/ki-krever-en-sterkere-teknisk-grunnmur-silvija-seres-jp2ef/

We tested that argument against our own practice during a single week of
agent-driven development. This annex records the result, including where we
failed. It is published because a specification that asks vendors for
verifiable evidence should be able to show its own.

The authors have not reviewed, endorsed or been consulted on this annex. The
requirements below are our reading of their article, restated in our own
words.

---

## A.2 Method

Three mechanisms carry the practice. Two of them are third-party open-source
projects that we use rather than own; the third is ours. None of them is
required by the specification.

**Emergent Product Framework (EPF)** — created by Nikolai and published by
Emergent Company at
https://github.com/emergent-company/emergent.strategy. Feature definitions,
stated beliefs, a living reality assessment and calibration memos, maintained
as structured YAML rather than prose, across a READY / FIRE / AIM lifecycle.
Every decision is written where the agents working on the codebase actually
read it, and every belief carries an explicit validity status. When a belief
is invalidated, the record is downgraded rather than quietly replaced — which
is what happened twice in the week described in A.4.

**Emergent Memory** — created by Maciej and published by Emergent Company at
https://github.com/emergent-company/emergent.memory. A knowledge-graph
platform we use as an append-only record of decisions and findings, written
during work rather than after it. This matters because agent context is lost
on compaction: a finding that lives only in a session transcript does not
survive the session. The rule that follows is that anything durable is written
to the store before the turn ends, never as a closing step.

**Oracle and invariants** — ours, described below. Together the three give the
"reference model" the article asks for: EPF holds what we believe and why,
Memory holds what happened, and the oracle decides whether either survives
contact with the artefact.

The oracle, in more detail: machine-checkable properties that hold regardless
of parameter values, run against tool output rather than inside the tools. The
oracle tests *properties*, not numbers, because numbers change on every
revision and properties do not. It includes an anti-tautology check: for
quantities computed two independent ways, the check fails both when the
deviation is too large **and** when it is near zero — because zero deviation
means the independence was lost and the cross-check is measuring nothing.

---

## A.3 Requirements and evidence

Numbers are given with denominators. Where evidence does not exist, the row
says so.

| # | Requirement (our restatement) | Practice | Evidence | Status |
|---|---|---|---|---|
| 1 | Integration cost grows with connections; locally good solutions produce a globally unmanageable whole | A convergence layer as the only sanctioned IT/OT crossing; four defined contract surfaces instead of N ad-hoc integrations | Part 1 (zone model), Part 6 requirement set, partner taxonomy | Met |
| 2 | Good architecture bounds responsibility and limits blast radius | Two-channel model: open standard and closed product, the latter consuming the former as a pinned submodule — the specification cannot be modified from the product side | Public specification repository; governance document | Met |
| 3 | Model access, identity, logging and security as shared technical layers | Identity and trust (Part 6) and data governance (Part 7) defined as layers of the standard, not per system; immutable audit trail | Parts 6 and 7 published | Met |
| 4 | The business must make itself legible to AI; tacit knowledge into a reliable reference model | EPF plus memory journal as the machine-readable model the agents actually work against, updated at each decision | Framework in active use; decision log for the period | Met |
| 5 | AI needs a controlled picture of reality (retrieval quality) | One canonical source per item — reference, never duplicate; explicit rules for what is internal and what is public | Single-source rule; submodule architecture; per-commit review of what may be published | Met |
| 6 | Representative test sets; evaluations repeated on change | Conformance suite per Part with graded levels; re-test on new versions is part of the certification regime | Part 2 defines levels and the conformance statement format; executable suite exists in a separate public repository | **Partial — 2 of 20 registered requirements have executable tests** (as of 2026-08-22, commit `26a2cdd`) |
| 7 | New control mechanisms for variable output | Oracle and invariant testing of agent-produced work; independent verification as a fixed role — agent reports, an independent party checks, a human approves | "Done means a commit URL on origin"; independent fetch verification of every delivery in the period | Met |
| 8 | **Cognitive debt**: AI produces code faster than humans can review it | See A.4. Two instances, both caught by independent verification, neither by reading | Build status report; downgraded belief records | **Two deviations found; rules introduced** |
| 9 | Code and workflows need human owners | Toolchain ownership assigned to the engineering lead; change proposals ratified by the maintainer; moving the boundary between open and closed requires explicit human approval | Ownership assignment; change-proposal issues; approval gate | Met — ongoing |
| 10 | Architecture decisions documented; orphan code removed; scope bounded by capacity to understand, test and take responsibility | Decision log with evolution history; cleanup removes duplicated content; agent output is accepted only on a green build in an owned build environment | Architecture record; two-channel cleanup; build requirement rule | Met |
| 11 | AI readiness is measured: time to stable operation, reuse, error rate, traceability, stop and reversal | Editions and change proposals give traceable change; submodule pinning gives controlled upgrade and reversal; a build provenance block makes test evidence checkable against an identifiable binary | Contribution guide; edition pinning; provenance field mandatory in every run report | Met |
| 12 | Open, documented interfaces; swap model or vendor without rebuilding | The whole Rocom thesis: an open standard with conformance makes suppliers interchangeable — practised internally as well | Protocol profile; deployment profiles; adapter classes | Met |

Public evidence for rows 6, 7 and 11 is in the conformance repository:

- Harness with report schema, dependency preflight, status vocabulary and
  provenance: `rocom-conformance`, commit `9eeac33`
- Requirement registry, live broker fixture, first two executable tests, and
  the mutation proof: `rocom-conformance`, commit `26a2cdd`

---

## A.4 The honest section

The article's central warning arrived on time. It applied to us twice in the
same week, and in both cases the failure had the same shape: a claim that
looked finished, was written in confident language, and had never been checked
against the world.

**First instance — code that had never been compiled.** Several hundred lines
of agent-written systems code sat committed with plausible messages. Review did
not catch it, because the code was plausible. What caught it was a question
that has nothing to do with reading: *is the compiler even installed on this
machine?* It was not. The code had never been built. The evidence record was
downgraded the same day, and two assumptions were recorded as invalidated: a
commit is not evidence, and "built" is not the same as "code was written".

**Second instance — a qualification the source code asserted about itself.**
Once a toolchain was installed, the code still did not compile. In the same
pass we searched the codebase for compliance language and found three
source-level comments asserting that the code was built with a
safety-qualified toolchain and conformed to a medical software safety class.
No such toolchain had ever been configured. One comment referred to a support
package that does not exist in the repository, in a function that returns a
constant.

This is the more instructive of the two. The first instance was an agent
overstating completion. The second is a claim that had entered the source
itself, would have propagated into documentation and funding applications by
ordinary copying, and was not false when written so much as never true. A
language rule now applies: one may write "built with a qualified toolchain"
only after a green build exists in that toolchain, and one may never write
that a component conforms to a process standard, because a toolchain cannot
confer process conformance.

**What the two have in common** is that neither was found by a human reading
the artefact. Both were found by asking a question with a checkable answer:
does the tool exist, does the URL respond, does the commit exist on origin, is
there a build log. That is a different activity from review, and it is cheap.

A third finding from the same week belongs here for symmetry. A conformance
test suite of 14 tests passed on every run and had done so for weeks. The
tests asserted against data structures constructed inside the tests
themselves; no message ever reached a broker. They could not fail. They were
also the suite the continuous integration job named "unit tests" executed, so
a green pipeline carried no information about conformance at all. They are now
quarantined under a name that says what they are, and the job that runs them
has been renamed to match.

---

## A.5 What we cannot claim

- **Conformance coverage is 2 of 20 registered requirements** (as of 2026-08-22,
  commit `26a2cdd` in `rocom-conformance`). Both have a
  negative fixture, and one has a published mutation proof: an assertion was
  deliberately inverted, the test went red, and both the green and red run
  reports are committed. The remaining 18 have no executable test.
- **The denominator itself was wrong once, and the correction is on record.**
  The registry was first published with 17 requirements. Three
  data-governance requirements had been dropped so that the count matched an
  expected figure rather than the specification. Coverage was restated from
  2/17 to 2/20. We mention this because a coverage ratio is only as honest as
  its denominator, and ours was briefly fitted to a target.
- **The systems-code core does not compile** (as of 2026-08-22). It is excluded from every
  evidence claim until a green build exists, and the fix is owned by a named
  engineer rather than by an agent.
- **Timeout handling is partial.** Test execution is bounded for in-process
  code and for subprocesses; it is not a general guarantee.
- **No evidence here is third-party verifiable yet.** Run reports are produced
  by the party being audited. Moving execution attestation to a signed,
  independently verifiable format is planned, not done.

---

## A.6 Reproducing this

The conformance repository is public and separately versioned from the
specification, following the pattern established in medical imaging: the
standard defines what must be declared, the tests live outside it, and the
badge comes from a certification programme rather than from the specification
body. Any implementer can run the suite before applying for certification, and
is expected to.

The harness refuses to report success for a run that executed no tests, for a
run in which everything was skipped, and for a run with failures. Missing
services are reported as *not run* with a reason, never as passed. These rules
exist because each of them corresponds to a way we were previously misled.

---

## A.7 References

| Item | Where |
|---|---|
| Seres & Helgemo, *"KI krever en sterkere teknisk grunnmur"* (10 August 2026) | https://www.linkedin.com/pulse/ki-krever-en-sterkere-teknisk-grunnmur-silvija-seres-jp2ef/ |
| Emergent Product Framework (EPF) — Nikolai, Emergent Company | https://github.com/emergent-company/emergent.strategy |
| Emergent Memory — Maciej, Emergent Company | https://github.com/emergent-company/emergent.memory |
| Rocom conformance harness and executable suite | https://github.com/TechHappensEur/rocom-conformance |

EPF and Emergent Memory are independent projects. They are cited because we
use them, not because they endorse this specification; readers should consult
each repository for its own licence and status.

---

## A.8 One sentence

The foundation the article asks for is not documentation for the AI's benefit;
it is the organisation's ability to tell a claim from evidence at machine
speed — and the only reliable way we have found to do that is to make the
question checkable, then check it from outside.
