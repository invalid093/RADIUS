# RADIUS — Research Specification

The mathematical specification of the RADIUS simulator, written **before** implementation. The
frame and attitude conventions are now implemented and verified (`radius/frames.py`,
`radius/math/quaternion.py`); every other subsystem described here is specified and **not yet
implemented**. Nothing described here is validated.

Read in order; each document depends on the ones above it.

| Document | Subject | Decides |
|---|---|---|
| [`../methodology/NOTATION_AND_CONVENTIONS.md`](../methodology/NOTATION_AND_CONVENTIONS.md) | Units, frame notation, transformation direction, Euler sequence, quaternion convention, sign conventions | ADR-0003 |
| [RS-001](RS-001_reference_frames.md) | Reference frames; the flat non-rotating Earth assumption, **quantified** | ADR-0003 |
| [RS-002](RS-002_attitude_representation.md) | Euler vs DCM vs quaternion; norm maintenance; attitude comparison | ADR-0004 |
| [RS-003](RS-003_state_representation.md) | The 14-element state; inertial vs body velocity; mass as a state | ADR-0005 |
| [RS-004](RS-004_equations_of_motion.md) | The nonlinear 6-DOF equations, including variable mass; analytical verification cases | — |
| [RS-005](RS-005_numerical_integration.md) | Integrator selection, step size, error behaviour, events, determinism | ADR-0006 |
| [RS-006](RS-006_atmosphere.md) | Exponential baseline and U.S. Standard Atmosphere 1976 | — |
| [RS-007](RS-007_aerodynamic_model.md) | Force/moment build-up, moment transfer, validity gate, coefficient provenance | — |
| [RS-008](RS-008_variable_mass_abstraction.md) | Generic mass-flow and external-force abstraction | — |
| [**QUALITY_GATE**](QUALITY_GATE.md) | The thirteen questions the specification must answer, and the verdict | — |
| [**PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT**](PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md) | Independent mathematical audit of the whole specification. **Four defects found and corrected**, one load-bearing | ADR-0009 |

Supporting: [`../assumptions.md`](../assumptions.md) (31 registered assumptions with consequences) ·
[`../architecture/ARCHITECTURE.md`](../architecture/ARCHITECTURE.md) ·
[`../methodology/VERIFICATION_AND_VALIDATION.md`](../methodology/VERIFICATION_AND_VALIDATION.md) ·
[`../../research/SOURCES.md`](../../research/SOURCES.md).

## Audit status

The specification was independently audited before implementation
([report](PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md), 2026-09-09): **PASS WITH REQUIRED CORRECTIONS**,
corrections applied. The frame conventions, quaternion kinematics, translational dynamics, gyroscopic
term and atmosphere model were **verified correct** by independent derivation and numerical check.
Four defects were found — the load-bearing one a factor-of-two error in the variable-mass rotational
equation (ADR-0009).

## Gate verdict

**PASS for Phases 2–6** — frames, mathematical utilities, state, equations of motion, numerical
integration, analytical verification. Implementation may begin.

**NOT PASS for Phase 8 (aerodynamics)** — no traceable coefficient source, and the Mach-dependence gap
is unassessed. Continue researching that subsystem rather than implementing it.

**Phase 7 (atmosphere)** may proceed once the layer table is checked directly against the U.S.
Standard Atmosphere 1976 document.

## What these documents deliberately do

- **Quantify assumptions rather than assert them.** The flat-Earth assumption comes with numbers.
- **Name omitted terms.** Jet damping is absent and *called* absent, with its consequence (damping is
  optimistically low) stated. An unnamed omission is indistinguishable from an error.
- **Specify tests before code.** Roughly 60 verification tests with pass criteria, ordered so a
  failure localises.
- **Record what cannot be claimed**, which is currently almost everything (QUALITY_GATE Q12).
