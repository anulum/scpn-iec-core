<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Iec Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics as spherical cathode grid geometry

Status: accepted (2026-09-04). Builds on ADR 0002 (device configuration
model), whose `ConfinementStructure` already carries the grid
transparency and the polyhedral coil count this record reads.

## Context

The repository's only cited work, Hirsch, *J. Appl. Phys.* **38** (1967)
4522, is behind a subscription and no copy is obtainable from a free,
legal source. It supplies the ion-energy relation ADR 0002 already
carries and nothing further that can be read here.

The question was therefore what a level-0 record can honestly compute
for this family. An IEC device's defining physics — the potential well,
the converging ion flow, the core density — is not closed-form; it is
the subject of the transport and space-charge calculations this
repository does not perform and could not check. What *is* closed-form,
and what the family's own configuration model already asks about, is the
**geometry of the cathode**: how many apertures a grid of a given ring
structure has, what fraction of the sphere its conductors leave open,
and what upper bound that fraction places on ion recirculation.

Two free sources were acquired and filed. An open-access 2024 paper in
*Scientific Reports* prints that geometry in closed form for both grid
families that became standard. A University of Wisconsin–Madison
technical report from 2007 prints the absolute dimensions of a built
device: chamber, cathode and anode diameters, the cathode wire gauge,
and the ring structure of the cathode it was operated with.

## Decision

1. The capability `level0_device_physics` is implemented as the
   published closed-form geometry of a spherical cathode grid, in three
   modules split by responsibility: the grid's combinatorics and angles,
   the transparency metrics, and the ion-recirculation bound. A fourth
   composes them into a record against one validated configuration.

2. **Equations are taken from the rendered pages, not the text layer.**
   `pdftotext` drops the tangent from the bridge-angle equation and
   leaves a bare fraction, and the paper's own table of four bridge
   angles agrees to every printed digit under both readings. Only the
   rendered equation settles it. A test records that the table
   corroborates nothing here, so that a later simplification of the
   tangent is caught by something.

3. **The two configurations meet these relations differently and the
   record keeps that visible.** A grid declaration is required for
   `gridded_iec` and refused for `polywell`, in both directions and by
   name. The pass-count relation diverges at a transparency of one,
   which is exactly the polywell's class invariant, so the record
   carries no pass count there rather than a large one.

4. **Aperture areas and neighbour half-angles are declared inputs.** The
   filed source computes them by meshing a grid model; this repository
   builds no such model, and producing our own numbers would be
   asserting a result we have no basis for. Where they are declared, the
   record recomputes the geometric transparency from them and reports it
   **beside** the transparency the configuration declares. Neither is
   derived from the other.

5. **A per-aperture measurement must match the grid it describes.** A
   sequence of a different length than the ring counts imply is refused
   rather than truncated or padded: it measures a different grid.

6. **The four permissible symmetric grids are a lookup, not a pattern.**
   The source states that beyond fifteen rings the varying aperture
   angle would violate the bound on a spherical triangle's angle sum,
   while noting that no proof of exhaustiveness is offered. Extrapolating
   the sequence would turn that caveat into a claim.

7. The distribution's potential-energy metric is **not** implemented. It
   is a sum over aperture centre points, which this package does not
   carry.

8. No kernel-library pin. Every relation is arithmetic and elementary
   trigonometry, so unlike the tier work this physics names no library
   commit.

## Consequences

- The manifest gains the capability `level0_device_physics` at
  `computational_prototype`, pointing at
  `VALIDATION.md#level-0-device-physics`; the implemented capability
  count becomes three, and the derived inventory and studio descriptor
  are regenerated from the manifest.
- The package root re-exports the record and the grid relations.
- Three numerical facts are recorded because they were measured rather
  than assumed, and each is asserted with the tolerance the measurement
  gave rather than as an equality: the factored pass-count denominator
  departs from the printed difference of squares by up to 5.5e-10 near a
  transparency of one; composing the circular-aperture and spherical-cap
  equations agrees with their single-step form to 8.4e-15; and a
  hemispherical cap lands one unit in the last place below half the
  sphere at every radius measured, because `cos(asin(1))` is not zero.
- **What this ADR does not decide.** The family's tier-G1 and tier-G2
  device models are not landed here and cannot be with the shared
  library as it stands. A gridded cathode is a cage of rods, and full
  fidelity means a model that is a cage of rods; the rings of such a
  cage are tori, and every longitude ring lies in a plane the library
  cannot yet place a body in. That is recorded against the rollout goal,
  not resolved here.
