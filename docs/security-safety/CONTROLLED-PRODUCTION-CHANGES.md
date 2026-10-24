# FILE: docs/security-safety/CONTROLLED-PRODUCTION-CHANGES.md
# Status: Informative guidance
# License: CC-BY 4.0
# Title: Controlled Production Changes — Zero Trust and Zero Touch

This guidance proposes operational practices for ROCOM deployments. It adds
no normative requirements, conformance levels or certification criteria.
Applicable requirements remain in the selected specification Edition,
deployment profile and approved local safety case.

## 1. Distinguish access from change execution

Google's *Building Secure and Reliable Systems*, Chapters 3 and 5, describes
complementary approaches:

| Term | Meaning in the cited source |
|---|---|
| Zero Trust Networking | Network location alone confers no privileged access; access depends on authenticated user and device context. |
| Zero Touch Production (ZTP) | Production changes use automation, software prevalidation or an audited emergency access mechanism. |
| Zero Touch Networking (ZTN) | The Zero Touch approach applied to network administration through controlled tools and automation. |

Here, **ZTN means Zero Touch Networking**. Spell out Zero Trust Networking
to avoid confusing the two. Zero Touch does not mean unreviewed changes or
the removal of human responsibility.

## 2. Apply this at ROCOM boundaries

ROCOM deployments can use an administrative service boundary with a small
set of authorised operations: register an interface, rotate an identity,
apply a versioned configuration, drain a service, deploy a specific artifact
or restore a verified backup. This can be part of an existing service;
it does not require a new microservice for each operation.

Normal administration should use those operations instead of unrestricted
shell, database or broker access. Apply authorisation to the initiating
person or workload, the operation and its target scope. An automation
service or AI agent should receive only the authority needed for its job.

For example, a maintenance operator may request a restart of Fleet A's
adapter without authority to restart Fleet B, alter BMS permissions or
change workforce eligibility. A robot's permission to request a door
opening does not include permission to modify the door's access policy.

## 3. Example controls for a deployment profile

The following are proposed controls to select and test according to local
risk. They are not additional ROCOM conformance requirements.

| Area | Example control and observable evidence |
|---|---|
| Access | Separate identities and permissions for runtime workloads, maintainers and change automation; reject unauthorised targets and operations. |
| Change request | Record the initiator, purpose, target interface/resource, intended configuration or artifact digest, expiry and approval reference. |
| Prevalidation | Check schema, version compatibility, permissions, declared dependencies and current resource obligations before applying a change. |
| Approval | Apply risk-based approval; use independent approval for high-impact changes. Do not make every ordinary task request a multi-party approval event. |
| Deployment | Roll out to a bounded scope, observe results and stop expansion when declared limits are breached. |
| Recovery | Define a tested recovery action. Database changes may require a forward repair or backup restore rather than a binary rollback. |
| Audit | Correlate request, authorisation, execution and outcome, including refusals and failures, with the actual artifact/configuration version. Protect records from modification by the actor being audited. |
| Emergency access | Provide explicit, time-limited breakglass access with attribution, alerting and subsequent review. Define recovery when the ordinary authorisation service is unavailable. |
| Networking | Apply network policy, routing and broker permission changes through validated, versioned operations. Verify intended connectivity and denied paths. |

## 4. Preserve local authority and availability

Administrative automation does not acquire authority over clinical priority,
human consent, building safety or robot emergency stop. Those responsibilities
remain with their respective systems. Emergency stop must remain effective
without waiting for the administrative service or its approval workflow.

An unavailable change service should block new administrative changes by
default. Runtime handling follows the approved degraded-mode policy and
existing resource obligations. Do not infer that an occupied lift or corridor
is free because a service or grant has timed out.

If an administrative proxy is used, define its redundancy, dependency limits
and emergency path. Avoid making a single proxy instance the only route for
every runtime and recovery operation. Reconnection alone is insufficient
evidence that a recovered interface can resume new commitments.

## 5. Suggested verification scenarios

Use an isolated environment and record expected results before execution:

1. A compromised Fleet A maintenance identity cannot change Fleet B, a BMS
   access policy or workforce permissions.
2. An artifact/configuration digest mismatch rejects the change; a valid,
   authorised request is traceable to its actual execution and outcome.
3. An adapter rollout failure stops expansion while unaffected fleets and
   independent workflows continue within their declared policies.
4. Loss of the administrative service preserves local safety behaviour and
   prevents unapproved changes; the documented emergency path still works.
5. Emergency access expires, produces reviewable evidence and leaves no
   permanent broad privilege.
6. A failed network-policy change has a tested recovery path that does not
   depend solely on the connectivity that the change can remove.

Keep operational secrets, customer topology and detailed vulnerability reports
in access-controlled implementation records. Publish the interoperable
contract, declared limitations and evidence summary needed to assess claims.

## 6. Relation to the specification

This guidance supports Part 6 (identity, transport and revocation), Part 7
(attribution and data handling), Part 2 service-quality and recovery profiles,
and CP-008 resource authority. It does not change their requirements or
resolve Edition/level migration questions. Any proposed normative additions
follow the process in CONTRIBUTING.md.

See also the [ROCOM Certification Plan — Example](../examples/ROCOM-CERTIFICATION-PLAN-EXAMPLE.md).

## References

- Google, *Building Secure and Reliable Systems*, [Chapter 3: Case Study — Safe Proxies](https://google.github.io/building-secure-and-reliable-systems/raw/ch03.html).
- Google, *Building Secure and Reliable Systems*, [Chapter 5: Design for Least Privilege](https://google.github.io/building-secure-and-reliable-systems/raw/ch05.html).

The deployment controls and scenarios above are ROCOM guidance proposed from
these principles; they are not a claim of Google endorsement or a Google
certification scheme.
