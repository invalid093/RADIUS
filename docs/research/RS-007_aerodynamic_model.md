# RS-007 — Aerodynamic Force and Moment Model

**Status:** Specification. Not implemented, not verified.
**Depends on:** RS-001, RS-003, RS-006

---

## 1. Design intent

The aerodynamic model is the part of RADIUS most likely to become a source of unfalsifiable results,
because coefficients can be chosen to produce almost any trajectory and a plausible trajectory is not
evidence of anything.

Two consequences shape the design.

1. **The interface matters more than the model.** RADIUS specifies a clean boundary between the
   dynamics engine and whatever supplies forces, so that the dynamics can be verified against
   analytical cases with aerodynamics switched off entirely, and the aerodynamic model can be swapped
   without touching the equations of motion.
2. **The first model is deliberately simple and transparent** — closed-form coefficients, not tables
   and not high fidelity. A simple model whose every term is inspectable makes the dynamics engine
   testable. A high-fidelity model built before the engine is verified only makes failures harder to
   localise.

---

## 2. Air-relative velocity, $\alpha$ and $\beta$

Aerodynamic forces depend on motion **relative to the air**, not relative to the ground:

$$\mathbf{v}^{I}_{\text{rel}} = \mathbf{v}^{I} - \mathbf{v}^{I}_{\text{wind}}, \qquad
\mathbf{v}^{B}_{\text{rel}} = \mathbf{T}_{BI}(q)\,\mathbf{v}^{I}_{\text{rel}} = (u, v, w)$$

$$V = \lVert\mathbf{v}^{B}_{\text{rel}}\rVert, \qquad
\alpha = \arctan2(w,\,u), \qquad
\beta = \arcsin\!\left(\frac{v}{V}\right)$$

**Sign conventions**, fixed here and tested by V-FRM-05:

- $\alpha > 0$ when the relative wind comes from below the vehicle's $x$–$y$ plane ($w > 0$).
- $\beta > 0$ when the relative wind comes from the vehicle's right ($v > 0$).

`arctan2` is used rather than `arctan(w/u)` so that $\alpha$ is correct through $u < 0$ (rearward
flight, which occurs during tumbling and at apogee of a lofted trajectory). This is not a
defensive-programming nicety: a vehicle that pitches past 90° has $u < 0$, and `arctan` would silently
return an angle in the wrong quadrant.

**Dynamic pressure:**

$$\bar q = \tfrac{1}{2}\rho(h)\,V^{2}$$

Written $\bar q$ / `q_bar` always, never `q` (`NOTATION_AND_CONVENTIONS.md` §5).

---

## 3. Force and moment build-up

### 3.1 Body-axis coefficient form

RADIUS uses **body-axis axial/normal coefficients** as the primary form:

$$\mathbf{F}^{B}_{\text{aero}} = \bar q\,S \begin{bmatrix} -C_A \\ C_Y \\ -C_N \end{bmatrix}$$

$$\mathbf{M}^{B}_{\text{aero,ref}} = \bar q\,S \begin{bmatrix} d\,C_l \\ d\,C_m \\ d\,C_n \end{bmatrix}$$

with $S$ a reference area and $d$ a reference length, both configuration parameters, both stated with
every coefficient set (a coefficient without its reference dimensions is meaningless).

**Why body axes rather than lift/drag.** For a roughly axisymmetric vehicle there is no wing and no
natural "lift" direction; axial and normal force are the physically natural decomposition, and using
them avoids a wind-frame round trip that is degenerate at $V \to 0$. Lift, drag and side force remain
available as *derived reporting* quantities via $\mathbf{T}_{WB}$.

### 3.2 Initial closed-form coefficient model

`ASSUMPTION` `A-AER-01`. Linear in the aerodynamic angles, with rate damping:

$$C_N = C_{N\alpha}\,\alpha, \qquad C_Y = C_{Y\beta}\,\beta, \qquad C_A = C_{A0}$$

$$C_m = C_{m\alpha}\,\alpha + C_{mq}\,\frac{q_{\text{body}}\,d}{2V}, \qquad
C_n = C_{n\beta}\,\beta + C_{nr}\,\frac{r\,d}{2V}, \qquad
C_l = C_{lp}\,\frac{p\,d}{2V}$$

The $d/2V$ factors are the standard non-dimensionalisation of rate derivatives. They are
**singular at $V = 0$** — see §5.

`LIMITATION`: this model is linear, has no Mach dependence, no stall, no nonlinearity at high $\alpha$,
and no coupling between axes beyond what the dynamics provides. It is valid for small $\alpha,\beta$
only. A **validity gate** on $|\alpha|$ and $|\beta|$ is therefore part of the model, not an optional
extra — see §6.

---

## 4. Moment reference point — the transfer that is easy to omit

Aerodynamic coefficients are referenced to a **fixed geometric point** on the vehicle. The equations
of motion require moments about the **instantaneous centre of mass**, which moves as propellant
depletes. The two are not the same point, and the difference grows through the burn.

$$\mathbf{M}^{B}_{\text{aero,cm}} = \mathbf{M}^{B}_{\text{aero,ref}} + \big(\mathbf{r}^{B}_{\text{ref}/\text{cm}}\big) \times \mathbf{F}^{B}_{\text{aero}}$$

`INTERPRETATION`: this term is not a correction, it is a **stability-determining** quantity. The
distance between the centre of pressure and the centre of mass is what sets whether the vehicle is
statically stable, and it changes sign if the CM moves past the CP. Omitting the transfer, or applying
it with the wrong sign, produces a simulation whose stability is qualitatively wrong while every
individual number looks reasonable.

This is registered as `A-AER-04` and tested by V-AER-05. Every function returning a moment states its
reference point in its signature; a moment without one is an error, not a default.

---

## 5. Degeneracies, and how they are handled

Two singularities are structural, not edge cases, and are specified rather than left to the
implementer.

### $V \to 0$

At zero air-relative speed: $\beta$ is undefined ($v/V \to 0/0$), $\alpha$ is undefined, and the rate
derivatives' $d/2V$ factor diverges.

**Handling.** Below a configured threshold $V_{\min}$ (default proposal $10^{-3}$ m·s⁻¹):
aerodynamic force and moment are returned as **exactly zero**, and $\alpha, \beta$ are reported as
`undefined` rather than as 0.

Justification: $\bar q \propto V^2 \to 0$, so the true aerodynamic force does vanish; the singularity
is in the *parameterisation*, not the physics. Returning zero is therefore correct, not a fudge. But
$\alpha$ and $\beta$ genuinely have no value, and reporting them as 0 would be a fabricated number
that later analysis could not distinguish from a real measurement.

`ASSUMPTION` `A-AER-02`: the damping terms' divergence is bounded by the same cutoff. Whether
$V_{\min}$ is well chosen is unmeasured.

### Rearward flight and large $\alpha$

`arctan2` keeps $\alpha$ correct through $u < 0$, but the *coefficient model* of §3.2 is linear and
meaningless there. This is a model-validity failure, not a numerical one, and it is caught by the
validity gate rather than by the angle computation.

---

## 6. Validity gate

Before any aerodynamic result is used, the model checks that the state lies within the region where
its coefficients mean anything:

| Gate | Default | On violation |
|---|---|---|
| $\lvert\alpha\rvert$ | < 10° | **Raise** |
| $\lvert\beta\rvert$ | < 10° | **Raise** |
| Mach | not gated in the initial model — there is no Mach dependence to be valid or invalid | — |
| $V$ | $\ge V_{\min}$ or exactly-zero-force branch | — |

**A gate that cannot be evaluated must raise, never return a pass.** If $\alpha$ is `NaN`, the gate
does not silently succeed. This invariant is inherited deliberately from AURA's engineering practice —
one of the few things worth carrying across, and carried as a principle rather than as code
(ADR-0002).

The gate exists because the alternative is a simulation that runs happily at $\alpha = 60°$ using
linear coefficients and produces a trajectory nobody can defend.

---

## 7. Wind

Wind enters only as $\mathbf{v}^{I}_{\text{wind}}(t, \mathbf{p}^{I})$, supplied by a separate
interface. The default is zero. Gust and turbulence models are deferred; when added they change the
wind interface only, and touch neither the aerodynamic model nor the dynamics.

---

## 8. Provenance of coefficients — an unresolved problem

`LIMITATION`, and the most serious one in this document.

RADIUS has **no traceable source for a coefficient set** (`research/SOURCES.md`, gaps table). Two
options, and the difference is not cosmetic:

1. **Find a published set** for a generic, non-operational configuration in the open literature. Then
   the aerodynamics are traceable, and results can be scoped to "the published configuration X".
2. **Declare the coefficients arbitrary and illustrative.** Then every result is scoped to "a
   hypothetical vehicle with the stated coefficients", and no statement about any real configuration
   is licensed — including statements that sound generic, like "the vehicle is statically stable".

Option 2 is the current state, and it is honest but weak. What is **not** acceptable is choosing
plausible-looking numbers and quietly letting them read as representative. Any coefficient set in
configuration carries a `provenance` field naming its source or stating `arbitrary-illustrative`, and
that field propagates into every result manifest.

Consistent with the scope boundary in `CLAUDE.md`, RADIUS will not use, seek or record operational
vehicle parameters. Option 1 means a *generic academic* configuration or nothing.

---

## 9. Verification tests this specification requires

| ID | Test | Passes if |
|---|---|---|
| V-AER-01 | $(V,\alpha,\beta) \to \mathbf{v}^B \to (V,\alpha,\beta)$ round trip over a grid | $<10^{-12}$ relative |
| V-AER-02 | $\alpha$ correct in all four quadrants including $u<0$ | matches hand-computed values |
| V-AER-03 | Zero-airspeed branch: force and moment exactly zero; $\alpha,\beta$ flagged undefined, not 0 | exact |
| V-AER-04 | Dynamic pressure against hand-computed $\frac{1}{2}\rho V^2$ at known $\rho$ | $<10^{-12}$ |
| V-AER-05 | **Moment transfer**: a pure force at a known offset produces the expected moment about the CM; sign checked by hand | exact |
| V-AER-06 | Static stability sign: with CM ahead of CP, a positive $\alpha$ disturbance produces a restoring (negative) pitching moment | sign correct |
| V-AER-07 | Validity gate raises outside the $\alpha$ / $\beta$ envelope, and raises on `NaN` rather than passing | exception raised in both cases |
| V-AER-08 | Coefficient provenance field present and propagated to the result manifest | field present, non-empty |
| V-AER-09 | Dimensional consistency of force and moment build-up | N and N·m respectively |

V-AER-06 is the test that would catch a sign error in the moment transfer of §4 — the error that
produces a qualitatively wrong but numerically plausible simulation.

V-AER-08 is not a physics test. It is there because an untraceable coefficient set silently
propagating into published results is the specific failure this document is trying to prevent.

---

## 10. Assumptions registered

`A-AER-01` … `A-AER-05` — see `docs/assumptions.md`.

---

## 11. Open questions

1. **Can a published generic coefficient set be found?** Unresolved and blocking the strength of every
   aerodynamic claim. This is the highest-value open item in the specification.
2. Is $V_{\min} = 10^{-3}$ m·s⁻¹ appropriate, and does the model behave continuously across it? A
   discontinuity at the cutoff would inject an impulse into the dynamics.
3. Should the initial model include Mach dependence? Omitting it makes the model invalid transonically
   — which for many trajectories of interest is most of the flight. This may make the linear model
   less useful than it appears, and it should be assessed before results are produced, not after.
4. When tabulated coefficients arrive, what interpolation scheme, and what is its own error
   contribution? Interpolation error is a discretisation error like any other and needs the same
   treatment.
