#!/usr/bin/env python3
"""Test fixtures for Sup-007: Policy Reference model.

Run: python3 build/test_policy_reference.py
"""
import json
import hashlib
import sys
from datetime import datetime, timezone, timedelta


def sha256_digest(text):
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


REQUIRED_FIELDS = [
    "policy_id", "namespace", "version", "digest",
    "issuer", "approval_ref", "valid_from", "scope",
]

SCOPE_REQUIRED = ["interfaces"]


def validate_policy(ref):
    """Returns (valid, error_message). Structural validation only."""
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in ref or ref[field] is None or ref[field] == "":
            return False, f"Missing required field: {field}"

    # Check scope has at least interfaces
    scope = ref.get("scope", {})
    if not isinstance(scope, dict):
        return False, "scope must be an object"
    if "interfaces" not in scope or not scope["interfaces"]:
        return False, "scope.interfaces is required and non-empty"

    # Check digest format
    digest = ref.get("digest", "")
    if not digest.startswith("sha256:"):
        return False, f"digest must start with 'sha256:', got: {digest}"

    # Check valid_from is parseable datetime
    try:
        datetime.fromisoformat(ref["valid_from"].replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return False, f"valid_from is not valid ISO 8601: {ref.get('valid_from')}"

    # Check valid_until if present
    if "valid_until" in ref and ref["valid_until"]:
        try:
            datetime.fromisoformat(ref["valid_until"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False, f"valid_until is not valid ISO 8601: {ref.get('valid_until')}"

    # Check revoked flag
    if ref.get("revoked"):
        return False, "Policy has been revoked"

    return True, "OK"


class PolicyContext:
    """Trusted verification context — separate from policy reference data.

    This context provides authoritative resolvers for content, issuers,
    approvals, revocations, extensions, and clock. Policy data MUST NOT
    extend or override these whitelists.
    """
    def __init__(self, current_time=None, known_issuers=None,
                 known_extensions=None, content_store=None,
                 approval_store=None, revocation_set=None):
        self.current_time = current_time or datetime.now(timezone.utc)
        self.known_issuers = set(known_issuers or [])
        self.known_extensions = set(known_extensions or [])
        self.content_store = content_store or {}  # policy_id:version → content
        self.approval_store = approval_store or {}  # approval_ref → {policy_id, version, digest, scope}
        self.revocation_set = set(revocation_set or [])  # policy_id:version


def validate_policy_runtime(ref, ctx):
    """Full runtime validation with explicit trusted context.

    Args:
        ref: policy reference dict (wire format)
        ctx: PolicyContext with authoritative resolvers
    Returns:
        (valid, error_message)
    """
    # 1. Structural validation first
    valid, msg = validate_policy(ref)
    if not valid:
        return False, msg

    pid = ref["policy_id"]
    ver = ref["version"]
    pkey = f"{pid}:{ver}"

    # 2. Temporal validity — strict < valid_until (§6.2)
    if "valid_until" in ref and ref["valid_until"]:
        expiry = datetime.fromisoformat(ref["valid_until"].replace("Z", "+00:00"))
        if ctx.current_time >= expiry:
            return False, f"Expired: {ref['valid_until']} <= {ctx.current_time.isoformat()}"
    start = datetime.fromisoformat(ref["valid_from"].replace("Z", "+00:00"))
    if ctx.current_time < start:
        return False, f"Not yet effective: {ref['valid_from']} > {ctx.current_time.isoformat()}"

    # 3. Issuer verification (§6.3)
    # Empty known_issuers means NO issuer is trusted — reject unknown.
    # Non-empty known_issuers means only listed issuers are trusted.
    if not ctx.known_issuers or ref["issuer"] not in ctx.known_issuers:
        return False, f"Unverified issuer: {ref['issuer']}"

    # 4. Revocation check (§6.6)
    if pkey in ctx.revocation_set:
        return False, f"Policy {pkey} has been revoked"

    # 5. Content integrity (§6.5)
    # If the policy has a digest, it MUST be verifiable against stored content.
    # Missing content for a digest-bearing policy is a verification failure.
    content_key = f"{pid}:{ver}"
    if content_key not in ctx.content_store:
        return False, f"No trusted content for {content_key} — digest cannot be verified"
    expected = sha256_digest(ctx.content_store[content_key])
    if ref["digest"] != expected:
        return False, f"Digest mismatch: {ref['digest']} != {expected}"

    # 6. Approval binding (§6.4)
    # Approval MUST be found and bind correctly: policy_id, version, digest, scope.
    approval_ref = ref["approval_ref"]
    if approval_ref not in ctx.approval_store:
        return False, f"Approval '{approval_ref}' not found in trusted approval store"
    approval = ctx.approval_store[approval_ref]
    if approval.get("policy_id") != pid:
        return False, f"Approval {approval_ref} binds policy {approval.get('policy_id')}, not {pid}"
    if approval.get("version") != ver:
        return False, f"Approval {approval_ref} binds version {approval.get('version')}, not {ver}"
    if approval.get("digest") and approval.get("digest") != ref["digest"]:
        return False, f"Approval {approval_ref} digest mismatch"
    if approval.get("scope") and approval.get("scope") != ref.get("scope"):
        return False, f"Approval {approval_ref} scope mismatch"

    # 7. Required extensions (§6.9)
    for ext in ref.get("required_extensions", []):
        if ext not in ctx.known_extensions:
            return False, f"Unsupported required extension: {ext}"

    return True, "OK"


# ── Fixtures ──

POLICY_CONTENT = "test policy content"

VALID_POLICY = {
    "policy_id": "test-policy-001",
    "namespace": "urn:test:facility",
    "version": "1.0.0",
    "digest": sha256_digest(POLICY_CONTENT),
    "issuer": "spiffe://test.local/authority/policy",
    "approval_ref": "board-minutes-2026-10-01/item-3",
    "valid_from": "2026-10-01T00:00:00Z",
    "scope": {
        "interfaces": ["robot", "infrastructure"],
        "workflows": ["meal-transport"],
        "sites": ["test-hospital"],
    },
}

VALID_APPROVAL = {
    "policy_id": "test-policy-001",
    "version": "1.0.0",
    "digest": sha256_digest(POLICY_CONTENT),
    "scope": VALID_POLICY["scope"],
}

# Default trusted context for full validation
def make_trusted_context(current_time=None):
    """Create a fully populated PolicyContext for valid policy verification."""
    return PolicyContext(
        current_time=current_time or NOW,
        known_issuers=[VALID_POLICY["issuer"]],
        content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
        approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
    )

# Clock injection timestamps
NOW = datetime(2026, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
PAST = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
FUTURE = datetime(2027, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

TEST_CASES = [
    # POL-T01: Valid policy structural
    ("POL-T01: Valid policy structural",
     lambda: validate_policy(dict(VALID_POLICY)), True),

    # POL-T02: Missing approval_ref
    ("POL-T02: Missing approval_ref",
     lambda: validate_policy({**VALID_POLICY, "approval_ref": ""}), False),

    # POL-T03: Expired policy — runtime check with injected clock
    ("POL-T03: Expired policy (injected past clock)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "valid_until": "2026-01-01T00:00:00Z"},
         ctx=make_trusted_context(current_time=NOW)
     ), False),

    # POL-T03b: Same policy, injected future clock → should pass
    ("POL-T03b: Not yet expired (injected early clock)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "valid_until": "2027-01-01T00:00:00Z"},
         ctx=make_trusted_context(current_time=NOW)
     ), True),

    # POL-T04: Missing namespace
    ("POL-T04: Missing namespace",
     lambda: validate_policy({**VALID_POLICY, "namespace": ""}), False),

    # POL-T05: Bad digest format
    ("POL-T05: Bad digest format",
     lambda: validate_policy({**VALID_POLICY, "digest": "md5:abc123"}), False),

    # POL-T06: Missing scope.interfaces
    ("POL-T06: Missing scope.interfaces",
     lambda: validate_policy({**VALID_POLICY, "scope": {}}), False),

    # POL-T07: scope is not object
    ("POL-T07: scope is not object",
     lambda: validate_policy({**VALID_POLICY, "scope": "string"}), False),

    # POL-T08: Digest matches content (compute sha256 and compare)
    ("POL-T08: Digest matches content",
     lambda: (True, "digest OK") if VALID_POLICY["digest"] == sha256_digest(POLICY_CONTENT) else (False, "digest mismatch"), True),

    # POL-T09: Digest mismatch — wrong content produces different digest
    ("POL-T09: Digest mismatch detected",
     lambda: (False, "digest mismatch") if VALID_POLICY["digest"] == sha256_digest("different content") else (True, "digests differ as expected"), True),

    # POL-T10: All optional fields present
    ("POL-T10: All fields present",
     lambda: validate_policy({
         **VALID_POLICY,
         "valid_until": "2027-12-31T23:59:59Z",
         "scope": {
             "interfaces": ["robot", "infrastructure", "workforce", "task"],
             "workflows": ["meal-transport", "linen-run"],
             "operations": ["lift_request", "lift_release"],
             "sites": ["test-hospital"],
             "contract_versions": ["sup-003-v1.0"],
         },
     }), True),

    # POL-T11: Revoked policy rejected
    ("POL-T11: Revoked policy rejected",
     lambda: validate_policy({**VALID_POLICY, "revoked": True}), False),

    # POL-T12: Non-revoked policy accepted
    ("POL-T12: Active (non-revoked) policy accepted",
     lambda: validate_policy({**VALID_POLICY, "revoked": False}), True),

    # POL-T13: Policy not yet effective (injected past clock)
    ("POL-T13: Policy not yet effective (injected clock)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "valid_from": "2027-01-01T00:00:00Z"},
         ctx=make_trusted_context(current_time=NOW)
     ), False),

    # POL-T14: Digest mismatch — runtime rejects wrong content hash
    ("POL-T14: Digest mismatch rejected (runtime)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY},
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": "different content"},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
         )
     ), False),

    # POL-T15: Digest matches — runtime accepts correct hash
    ("POL-T15: Digest verified (runtime, correct content)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY},
         ctx=make_trusted_context(current_time=NOW)
     ), True),

    # POL-T16: Unknown issuer rejected (context does NOT include attacker)
    ("POL-T16: Unknown issuer rejected (runtime)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "issuer": "spiffe://unknown.attacker/evil"},
         ctx=make_trusted_context(current_time=NOW)
     ), False),

    # POL-T17: Unknown required extension rejected
    ("POL-T17: Unknown required extension rejected (runtime)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "required_extensions": ["unsupported:ext-v1"]},
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             known_extensions=["supported:ext-v1"],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
         )
     ), False),

    # POL-T18: At valid_until boundary — rejected (strict <)
    ("POL-T18: At valid_until boundary rejected (strict <)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "valid_until": "2026-10-15T12:00:00Z"},
         ctx=make_trusted_context(current_time=NOW)
     ), False),

    # POL-T19: Just before valid_until — accepted
    ("POL-T19: Just before valid_until accepted",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "valid_until": "2026-10-15T12:00:01Z"},
         ctx=make_trusted_context(current_time=NOW)
     ), True),

    # POL-T20: Optional extension unsupported — accepted (ignored)
    ("POL-T20: Optional extension ignored (runtime)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "optional_extensions": ["unsupported:opt-v1"]},
         ctx=make_trusted_context(current_time=NOW)
     ), True),

    # POL-T21: Approval binding — wrong version rejected
    ("POL-T21: Approval binds wrong version (rejected)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY},
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={
                 VALID_POLICY["approval_ref"]: {
                     "policy_id": VALID_POLICY["policy_id"],
                     "version": "9.9.9",  # wrong version
                     "digest": VALID_POLICY["digest"],
                     "scope": VALID_POLICY["scope"],
                 }
             }
         )
     ), False),

    # POL-T22: Revoked policy rejected via context
    ("POL-T22: Revoked policy rejected (context)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY},
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             revocation_set=[f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}"]
         )
     ), False),

    # POL-T23: Context separation — policy data cannot extend whitelists
    ("POL-T23: Context separation (policy cannot self-authorise)",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "issuer": "spiffe://attacker/evil"},
         ctx=make_trusted_context(current_time=NOW)
     ), False),

    # POL-T24: Empty context — no trusted issuers → rejection
    ("POL-T24: Empty context rejects (no trusted issuers)",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(current_time=NOW)
     ), False),

    # POL-T25: Context with issuer+content but no approval → rejection
    ("POL-T25: Missing approval in context → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
         )
     ), False),

    # POL-T26: Approval with wrong digest → rejection
    ("POL-T26: Approval digest mismatch → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={
                 VALID_POLICY["approval_ref"]: {
                     "policy_id": VALID_POLICY["policy_id"],
                     "version": VALID_POLICY["version"],
                     "digest": "sha256:wrongdigest",
                     "scope": VALID_POLICY["scope"],
                 }
             }
         )
     ), False),

    # POL-T27: Approval with wrong scope → rejection
    ("POL-T27: Approval scope mismatch → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={
                 VALID_POLICY["approval_ref"]: {
                     "policy_id": VALID_POLICY["policy_id"],
                     "version": VALID_POLICY["version"],
                     "digest": VALID_POLICY["digest"],
                     "scope": {"interfaces": ["wrong"]},
                 }
             }
         )
     ), False),

    # POL-T28: No content in context → rejection
    ("POL-T28: No trusted content → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
         )
     ), False),

    # POL-T29: Full valid runtime with complete context
    ("POL-T29: Full valid runtime verification",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=make_trusted_context(current_time=NOW)
     ), True),

    # POL-T30: Required extension with empty known_extensions → rejection
    ("POL-T30: Required extension with empty known_extensions → rejection",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "required_extensions": ["local:ext-v1"]},
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             known_extensions=[],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
         )
     ), False),
]


def main():
    passed = 0
    failed = 0
    for name, checker, should_pass in TEST_CASES:
        valid, msg = checker()
        if valid == should_pass:
            print(f"  PASS: {name} — {msg}")
            passed += 1
        else:
            print(f"  FAIL: {name} — expected {'valid' if should_pass else 'invalid'}, got {valid}: {msg}")
            failed += 1

    print(f"\n  {passed}/{len(TEST_CASES)} passed")
    if failed > 0:
        print(f"  {failed} FAILED")
        sys.exit(1)
    print("  All policy reference tests passed")


if __name__ == "__main__":
    main()
