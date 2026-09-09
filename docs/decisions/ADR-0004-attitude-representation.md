# ADR-0004 — Quaternion as the internal attitude representation

**Date:** 2026-09-09 · **Status:** Accepted · **Detail:** RS-002

## Context

Attitude is a point on $SO(3)$, which cannot be covered by a single global chart. Every
three-parameter representation has a singularity; avoiding one requires more parameters than degrees
of freedom, and therefore a constraint to maintain. The choice is which cost to pay.

## Decision

| Role | Representation |
|---|---|
| Integrated state | **Quaternion** — Hamilton, scalar-first, $q_{BI}$ |
| Transformation | DCM, computed from $q$ on demand, never stored or integrated |
| Input, output, reporting | Euler angles 3-2-1, converted at the boundary |

Norm maintained by **explicit renormalisation after each completed step**, never inside an RK stage.

## Alternatives considered

- **Euler angles as the integrated state.** Rejected decisively, and for a RADIUS-specific reason. In
  a 3-2-1 sequence the singularity is at $\theta=\pm90°$. For an aircraft that is an aerobatic edge
  case; for a **vertically launched vehicle it is the initial condition**. A 3-2-1 Euler state would
  be singular at $t=0$ of the most obvious test case the project will run. Choosing a different
  sequence moves the singularity rather than removing it, and makes the representation's validity a
  function of the trajectory — a hidden precondition of exactly the kind RADIUS exists to avoid.
- **Direction cosine matrix as the integrated state.** Rejected. Nine states and six constraints for
  three degrees of freedom, needing re-orthonormalisation. Worse, DCM drift is not benign: a matrix
  that loses orthonormality starts scaling and shearing vectors, so numerical error becomes a spurious
  *physical* effect on computed force magnitudes. Quaternion norm error is first-order and removed
  exactly by a division.
- **Baumgarte constraint stabilisation** instead of renormalisation. Rejected for now: introduces a
  tuning parameter with no principled value, stiffens the ODE as it grows, and solves a problem a
  division already solves exactly. It is the right tool when the constraint cannot be cheaply
  projected onto; here it can.
- **In-stage normalisation.** Rejected and explicitly warned against: it changes the stage function
  from the $f$ the Butcher tableau's order conditions were derived for, silently invalidating the
  method's order — producing a plausible trajectory with the wrong convergence rate.

## Consequences

- No singularity at any attitude, including vertical launch.
- Kinematics are bilinear: no trigonometry, no division, **no branches** in the inner loop. Branch-free
  arithmetic is deterministic, which the reproducibility guarantee depends on.
- Double cover ($q \equiv -q$) means attitude comparison must use the geodesic angle
  $\Delta\Theta = 2\arccos|q_{\text{err},0}|$, never component-wise differences. Canonicalisation to
  $q_0\ge0$ happens at boundaries only, never during integration.
- Quaternions are unreadable; Euler conversion at every output boundary is mandatory, and the
  extraction is ill-conditioned near $|\theta|=90°$ — the Euler singularity reappearing at the
  *reporting* layer, where it is harmless but must be flagged rather than printed.
- **The claim that post-step normalisation preserves 4th-order accuracy is a prediction, not a fact**
  (`A-ATT-01`). V-NUM-07 tests it; if it fails, ADR-0006 reopens.

## Revisit if

An attitude estimator is added — its local error representation (MRPs or a rotation-vector error
state) is a separate decision this ADR does not settle. Or if V-NUM-07 shows normalisation degrades
the observed order.
