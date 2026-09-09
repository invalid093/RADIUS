# RS-002 — Attitude Representation

**Status:** Specification. Not implemented, not verified.
**Depends on:** RS-001, `docs/methodology/NOTATION_AND_CONVENTIONS.md`
**Decides:** ADR-0004

---

## 1. The question

Attitude is a point on $SO(3)$, a three-dimensional manifold that **cannot be covered by a single
global chart**. Every three-parameter representation therefore has a singularity somewhere; the only
way to avoid one is to use more parameters than the manifold has dimensions and carry a constraint.

The choice is which cost to pay: a singularity, or a constraint that must be numerically maintained.

Three candidates are evaluated. The conclusion (quaternions) is the conventional one, but the
reasoning below is what licenses it, and one of the arguments turns out to be far stronger for RADIUS
than for a general flight simulator.

---

## 2. Euler angles (3-2-1)

**Parameters:** 3 — $(\phi, \theta, \psi)$. Minimal, no constraint.

**Kinematics:**

$$\begin{bmatrix}\dot\phi\\\dot\theta\\\dot\psi\end{bmatrix} =
\begin{bmatrix}
1 & \sin\phi\tan\theta & \cos\phi\tan\theta\\
0 & \cos\phi & -\sin\phi\\
0 & \sin\phi\sec\theta & \cos\phi\sec\theta
\end{bmatrix}\begin{bmatrix}p\\q\\r\end{bmatrix}$$

**The singularity.** At $\theta = \pm\pi/2$, $\tan\theta$ and $\sec\theta$ diverge. $\phi$ and $\psi$
become indistinguishable — one rotational degree of freedom is lost from the *parameterisation*
(the physical vehicle is unaffected). Near the singularity the equations are not merely inelegant,
they are numerically catastrophic: $\dot\psi \to \infty$ and any fixed-step integrator produces
garbage.

**Why this is decisive for RADIUS specifically.**

For an aircraft, $\theta = \pm 90°$ is an aerobatic edge case that many simulators simply exclude.
For RADIUS it is the **nominal condition**. A vertically launched vehicle sits at pitch $= 90°$ *at
$t = 0$*, and a lofted trajectory passes through steep pitch attitudes as a matter of course.

A 3-2-1 Euler-angle state would therefore be singular at the initial condition of the most obvious
test case RADIUS will run. `INTERPRETATION`: this alone rules Euler angles out as the integrated
state, independent of any other consideration.

*Alternative sequences* (e.g. 3-1-3) move the singularity rather than removing it — there is no
sequence without one, by the topological argument in §1. Choosing a sequence whose singularity lies
outside the expected flight envelope is a real technique, but it makes the representation's validity
a function of the trajectory, which is exactly the kind of hidden precondition RADIUS is trying to
avoid.

**Retained for:** configuration input, reporting, plotting, and human interpretation. Euler angles are
the only representation a person can read, which is not a small thing. They are computed *from* the
attitude state, never integrated.

---

## 3. Direction cosine matrix

**Parameters:** 9, with 6 constraints ($\mathbf{T}^{\mathsf{T}}\mathbf{T} = \mathbf{I}$).

**Kinematics:** $\dot{\mathbf{T}}_{BI} = -[\boldsymbol{\omega}^{B}\times]\,\mathbf{T}_{BI}$ — linear,
no singularity, no trigonometry.

**Against.**

- **Nine states to integrate** for three degrees of freedom, and six constraints to maintain rather
  than one. Orthonormality drift requires periodic re-orthonormalisation (Gram–Schmidt or a
  polar/SVD projection), which is more expensive and less obviously harmless than normalising a
  4-vector.
- **Drift is not benign.** A DCM that loses orthonormality silently stops being a rotation: it starts
  scaling and shearing vectors, so a small numerical error becomes a spurious *physical* effect,
  changing computed force magnitudes. A quaternion whose norm drifts produces a scaled rotation whose
  error is first-order in the norm error and is removed exactly by normalisation.
- More storage and arithmetic per step, for no benefit RADIUS needs.

**Retained for:** the transformation itself. $\mathbf{T}_{BI}$ is computed from the quaternion at each
evaluation, used, and discarded. It is never stored in the state and never integrated.

---

## 4. Quaternion

**Parameters:** 4, with 1 constraint $\lVert q\rVert = 1$.

Convention fixed in `NOTATION_AND_CONVENTIONS.md` §4: **Hamilton product, scalar-first,
$q \equiv q_{BI}$**. This is stated because it differs between communities (SRC-005) and is the single
most common source of silent sign errors in 6-DOF code.

**Kinematics.**

$$\dot q = \tfrac{1}{2}\, q \otimes \big(0,\;\boldsymbol{\omega}^{B}_{B/I}\big)$$

equivalently $\dot q = \tfrac{1}{2}\boldsymbol{\Omega}(\boldsymbol{\omega})\,q$ with

$$\boldsymbol{\Omega}(\boldsymbol{\omega}) =
\begin{bmatrix}
0 & -\omega_x & -\omega_y & -\omega_z\\
\omega_x & 0 & \omega_z & -\omega_y\\
\omega_y & -\omega_z & 0 & \omega_x\\
\omega_z & \omega_y & -\omega_x & 0
\end{bmatrix}
= \begin{bmatrix} 0 & -\boldsymbol{\omega}^{\mathsf{T}} \\ \boldsymbol{\omega} & -[\boldsymbol{\omega}\times]\end{bmatrix}$$

**Independently re-derived and confirmed in the pre-implementation audit (2026-09-09).** The
derivation assumes $\dot q = \frac12 q\otimes\tilde{\boldsymbol\omega}$ and shows it implies
$\dot{\mathbf{v}}^{B} = -\boldsymbol\omega\times\mathbf{v}^{B}$ for a constant inertial vector — the
required behaviour. Numerically confirmed with a **non-principal** axis
$\boldsymbol\omega=(0.37,-0.81,1.23)$ against $\exp(-[\boldsymbol\omega\times]t)$: error
$7\times10^{-13}$, while the reversed product order errs by $3.6\times10^{-1}$. See
`PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md` §2.2.

`CALCULATION` — derived during specification (2026-09-09) by expanding
$\dot q = \frac{1}{2}(-\mathbf{q}_v\!\cdot\!\boldsymbol{\omega},\; q_0\boldsymbol{\omega} - [\boldsymbol{\omega}\times]\mathbf{q}_v)$
and cross-checked on a constant-yaw-rate case. **This derivation is not the authority.** The
authority is test V-ATT-02, which compares propagation against a closed-form solution and would catch
a sign error in any element. A document assertion that "the matrix is right" is worth very little;
the test is what makes it true.

**For.**

- **No singularity anywhere.** Valid at vertical launch and at every attitude thereafter.
- **Bilinear kinematics.** $\dot q$ is linear in $q$ for given $\boldsymbol{\omega}$ and linear in
  $\boldsymbol{\omega}$ for given $q$ — no trigonometric functions in the inner loop, no division,
  no conditional branches. This is not merely fast: branch-free arithmetic is *deterministic*, which
  the reproducibility guarantee (`docs/PROVENANCE.md` §5) depends on.
- **One cheap constraint.** Normalisation is a division by a norm.
- The DCM and Euler angles are both recoverable algebraically.

**Against, honestly.**

- **Double cover.** $q$ and $-q$ are the same attitude. Comparing two attitudes by comparing
  quaternion components naively can report a large error for identical attitudes. RADIUS therefore
  never compares raw components — see §7.
- **Not human-readable.** Mitigated by converting to Euler angles at every output boundary.
- **Convention hazard.** Four conventions are in circulation (Hamilton/JPL × scalar-first/last), all
  written "quaternion". Mitigated by fixing the convention in one document and pinning it with
  hand-computed tests (V-FRM-08, V-ATT-01).

---

## 5. Decision

| Role | Representation |
|---|---|
| **Integrated state** | **Quaternion**, Hamilton, scalar-first, $q_{BI}$ |
| Transformation | DCM, computed from $q$ on demand, never stored or integrated |
| Input / output / reporting | Euler angles 3-2-1, converted at the boundary |

Recorded as ADR-0004. The decisive argument is §2: for a vertically launched vehicle, the Euler
singularity is at the initial condition, not at the edge of the envelope.

---

## 6. Numerical maintenance of the norm

The state lives on $\mathbb{R}^{13}\times S^3$, not $\mathbb{R}^{14}$. An unconstrained integrator
does not know about $S^3$ and will leave it.

**Drift magnitude.** For an explicit RK method of order $p$, the norm error introduced per step is
$O(h^{p+1})$ — the same order as the local truncation error, because the exact flow preserves the
norm and the method's error is what departs from the exact flow. For RK4 with $h = 10^{-3}$ s this is
negligible per step and accumulates slowly, but it accumulates monotonically over long runs and must
be removed.

**Prerequisite: $\mathbf{T}_{BI}$ must be defined off the unit sphere.** Inside an RK stage
$\lVert q\rVert \neq 1$ necessarily. Since $\mathbf{T}_{BI}(kq)=k^2\mathbf{T}_{BI}(q)$, the raw
formula is not a rotation there; RADIUS divides by $q\cdot q$
(`NOTATION_AND_CONVENTIONS.md` §4, `A-NUM-05`, test V-FRM-09). This was missing from the original
specification — audit finding F-3.

**Method chosen: explicit renormalisation after each completed step.**

$$q \leftarrow \frac{q}{\lVert q \rVert}$$

**Placement matters, and this is the subtle part.** Normalisation is applied **after the step is
complete**, never inside the RK stages. Normalising within a stage would make the stage function
differ from the $f$ that the Butcher tableau's order conditions were derived for, silently
invalidating the method's order. This is a real and easy mistake, and it is exactly the kind that
produces a plausible trajectory with the wrong convergence rate — which V-NUM-01 would then catch as
an order-of-accuracy failure with a confusing cause. Stated here so it is not made.

**Does post-step normalisation degrade the order?** No. The projection moves the solution by an
amount of the same size as the norm error, $O(h^{p+1})$ per step — the same order as the local
truncation error already being committed. Accumulated over $O(1/h)$ steps, this contributes
$O(h^{p})$ to the global error, leaving the method's global order unchanged.
`CALCULATION`/`HYPOTHESIS`: this is a standard argument and RADIUS treats it as a **prediction to be
tested**, not a fact. V-NUM-01 measures the observed order with normalisation enabled; if the
measured slope is not 4, this argument is wrong and the finding is reported.

**Alternative considered: Baumgarte-style constraint stabilisation**, adding
$\lambda(1 - \lVert q\rVert^2)\,q$ to $\dot q$. Rejected for the initial implementation: it
introduces a tuning parameter $\lambda$ with no principled value, it makes the ODE stiffer as
$\lambda$ grows, and it solves a problem that a division already solves exactly. It is the right tool
when the constraint cannot be projected onto cheaply; here it can.

---

## 7. Comparing and reporting attitude

**Never compare quaternion components directly.** Because of double cover, $q$ and $-q$ are the same
attitude with maximal component-wise difference.

The attitude error between a computed $q$ and a reference $q_{\text{ref}}$ is the **geodesic angle**:

$$q_{\text{err}} = q_{\text{ref}}^{-1} \otimes q, \qquad
\Delta\Theta = 2\arccos\!\big(\min(1,\,|q_{\text{err},0}|)\big)$$

The absolute value handles double cover; the $\min(1,\cdot)$ guards $\arccos$ against a
floating-point argument marginally above 1, which happens routinely and produces a `NaN` if
unguarded. $\Delta\Theta \in [0,\pi]$ is a metric on $SO(3)$, in radians, and is the quantity plotted
in every attitude convergence study.

**Canonicalisation** to $q_0 \ge 0$ is applied at output and comparison boundaries only — never
during integration, where forcing the sign would introduce a discontinuity into a continuous state
and corrupt the very convergence studies the representation was chosen to enable.

**Euler extraction** uses `atan2` for $\phi$ and $\psi$, and $\arcsin$ with clamping for $\theta$.
Near $|\theta| = \pi/2$ the extracted $\phi$ and $\psi$ are ill-conditioned — this is the Euler
singularity reappearing at the *output* boundary. It is harmless (the state is unaffected) but the
reporting layer must flag it rather than print two meaningless numbers.

---

## 8. Verification tests this specification requires

| ID | Test | Passes if |
|---|---|---|
| V-ATT-01 | Hand-computed conversions: 90° yaw, 90° pitch, 90° roll quaternions produce the expected DCMs, hard-coded | $<10^{-15}$ |
| V-ATT-02 | Constant body rate $\boldsymbol{\omega} = (0,0,\omega)$ from identity: propagated $q(t)$ matches the closed-form $(\cos\frac{\omega t}{2},0,0,\sin\frac{\omega t}{2})$ | $\Delta\Theta < 10^{-9}$ rad over 10 s |
| **V-ATT-02b** | **Non-principal axis, mandatory.** The same check with $\boldsymbol{\omega}$ not aligned to a body axis, against $\exp(-[\boldsymbol{\omega}\times]t)$ | $\Delta\Theta<10^{-9}$ rad. **Must fail by $>10^{-3}$ under the reversed product order** |
| V-ATT-03 | Same, about each of the three body axes independently, and about a non-principal axis $(1,1,1)/\sqrt{3}$ | as above |
| V-ATT-04 | Norm preservation: $\big\lvert\lVert q\rVert - 1\big\rvert$ bounded over a long run with normalisation on | $<10^{-12}$ throughout |
| V-ATT-05 | Norm *drift* with normalisation **off** scales as $O(h^{p+1})$ per step | measured exponent within 0.2 of 5 |
| V-ATT-06 | Double cover: $q$ and $-q$ give identical DCMs, and $\Delta\Theta(q,-q) = 0$ | exact / $<10^{-12}$ |
| V-ATT-07 | Euler round trip over a grid excluding $\lvert\theta\rvert > 89°$; and correct flagging inside the excluded band | $<10^{-10}$ rad; flag raised |
| V-ATT-08 | $\arccos$ guard: $\Delta\Theta$ returns 0, not `NaN`, for identical quaternions | no `NaN` |

**V-ATT-02b is not optional and not redundant with V-ATT-02.** For a constant-axis rotation, $q$ and
$\tilde{\boldsymbol\omega}$ commute, so a principal-axis test **cannot distinguish**
$q\otimes\tilde{\boldsymbol\omega}$ from $\tilde{\boldsymbol\omega}\otimes q$ — the two most likely
competing conventions. The audit needed a non-principal axis to separate them, and it separated them
by twelve orders of magnitude. A test that cannot fail under the wrong convention is not testing the
convention.

V-ATT-05 is unusual and worth keeping: it verifies that the *unmaintained* system misbehaves in the
predicted way. A test suite that only checks the corrected system cannot distinguish "normalisation
works" from "there was never any drift to correct", and the second would indicate the integrator is
not doing what is believed.

---

## 9. Assumptions registered

`A-ATT-01`, `A-ATT-02` — see `docs/assumptions.md`.

---

## 10. Open questions

1. Does post-step normalisation preserve the observed fourth-order convergence in practice? §6 argues
   yes. Unmeasured until V-NUM-01 runs. If it does not, the integrator study (RS-005) reopens.
2. For very long propagations at high rates, does normalisation alone bound the *orientation* error,
   or only the norm? These are different: a quaternion can have unit norm and still have accumulated
   rotational error. Only the second is checked by V-ATT-04; the first needs V-ATT-02 run long.
3. If a future phase adds an attitude estimator, the three-parameter local error representation
   (e.g. modified Rodrigues parameters or a rotation-vector error state) will need its own decision.
   Out of scope here — noted so it is not assumed to be settled by this document.
