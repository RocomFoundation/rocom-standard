# CP-007 — Agent Identity Model (issuer-agnostic, UDI-aligned)

**Status:** MERGED (Edition 2026a draft)
**Target:** Part 3 — Information Model (Edition 2026a, draft)
**Also affects:** Part 4 (Service Contracts), Part 5 (Transport Profile),
Sup-001 (Orchestrator Service Interface)
**Raised:** 28 August 2026
**Author:** Rocom Project

---

## 1. Problem

The current information model identifies an agent by an
implementation-assigned identifier only. This has three consequences,
all observed in a running implementation:

1. **External systems cannot address an agent they registered.** A robot
   that registers itself over VDA 5050 announces `manufacturer` and
   `serialNumber`, but has no way to resolve those to the identifier the
   orchestrator assigned. Every state update from that robot is
   unroutable.
2. **Type, configuration and unit are conflated.** There is no way to
   express that two units are the same model, or that the same unit is
   now running different software — which is exactly the distinction a
   conformance certificate depends on.
3. **The model has no place for regulatory identity.** Where an agent is
   a regulated medical device, its Unique Device Identification data has
   nowhere to live, and the hospital's device register and the
   orchestrator's agent register cannot be reconciled.

## 2. Design basis

The European UDI system, established by Regulation (EU) 2017/745 and
Regulation (EU) 2017/746, solves the same problem for medical devices.
Two properties of that design are adopted here:

**Layered identifiers.** A Basic UDI-DI identifies a group of devices
with the same intended purpose and design, and is the global access key
for EUDAMED. UDI-DI identifies the specific device configuration and
packaging level; production identifiers identify the individual unit.

**Issuer-agnostic structure.** Four issuing entities are designated to
operate UDI assignment systems under Commission Implementing Decision
(EU) 2019/939: GS1 AISBL; Health Industry Business Communications
Council (HIBCC); International Council for Commonality in Blood Banking
Automation (ICCBBA); and Informationsstelle für Arzneispezialitäten
(IFA) GmbH. A manufacturer may use different issuing entities at
different packaging levels and for the Basic UDI-DI; the issuing entity
is recorded as a data field, and EUDAMED links the identifiers
regardless of which entity issued them. Designations are valid for five
years, renewable, and may be suspended or revoked.

Rocom therefore adopts the *pattern*, not the regulatory claim: three
identifier layers, issuer declared per identifier, and a separate
optional block for actual regulatory identity.

## 3. Normative requirements

**ID-10** — Every agent SHALL have an `agent_identity` object containing
`access_key`, `device_identifier` and `production_identifier`.

**ID-11** — `access_key` SHALL be stable across software versions,
configuration changes and individual units of the same agent type. It is
the canonical lookup key for the agent type.

**ID-12** — `device_identifier` SHALL change when the configuration that
conformance was assessed against changes, including software version
where that version affects declared capabilities or protocol behaviour.

**ID-13** — `production_identifier` SHALL identify the individual unit.
Where the agent communicates over VDA 5050, `serial_number` SHALL carry
the VDA 5050 `serialNumber` value verbatim.

**ID-14** — `issuing_entity` SHALL be declared per identifier.
Implementations SHALL NOT require that `access_key.issuing_entity` and
`device_identifier.issuing_entity` are equal.

**ID-15** — Implementations SHALL support agent lookup by
`access_key` and by `production_identifier.serial_number`, without the
caller possessing any implementation-assigned identifier.

**ID-16** — Implementation-assigned identifiers (for example database
keys) MAY exist but SHALL NOT be required for any interaction defined by
this standard.

**ID-17** — Where an agent is a medical device within the scope of
Regulation (EU) 2017/745 or (EU) 2017/746, the `regulatory` block SHALL
carry its Basic UDI-DI and UDI-DI. Where the agent is not a regulated
device, the `regulatory` block SHALL be absent. Presence of
`agent_identity` alone SHALL NOT be construed as a claim of regulatory
status.

**ID-18** — Agent state reported by an agent about itself is an
observation, not a command. An implementation SHALL accept a reported
state equal to the current state as a successful no-op. Lifecycle
transition rules apply to *commanded* state changes only.

## 4. Schema

```yaml
agent_identity:
  access_key:
    issuing_entity: gs1 | hibcc | iccbba | ifa | vda5050 | internal
    value: string          # Basic UDI-DI where regulated; otherwise a
                           # stable manufacturer+model key
  device_identifier:
    issuing_entity: gs1 | hibcc | iccbba | ifa | vda5050 | internal
    value: string          # configuration/version-bearing identifier
    software_version: string        # optional, informative
  production_identifier:
    serial_number: string           # VDA 5050 serialNumber verbatim
    manufacture_date: date          # optional
  regulatory:                        # optional; only for regulated devices
    basic_udi_di: string
    udi_di: string
    eudamed_registered: boolean
```

**Note on the issuer enumeration.** `gs1`, `hibcc`, `iccbba` and `ifa`
are the entities designated under Decision (EU) 2019/939. `vda5050`
denotes an identity asserted through the VDA 5050 factsheet;
`internal` denotes an identity assigned by the operating organisation.
Implementations SHALL treat the enumeration as extensible: designations
are time-limited and may change.

## 5. VDA 5050 mapping (informative)

| VDA 5050 | Rocom `agent_identity` |
|---|---|
| `manufacturer` | contributes to `access_key.value` (with model) |
| `serialNumber` | `production_identifier.serial_number` |
| factsheet `typeSpecification` | `device_identifier.value` |
| factsheet version fields | `device_identifier.software_version` |

An agent registering over VDA 5050 SHALL be resolvable by
`serial_number` alone, per ID-15.

## 6. Human agents (informative)

The same structure applies to people: `access_key` identifies the role
or qualification class, `device_identifier` is not used, and
`production_identifier` carries the workforce identifier issued by the
employing organisation. Part 7 constraints on personal data apply
unchanged; no clinical or personal attribute is carried in
`agent_identity`.

## 7. Conformance tests

**ID-10** — An agent registered with a full `agent_identity` can be
retrieved by `access_key`.
**ID-11** — An agent registered over VDA 5050 can be retrieved by
`serial_number` alone, with no implementation identifier known to the
caller.
**ID-12** — An agent whose `access_key.issuing_entity` differs from its
`device_identifier.issuing_entity` is accepted.
**ID-13** — Reporting the current state twice returns success both
times, and no lifecycle violation is raised.
**ID-14** — An agent without a `regulatory` block is accepted, and no
regulatory status is asserted in any output.

## 8. Migration

Existing implementations that assign identifiers internally remain
conformant provided ID-15 and ID-16 are met: the internal identifier may
continue to exist, but external lookup by `access_key` and
`serial_number` must be available. Registration payloads without
`agent_identity` SHOULD be rejected from Edition 2026b onwards.

## 9. Normative references

- Regulation (EU) 2017/745 (Medical Devices Regulation), Article 27
- Regulation (EU) 2017/746 (IVDR), Article 24
- Commission Implementing Decision (EU) 2019/939 of 6 June 2019
  designating issuing entities for the assignment of Unique Device
  Identifiers
- VDA 5050 v2.1 (pinned in Part 5 §1.1)
