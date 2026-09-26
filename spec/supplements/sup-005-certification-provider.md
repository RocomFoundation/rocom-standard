# Sup-005 — Certification Provider Requirements

| Field | Value |
|-------|-------|
| **Supplement** | Sup-005 |
| **Title** | Certification Provider Requirements |
| **Status** | DRAFT |
| **Edition** | 2026a |
| **Depends On** | Part 2 (Conformance), GOVERNANCE.md (Certification Program), Sup-004 (Governance Structure) |
| **License** | CC-BY 4.0 |

## 1. Scope

This supplement defines the requirements for an organization operating
the Rocom Certification Program on behalf of the ROCOM association.
The Certification Provider executes conformance testing, issues
certificates, and maintains the public certificate registry.

The Certification Provider operates under ROCOM Board oversight and
does not hold independent authority over certification policy.

## 2. Role

The Certification Provider is responsible for:

1. **Conformance testing.** Executing the Rocom conformance test suite
   against implementer submissions.
2. **Certificate issuance.** Awarding Rocom Certified status per Part
   and per level (L1 through L3) upon successful testing.
3. **Annual re-testing.** Maintaining certificate validity through
   periodic re-evaluation.
4. **Registry maintenance.** Operating a public, queryable certificate
   registry.
5. **Reporting.** Quarterly reporting to the ROCOM Board on certification
   activity, test results, and deviations.

## 3. Technical Requirements

### 3.1. Test Execution

| ID | Requirement |
|----|-------------|
| **CP-REQ-01** | The provider SHALL execute the full Rocom conformance test suite as published in the specification repository. Tests SHALL NOT be modified without ROCOM Board approval. |
| **CP-REQ-02** | Test execution SHALL be independent of the implementer's own test reports. The provider SHALL run tests against the implementer's build artifact, not source code. |
| **CP-REQ-03** | Test results SHALL be recorded with sufficient detail to reproduce: environment, test inputs, observed outputs, and pass/fail determination. |

### 3.2. Build Provenance

| ID | Requirement |
|----|-------------|
| **CP-REQ-04** | The provider SHALL verify the implementer's `build_provenance` block (Part 2, Section 3) before testing: toolchain, target, build command, artifact hash, and build log reference. |
| **CP-REQ-05** | If the artifact hash does not match the reproducible build, the provider SHALL reject the submission and request a corrected artifact. |

### 3.3. Certificate Granularity

| ID | Requirement |
|----|-------------|
| **CP-REQ-06** | Certificates SHALL be issued per Part and per conformance level (L1, L2, or L3). A single certificate covers one Part at one level. |
| **CP-REQ-07** | The certificate SHALL include: `certificate_id`, `certified_by` (provider name), `implementer`, `product`, `part`, `level`, `valid_until`, and issuance date. |
| **CP-REQ-08** | The `valid_until` date SHALL NOT exceed 12 months from issuance. |

### 3.4. Partial Conformance

| ID | Requirement |
|----|-------------|
| **CP-REQ-09** | The provider SHALL process partial conformance declarations per Part 2, Section 4: each deviation must list requirement ID, status, rationale, and planned resolution. |
| **CP-REQ-10** | Systems with more than three deviations at L2 or above SHALL NOT be eligible for Rocom Certified status. The provider SHALL reject such submissions. |

## 4. Operational Requirements

### 4.1. Application Process

| ID | Requirement |
|----|-------------|
| **OP-REQ-01** | The provider SHALL accept certification applications via a defined process. The applicant submits a Conformance Statement (Part 2, Section 3) with test evidence. |
| **OP-REQ-02** | The provider SHALL validate the Conformance Statement against the Part 2 template before scheduling testing. |
| **OP-REQ-03** | The provider SHALL communicate application status to the applicant: received, under review, testing, decision. |
| **OP-REQ-04** | The provider SHALL complete initial certification review within 30 business days of receiving a valid application. |

### 4.2. Re-testing

| ID | Requirement |
|----|-------------|
| **OP-REQ-05** | The provider SHALL notify the implementer at least 60 days before certificate expiry. |
| **OP-REQ-06** | The provider SHALL re-execute the full conformance test suite at the originally declared level. |
| **OP-REQ-07** | If the specification has advanced to a new Edition since the last certification, the provider SHALL test against the Edition valid at the time of the original certification, with an option to test against the newer Edition. |

### 4.3. Certificate Registry

| ID | Requirement |
|----|-------------|
| **OP-REQ-08** | The provider SHALL maintain a public, queryable certificate registry. Minimum exposure: URL-accessible list of certificates with `certificate_id`, `implementer`, `product`, `part`, `level`, and `valid_until`. |
| **OP-REQ-09** | Revoked or expired certificates SHALL be marked as such in the registry, with revocation date and reason. |

## 5. Independence Requirements

| ID | Requirement |
|----|-------------|
| **IND-REQ-01** | The provider SHALL NOT manufacture or sell robot hardware, Rocom-conformant management systems, or any product that could be certified under the Rocom standard. |
| **IND-REQ-02** | The provider SHALL NOT be under the same corporate ownership or controlling interest as any Rocom implementer applying for certification. |
| **IND-REQ-03** | Conflicts of interest SHALL be declared to the ROCOM Board and resolved by the Board, not the provider. |
| **IND-REQ-04** | The provider SHALL NOT modify certification criteria, test suites, or conformance requirements without explicit ROCOM Board approval. |

## 6. Data and Infrastructure Requirements

| ID | Requirement |
|----|-------------|
| **INF-REQ-01** | All certification data SHALL be stored with full audit trail: application submission, test execution logs, reviewer decisions, and certificate issuance. |
| **INF-REQ-02** | Test results SHALL be machine-readable (structured JSON or YAML), not solely human-readable documents. |
| **INF-REQ-03** | The certificate registry SHALL expose a read-only API (minimum: queryable list of active certificates). |
| **INF-REQ-04** | The provider SHALL produce a quarterly report for the ROCOM Board covering: applications received, certifications issued, re-tests completed, certificates revoked, and deviations logged. |

## 7. Provider Selection

The ROCOM Board is responsible for selecting the Certification Provider.
Criteria for selection include:

1. **Independence.** Demonstrated absence of conflict of interest per Section 5.
2. **Technical capability.** Ability to execute automated conformance test suites against compiled artifacts across multiple platforms.
3. **Experience.** Prior experience with standards-based certification (e.g., ISO 27001, IEC 62304, DICOM, HL7 FHIR implementation guides).
4. **Infrastructure.** Secure, auditable test infrastructure with reproducible environments.
5. **Geographic coverage.** Ability to serve implementers in Europe and internationally.

The Board may engage multiple providers for different geographic regions
or Parts, provided each provider satisfies these requirements independently.

## 8. Current Status

As of this supplement, a Certification Provider has not yet been selected.
The Specification Steward (Tech Happens Europe ApS) provides interim
stewardship and conformance testing capability. The ROCOM Board will
conduct provider selection after the Board is constituted.

## 9. Cross-References

- Part 2 — Conformance levels, Conformance Statement template
- GOVERNANCE.md — Certification Program overview
- Sup-004 — Governance Structure (Board authority over provider selection)
- CONTRIBUTING.md — Edition and Supplement process
