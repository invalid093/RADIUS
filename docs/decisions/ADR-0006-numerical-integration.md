# ADR-0006 — Fixed-step RK4 as the initial integrator

**Date:** 2026-09-09 · **Status:** Accepted · **Detail:** RS-005

## Context

Choosing an integrator by familiarity is how a simulator acquires behaviour nobody can account for.
Requirements were therefore ranked before methods were considered:

1. **Determinism** — identical inputs give bitwise-identical outputs on a platform.
2. **Verifiable order of accuracy** — the convergence rate must be measurable and match theory.
3. **Transparency** — a reader can state exactly what happens per step.
4. Adequate accuracy at a cost permitting Monte Carlo.
5. Event handling.
6. Compatibility with post-step quaternion normalisation.

Requirement 1 is not a preference. The publication policy (ADR-0008) declines to publish Monte Carlo
ensembles on the grounds that they are regenerable — which is true only if regeneration is exact.
Determinism is therefore load-bearing for the repository's governance, not just for tidiness.

## Decision

**Fixed-step classical RK4**, with **explicit Euler retained as a verification comparator**.

Step size is a configuration parameter, never hard-coded, justified per experiment. Proposed default
$h=10^{-3}$ s — a **proposal, not a result**, pending V-NUM-02.

Events are located by **bisection** on a sign change, with integration restarted from the event state.

## Alternatives considered

- **Explicit Euler as the production integrator.** Rejected. First order demands a far smaller step for
  equivalent error, costing more total evaluations than RK4 despite being cheaper per step. Worse, its
  stability region excludes the imaginary axis, making it *unconditionally unstable* for undamped
  oscillatory dynamics — which is what torque-free rotation is. Coning would grow without bound as a
  property of the method.

  **Retained deliberately as a comparator.** V-NUM-01 requires slopes of 1 for Euler and 4 for RK4.
  Having a method with a *different* expected slope is what makes the test meaningful: if both
  measured 4, the harness is measuring something other than the integrator.

- **Embedded adaptive RK5(4), Dormand–Prince (SRC-009).** Rejected for the initial phase — not on
  accuracy, where it is the better method per unit work, but on requirements 1 and 2:
  - Its accepted step sequence depends on a floating-point error estimate compared against a
    tolerance. A last-bit difference can flip an accept/reject decision, after which two runs take
    different step sequences and diverge. Determinism becomes conditional rather than structural.
  - Order-of-accuracy measurement requires varying $h$ and fitting a slope. With an adaptive
    controller $h$ is not an input — the tolerance is — and the map from tolerance to effective step
    is not a clean power law. The single most informative verification test becomes much harder to
    interpret.

- **A third-party ODE solver (e.g. SciPy).** Rejected. The integrator is a *subject of study* in
  RADIUS, not a black box; delegating it would take the determinism and order-of-accuracy properties
  out of the project's control. RK4 is about thirty lines.

- **Brent's method for event location.** Rejected in favour of bisection: faster, but with a
  data-dependent iteration count, reintroducing the determinism concern that ruled out adaptive
  stepping. Events are rare; the cost is negligible.

## Consequences

- The step must be chosen conservatively for the fastest retained mode, and small steps are paid for
  everywhere including quiescent phases. Accepted.
- **Stability is not the binding constraint; accuracy is.** RK4's imaginary-axis stability limit
  ($|\lambda h| \lesssim 2.83$) permits $h < 90$ ms for a 5 Hz mode, while a 20-steps-per-period
  accuracy rule demands $\le 10$ ms — a factor of nine. The stability bound is never used for step
  selection.
- Convergence studies must identify the **roundoff floor**: below a minimum-error step, refining makes
  the answer worse and the measured slope flattens. That flattening is expected behaviour and evidence
  the study went deep enough — not a defect. V-NUM-01 must report the full curve.
- Order of accuracy must be verified *across* an event (V-NUM-06). Event restart logic is where order
  quietly dies, and it is the test most likely to be skipped.
- Cross-platform bitwise reproducibility is **not** claimed — only same-platform bitwise, and
  cross-platform agreement within a stated tolerance.

## Revisit if

A stiff or genuinely multi-scale problem makes fixed steps uneconomic; long-duration runs make
accuracy-per-cost dominant; V-NUM-01 shows RK4 does not achieve fourth order in this system; or
`A-NUM-02` (non-stiffness near mass depletion) is refuted.
