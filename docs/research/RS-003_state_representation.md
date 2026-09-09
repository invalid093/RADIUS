# RS-003 — State Representation

**Status:** Specification. Not implemented, not verified.
**Depends on:** RS-001, RS-002
**Decides:** ADR-0005

---

## 1. What has to be decided

Not "what quantities describe the vehicle" — that is largely forced — but **which representation of
each quantity is integrated**. The physics is identical either way; the numerical behaviour, the
number of terms that can be got wrong, and the difficulty of verification are not.

Three genuine choices exist:

1. Position: inertial or something else?
2. Velocity: resolved in $I$ or in $B$?
3. Mass: an integrated state or a prescribed function of time?

Attitude was decided in RS-002 (quaternion). Angular velocity is resolved in $B$ without real
alternative, because the inertia tensor is constant-ish in body axes and wildly time-varying in
inertial axes.

---

## 2. Position

$$\mathbf{p}^{I}_{c/O} \in \mathbb{R}^3$$

Position of the centre of mass relative to the frame origin, resolved in $I$. There is no serious
alternative: forces integrate to inertial velocity, which integrates to inertial position, and any
other choice adds a transformation for nothing.

Altitude is derived, $h = -p^I_z$ (RS-001 §2.1, flat-Earth). It is a named function, not a raw
component access, so that the ECEF extension changes one function rather than every call site.

---

## 3. Velocity: the real decision

### Option A — inertial velocity $\mathbf{v}^{I}$

$$\dot{\mathbf{p}}^{I} = \mathbf{v}^{I}, \qquad \dot{\mathbf{v}}^{I} = \frac{1}{m}\,\mathbf{F}^{I}$$

### Option B — body-axis velocity $\mathbf{v}^{B} = (u,v,w)$

$$\dot{\mathbf{p}}^{I} = \mathbf{T}_{IB}\,\mathbf{v}^{B}, \qquad
\dot{\mathbf{v}}^{B} = \frac{1}{m}\mathbf{F}^{B} - \boldsymbol{\omega}^{B}\times\mathbf{v}^{B}$$

Option B is the aerospace convention — Stevens & Lewis, Beard & McLain and most aircraft simulators
integrate $(u,v,w)$ — because aerodynamic forces are naturally body-referenced and $\alpha,\beta$
follow directly from the state without any transformation.

### Decision: Option A, inertial velocity

Four reasons, in order of weight.

1. **The translational equation has no transport term.** $\dot{\mathbf{v}}^I = \mathbf{F}^I/m$ is one
   term. Option B carries $-\boldsymbol{\omega}\times\mathbf{v}$, a term whose sign is easy to get
   wrong and whose error is *small and plausible* — it does not blow the simulation up, it produces a
   subtly wrong trajectory. Given that RADIUS's entire premise is auditability, the formulation with
   fewer opportunities for a plausible-looking error is preferred even at some cost elsewhere.

2. **Analytical verification is exact and trivial.** The verification programme (RS-004 §7) rests on
   closed-form comparisons. Free-fall, ballistic and force-free cases are *exactly* linear in
   $\mathbf{v}^I$, so the reference solution is a two-line expression with no attitude dependence at
   all. In Option B the same physical test case requires the reference to be expressed through the
   attitude history, which couples the translational test to the rotational implementation — so a
   failure no longer localises. **A test that cannot localise a failure is worth much less than one
   that can.**

3. **Variable mass separates cleanly.** RS-004 §3 shows that the variable-mass translational equation
   is most safely written in an inertial frame, where the momentum-flux term appears explicitly and
   is not entangled with a frame-rotation term. Writing both in body axes makes it easy to
   double-count or drop a term, and this is a known failure mode in variable-mass derivations.

4. **The transformation is needed regardless.** Option B's advantage is avoiding a transformation —
   but aerodynamics needs $\alpha, \beta$, which need body-frame *air-relative* velocity, which
   requires subtracting the wind field (an inertial-frame quantity) anyway. So $\mathbf{T}_{BI}$ is
   evaluated every derivative call in either formulation. Option B's advantage is smaller than it
   appears; the cost is one $3\times3$ matrix-vector product.

**Cost of this choice, stated plainly.** $u, v, w$ are not state components and must be computed for
reporting and for aerodynamics. Comparison against literature that tabulates $(u,v,w)$ requires a
conversion. This is a real inconvenience and it is accepted.

**Falsifiable consequence.** If a later phase shows the extra transformation is a measurable cost, or
that expressing aerodynamic derivatives is materially harder, ADR-0005 is revisited. The two
formulations are analytically equivalent, so switching invalidates no physics — only stored reference
trajectories, which are regenerable.

---

## 4. Attitude and angular velocity

$$q_{BI} \in S^3 \subset \mathbb{R}^4, \qquad \boldsymbol{\omega}^{B}_{B/I} = (p,q,r) \in \mathbb{R}^3$$

Quaternion per RS-002. Angular velocity resolved in $B$ because the rotational equation is
$\mathbf{I}\dot{\boldsymbol{\omega}} + \boldsymbol{\omega}\times(\mathbf{I}\boldsymbol{\omega}) = \mathbf{M}$
with $\mathbf{I}$ expressed in body axes, where it is constant for a rigid constant-mass body and
slowly varying for a depleting one. Resolved in $I$, the inertia tensor would vary at the vehicle's
full rotation rate — turning a slowly varying coefficient into a rapidly varying one for no gain.

---

## 5. Mass

$$m \in \mathbb{R}^{+}$$

**Decision: mass is an integrated state**, with $\dot m = -\dot m_{\text{out}}(t, \mathbf{x})$
supplied by the mass-flow interface (RS-008).

**Alternative considered: prescribe $m(t)$ analytically** and remove it from the state. Simpler, and
adequate whenever mass flow depends only on time. Rejected as the *general* case because as soon as
mass flow depends on the state — throttle commanded by a controller, flow depending on ambient
pressure — a prescribed $m(t)$ is wrong, and the failure is silent. Prescribed mass is available as
the special case where the interface ignores its state argument, which costs nothing.

**Positivity is not automatic.** Nothing in the ODE prevents $m$ crossing zero; an unguarded
$1/m$ then produces a division by a negative number and a trajectory that accelerates backwards
before it produces `inf`. Handling is specified in RS-008 §6 as an **event**, not a clamp — clamping
mass would silently violate mass conservation while producing plausible-looking output, which is
worse than stopping.

---

## 6. The state vector

$$\mathbf{x} = \big[\;\underbrace{\mathbf{p}^{I}}_{3}\;\;\underbrace{\mathbf{v}^{I}}_{3}\;\;\underbrace{q_{BI}}_{4}\;\;\underbrace{\boldsymbol{\omega}^{B}}_{3}\;\;\underbrace{m}_{1}\;\big]^{\mathsf{T}} \in \mathbb{R}^{14}$$

| Index | Symbol | Quantity | Frame | Unit |
|---|---|---|---|---|
| 0–2 | $\mathbf{p}^{I}$ | position of CM | $I$ | m |
| 3–5 | $\mathbf{v}^{I}$ | velocity of CM w.r.t. $I$ | $I$ | m·s⁻¹ |
| 6–9 | $q_{BI}$ | attitude, scalar-first | — | — |
| 10–12 | $\boldsymbol{\omega}^{B}_{B/I}$ | angular velocity w.r.t. $I$ | $B$ | rad·s⁻¹ |
| 13 | $m$ | total vehicle mass | — | kg |

**The state manifold is $\mathbb{R}^{13}\times S^3$, not $\mathbb{R}^{14}$.** The 14 numbers carry
13 degrees of freedom plus one constraint. This is not pedantry: it determines that a quaternion
normalisation step exists (RS-002 §6), that error norms over the state vector are not meaningful
without treating the quaternion block separately (RS-002 §7), and that any future covariance
propagation must use a 13-dimensional error state rather than a 14-dimensional one.

**Time is not a state.** It is passed explicitly to the derivative function. Autonomous-form
augmentation ($\dot t = 1$) is rejected: it adds a state whose only purpose is to hide a dependency
that is clearer when visible.

**The inertia tensor is not a state.** It is a function of mass and time supplied by the mass model
(RS-008 §4). Integrating it would introduce nine states with six constraints for a quantity that is
algebraically determined.

---

## 7. What is deliberately absent, and when it arrives

| Not a state now | Arrives with |
|---|---|
| Actuator positions and rates | Phase 12, if actuator lag is modelled. Algebraic actuators need no state — an assumption to be registered then, not now |
| Controller integrator states | Phase 12 |
| Individual propellant-tank masses, CM offset states | Only if a multi-tank mass model is justified. The single lumped $m$ is the current model |
| Aeroelastic / flexible-body states | Out of scope (`CLAUDE.md`) |
| Navigation filter states | Phase 11, and in a *separate* state vector — the estimator's state is not the vehicle's, and conflating them is how a simulator accidentally gives its estimator access to truth |

The last row is the one that matters most for the eventual AURA relationship, and it is recorded now
so that the separation is architectural rather than remembered.

---

## 8. Verification tests this specification requires

| ID | Test | Passes if |
|---|---|---|
| V-STA-01 | Pack/unpack round trip: named state ↔ flat 14-vector | bitwise identical |
| V-STA-02 | Indices in code match the table in §6 (asserted against hard-coded constants) | exact |
| V-STA-03 | Derived quantities $(u,v,w)$, $\alpha$, $\beta$, $h$ recomputed from state agree with values used to construct it | $<10^{-12}$ relative |
| V-STA-04 | Mass positivity: a run configured to deplete mass raises the depletion event and does not produce $m \le 0$ | event raised, no negative mass |
| V-STA-05 | State-error norm treats the quaternion block geodesically, not component-wise | $\Delta\Theta(q,-q)=0$ within the state metric |

V-STA-02 looks trivial and is not. An index shift between the packing and unpacking code produces a
simulation that runs, conserves nothing, and looks like a physics bug.

---

## 9. Assumptions registered

`A-STA-01`, `A-STA-02` — see `docs/assumptions.md`.

---

## 10. Open questions

1. Is inertial velocity still the right choice once aerodynamic *derivatives* (as opposed to forces)
   are needed — for trim, linearisation, or a controller? Those are conventionally expressed in body
   axes. Unresolved; revisit at Phase 12. It does not affect Phases 2–10.
2. Should the state carry a *dimensionless* scaled form for numerical conditioning? Position ~10⁴ m
   and quaternion components ~1 differ by four orders of magnitude, which matters for an adaptive
   error norm but not for fixed-step RK4. Deferred to RS-005, where the error norm is defined.
3. Does the single lumped mass state suffice once the CM offset becomes significant? RS-008 §5 argues
   yes for the current model, but it is an assumption, not a result.
