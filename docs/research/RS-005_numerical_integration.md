# RS-005 — Numerical Integration

**Status:** Specification. Not implemented, not verified.
**Depends on:** RS-002, RS-003, RS-004
**Decides:** ADR-0006

---

## 1. Requirements, stated before methods are considered

Choosing an integrator by familiarity is how a simulator acquires behaviour nobody can account for.
The requirements come first, in priority order for RADIUS's current phase:

| # | Requirement | Why it is where it is |
|---|---|---|
| R1 | **Determinism** — identical inputs give bitwise-identical outputs on a given platform | The publication policy does not publish Monte Carlo ensembles, on the grounds that they are regenerable. That is only true if regeneration is exact |
| R2 | **Verifiable order of accuracy** — the method's convergence rate must be measurable and match theory | This is the primary evidence that the integrator and the equations are both correct |
| R3 | **Transparency** — a reader can state exactly what the method does per step | RADIUS's premise is auditability |
| R4 | **Adequate accuracy** at a cost that permits Monte Carlo | Thousands of runs must be affordable |
| R5 | **Event handling** — staging, depletion, ground impact must be located, not stepped over | Events are physical discontinuities; missing one silently changes the trajectory |
| R6 | Constraint compatibility — must tolerate post-step quaternion normalisation | RS-002 §6 |

R1 and R2 are ranked above raw efficiency. That ordering is the decision; everything below follows
from it.

---

## 2. Candidates

### 2.1 Explicit (forward) Euler

$$\mathbf{x}_{n+1} = \mathbf{x}_n + h\,\mathbf{f}(t_n, \mathbf{x}_n)$$

Global order 1. One evaluation per step. Trivially transparent and deterministic.

**Rejected as a production integrator.** First-order accuracy demands a timestep smaller by orders of
magnitude for equivalent error, which costs more total evaluations than RK4 despite being cheaper per
step. Its stability region excludes the imaginary axis entirely, so it is *unconditionally unstable*
for undamped oscillatory dynamics — which is exactly what torque-free rotation is. A coning motion
would grow without bound, and this is a property of the method, not of the physics.

**Retained as a verification instrument.** V-NUM-01 measures convergence for both Euler and RK4 and
requires slopes of 1 and 4 respectively. Having a method whose expected slope is *different* is what
makes the test meaningful: if both came out at 4, the test harness is measuring something other than
the integrator.

### 2.2 Classical RK4

$$\mathbf{x}_{n+1} = \mathbf{x}_n + \tfrac{h}{6}\big(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4\big)$$

$$\mathbf{k}_1 = \mathbf{f}(t_n,\mathbf{x}_n),\quad
\mathbf{k}_2 = \mathbf{f}\big(t_n + \tfrac{h}{2},\, \mathbf{x}_n + \tfrac{h}{2}\mathbf{k}_1\big),\quad
\mathbf{k}_3 = \mathbf{f}\big(t_n + \tfrac{h}{2},\, \mathbf{x}_n + \tfrac{h}{2}\mathbf{k}_2\big),\quad
\mathbf{k}_4 = \mathbf{f}\big(t_n + h,\, \mathbf{x}_n + h\mathbf{k}_3\big)$$

Global order 4, four evaluations per step, no history, no step-size controller, no branches.

### 2.3 Embedded adaptive RK5(4) — Dormand–Prince (SRC-009)

Seven stages with FSAL, an embedded 4th-order solution for error estimation, and a step-size
controller.

**Rejected for the initial phase**, on R1 and R2 rather than on accuracy — it is the more accurate
method per unit work, and that is not in dispute.

- **R1.** The accepted step sequence depends on an error estimate computed in floating point and
  compared against a tolerance. A difference in the last bit of one estimate can flip an
  accept/reject decision, after which the two runs take entirely different step sequences and
  diverge. Determinism becomes conditional on floating-point details rather than guaranteed by
  construction.
- **R2.** Measuring order of accuracy requires varying $h$ and observing the error slope. With an
  adaptive controller, $h$ is not an input — the tolerance is, and the map from tolerance to
  effective step size is not a clean power law. The single most informative verification test becomes
  much harder to interpret.
- **R5.** Its main practical advantage — small steps where dynamics are fast — is partly what event
  location provides more directly and more visibly.

**Revisit when** a stiff or multi-scale problem makes fixed steps genuinely uneconomic, or when
long-duration runs make the accuracy-per-cost argument dominant. Recorded in ADR-0006 with this
condition attached, so that the deferral is a decision with an expiry rather than an oversight.

---

## 3. Decision

**Fixed-step classical RK4**, with explicit Euler retained as a verification comparator.

This is the simplest method that meets the requirements. Per `CLAUDE.md`: if RK4 answers the
question, that is the finding — reaching for an adaptive method to look sophisticated would trade the
two highest-priority requirements for accuracy that has not been shown to be needed.

---

## 4. Timestep selection

The step is a **configuration parameter**, never hard-coded, and its value is justified per experiment
rather than inherited.

**Stability bound.** RK4's linear stability region intersects the imaginary axis for
$|\lambda h| \lesssim 2\sqrt{2} \approx 2.828$. For an oscillatory mode of angular frequency
$\omega_n$ this gives $h < 2.828/\omega_n$ — a *necessary* condition only. A step at the stability
limit is stable and grossly inaccurate.

**Accuracy bound.** The binding constraint. A working rule of at least 20 steps per period of the
fastest mode retained:

$$h \le \frac{1}{20 f_{\max}} = \frac{2\pi}{20\,\omega_{\max}}$$

`CALCULATION` (2026-09-09): for a pitch mode at $f = 5$ Hz, stability permits $h < 90$ ms while
accuracy demands $h \le 10$ ms — a factor of nine. The gap is why the stability bound is never used as
the step-selection criterion.

**Proposed default: $h = 10^{-3}$ s**, pending measurement. `HYPOTHESIS`, not a result: the value is
justified only by the timestep-refinement study (V-NUM-02), which measures the error at that step
rather than assuming it. Until that study runs, the default is provisional and must be reported as
such.

**What sets $f_{\max}$** is the fastest mode *retained in the model*, which for the current
formulation is the aerodynamic rotational mode. Actuator dynamics (Phase 12) will be faster and will
reopen this.

---

## 5. Error behaviour

**Global truncation error** for RK4 is $O(h^4)$. This is the claim V-NUM-01 tests, by computing
$\log\lVert e\rVert$ against $\log h$ and fitting a slope.

**The roundoff floor.** Total error behaves roughly as

$$\lVert e(h) \rVert \;\approx\; C h^{4} \;+\; \frac{\kappa\,\varepsilon_{\text{mach}}}{h}$$

Truncation falls as $h$ shrinks; accumulated roundoff *grows*, because the number of steps grows as
$1/h$. There is therefore a minimum-error step, below which refining makes the answer **worse**.

This matters for the test, not only for the physics: a convergence study pushed past that point shows
the measured slope flattening and then reversing, which looks exactly like a broken integrator.
V-NUM-01 must therefore report the full curve and identify the roundoff floor rather than fitting a
slope through all points blindly. `INTERPRETATION`: flattening at the smallest steps is expected
behaviour and is evidence the study went deep enough — not evidence of a bug.

**Error norm.** RS-003 §6 notes the state is not a flat $\mathbb{R}^{14}$. The error norm therefore
treats blocks separately, with the quaternion block contributing the geodesic angle
$\Delta\Theta$ (RS-002 §7) rather than a component-wise difference, and each block reported in its own
units. A single scalar mixing metres, radians and kilograms is not a meaningful quantity and RADIUS
does not compute one.

---

## 6. Events

Physical discontinuities — mass depletion, staging, ground impact — must be **located**, not stepped
over. A fixed-step integrator that steps past ground impact reports a trajectory continuing
underground.

**Mechanism.** Each event is a scalar function $g(t, \mathbf{x})$ with a declared crossing direction.
After each accepted step, sign changes are checked. On a change, the crossing is bracketed and located
by bisection on a dense output within the step, to a configured time tolerance; the step is then
retaken to land exactly on the event, the discontinuous action is applied, and integration restarts.

**Why bisection rather than a smarter root-finder.** Bisection is deterministic, has a guaranteed and
predictable iteration count for a given tolerance, and cannot fail to converge on a bracketed sign
change. Brent's method is faster but its iteration count is data-dependent, which reintroduces the
determinism concern that ruled out adaptive stepping. The cost is negligible — events are rare.

**Restart, do not continue.** After a discontinuous change, integration restarts from the event state.
Carrying stage values across a discontinuity would apply a smooth method across a non-smooth point,
silently destroying the order of accuracy.

**Mass depletion is an event, not a clamp** (RS-003 §5). Clamping $m$ at a floor conserves nothing
while producing plausible output — the worst failure mode available. The event fires, mass flow stops,
and the run continues or terminates per configuration.

---

## 7. Determinism

R1 is met by construction:

- fixed step — no data-dependent control flow;
- fixed evaluation and summation order — no reassociation, no parallel reduction;
- no global RNG; every stochastic component takes a derived seed (`docs/PROVENANCE.md` §4);
- no wall-clock, process-ID or address-dependent behaviour;
- no threading in the integration loop;
- bisection with a fixed iteration bound for events.

**What is claimed:** bitwise-identical output for identical commit, configuration, seed, platform and
library versions. **What is not claimed:** cross-platform bitwise identity — floating-point summation
order, FMA contraction and library differences break it. Cross-platform agreement is claimed within a
stated tolerance only. See `docs/PROVENANCE.md` §5.

---

## 8. Quaternion normalisation

After each **completed** step, never inside a stage. The reasoning, and why in-stage normalisation
silently invalidates the method's order, is in RS-002 §6. Restated here because it is an integrator
implementation detail and this is where an implementer will look.

---

## 9. Verification tests this specification requires

| ID | Test | Passes if |
|---|---|---|
| V-NUM-01 | Order of accuracy: error vs $h$ on V-EOM-02 and V-EOM-04, log-log slope | RK4 slope $4.0 \pm 0.2$; Euler slope $1.0 \pm 0.2$; roundoff floor identified and excluded from the fit |
| V-NUM-02 | Timestep refinement: error at the proposed default $h$ | error below the per-experiment tolerance, stated in advance |
| V-NUM-03 | **Determinism**: identical run repeated, same platform | bitwise-identical output arrays |
| V-NUM-04 | Determinism across process restarts and run order | bitwise identical |
| V-NUM-05 | Event location: analytically known ground-impact time | located within the configured time tolerance |
| V-NUM-06 | Order preserved *across* an event (restart correctness) | slope still $4.0 \pm 0.2$ for a trajectory containing an event |
| V-NUM-07 | Normalisation does not degrade order (RS-002 §6 prediction) | slope unchanged with normalisation on vs off |
| V-NUM-08 | Invariant drift: $\lVert\mathbf{h}\rVert$ and $T$ on V-EOM-05 over a long run | drift consistent with $O(h^4)$, no secular growth beyond it |

V-NUM-03 is load-bearing for the publication policy, not merely a nicety: it is what makes *not*
publishing Monte Carlo ensembles legitimate. If it fails, ADR-0008's argument fails with it.

V-NUM-06 is the one most likely to be skipped and most likely to catch a real defect — event restart
logic is where order of accuracy quietly dies.

---

## 10. Assumptions registered

`A-NUM-01` … `A-NUM-04` — see `docs/assumptions.md`.

---

## 11. Open questions

1. Is $h = 10^{-3}$ s adequate? Unmeasured. It is a proposal, not a result.
2. Does the coupled variable-mass system remain non-stiff across a full burn? If the mass model
   introduces a fast timescale near depletion, the explicit method's step could collapse. Unassessed —
   the stiffness of the coupled system has not been examined and this is a genuine unknown.
3. Does finite-differencing $\dot{\mathbf{J}}$ inside an RK stage (RS-004 §9) introduce a second
   discretisation that degrades the observed order? If V-NUM-01 shows a slope below 4 once the mass
   model is active, this is the first hypothesis to test.
4. Is the block-wise error norm of §5 the right one for a future adaptive controller? It is adequate
   for fixed-step convergence studies; an adaptive method would need a scaled, dimensionless norm.
