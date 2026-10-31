<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN IEC Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the two registry
configurations this repository owns (`gridded_iec`, `polywell`). The
claim boundary and repository-level `evidence_maturity` semantics
follow the family pilot.

## Decision

1. The package `scpn_iec_core` implements the device configuration
   model as frozen, strictly typed value objects: the confinement
   structure (grid or virtual-cathode class, cathode-grid transparency,
   polyhedral coil count) and the electrostatic drive (well voltage).
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Hard class invariants: `gridded_iec` requires a physical cathode
   grid — transparency strictly inside ``(0, 1)`` — and no magnetic
   coils; `polywell` requires at least six polyhedral coils forming the
   virtual cathode and a transparency of exactly one (no physical grid
   intercepts). The filed thesis R. F. Radel, UWFDM-1325 (2007), PDF
   pp. 21-22 (printed pp. 6-7), describes both: the gridded device with
   its cathode grid, and Bussard's grid-less polywell, whose cusp
   magnetic fields form an electron cloud that acts as the cathode. The
   minimum of six coils is declared.
4. Derived quantity: the maximum singly-charged ion energy
   ``E = e U`` (``ion_energy_kev`` equals the well voltage in
   kilovolts). Advisory finding, reported by `consistency_report()`
   and never clamped: a well voltage below a declared ``20 kV`` floor.
   The filed Radel (2007) thesis reports Hirsch's tabletop D-T result at
   a cathode voltage of 150 kV (PDF p. 21, printed p. 6).
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (well/convergence/yield diagnostic semantics, safety
  envelope) build on these types; maturity advances per capability only
  with the evidence the family standard requires.

## Amendment 2026-10-31

The class invariants, the ion-energy relation and the voltage floor were
credited to R. L. Hirsch, J. Appl. Phys. 38 (1967) 4522, which is not on
file. The earlier text also said that Hirsch operated near 100 kV; the
filed Radel (2007) thesis reports 150 kV (PDF p. 21, printed p. 6). The
invariants are now bound to Radel's description of the gridded and
polywell devices, the ion energy is stated as energy conservation, and
the 20 kV floor is named declared. No invariant, value or check changed.
