# ADR-0009 — Variable-mass rotational equation: the inertia-rate term is removed

**Date:** 2026-09-09 · **Status:** Accepted
**Amends:** RS-004 §4, RS-008 §4 · **Evidence:** `docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md` §5

## Context

RS-004 previously specified

$$\dot{\boldsymbol\omega} = \mathbf{J}^{-1}\big[\mathbf{M} - \boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega) - \dot{\mathbf{J}}\boldsymbol\omega + \mathbf{M}_{\text{jet}}\big]$$

with $-\dot{\mathbf{J}}\boldsymbol\omega$ **implemented** and $\mathbf{M}_{\text{jet}}$ **omitted**
and undefined.

The pre-implementation mathematical audit found this incorrect. The two terms arise from a **single**
physical process — mass leaving the vehicle — so implementing one while omitting the other is not a
conservative approximation of the full equation. It is a different, and unphysical, model.

**Demonstration.** Torque-free axisymmetric body spinning at $\omega_z = 10$ rad·s⁻¹ about its
symmetry axis, depleting uniformly from 1000 kg to 500 kg over 20 s, inertia proportional to mass, no
external moment:

| | $\omega_z(20\ \text{s})$ |
|---|---|
| Truth — each element leaves carrying its own angular momentum | **10.000** rad·s⁻¹ |
| Formulation as specified | **20.000** rad·s⁻¹ |

A **factor-of-two spurious spin-up**. The $-\dot{\mathbf{J}}\boldsymbol\omega$ term forces
conservation of $\mathbf{J}\boldsymbol\omega$ — the physics of a skater pulling their arms in, which
is internal *redistribution*, not ejection. When mass is ejected, each material element keeps its own
angular velocity, so the remaining body spins at the same rate with less angular momentum.

The error is the exact rotational analogue of the one RS-004 §3.1 identifies and rejects for linear
momentum. The specification argued carefully that treating departing mass as vanishing is wrong for
translation, and then did it for rotation three sections later.

## Decision

Adopt

$$\mathbf{J}(t)\,\dot{\boldsymbol\omega} + \boldsymbol\omega\times\big(\mathbf{J}(t)\boldsymbol\omega\big) = \mathbf{M}_{\text{ext}}$$

under a new explicit assumption:

> **`A-VM-05`** — ejected mass leaves **co-rotating, with negligible velocity relative to the
> structure at its exit location**. Under this assumption the angular-momentum flux carried out by the
> departing mass is $-\dot{\mathbf{J}}\boldsymbol\omega$, which **cancels the $\dot{\mathbf{J}}\boldsymbol\omega$
> term on the left-hand side exactly**.

Consequences of the decision:

- $\dot{\mathbf{J}}$ **does not appear** in the equations of motion. `inertia_rate_body` is retained in
  the `MassProperties` interface as a **diagnostic** only.
- $\mathbf{M}_{\text{jet}}$ ceases to be an undefined symbol in a boxed governing equation. Jet
  damping is now precisely defined as the moment arising when the exhaust leaves with **non-zero**
  velocity relative to the structure at a point offset from the CM. It remains omitted
  (`A-VM-03`), but as a single separable term rather than half of an entangled pair.
- **V-EOM-09 / V-VM-10** added: variable-mass torque-free spin, hand-computed, requiring
  $\omega_z$ constant.

## Alternatives considered

- **Keep $-\dot{\mathbf{J}}\boldsymbol\omega$ and also derive $\mathbf{M}_{\text{jet}}$.** Rejected as
  the baseline. It is not wrong, but under `A-VM-05` the two terms cancel identically, so carrying
  both is arithmetic that computes zero at the cost of requiring $\dot{\mathbf{J}}$ inside every RK
  stage. The audit brief's stated preference — *the simplest mathematically correct model compatible
  with the declared scope* — selects the cancelled form.
- **Keep the term and treat the discrepancy as "conservative".** Rejected: a factor-of-two error in
  spin rate is not a conservative approximation in any direction, and calling it one would be the kind
  of after-the-fact rationalisation the project's rules exist to prevent.
- **Model the exhaust explicitly** to derive both terms from first principles. Rejected: it requires
  exit-plane geometry and exhaust velocity, which is propulsion hardware detail and outside the scope
  boundary in `CLAUDE.md`.
- **Retain the term for internal redistribution.** Not applicable now — RADIUS models depletion, not
  redistribution — but recorded: for a moving internal mass ($\dot{\mathbf{J}}\neq0$ with $\dot m=0$)
  the term **is** correct and would return with its own derivation.

## Consequences

- The rotational equation is **simpler** than before and **more** correct. That combination is
  unusual enough to be worth stating.
- Two hazards disappear with the term: the open question of computing $\dot{\mathbf{J}}$ analytically
  versus by finite difference, and the risk that a finite-difference derivative nested inside an RK
  stage acts as a second discretisation degrading the observed convergence order (RS-005 §11).
- `A-VM-05` is now load-bearing. It is **not** an assumption that jet damping is small — it is the
  assumption that isolates jet damping as the entirety of the remaining effect. That is a better-posed
  open question than the one it replaces.
- Any future exhaust model must supply the jet-damping moment through the existing
  `moment_body` interface, not by reintroducing $\dot{\mathbf{J}}$.

## Revisit if

RADIUS models internal mass redistribution; a reference bounds the jet-damping magnitude
(`A-VM-03`); or a case arises where the exhaust demonstrably carries significant transverse momentum
relative to the structure, making `A-VM-05` too coarse.
