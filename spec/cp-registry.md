# Correction Proposal (CP) and Supplement (Sup) Registry

This registry is the authoritative source for CP and Sup numbering.
Numbers are assigned ONLY from this registry. Registry update is part
of the same commit as the CP/Sup content.

## Correction Proposals

| CP | Title | Commit | Date | Status | Repo |
|----|-------|--------|------|--------|------|
| CP-001 | Split architecture figure from Part map | 6db39cf | 2026-08-12 | MERGED | rocom-standard |
| CP-002 | Remove FILE scaffolding from CONFORMANCE.md; fix requirement format | 6db39cf | 2026-08-12 | MERGED | rocom-standard |
| CP-003 | GOVERNANCE.md — funding, held-in-trust, Advisory Board | 1aafa99 | 2026-08-12 | MERGED | rocom-standard |
| CP-004 | — | — | — | RESERVED | — |
| CP-005 | Pin VDA 5050 version to 2.1 | d69e8ce | 2026-08-21 | MERGED | rocom-standard |
| CP-006 | CostModel generalization — cost_factors array | 76c4cbb | 2026-08-22 | MERGED | rocom-standard |
| CP-007 | Agent Identity Model (issuer-agnostic, UDI-aligned) | — | 2026-08-28 | PROPOSAL | rocom-standard |
| CP-008 | Resource Authority Model | — | 2026-08-30 | PROPOSAL | rocom-standard |
| CP-009 | Priority and Preemption Model | — | 2026-08-31 | PROPOSAL | rocom-standard |
| CP-010 | Shared Occupancy and Physical State Authority | — | 2026-09-17 | PROPOSAL | rocom-standard |

> Note: Commit d69e8ce message says "CP-001" — incorrect labeling.
> This registry is authoritative.

## Supplements

| Sup | Title | Commit | Date | Status |
|-----|-------|--------|------|--------|
| Sup-001 | Orchestrator Service Interface | 2df097b | 2026-08-12 | MERGED |
| Sup-002 | Annex A — Engineering Practice Notes | e257ab5 | 2026-08-18 | MERGED |
| Sup-003 | BMS Infrastructure Contract | c75b931 (scope), 1d742df (normative) | 2026-08-21 | DRAFT |
| Sup-004 | — | — | — | RESERVED |

## Numbering Rules

1. Numbers are sequential within each series (CP-001, CP-002, ... Sup-001, Sup-002, ...).
2. The NEXT available number is **CP-011** and **Sup-004**.
3. New CPs/Sup must update this registry in the same commit.
4. Commit messages reference the CP/Sup number; the registry is authoritative.
