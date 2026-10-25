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

    # Check digest format: must be sha256: followed by exactly 64 hex chars
    import re
    digest = ref.get("digest", "")
    if not digest.startswith("sha256:"):
        return False, f"digest must start with 'sha256:', got: {digest}"
    hex_part = digest[len("sha256:"):]
    if not re.fullmatch(r'[0-9a-f]{64}', hex_part):
        return False, f"digest must be sha256: followed by 64 hex chars, got: {digest}"

    # Check valid_from is parseable datetime with timezone
    try:
        vf = ref.get("valid_from", "")
        if not isinstance(vf, str):
            return False, f"valid_from must be a string: {vf}"
        parsed = datetime.fromisoformat(vf.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return False, f"valid_from requires timezone (Z/+HH:MM): {vf}"
    except (ValueError, AttributeError, TypeError) as e:
        return False, f"valid_from is not valid ISO 8601: {ref.get('valid_from')} — {e}"

    # Check valid_until if present
    if "valid_until" in ref and ref["valid_until"]:
        try:
            vu = ref["valid_until"]
            if not isinstance(vu, str):
                return False, f"valid_until must be a string: {vu}"
            parsed_u = datetime.fromisoformat(vu.replace("Z", "+00:00"))
            if parsed_u.tzinfo is None:
                return False, f"valid_until requires timezone (Z/+HH:MM): {vu}"
        except (ValueError, AttributeError, TypeError) as e:
            return False, f"valid_until is not valid ISO 8601: {ref.get('valid_until')} — {e}"

    # Check revoked flag
    if ref.get("revoked"):
        return False, "Policy has been revoked"

    return True, "OK"


class PolicyContext:
    """Trusted verification context — separate from policy reference data.

    This context provides authoritative resolvers for content, issuers,
    approvals, revocations, extensions, clock, decision scope, supported
    versions, revocation freshness, and audit correlation. Policy data
    MUST NOT extend or override these whitelists.
    """
    def __init__(self, current_time=None, known_issuers=None,
                 known_extensions=None, content_store=None,
                 approval_store=None, revocation_set=None,
                 decision_scope=None, supported_versions=None,
                 revocation_checked_at=None, audit_store=None):
        self.current_time = current_time or datetime.now(timezone.utc)
        self.known_issuers = set(known_issuers or [])
        self.known_extensions = set(known_extensions or [])
        self.content_store = content_store or {}  # policy_id:version → content
        self.approval_store = approval_store or {}  # approval_ref → {policy_id, version, digest, scope, namespace}
        self.revocation_set = set(revocation_set or [])  # policy_id:version

        # Decision scope: authoritative scope for the decision being made.
        # Must be explicitly set — missing scope means the context cannot
        # authorize the policy for the intended use.
        self.decision_scope = decision_scope  # {interfaces, workflows, sites}

        # Supported versions: authoritative list of spec editions this context
        # can validate against. Empty means no version is supported.
        self.supported_versions = set(supported_versions or [])

        # Revocation freshness: timestamp of last revocation list update.
        # Must be within REVOCATION_FRESHNESS_MAX (default 24h).
        self.revocation_checked_at = revocation_checked_at

        # Audit store: approval_ref → audit log entry
        # Used to correlate approvals with decision records.
        self.audit_store = audit_store or {}  # approval_ref → {decision_time, decider, approval_ref}


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
    # Approval MUST be found and bind ALL fields: policy_id, version, digest, scope, namespace.
    # Missing digest or scope on the approval entry is a verification failure — not optional.
    approval_ref = ref["approval_ref"]
    if approval_ref not in ctx.approval_store:
        return False, f"Approval '{approval_ref}' not found in trusted approval store"
    approval = ctx.approval_store[approval_ref]

    # Required approval fields — missing is rejection, not pass-through
    if "policy_id" not in approval:
        return False, f"Approval {approval_ref} missing policy_id binding"
    if "version" not in approval:
        return False, f"Approval {approval_ref} missing version binding"
    if "digest" not in approval:
        return False, f"Approval {approval_ref} missing digest binding"
    if "scope" not in approval:
        return False, f"Approval {approval_ref} missing scope binding"

    if approval["policy_id"] != pid:
        return False, f"Approval {approval_ref} binds policy {approval['policy_id']}, not {pid}"
    if approval["version"] != ver:
        return False, f"Approval {approval_ref} binds version {approval['version']}, not {ver}"
    if approval["digest"] != ref["digest"]:
        return False, f"Approval {approval_ref} digest mismatch"
    if approval["scope"] != ref.get("scope"):
        return False, f"Approval {approval_ref} scope mismatch"

    # 6b. Namespace authority (§6.3): the approval must explicitly bind the
    # policy's namespace. If the approval entry lacks a namespace field, it
    # cannot attest to the policy's namespace — reject.
    ns = ref.get("namespace", "")
    if "namespace" not in approval:
        return False, f"Approval {approval_ref} missing namespace binding"
    if approval["namespace"] != ns:
        return False, f"Approval {approval_ref} namespace '{approval['namespace']}' != policy namespace '{ns}'"

    # 7. Required extensions (§6.9)
    for ext in ref.get("required_extensions", []):
        if ext not in ctx.known_extensions:
            return False, f"Unsupported required extension: {ext}"

    # 8. Decision scope (§6.4): the context must have an explicit decision scope
    # whose interfaces, sites, and workflows all intersect the policy scope.
    # Missing or non-overlapping on any dimension means the context cannot
    # authorize this policy for the intended use.
    if not ctx.decision_scope:
        return False, "Context has no decision scope — cannot authorize policy application"
    policy_scope = ref.get("scope", {})
    for dim in ("interfaces", "sites", "workflows"):
        decision_dim = set(ctx.decision_scope.get(dim, []))
        policy_dim = set(policy_scope.get(dim, []))
        if not decision_dim.intersection(policy_dim):
            return False, f"Policy scope {dim} {sorted(policy_dim)} do not overlap " \
                          f"with decision scope {sorted(decision_dim)}"

    # 9. Supported version context: the context's supported_versions must include
    # the spec edition that this policy was authored against. The approval entry
    # binds the policy to a spec edition via its content — we verify the approval's
    # spec_edition (if present) is in the context's supported set. If the approval
    # does not carry spec_edition, we fall back to the content store key which maps
    # policy_id:version → content. We require the context to support at least one
    # edition relevant to this policy.
    if not ctx.supported_versions:
        return False, "Context has no supported versions — cannot validate policy edition"
    # Check if approval binds a spec_edition
    # Mandatory: the approval MUST carry a spec_edition to resolve the policy's
    # contract version against the context's supported versions. Missing spec_edition
    # means the approval cannot attest to the policy's edition — reject.
    approval_edition = approval.get("spec_edition")
    if not approval_edition:
        return False, f"Approval {approval_ref} missing spec_edition — " \
                      f"cannot resolve policy edition against supported versions"
    if approval_edition not in ctx.supported_versions:
        return False, f"Approval spec_edition '{approval_edition}' not in supported " \
                      f"versions {sorted(ctx.supported_versions)}"

    # 10. Revocation freshness: the revocation list must have been checked
    # recently enough to be trustworthy. Validate timezone and direction first.
    if ctx.revocation_checked_at is None:
        return False, "Revocation list has never been checked — freshness unknown"
    if ctx.revocation_checked_at.tzinfo is None:
        return False, "revocation_checked_at requires timezone-aware timestamp"
    revocation_age = ctx.current_time - ctx.revocation_checked_at
    # Future revocation check is invalid — the check must have happened in the past
    if revocation_age.total_seconds() < 0:
        return False, f"revocation_checked_at is in the future: " \
                      f"{ctx.revocation_checked_at.isoformat()} > {ctx.current_time.isoformat()}"
    if revocation_age > REVOCATION_FRESHNESS_MAX:
        return False, f"Revocation list stale: {revocation_age} > {REVOCATION_FRESHNESS_MAX}"

    # 11. Audit/decision correlation: the approval must be recorded in the
    # audit store with matching approval_ref, policy_id, version, and digest.
    # All four fields are mandatory — the decision must bind to the exact policy
    # instance. Missing fields mean insufficient correlation.
    approval_ref = ref["approval_ref"]
    if approval_ref not in ctx.audit_store:
        return False, f"Approval '{approval_ref}' not found in audit store — " \
                      f"cannot correlate decision"
    audit_entry = ctx.audit_store[approval_ref]
    if audit_entry.get("approval_ref") != approval_ref:
        return False, f"Audit entry for '{approval_ref}' has mismatched approval_ref"
    # Mandatory: audit must bind exact policy instance
    if "policy_id" not in audit_entry:
        return False, f"Audit entry for '{approval_ref}' missing policy_id — insufficient correlation"
    if audit_entry["policy_id"] != pid:
        return False, f"Audit entry binds policy {audit_entry['policy_id']}, not {pid}"
    if "version" not in audit_entry:
        return False, f"Audit entry for '{approval_ref}' missing version — insufficient correlation"
    if audit_entry["version"] != ver:
        return False, f"Audit entry binds version {audit_entry['version']}, not {ver}"
    if "digest" not in audit_entry:
        return False, f"Audit entry for '{approval_ref}' missing digest — insufficient correlation"
    if audit_entry["digest"] != ref["digest"]:
        return False, f"Audit entry digest mismatch for policy {pkey}"

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
    "namespace": VALID_POLICY["namespace"],
    "spec_edition": "2026a",
}

# Default trusted context for full validation
def make_trusted_context(current_time=None):
    """Create a fully populated PolicyContext for valid policy verification."""
    ct = current_time or NOW
    return PolicyContext(
        current_time=ct,
        known_issuers=[VALID_POLICY["issuer"]],
        content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
        approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
        decision_scope=VALID_POLICY["scope"],
        supported_versions=["2026a"],
        revocation_checked_at=ct,  # Fresh revocation check
        audit_store={
            VALID_POLICY["approval_ref"]: {
                "decision_time": NOW,
                "decider": "board-2026",
                "approval_ref": VALID_POLICY["approval_ref"],
                "policy_id": VALID_POLICY["policy_id"],
                "version": VALID_POLICY["version"],
                "digest": VALID_POLICY["digest"],
            }
        },
    )

# Revocation freshness: max age of revocation list (24 hours)
REVOCATION_FRESHNESS_MAX = timedelta(hours=24)


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

    # POL-T31: Approval missing digest → rejection
    ("POL-T31: Approval missing digest binding → rejection",
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
                     "scope": VALID_POLICY["scope"],
                     "namespace": VALID_POLICY["namespace"],
                     # digest intentionally missing
                 }
             },
         )
     ), False),

    # POL-T32: Approval missing scope → rejection
    ("POL-T32: Approval missing scope binding → rejection",
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
                     "namespace": VALID_POLICY["namespace"],
                     # scope intentionally missing
                 }
             },
         )
     ), False),

    # POL-T33: Namespace mismatch → rejection
    ("POL-T33: Namespace not within approval → rejection",
     lambda: validate_policy_runtime(
         {**VALID_POLICY, "namespace": "urn:other:authority"},
         ctx=make_trusted_context(current_time=NOW)
     ), False),

    # POL-T34: Invalid SHA-256 hex format → structural rejection
    ("POL-T34: Invalid SHA-256 hex format → rejection",
     lambda: validate_policy({**VALID_POLICY, "digest": "sha256:not-a-64-hex-digest"}), False),

    # POL-T35: valid_from without timezone → structural rejection (not TypeError)
    ("POL-T35: valid_from without timezone → rejection",
     lambda: validate_policy({**VALID_POLICY, "valid_from": "2026-10-01T00:00:00"}), False),

    # POL-T36: Missing decision scope in context → rejection
    ("POL-T36: Missing decision scope → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             # decision_scope intentionally omitted
             supported_versions=["2026a"],
             revocation_checked_at=NOW,
             audit_store={
                 VALID_POLICY["approval_ref"]: {
                     "decision_time": NOW,
                     "decider": "board-2026",
                     "approval_ref": VALID_POLICY["approval_ref"],
                 }
             },
         )
     ), False),

    # POL-T37: Decision scope non-overlapping with policy scope → rejection
    ("POL-T37: Decision scope non-overlapping → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope={"interfaces": ["workforce"], "workflows": ["other"], "sites": ["other"]},
             supported_versions=["2026a"],
             revocation_checked_at=NOW,
             audit_store={
                 VALID_POLICY["approval_ref"]: {
                     "decision_time": NOW,
                     "decider": "board-2026",
                     "approval_ref": VALID_POLICY["approval_ref"],
                 }
             },
         )
     ), False),

    # POL-T38: Stale revocation list → rejection
    ("POL-T38: Stale revocation list → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions=["2026a"],
             revocation_checked_at=NOW - timedelta(hours=48),  # 48h > 24h max
             audit_store={
                 VALID_POLICY["approval_ref"]: {
                     "decision_time": NOW,
                     "decider": "board-2026",
                     "approval_ref": VALID_POLICY["approval_ref"],
                 }
             },
         )
     ), False),

    # POL-T39: Missing audit correlation → rejection
    ("POL-T39: Missing audit correlation → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions=["2026a"],
             revocation_checked_at=NOW,
             # audit_store intentionally omitted
         )
     ), False),

    # POL-T40: Full valid with all new context checks → accepted
    ("POL-T40: Full valid with decision scope, revocation freshness, audit → accepted",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=make_trusted_context(current_time=NOW)
     ), True),

    # POL-T41: decision_scope.sites mismatch → rejection
    ("POL-T41: Decision scope sites mismatch → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope={**VALID_POLICY["scope"], "sites": ["other-hospital"]},
             supported_versions={"2026a"},
             revocation_checked_at=NOW,
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"]}},
         )
     ), False),

    # POL-T42: decision_scope.workflows mismatch → rejection
    ("POL-T42: Decision scope workflows mismatch → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope={**VALID_POLICY["scope"], "workflows": ["other-workflow"]},
             supported_versions={"2026a"},
             revocation_checked_at=NOW,
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"]}},
         )
     ), False),

    # POL-T43: unsupported spec_edition → rejection
    ("POL-T43: Unsupported spec_edition → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"unrelated-edition"},
             revocation_checked_at=NOW,
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"]}},
         )
     ), False),

    # POL-T44: audit entry with wrong policy_id/version/digest → rejection
    ("POL-T44: Audit entry wrong policy binding → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"2026a"},
             revocation_checked_at=NOW,
             audit_store={
                 VALID_POLICY["approval_ref"]: {
                     "decision_time": NOW,
                     "decider": "board-2026",
                     "approval_ref": VALID_POLICY["approval_ref"],
                     "policy_id": "wrong-policy",
                     "version": "9.9.9",
                     "digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
                 }
             },
         )
     ), False),

    # POL-T45: future revocation_checked_at → rejection
    ("POL-T45: Future revocation_checked_at → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"2026a"},
             revocation_checked_at=NOW + timedelta(days=2),
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"]}},
         )
     ), False),

    # POL-T46: naive revocation_checked_at (no timezone) → rejection (not TypeError)
    ("POL-T46: Naive revocation_checked_at → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"2026a"},
             revocation_checked_at=NOW.replace(tzinfo=None),
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"]}},
         )
     ), False),

    # POL-T47: audit missing policy_id → rejection (F1 regression)
    ("POL-T47: Audit missing policy_id → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"2026a"},
             revocation_checked_at=NOW,
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"]}},
         )
     ), False),

    # POL-T48: audit missing version → rejection (F1 regression)
    ("POL-T48: Audit missing version → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"2026a"},
             revocation_checked_at=NOW,
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"], "policy_id": VALID_POLICY["policy_id"]}},
         )
     ), False),

    # POL-T49: audit missing digest → rejection (F1 regression)
    ("POL-T49: Audit missing digest → rejection",
     lambda: validate_policy_runtime(
         VALID_POLICY,
         ctx=PolicyContext(
             current_time=NOW,
             known_issuers=[VALID_POLICY["issuer"]],
             content_store={f"{VALID_POLICY['policy_id']}:{VALID_POLICY['version']}": POLICY_CONTENT},
             approval_store={VALID_POLICY["approval_ref"]: VALID_APPROVAL},
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"2026a"},
             revocation_checked_at=NOW,
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"], "policy_id": VALID_POLICY["policy_id"], "version": VALID_POLICY["version"]}},
         )
     ), False),

    # POL-T50: approval missing spec_edition → rejection (F2 regression)
    ("POL-T50: Approval missing spec_edition → rejection",
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
                     "scope": VALID_POLICY["scope"],
                     "namespace": VALID_POLICY["namespace"],
                     # spec_edition intentionally missing
                 }
             },
             decision_scope=VALID_POLICY["scope"],
             supported_versions={"2026a"},
             revocation_checked_at=NOW,
             audit_store={VALID_POLICY["approval_ref"]: {"decision_time": NOW, "decider": "board-2026", "approval_ref": VALID_POLICY["approval_ref"], "policy_id": VALID_POLICY["policy_id"], "version": VALID_POLICY["version"], "digest": VALID_POLICY["digest"]}},
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
