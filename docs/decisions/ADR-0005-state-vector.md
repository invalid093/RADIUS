# ADR-0005 — State vector definition

**Date:** 2026-09-09 · **Status:** Accepted · **Detail:** RS-003

## Context

The physics does not depend on which representation of each quantity is integrated. The numerical
behaviour, the number of terms that can be got wrong, and — most importantly here — the *difficulty of
verification* do.

The genuine choices were: velocity resolved in $I$ or $B$; mass as an integrated state or a prescribed
function; and what else, if anything, belongs in the state.

## Decision

$$\mathbf{x} = \big[\mathbf{p}^{I},\ \mathbf{v}^{I},\ q_{BI},\ \boldsymbol{\omega}^{B},\ m\big]^{\mathsf{T}} \in \mathbb{R}^{14}$$

with the state manifold $\mathbb{R}^{13}\times S^{3}$, not $\mathbb{R}^{14}$.

Velocity is resolved in the **inertial** frame. Mass is an **integrated state**. Time is not a state;
the inertia tensor is not a state.

## Alternatives considered

- **Body-axis velocity $(u,v,w)$** — the aerospace convention, used by most aircraft simulators
  because aerodynamic forces are body-referenced and $\alpha,\beta$ follow without transformation.
  Rejected on three grounds, the second being decisive:
  1. The translational equation acquires a transport term $-\boldsymbol{\omega}\times\mathbf{v}$ whose
     sign is easy to get wrong and whose error is *small and plausible* — it does not blow up, it
     produces a subtly wrong trajectory.
  2. **Verification would no longer localise.** Free-fall and ballistic reference solutions are exact
     and attitude-independent in inertial velocity. In body axes the same physical test requires the
     reference expressed through the attitude history, coupling the translational test to the
     rotational implementation — so a failure no longer says which is broken. A test that cannot
     localise a failure is worth much less than one that can.
  3. The variable-mass momentum-flux term separates more cleanly in an inertial frame, where it is not
     entangled with a frame-rotation term. Double-counting or dropping a term here is a known failure
     mode in variable-mass derivations.

  The claimed advantage — avoiding a transformation — is smaller than it appears: $\alpha,\beta$
  require *air-relative* body velocity, so the wind field (an inertial quantity) must be subtracted
  and $\mathbf{T}_{BI}$ evaluated in either formulation.

- **Prescribed $m(t)$ instead of a mass state.** Rejected as the general case: as soon as mass flow
  depends on the state (a commanded throttle, ambient-pressure dependence), a prescribed $m(t)$ is
  wrong and fails *silently*. Prescribed mass remains available as the special case where the
  interface ignores its state argument, which costs nothing.

- **Augmenting with $\dot t = 1$** for autonomous form. Rejected: adds a state whose only purpose is to
  hide a dependency that is clearer when visible.

- **Integrating the inertia tensor.** Rejected: nine states and six constraints for a quantity that is
  algebraically determined by the mass model.

## Consequences

- $u,v,w$ are not state components and must be computed for aerodynamics and for comparison with
  literature that tabulates them. A real inconvenience, accepted.
- The two formulations are analytically equivalent, so switching later invalidates no physics — only
  stored reference trajectories, which are regenerable. The decision is therefore cheap to revisit,
  which is part of why it was made on verification grounds rather than by convention.
- Because the manifold is not $\mathbb{R}^{14}$: a quaternion normalisation step must exist; error
  norms must treat the quaternion block geodesically; and any future covariance propagation uses a
  13-dimensional error state.
- Mass positivity is not automatic. It is handled as an **event**, never a clamp — clamping would
  create infinite propellant while producing plausible output.
- The estimator, when it arrives, gets its **own** state vector. Architectural, not stylistic: a
  navigation module that can reach truth eventually will.

## Revisit if

Aerodynamic *derivatives* (trim, linearisation, control design at Phase 12) prove materially harder to
express in this formulation; or a multi-tank mass model makes the single lumped $m$ inadequate.
