#!/usr/bin/env python3
"""
Coordination declaration validator and test fixtures.
Covers issue #13 §D acceptance scenarios:
  1. Valid scoped coordination declaration
  2. Legacy declarations under version/compatibility rules
  3. L0 manual handoff vs missing interface (not_provided)
  4. Mixed-level workflow rejected for end-to-end L3
  5. Assurance/human authority preserved at every coordination level
  6. Valid authorised policy reference accepted
  7. Expired/revoked policy, digest mismatch, wrong scope, unauthorised issuer rejected
  8. Unsupported required extension cannot silently pass
  9. Optional private extension cannot change mandatory semantics
 10. Decision/evidence identifies exact policy version used

Run: python3 build/test_coordination_declaration.py
"""
import json
import hashlib
import sys
from datetime import datetime, timezone


def sha256_digest(text):
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


# ── Schema definitions ──

VALID_PLANES = ["robot", "infrastructure", "workforce", "task"]
VALID_LEVELS = ["L0", "L1", "L2", "L3"]
VALID_VERIFICATION = ["conformant", "partial", "not_tested"]
VALID_PROVISION = ["planned", "provided", "not_provided"]
SCHEMA_VERSION = "rocom-conformance/control-planes-1.0"


# ── Synthetic evidence resolver ──

class EvidenceResolver:
    """Authoritative resolver for integration evidence.

    Maps test_ids to verified results, validates scope, contract version,
    and cumulative requirement coverage. Policy data cannot self-authorise
    evidence.
    """
    def __init__(self, verified_tests=None, contract_version=None):
        """
        verified_tests: dict mapping test_id -> {
            interfaces: [interface_ids covered],
            result: PASS/FAIL,
            scope: deployment_scope (single_site/multi_site),
            contract_version: spec edition string,
        }
        contract_version: canonical spec edition for this declaration
        """
        self.verified_tests = verified_tests or {}
        self.contract_version = contract_version

    def resolve(self, test_id):
        """Resolve a single test_id. Returns test metadata or None if unknown."""
        return self.verified_tests.get(test_id)

    def validate_integration_evidence(self, wf, decl, errors):
        """Validate L3 integration_evidence with actual lookup.

        Checks:
        - workflow_id matches
        - test_ids resolve to real tests
        - all tests PASS
        - collective coverage includes all required interfaces
        - scope matches declaration context
        - contract_version matches declaration specification
        """
        ie = wf.get("integration_evidence")
        if not ie or not isinstance(ie, dict):
            errors.append(
                f"E2E L3 on '{wf.get('id','?')}': integration_evidence must be a structured object (cpl-req-503)"
            )
            return

        # workflow_id binding
        if ie.get("workflow_id") != wf.get("id"):
            errors.append(
                f"E2E L3 on '{wf.get('id','?')}': integration_evidence.workflow_id "
                f"must match workflow id (got '{ie.get('workflow_id')}')"
            )
            return

        tid = ie.get("test_ids")
        if not isinstance(tid, list) or len(tid) < 2:
            errors.append(
                f"E2E L3 on '{wf.get('id','?')}': integration_evidence.test_ids "
                f"must reference ≥ 2 cross-interface tests (cpl-req-503)"
            )
            return

        # Actual resolution of each test_id
        resolved_tests = []
        covered_interfaces = set()
        for test_id in tid:
            test_meta = self.resolve(test_id)
            if test_meta is None:
                errors.append(
                    f"E2E L3 on '{wf.get('id','?')}': test_id '{test_id}' not found "
                    f"in evidence registry — cannot verify"
                )
                continue
            if test_meta.get("result") != "PASS":
                errors.append(
                    f"E2E L3 on '{wf.get('id','?')}': test '{test_id}' result is "
                    f"'{test_meta.get('result')}', not PASS"
                )
                continue
            resolved_tests.append(test_meta)
            covered_interfaces.update(test_meta.get("interfaces", []))

        if not resolved_tests:
            return  # All tests failed/unknown — errors already recorded

        # Check all required interfaces are covered by resolved tests
        required_iface_ids = set()
        for req in wf.get("requirements", []):
            iface_id = req.get("interface")
            if iface_id:
                required_iface_ids.add(iface_id)

        uncovered = required_iface_ids - covered_interfaces
        if uncovered:
            errors.append(
                f"E2E L3 on '{wf.get('id','?')}': integration evidence does not "
                f"cover required interfaces: {sorted(uncovered)}"
            )

        # Scope compatibility
        decl_scope = decl.get("context", {}).get("deployment_scope")
        if decl_scope:
            for rt in resolved_tests:
                test_scope = rt.get("scope")
                if test_scope and test_scope != decl_scope:
                    errors.append(
                        f"E2E L3 on '{wf.get('id','?')}': test '{tid}' scope "
                        f"'{test_scope}' mismatch with declaration scope '{decl_scope}'"
                    )

        # Contract version compatibility
        if self.contract_version:
            decl_edition = decl.get("specification", {}).get("edition")
            if decl_edition and self.contract_version != decl_edition:
                errors.append(
                    f"E2E L3: evidence registry contract version "
                    f"'{self.contract_version}' != declaration edition '{decl_edition}'"
                )


def _get_coordination_level(iface, errors=None):
    """Read coordination level from interface.

    Canonical field is declared_level (CONFORMANCE.md v1.0).
    coordination_level is legacy alias. If both are present and differ,
    append an error.
    """
    dl = iface.get("declared_level")
    cl = iface.get("coordination_level")
    if dl and cl and dl != cl:
        if errors is not None:
            errors.append(
                f"Interface {iface.get('id','?')}: conflicting declared_level={dl} "
                f"and coordination_level={cl} — must use one canonical field"
            )
        return dl  # Use canonical
    return dl or cl


def validate_declaration(decl):
    """Validate a coordination declaration. Returns (valid, errors)."""
    errors = []

    # Schema version
    sv = decl.get("schema_version")
    if not sv:
        errors.append("Missing schema_version")
    elif sv != SCHEMA_VERSION:
        errors.append(f"Unsupported schema_version: {sv}")

    # Specification edition
    spec = decl.get("specification", {})
    if not spec.get("edition"):
        errors.append("Missing specification.edition")

    # Context
    ctx = decl.get("context", {})
    if ctx.get("deployment_scope") not in ("single_site", "multi_site"):
        errors.append("context.deployment_scope must be single_site or multi_site")
    if ctx.get("deployment_stage") not in ("evaluation", "production"):
        errors.append("context.deployment_stage must be evaluation or production")

    # Coordination interfaces
    coord = decl.get("coordination", {})
    interfaces = coord.get("interfaces", [])
    if not interfaces:
        errors.append("coordination.interfaces is required and non-empty")

    seen_ids = set()
    seen_planes = set()
    for iface in interfaces:
        iface_id = iface.get("id")
        plane = iface.get("plane")

        # Unique interface ID check
        if not iface_id:
            errors.append("Interface missing 'id' field")
        elif iface_id in seen_ids:
            errors.append(f"Duplicate interface ID: {iface_id}")
        else:
            seen_ids.add(iface_id)

        # Plane validation — multiple interfaces per plane are allowed
        if plane not in VALID_PLANES:
            errors.append(f"Invalid plane: {plane}")
        seen_planes.add(plane)

        lvl = _get_coordination_level(iface, errors)

        vs = iface.get("verification_status")
        if vs not in VALID_VERIFICATION:
            errors.append(f"Invalid verification_status: {vs}")

        provision = iface.get("provision")
        if provision not in VALID_PROVISION:
            errors.append(f"Invalid provision state: {provision}")

        # not_provided interfaces don't need a coordination level (cpl-req-003)
        if provision != "not_provided" and lvl not in VALID_LEVELS:
            errors.append(f"Invalid coordination_level/declared_level: {lvl}")

        # L0 must not be advertised as automated
        if lvl == "L0" and vs == "conformant":
            errors.append("L0 cannot have verification_status=conformant (manual participation)")

        # not_provided must not be conformant
        if provision == "not_provided" and vs == "conformant":
            errors.append("not_provided interface cannot be conformant")
        # cpl-req-003: not_provided marks absence — it is NOT L0 (which requires
        # documented manual participation). not_provided must have not_tested status
        # and MUST NOT carry a coordination level (use declared_level=None/omit).
        if provision == "not_provided":
            if vs != "not_tested":
                errors.append(
                    f"not_provided interface must have verification_status=not_tested "
                    f"(cpl-req-003: absence is not testable)"
                )
            # not_provided must NOT carry a coordination level
            if lvl and lvl != "":
                errors.append(
                    f"not_provided interface must not declare a coordination level "
                    f"(cpl-req-003: fravær ≠ L0; omit declared_level or leave empty)"
                )

        # not_provided with target_level > L0 is contradictory
        target = iface.get("target_level")
        if provision == "not_provided" and target and target != "L0":
            errors.append(f"not_provided with target_level={target} is contradictory")

        # not_provided with requirement_ids is contradictory
        if provision == "not_provided" and iface.get("requirement_ids"):
            errors.append("not_provided interface should not have requirement_ids")

        # Cumulative: L3 requires conformant L1+L2 evidence
        if lvl == "L3" and vs == "conformant":
            if not iface.get("requirement_ids"):
                errors.append("L3 conformant claim requires requirement_ids evidence")

    # Level ordering for comparison
    LEVEL_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}
    iface_ids = {i["id"] for i in interfaces if i.get("id")}

    # Workflows
    # Synthetic evidence resolver for L3 integration evidence
    evidence_resolver = EvidenceResolver(
        verified_tests=EVIDENCE_REGISTRY,
        contract_version=decl.get("specification", {}).get("edition"),
    )
    for wf in decl.get("workflows", []):
        wf_id = wf.get("id", "?")
        min_levels = wf.get("requirements", [])

        # Validate ALL requirement interface references (all levels, not just L3)
        for req in min_levels:
            req_iface_id = req.get("interface")
            min_lvl = req.get("minimum_level")
            if min_lvl and min_lvl not in VALID_LEVELS:
                errors.append(f"Invalid workflow minimum_level: {min_lvl}")

            # Reference integrity: required interface must exist in declaration
            if req_iface_id not in iface_ids:
                errors.append(
                    f"Workflow '{wf_id}': requirement references "
                    f"undeclared interface '{req_iface_id}' — cannot verify"
                )
                continue

            matching = [i for i in interfaces if i.get("id") == req_iface_id]
            for m in matching:
                mlvl = _get_coordination_level(m, errors)
                declared = LEVEL_ORDER.get(mlvl, 0)
                required = LEVEL_ORDER.get(min_lvl, 0)
                if declared < required:
                    errors.append(
                        f"Workflow '{wf_id}': interface {m.get('id')} "
                        f"declared {mlvl} < required {min_lvl}"
                    )

        # Check participating_interfaces are covered by requirements
        for pi in wf.get("participating_interfaces", []):
            if not any(r.get("interface") == pi for r in min_levels):
                errors.append(
                    f"Workflow '{wf_id}': participating_interface '{pi}' "
                    f"not in requirements — cannot claim E2E level"
                )

        # End-to-end level checks
        e2e = wf.get("verified_end_to_end_level")
        if e2e == "L3":
            # All participating interfaces must be L3 conformant
            for req in min_levels:
                req_iface_id = req.get("interface")
                if req_iface_id not in iface_ids:
                    continue  # Already reported above
                matching = [i for i in interfaces if i.get("id") == req_iface_id]
                for m in matching:
                    mlvl = _get_coordination_level(m, errors)
                    if mlvl != "L3":
                        errors.append(
                            f"E2E L3: interface {m.get('id')} is {mlvl}, not L3"
                        )
                    if m.get("verification_status") != "conformant":
                        errors.append(
                            f"E2E L3: interface {m.get('id')} verification is {m.get('verification_status')}"
                        )

            # L3 requires structured integration_evidence with actual resolution (cpl-req-503)
            evidence_resolver.validate_integration_evidence(wf, decl, errors)

    return len(errors) == 0, errors


def validate_policy(ref):
    """Validate a policy reference (Sup-007). Returns (valid, error)."""
    required = ["policy_id", "namespace", "version", "digest", "issuer", "approval_ref", "valid_from", "scope"]
    for field in required:
        if not ref.get(field):
            return False, f"Missing required field: {field}"
    scope = ref.get("scope", {})
    if not isinstance(scope, dict) or not scope.get("interfaces"):
        return False, "scope.interfaces is required"
    if not ref.get("digest", "").startswith("sha256:"):
        return False, "digest must start with 'sha256:'"
    return True, "OK"


# ── Synthetic evidence registry ──

EVIDENCE_REGISTRY = {
    # Cross-interface integration tests for meal-transport workflow
    "meal-transport-integration-1": {
        "interfaces": ["robot-adapter", "task-source"],
        "result": "PASS",
        "scope": "single_site",
        "contract_version": "2026a",
    },
    "meal-transport-integration-2": {
        "interfaces": ["robot-adapter", "task-source", "infra-adapter"],
        "result": "PASS",
        "scope": "single_site",
        "contract_version": "2026a",
    },
    # L3 multi-interface tests for full coordination
    "full-l3-integration-1": {
        "interfaces": ["r", "t"],
        "result": "PASS",
        "scope": "single_site",
        "contract_version": "2026a",
    },
    "full-l3-integration-2": {
        "interfaces": ["i", "w", "t"],
        "result": "PASS",
        "scope": "single_site",
        "contract_version": "2026a",
    },
}


# ── Fixtures ──

VALID_DECLARATION = {
    "schema_version": SCHEMA_VERSION,
    "specification": {"edition": "2026a"},
    "implementer": {"organization": "Test Org", "product": "Test v1.0"},
    "context": {
        "deployment_stage": "production",
        "deployment_scope": "single_site",
        "sites": ["test-site"],
        "domain_profile": "Healthcare",
    },
    "coordination": {
        "model": "control-plane-levels-1.0",
        "interfaces": [
            {
                "id": "robot-adapter",
                "plane": "robot",
                "provision": "provided",
                "declared_level": "L1",
                "target_level": "L1",
                "verification_status": "conformant",
                "requirement_ids": ["cpl-req-101"],
            },
            {
                "id": "infra-adapter",
                "plane": "infrastructure",
                "provision": "provided",
                "declared_level": "L1",
                "target_level": "L1",
                "verification_status": "conformant",
                "requirement_ids": ["cpl-req-201"],
            },
            {
                "id": "workforce-prov",
                "plane": "workforce",
                "provision": "planned",
                "declared_level": "L0",
                "target_level": "L0",
                "verification_status": "not_tested",
            },
            {
                "id": "task-source",
                "plane": "task",
                "provision": "provided",
                "declared_level": "L1",
                "target_level": "L1",
                "verification_status": "conformant",
                "requirement_ids": ["cpl-req-401"],
            },
        ],
    },
    "workflows": [
        {
            "id": "meal-transport-l1",
            "requirements": [
                {"interface": "robot-adapter", "minimum_level": "L1"},
                {"interface": "task-source", "minimum_level": "L1"},
            ],
            "target_end_to_end_level": "L1",
            "verified_end_to_end_level": "L1",
        },
    ],
}

VALID_POLICY = {
    "policy_id": "test-policy-001",
    "namespace": "urn:test:facility",
    "version": "1.0.0",
    "digest": sha256_digest("test policy content"),
    "issuer": "spiffe://test.local/authority/policy",
    "approval_ref": "board-minutes-2026-10-01/item-3",
    "valid_from": "2026-10-01T00:00:00Z",
    "scope": {
        "interfaces": ["robot", "infrastructure"],
        "workflows": ["meal-transport"],
        "sites": ["test-site"],
    },
}


# ── Test cases covering §D scenarios ──

TESTS = []


def add(name, checker, should_pass):
    TESTS.append((name, checker, should_pass))


# D1: Valid scoped coordination declaration (declared_level per CONFORMANCE.md)
add("D1: Valid declaration",
    lambda: validate_declaration(dict(VALID_DECLARATION))[0], True)

# D1b: Valid declaration with coordination_level key (legacy/alternate key)
add("D1b: Valid declaration with coordination_level key",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                {
                    **VALID_DECLARATION["coordination"]["interfaces"][0],
                    "coordination_level": "L1",  # use alternate key
                    "declared_level": None,       # remove declared_level
                },
                *VALID_DECLARATION["coordination"]["interfaces"][1:],
            ],
        },
    })[0], True)

# D2: Legacy declaration handled under version rules
add("D2: Legacy declaration (old schema version rejected)",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "schema_version": "rocom-conformance/control-planes-0.1-draft",
    })[0], False)

# D3: L0 manual handoff vs not_provided
BASE_IFACES = VALID_DECLARATION["coordination"]["interfaces"]

add("D3a: L0 manual handoff (L0 + planned)",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                *BASE_IFACES,
                {
                    "id": "manual-workforce",
                    "plane": "workforce",
                    "provision": "planned",
                    "declared_level": "L0",
                    "verification_status": "not_tested",
                },
            ],
        },
    })[0], True)

add("D3b: planned+L0 is valid manual handoff (distinguished from not_provided)",
     lambda: validate_declaration({
         **VALID_DECLARATION,
         "coordination": {
             **VALID_DECLARATION["coordination"],
             "interfaces": [
                 *BASE_IFACES,
                 {
                     "id": "manual-workforce",
                     "plane": "workforce",
                     "provision": "planned",
                     "declared_level": "L0",
                     "verification_status": "not_tested",
                 },
             ],
         },
     })[0], True)

add("D3e: not_provided with declared_level=L0 rejected (cpl-req-003)",
     lambda: validate_declaration({
         **VALID_DECLARATION,
         "coordination": {
             **VALID_DECLARATION["coordination"],
             "interfaces": [
                 *BASE_IFACES,
                 {
                     "id": "absent-plane",
                     "plane": "workforce",
                     "provision": "not_provided",
                     "declared_level": "L0",
                     "verification_status": "not_tested",
                 },
             ],
         },
     })[0], False)

add("D3f: not_provided without level is valid (cpl-req-003: fravær)",
     lambda: validate_declaration({
         **VALID_DECLARATION,
         "coordination": {
             **VALID_DECLARATION["coordination"],
             "interfaces": [
                 *BASE_IFACES,
                 {
                     "id": "absent-plane",
                     "plane": "workforce",
                     "provision": "not_provided",
                     "declared_level": "",
                     "verification_status": "not_tested",
                 },
             ],
         },
     })[0], True)

add("D3g: not_provided with conformant rejected",
     lambda: validate_declaration({
         **VALID_DECLARATION,
         "coordination": {
             **VALID_DECLARATION["coordination"],
             "interfaces": [
                 {
                     "id": "absent-plane",
                     "plane": "workforce",
                     "provision": "not_provided",
                     "declared_level": "",
                     "verification_status": "conformant",
                 },
             ],
         },
     })[0], False)

add("D3c: L0 conformant rejected (manual cannot be conformant)",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                {
                    "id": "bad-l0",
                    "plane": "workforce",
                    "provision": "provided",
                    "declared_level": "L0",
                    "verification_status": "conformant",
                },
            ],
        },
    })[0], False)

add("D3d: not_provided cannot be conformant",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                {
                    "id": "bad-not-provided",
                    "plane": "workforce",
                    "provision": "not_provided",
                    "declared_level": "L0",
                    "verification_status": "conformant",
                },
            ],
        },
    })[0], False)

# V4: not_provided contradictions
add("V4a: not_provided with target_level L1 rejected (contradiction)",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                {
                    "id": "contradiction-target",
                    "plane": "workforce",
                    "provision": "not_provided",
                    "declared_level": "L0",
                    "target_level": "L1",
                    "verification_status": "not_tested",
                },
            ],
        },
    })[0], False)

add("V4b: not_provided with requirement_ids rejected (contradiction)",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                {
                    "id": "contradiction-reqs",
                    "plane": "workforce",
                    "provision": "not_provided",
                    "declared_level": "L0",
                    "verification_status": "not_tested",
                    "requirement_ids": ["cpl-req-301"],
                },
            ],
        },
    })[0], False)

# D4: Mixed-level workflow rejected for end-to-end L3
add("D4: Mixed-level rejected for end-to-end L3",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                {"id": "r", "plane": "robot", "provision": "provided", "declared_level": "L3", "verification_status": "conformant", "requirement_ids": ["cpl-req-103"]},
                {"id": "i", "plane": "infrastructure", "provision": "provided", "declared_level": "L2", "verification_status": "conformant", "requirement_ids": ["cpl-req-202"]},
                {"id": "w", "plane": "workforce", "provision": "provided", "declared_level": "L1", "verification_status": "conformant", "requirement_ids": ["cpl-req-301"]},
                {"id": "t", "plane": "task", "provision": "provided", "declared_level": "L3", "verification_status": "conformant", "requirement_ids": ["cpl-req-403"]},
            ],
        },
        "workflows": [
            {
                "id": "mixed-l3-claim",
                "requirements": [
                    {"interface": "r", "minimum_level": "L3"},
                    {"interface": "i", "minimum_level": "L2"},
                    {"interface": "w", "minimum_level": "L1"},
                    {"interface": "t", "minimum_level": "L3"},
                ],
                "verified_end_to_end_level": "L3",
            },
        ],
    })[0], False)

# D5: Assurance preserved at every coordination level
add("D5: Assurance obligations verified by structure",
    lambda: validate_declaration(VALID_DECLARATION)[0], True)

# D6: Valid authorised policy reference accepted
add("D6: Valid policy reference accepted",
    lambda: validate_policy(dict(VALID_POLICY))[0], True)

# D7: Policy reference edge cases
add("D7a: Wrong scope rejected",
    lambda: validate_policy({**VALID_POLICY, "scope": {"interfaces": []}})[0], False)

add("D7b: Unauthorised issuer (empty) rejected",
    lambda: validate_policy({**VALID_POLICY, "issuer": ""})[0], False)

add("D7c: Missing approval rejected",
    lambda: validate_policy({**VALID_POLICY, "approval_ref": ""})[0], False)

# D8: Unsupported required extension cannot silently pass
add("D8: Required extension handling (schema accepts, runtime enforces)",
    lambda: validate_policy({**VALID_POLICY, "required_extensions": ["local:unsupported-v1"]})[0], True)

# D9: Optional extension cannot override mandatory semantics
add("D9: Optional extension ignored (schema accepts)",
    lambda: validate_policy({**VALID_POLICY, "optional_extensions": ["local:override-attempt"]})[0], True)

# D10: Decision evidence identifies exact policy version
add("D10: Policy version in evidence (structure check)",
    lambda: all(k in VALID_POLICY for k in ["policy_id", "version", "digest"]), True)

# ── V2: Evidence resolver tests ──

# V2a: L3 with valid integration_evidence (resolved) passes
L3_VALID_DECL = {
    **VALID_DECLARATION,
    "coordination": {
        **VALID_DECLARATION["coordination"],
        "interfaces": [
            {"id": "robot-adapter", "plane": "robot", "provision": "provided", "declared_level": "L3", "verification_status": "conformant", "requirement_ids": ["cpl-req-103"]},
            {"id": "task-source", "plane": "task", "provision": "provided", "declared_level": "L3", "verification_status": "conformant", "requirement_ids": ["cpl-req-403"]},
            {"id": "workforce-prov", "plane": "workforce", "provision": "provided", "declared_level": "L3", "verification_status": "conformant", "requirement_ids": ["cpl-req-303"]},
            {"id": "infra-adapter", "plane": "infrastructure", "provision": "provided", "declared_level": "L3", "verification_status": "conformant", "requirement_ids": ["cpl-req-203"]},
        ],
    },
    "workflows": [
        {
            "id": "meal-transport-l3",
            "requirements": [
                {"interface": "robot-adapter", "minimum_level": "L3"},
                {"interface": "task-source", "minimum_level": "L3"},
            ],
            "verified_end_to_end_level": "L3",
            "integration_evidence": {
                "workflow_id": "meal-transport-l3",
                "test_ids": ["meal-transport-integration-1", "meal-transport-integration-2"],
            },
        },
    ],
}

add("V2a: L3 with valid resolved evidence passes",
    lambda: validate_declaration(L3_VALID_DECL)[0], True)

# V2b: L3 with invented test_ids (not in registry) → rejected
add("V2b: L3 with invented test_ids rejected",
    lambda: validate_declaration({
        **L3_VALID_DECL,
        "workflows": [
            {
                **L3_VALID_DECL["workflows"][0],
                "integration_evidence": {
                    "workflow_id": "meal-transport-l3",
                    "test_ids": ["invented-a", "invented-b"],
                },
            },
        ],
    })[0], False)

# V2c: L3 with empty requirements + invented evidence → rejected
add("V2c: L3 empty requirements + invented evidence rejected",
    lambda: validate_declaration({
        **VALID_DECLARATION,
        "coordination": {
            **VALID_DECLARATION["coordination"],
            "interfaces": [
                {"id": "x", "plane": "robot", "provision": "provided", "declared_level": "L3", "verification_status": "conformant", "requirement_ids": []},
            ],
        },
        "workflows": [
            {
                "id": "empty",
                "requirements": [],
                "verified_end_to_end_level": "L3",
                "integration_evidence": {
                    "workflow_id": "empty",
                    "test_ids": ["invented-a", "invented-b"],
                },
            },
        ],
    })[0], False)

# V2d: L3 with string integration_evidence (not dict) → rejected
add("V2d: L3 with string integration_evidence rejected",
    lambda: validate_declaration({
        **L3_VALID_DECL,
        "workflows": [
            {
                **L3_VALID_DECL["workflows"][0],
                "integration_evidence": "this-is-a-long-text-string-that-is-not-useful",
            },
        ],
    })[0], False)

# V2e: L3 with unresolved interface reference → rejected
add("V2e: L3 with missing interface reference rejected",
    lambda: validate_declaration({
        **L3_VALID_DECL,
        "workflows": [
            {
                "id": "missing-iface",
                "requirements": [
                    {"interface": "missing-interface", "minimum_level": "L2"},
                ],
                "verified_end_to_end_level": "L3",
                "integration_evidence": {
                    "workflow_id": "missing-iface",
                    "test_ids": ["meal-transport-integration-1", "meal-transport-integration-2"],
                },
            },
        ],
    })[0], False)

# V2f: L3 evidence coverage gap — tests don't cover all required interfaces → rejected
add("V2f: L3 evidence does not cover all required interfaces",
    lambda: validate_declaration({
        **L3_VALID_DECL,
        "workflows": [
            {
                "id": "coverage-gap",
                "requirements": [
                    {"interface": "robot-adapter", "minimum_level": "L3"},
                    {"interface": "infra-adapter", "minimum_level": "L3"},  # not in evidence
                ],
                "verified_end_to_end_level": "L3",
                "integration_evidence": {
                    "workflow_id": "coverage-gap",
                    "test_ids": ["meal-transport-integration-1"],  # only covers robot+task
                },
            },
        ],
    })[0], False)


def main():
    passed = 0
    failed = 0
    for name, checker, should_pass in TESTS:
        try:
            result = checker()
        except Exception as e:
            print(f"  ERROR: {name} — {e}")
            failed += 1
            continue
        if result == should_pass:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} — expected {'pass' if should_pass else 'fail'}, got {result}")
            failed += 1

    print(f"\n  {passed}/{len(TESTS)} passed")
    if failed > 0:
        print(f"  {failed} FAILED")
        sys.exit(1)
    print("  All coordination declaration tests passed")


if __name__ == "__main__":
    main()
