# R1 — VDA 5050 / VDMA Roadmap: Elevator Dispatch & Door Access

**Date:** 2026-08-22
**Author:** Kvasir
**Status:** LEVERT

## Question

Does VDA 5050 (current or planned) cover elevator dispatch or door access semantics?
If yes, Sup-003 scope can shrink to reference the standard instead of defining
its own contract.

## Findings

### VDA 5050 v2.1.0 Scope (Current)

VDA 5050-2, version 2.1.0 (published January 2025) covers:
- Factsheet publication (`vda5050/factsheet`)
- State updates (`vda5050/state/<serialNumber>`)
- Order dispatch (`vda5050/order/<serialNumber>`)
- Connection state (`vda5050/connection/<serialNumber>`)
- Order cancellation via `instantActions` with `cancelOrder`:
  `vda5050/instantActions/<serialNumber>`
- Navigation nodes with building/floor attributes

**NOT covered:**
- Elevator dispatch (no elevator topic, no boarding status)
- Door access (no door lock/unlock semantics)
- Building infrastructure interaction

### VDA 5050 3.0 (April 2026)

VDA 5050 3.0 was published in April 2026. New features include:
- Zone definitions with explicit permission requirements
- Movement rules within zones
- Area-based access control

The VDA 5050 specification is publicly available at:
https://github.com/VDA5050/VDA5050

Rocom has reviewed VDA 5050 3.0. Version 2.1.0 is retained as the normative
baseline because it provides sufficient coverage for current deployments
and is widely implemented. Overlap with 3.0 zone semantics is addressed
through Rocom's own zone model (Part 1) and the Healthcare profile.

**Kilde-sjekk:**
- VDA hjemmeside (vda.de): Ingen offentlig roadmap for VDA 5050 funnet.
  VDA 5050-dedikerte sider returnerer 404.
- VDA 5050 er offentlig tilgjengelig via GitHub:
  https://github.com/VDA5050/VDA5050
- Ingen VDMA roadmap dokument funnet offentlig.

### Relevante Standarder

- **EN 81-28** (Elevators — Safety rules — Additional requirements for power-operated
  pedestrian access doors): Eksisterer, men er en sikkerhetsstandard, ikke
  en kommunikasjonsprotokoll for robot-elevator-interaksjon.
- **BACnet** (ASHRAE Standard 135): Har `AccessDoor` og `ElevatorGroup` objekter,
  men er BMS-intern — ikke designet for robot-initiert kommunikasjon.

## Conclusion

**FINNES IKKE.** VDA 5050 dekker verken elevator dispatch eller door access,
og det finnes ingen offentlig indikasjon på at dette planlegges.

**Konsekvens for Sup-003:** Full scope beholde. Sup-003s normative schema for
elevator dispatch og door access er nødvendig — det finnes ingen standard å
referere til.

## Sources

### VDA 5050 scope (konkret verifisert mot standardtekst)
- VDA 5050-2, version 2.1.0 (january 2025) — offentlig tilgjengelig:
  https://github.com/VDA5050/VDA5050
- MQTT topic-oversikt fra standarden bekrefter 6 topic-familier; ingen
  dekker elevator eller dør: `vda5050/factsheet`, `vda5050/state`,
  `vda5050/order`, `vda5050/connection`,
  `vda5050/instantActions` (cancelOrder via instantActions),
  `vda5050/navigation`
- VDA 5050-1 (2022, tidligere utgave) dekker samme omfang — ingen endring

### VDA 5050 roadmap / fremtidige versjoner
- VDA hjemmeside (https://www.vda.de/de/themen/zukunft-mobilitaet/branchenlosungspakete/vda-5050):
  Ingen offentlig roadmap, ingen versjonsoversikt, ingen planlagte utvidelser nevnt
- VDA 5050 3.0 published April 2026 (zones, movement rules, permission areas)
- VDMA (https://www.vdma.org/): Ingen offentlig roadmap for VDA 5050 eller
  robot-heis/dør-utvidelser funnet

### Relaterte standarder som DEKKER heis/dør (men ikke fra robot-siden)
- EN 81-28: https://en.wikipedia.org/wiki/EN_81-28 (sikkerhet, ikke protokoll)
- EN 81-20/50: https://cenvig.com/en-81-20-50/ (heiskonstruksjon, ikke kommunikasjon)
- BACnet (ASHRAE 135): https://www.bacnet.org/standards/bacnet-2020-standard/ — har
  `AccessDoor` og `ElevatorGroup` objekter, men BMS-intern, ikke robot-initiert
- IEC 60335-2-53: https://webstore.iec.ch/publication/63992 — heissikkerhet, ikke kommunikasjon
