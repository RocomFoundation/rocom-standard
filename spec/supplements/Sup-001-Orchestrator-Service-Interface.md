# FILE: spec/supplements/Sup-001-Orchestrator-Service-Interface.md
# Sup-001 — Orchestrator Service Interface
# Status: MERGED (Edition 2026a draft)
# License: CC-BY 4.0
# Scope: Define the normative orchestrator service interface by splitting
#        a management system product API into standard and product-specific endpoints.
# NOTE:  Incorporated into Edition 2026a draft as normative text.

## Purpose

The orchestrator service interface defines the REST API that any
conformant orchestrator MUST implement. Currently, a management system product
API (17 endpoints) mixes standard requirements with product-specific
features. This supplement proposes a split so that the standard can
specify the interface independently of any single implementation.

## Endpoint Analysis

### 1. Agents — NORMATIVE (all 7 endpoints)

| Endpoint | Rationale |
|----------|-----------|
| `GET /agents` | Every orchestrator MUST expose its agent registry. Foundational. |
| `POST /agents` | Agent onboarding is a core orchestrator function (Part 6, it-p-002). |
| `GET /agents/{id}` | Single-agent lookup is required for task allocation and auditing. |
| `PATCH /agents/{id}` | Capability and status updates are fundamental to agent lifecycle. |
| `DELETE /agents/{id}` | Agent offboarding (deregistration) is required by Part 6 (it-p-002). |
| `GET /agents/{id}/availability` | Availability polling is the standard contract for availability providers (Part 4). |
| `GET /agents/{id}/data-profile` | Data profile retrieval is required by Part 7 (dg-req-001). |

**Verdict:** All 7 endpoints are normative minimum for any orchestrator.

### 2. Tasks — NORMATIVE (4 endpoints)

| Endpoint | Rationale |
|----------|-----------|
| `GET /tasks` | Task listing is fundamental to orchestrator visibility. |
| `POST /tasks` | Task creation is the primary input to the orchestrator (Part 4, task-source contract). |
| `GET /tasks/{id}` | Single-task lookup required for status tracking and auditing. |
| `PATCH /tasks/{id}` | Task status updates are fundamental (assignment, completion, cancellation). |

**Verdict:** All 4 endpoints are normative minimum. The "Cancel Task"
request (`PATCH /tasks/{id}` with `status: cancelled`) is a status
update, not a separate endpoint — covered by the PATCH above.

### 3. Audit — NORMATIVE (2 endpoints)

| Endpoint | Rationale |
|----------|-----------|
| `GET /audit` | Audit trail access is required by Part 2 (conformance) and Part 6 (it-p-004). |
| `GET /audit/verify` | Cryptographic verification is required for Part 6 conformance (immutable audit trail). |

**Verdict:** Both endpoints are normative. The audit trail is a
cross-cutting requirement that every conformant orchestrator MUST provide.

### 4. Proposals — PRODUCT-SPECIFIC (3 endpoints)

| Endpoint | Rationale |
|----------|-----------|
| `POST /proposals` | Proposal generation with strategies (`greedy`, `cost_optimized`, `fastest`) is a product-specific allocation approach. |
| `POST /proposals/{id}/accept` | The accept/reject workflow is a product-specific human-in-the-loop design choice. |
| `POST /proposals/{id}/reject` | Same — a product-specific approval workflow. |

**Verdict:** Product-specific. Other orchestrators may use direct
assignment, automated allocation, or different approval workflows.
The standard MUST NOT prescribe the proposal model — it is one valid
approach among many.

## Proposed Split

| Category | Endpoints | Standard? |
|----------|-----------|-----------|
| Agents | 7 | YES — normative (Part 8: Orchestrator Service Interface) |
| Tasks | 4 | YES — normative |
| Audit | 2 | YES — normative |
| Proposals | 3 | NO — product-specific feature

**Standard interface:** 13 endpoints (Agents + Tasks + Audit)
**Product-specific:** 3 endpoints (Proposals)
**Total:** 16 endpoints (13 standard + 3 product-specific)

> Note: Postman collection has 17 requests because "Cancel Task" is a
> separate request for PATCH /tasks/{id} with `status: cancelled` — not
> a distinct endpoint. The OpenAPI spec has 16 paths. The count of
> 13 standard endpoints excludes the 3 proposal endpoints, which are
> product-specific features, not normative.

## Recommendation

The 13 normative endpoints are incorporated as the orchestrator service
interface requirement in Edition 2026a draft. After full Edition
publication:
1. OpenAPI spec is published as a standalone machine-readable artifact.
2. A management system's Postman collection references the standard's
   13 endpoints via submodule and extends with its own 3 proposal
   endpoints.
3. The proposal model is documented in the management system's product
   docs, not in the standard.
