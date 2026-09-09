# Pre-Implementation Mathematical Audit

**Date:** 2026-09-09 · **Scope:** RS-001 … RS-008, `NOTATION_AND_CONVENTIONS.md`, ADR-0003…0006,
`assumptions.md` · **Audited at commit:** `5b831ed`

An independent review of the RADIUS mathematical specification, treating it as a *candidate* rather
than as settled because it passed an earlier gate. Numerical checks were run as audit artifacts; no
implementation was written and no module was created.

---

## Executive Verdict

# PASS WITH REQUIRED CORRECTIONS

Four defects were found. **One is load-bearing and changes a governing equation**; three are
specification gaps that would each have produced a plausible-looking wrong implementation. All four
have determinate fixes, applied in this commit.

The core formulation — frame conventions, quaternion kinematics, translational dynamics, the
gyroscopic term, and the atmosphere model — **survives the audit and is verified correct** by
independent derivation and numerical check.

| # | Finding | Severity | Status |
|---|---|---|---|
| **F-1** | The rotational equation's $-\dot{\mathbf{J}}\boldsymbol{\omega}$ term is **wrong for mass ejection**. It models internal redistribution, not depletion | **Load-bearing — wrong physics** | Corrected |
| **F-2** | $\mathbf{T}_{BW} = \mathbf{R}_y(-\alpha)\mathbf{R}_z(\beta)$ is **sign-inconsistent** with RADIUS's own definitions of $\alpha$ and $\beta$ | **Load-bearing — sign error** | Corrected |
| **F-3** | $\mathbf{T}_{BI}(q)$ is **undefined for the non-unit quaternions that necessarily arise inside RK stages** | **Load-bearing — spec gap** | Corrected |
| **F-4** | Quaternion composition order is **the reverse of** matrix composition order, and this was nowhere stated | Load-bearing — convention trap | Corrected |
| F-5 | `arctan` vs `arctan2` for $\alpha$: RS-001 and RS-007 disagree | Minor inconsistency | Corrected |
| F-6 | Lapse rates tabulated in K·km⁻¹ but used in a formula requiring K·m⁻¹ | Minor — unit trap | Corrected |
| F-7 | Inverse-square scaling applied to a $g$ that already contains a centrifugal part which does **not** scale that way | Minor — quantified as negligible | Recorded |

Phase 2 (`radius/math/`, `radius/frames/`) may begin **once the corrections in this commit are in
place**, which they now are. F-1 affects Phase 4/9, not Phase 2.

---

## 1. Frames and transformations — **VERIFIED**

**Current formulation.** Right-handed NED inertial frame ($z$ down), body frame at the instantaneous
CM, passive transformations with subscripts reading "to ← from", Euler 3-2-1 with elementary matrices
written out.

**Audit result: correct and internally consistent.** Numerical checks (audit artifact, 2026-09-09):

| Check | Result |
|---|---|
| $\mathbf{R}_x,\mathbf{R}_y,\mathbf{R}_z$ at 90° orthonormal, $\det=+1$ | pass |
| Yaw 90° ⟹ $x_B$ = East; pitch 90° ⟹ $x_B$ = Up ($-z_I$); roll 90° ⟹ $y_B$ = Down | pass |
| **V-FRM-08 as written in RS-001 §6**: 90° yaw maps $\hat{x}_I \to -\hat{y}_B$ | **pass** — the hand-computed value in the specification is correct |
| Identity, inverse ($\mathbf{T}^{-1}=\mathbf{T}^{\mathsf{T}}$), composition by adjacency | pass |

The hand-computed expected value in V-FRM-08 was checked independently and is right. This matters
because it is the one test class capable of catching a uniformly applied wrong convention.

**No correction required.** The conventions are retained; they are mathematically sound, and per the
audit brief they are not changed merely because another convention is more common.

---

## 2. Quaternion formulation — **VERIFIED** (with two gaps, F-3 and F-4)

**Current formulation.** Hamilton product, scalar-first, $q \equiv q_{BI}$,
$\mathbf{T}_{BI}(q) = (q_0^2-\mathbf{q}_v\!\cdot\!\mathbf{q}_v)\mathbf{I} + 2\mathbf{q}_v\mathbf{q}_v^{\mathsf{T}} - 2q_0[\mathbf{q}_v\times]$,
and $\dot q = \tfrac12\boldsymbol{\Omega}(\boldsymbol\omega)q$.

### 2.1 What $q_{BI}$ means, established rather than assumed

RADIUS's $\mathbf{T}_{BI}(q)$ is the **transpose** of the conventional Hamilton *active* rotation
matrix $\mathbf{R}(q) = (q_0^2-|\mathbf{q}_v|^2)\mathbf{I} + 2\mathbf{q}_v\mathbf{q}_v^{\mathsf{T}} + 2q_0[\mathbf{q}_v\times]$
(note the sign of the last term). Therefore

$$\mathbf{v}^{B} = \mathbf{T}_{BI}(q)\,\mathbf{v}^{I} \quad\Longleftrightarrow\quad \tilde{\mathbf{v}}^{B} = q^{*} \otimes \tilde{\mathbf{v}}^{I} \otimes q$$

This — *not* $q \otimes \mathbf{v} \otimes q^{*}$ — is the rotation operator RADIUS's matrix
corresponds to. It was not previously stated and is now recorded in `NOTATION_AND_CONVENTIONS.md`.

**Evidence:** $\mathbf{T}_{BI}(q)$ was compared against $\mathbf{T}_{BI}(\phi,\theta,\psi)$ built from
the 3-2-1 elementary matrices, over **2000 random attitudes**: maximum element error
$5.55\times10^{-16}$. The quaternion-to-DCM formula and the Euler-to-quaternion formula are mutually
consistent to machine precision.

### 2.2 Derivation of $\dot q$ — independent, and not degenerate

The specification's own cross-check (constant rate about a principal axis) is **insufficient**: for a
constant-axis rotation $q$ and $\tilde{\boldsymbol\omega}$ commute, so that check cannot distinguish
$q\otimes\tilde{\boldsymbol\omega}$ from $\tilde{\boldsymbol\omega}\otimes q$. A proper derivation:

Assume $\dot q = \tfrac12 q \otimes \tilde{\boldsymbol\omega}$, with $\tilde{\boldsymbol\omega}$ pure
so $\tilde{\boldsymbol\omega}^{*}=-\tilde{\boldsymbol\omega}$. For a **constant inertial** vector,
$\tilde{\mathbf{v}}^{B} = q^{*}\otimes\tilde{\mathbf{v}}^{I}\otimes q$, so

$$\dot{\tilde{\mathbf{v}}}^{B} = \dot q^{*}\otimes\tilde{\mathbf{v}}^{I}\otimes q + q^{*}\otimes\tilde{\mathbf{v}}^{I}\otimes\dot q
= \tfrac12\big(\tilde{\mathbf{v}}^{B}\otimes\tilde{\boldsymbol\omega} - \tilde{\boldsymbol\omega}\otimes\tilde{\mathbf{v}}^{B}\big)$$

For pure quaternions $a\otimes b - b\otimes a = (0,\,2\,\mathbf{a}\times\mathbf{b})$, giving

$$\dot{\mathbf{v}}^{B} = \mathbf{v}^{B}\times\boldsymbol\omega = -\,\boldsymbol\omega\times\mathbf{v}^{B}$$

which is exactly the required behaviour of a fixed inertial vector seen in a rotating frame. **The
stated equation is correct for RADIUS's exact convention.**

Expanding gives $\boldsymbol{\Omega}(\boldsymbol\omega) = \begin{bmatrix}0 & -\boldsymbol\omega^{\mathsf{T}}\\ \boldsymbol\omega & -[\boldsymbol\omega\times]\end{bmatrix}$,
matching the written-out matrix in RS-002 §4 element for element.

**Numerical confirmation with a deliberately non-principal axis**
$\boldsymbol\omega = (0.37,-0.81,1.23)$ rad·s⁻¹, propagated 1.7 s and compared against
$\mathbf{T}(t) = \exp(-[\boldsymbol\omega\times]t)\,\mathbf{T}(0)$:

- as specified, $\dot q = \tfrac12 q\otimes\tilde{\boldsymbol\omega}$ — max error $7.25\times10^{-13}$ ✓
- reversed order, $\tfrac12\tilde{\boldsymbol\omega}\otimes q$ — max error $3.6\times10^{-1}$ ✗

The reversed convention is **distinguishable by a factor of $10^{12}$**, confirming the test is not
degenerate.

### 2.3 Norm preservation — analytic

$\boldsymbol{\Omega}$ is skew-symmetric, so $\frac{d}{dt}\lVert q\rVert^2 = q^{\mathsf{T}}\boldsymbol{\Omega}q = 0$
**exactly**. All norm drift is therefore integrator truncation error, not a property of the
kinematics — which validates the RS-002 §6 reasoning and makes V-ATT-05 (drift with normalisation
off) a meaningful test of the *integrator*.

### 2.4 F-3 — $\mathbf{T}_{BI}(q)$ at non-unit quaternions **[LOAD-BEARING GAP]**

RK4 evaluates the derivative at $\mathbf{x}_n + \tfrac{h}{2}\mathbf{k}_1$, where the quaternion block
is **necessarily not of unit norm**. The specification said normalisation happens after a completed
step — but never said what $\mathbf{T}_{BI}$ does in the meantime, which is a question every stage
evaluation asks.

**Verified:** $\mathbf{T}_{BI}(kq) = k^{2}\,\mathbf{T}_{BI}(q)$. For $k=1.037$ the raw matrix has
$\lVert \mathbf{T}^{\mathsf{T}}\mathbf{T}-\mathbf{I}\rVert_\infty = 0.156$ — not a rotation. Using it
raw would scale every aerodynamic and propulsive force by $\lVert q\rVert^2$ inside stages 2–4.

**Correction (exact, branch-free, no in-stage normalisation):**

$$\mathbf{T}_{BI}(q) = \frac{(q_0^2-\mathbf{q}_v\!\cdot\!\mathbf{q}_v)\mathbf{I} + 2\mathbf{q}_v\mathbf{q}_v^{\mathsf{T}} - 2q_0[\mathbf{q}_v\times]}{q\cdot q}$$

Verified orthonormal for non-unit $q$. Because it is a division rather than a normalisation, it does
**not** alter the stage function in a way that breaks the Butcher tableau's order conditions — it
evaluates the *same* smooth $f$ that the order conditions assume.

### 2.5 F-4 — quaternion composition order **[CONVENTION TRAP]**

`NOTATION_AND_CONVENTIONS.md` §4 states matrices compose by adjacency,
$\mathbf{T}_{CA}=\mathbf{T}_{CB}\mathbf{T}_{BA}$. **Verified numerically:** for RADIUS's convention,
quaternions compose in the *opposite* order:

$$\mathbf{T}(q_a\otimes q_b) = \mathbf{T}(q_b)\,\mathbf{T}(q_a) \qquad\text{(NOT } \mathbf{T}(q_a)\mathbf{T}(q_b))$$

An implementer would reasonably assume the orders match. This is precisely the class of silent error
the notation document exists to prevent, and it was missing from it. Now stated, with test V-FRM-10.

### 2.6 Does post-step normalisation alter formal convergence order?

**Answered, and the answer is: no, but it is a prediction, not a proof.** Since the exact flow
preserves the norm (§2.3), the norm error after one RK4 step is the same order as the local truncation
error, $O(h^{5})$. Projection moves the solution by that amount; accumulated over $O(1/h)$ steps this
contributes $O(h^{4})$ — the existing global order. The argument is standard and RADIUS treats it as
`HYPOTHESIS` tested by V-NUM-07. **The audit does not upgrade it to a fact.**

---

## 3. State representation — **VERIFIED, one clarification**

$\mathbf{x}=[\mathbf{p}^{I},\mathbf{v}^{I},q_{BI},\boldsymbol\omega^{B},m]$ on
$\mathbb{R}^{13}\times S^{3}$. Dimensionally consistent; sufficient under its stated assumptions.

**Clarification recorded:** $\mathbf{p}^{I}$ tracks the **instantaneous centre of mass**, which is a
*material-changing point* during a burn. The trajectory RADIUS computes is the CM trajectory; relating
it to a fixed structural point requires $\mathbf{r}_{\text{ref}/\text{cm}}(t)$ from the mass model.
This is correct but was implicit, and is now explicit in RS-003.

No additional states are required. The audit specifically declines to add CM-velocity or
inertia states: under `A-VM-02` (quasi-static CM) they are not needed, and adding them would
introduce states the mass model already determines algebraically.

---

## 4. Translational dynamics — **VERIFIED**

$$\dot{\mathbf{p}}^{I}=\mathbf{v}^{I},\qquad m\dot{\mathbf{v}}^{I}=\mathbf{T}_{IB}\big[\mathbf{F}^{B}_{\text{aero}}+\mathbf{F}^{B}_{\text{prop}}\big]+m\,g(h)\,\hat{z}_I$$

**Dimensional analysis:** every term N; every term of $\dot{\mathbf{v}}$ m·s⁻². Pass.

**Frame audit.** Aerodynamic and propulsive forces are genuinely body-frame quantities (they depend on
$\alpha,\beta$ and on the vehicle's geometry) and are transformed once by $\mathbf{T}_{IB}$. Gravity
is naturally inertial and is added *after* transformation — correct, and specifically **not**
transformed into the body frame and back, which would be a redundant round trip. Transformation
direction is correct: $\mathbf{T}_{IB}=\mathbf{T}_{BI}^{\mathsf{T}}$ maps body components to inertial.

**Limiting cases** (audit artifact):

| Case | Prediction | Correct? |
|---|---|---|
| **A** no aero, no thrust, $\boldsymbol\omega=0$ | free fall; attitude frozen | ✓ |
| **B** 500 N along $x_B$, identity attitude, $m=100$ | $\mathbf{a}=(5,0,g_0)$ m·s⁻² | ✓ |
| **C** gravity only, 3 s from rest | $+44.1299$ m in $+z$ (**downward** — sign correct for NED) | ✓ |
| **D** constant body force, yawing at $r=0.5$ rad·s⁻¹ | numerically $(9.092974, 14.161468)$ vs closed form $\frac{F}{mr}(\sin rT, 1-\cos rT)=(9.092974, 14.161468)$ | ✓ |

Case D is the discriminating one: it exercises the force transformation *while the attitude changes*,
which is where a transposed $\mathbf{T}$ would show up. It agrees with the closed form to 6 decimals.

**The variable-mass translational form is correct**: $m\dot{\mathbf{v}}=\mathbf{F}$ with
$\mathbf{F}_{\text{prop}}=\dot m\,\mathbf{c}$ included as an explicit momentum-flux term, and **no**
$\dot m\mathbf{v}$ term. RS-004 §3.1's rejection of $\frac{d}{dt}(m\mathbf{v})=\mathbf{F}$ is right.

---

## 5. Rotational dynamics and variable mass — **F-1: INCORRECT AS WRITTEN**

This is the finding that justifies the audit.

### 5.1 Current formulation

$$\dot{\boldsymbol\omega} = \mathbf{J}^{-1}\Big[\mathbf{M}-\boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega)-\dot{\mathbf{J}}\boldsymbol\omega+\mathbf{M}_{\text{jet}}\Big]$$

with $-\dot{\mathbf{J}}\boldsymbol\omega$ **implemented** and $\mathbf{M}_{\text{jet}}$ **omitted**.

### 5.2 Audit result: **D — incorrect**, not merely incomplete

$-\dot{\mathbf{J}}\boldsymbol\omega$ and $\mathbf{M}_{\text{jet}}$ arise from **one physical process**
— mass leaving the vehicle. Implementing one and omitting the other is not a conservative
approximation of the full equation. It is a different, and unphysical, model.

**Derivation.** Let mass leave co-rotating, with negligible velocity relative to the structure at its
own location. The angular momentum it carries out per unit time, about the CM, is
$\int \mathbf{r}\times(\boldsymbol\omega\times\mathbf{r})\,d\dot m = -\dot{\mathbf{J}}\boldsymbol\omega$.
Then

$$\underbrace{\dot{\mathbf{J}}\boldsymbol\omega+\mathbf{J}\dot{\boldsymbol\omega}+\boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega)}_{d\mathbf{h}/dt|_I} = \mathbf{M}_{\text{ext}} + \underbrace{\dot{\mathbf{J}}\boldsymbol\omega}_{\text{flux in/out}}$$

**The $\dot{\mathbf{J}}\boldsymbol\omega$ terms cancel exactly**, leaving

$$\boxed{\;\mathbf{J}(t)\,\dot{\boldsymbol\omega}+\boldsymbol\omega\times\big(\mathbf{J}(t)\boldsymbol\omega\big)=\mathbf{M}_{\text{ext}}\;}$$

**Numerical demonstration** (audit artifact). Torque-free axisymmetric body spinning at
$\omega_z = 10$ rad·s⁻¹ about its symmetry axis, depleting uniformly from 1000 kg to 500 kg over 20 s,
inertia proportional to mass, no external moment:

| | $\omega_z(T)$ |
|---|---|
| Truth (ejected mass carries its own angular momentum) | **10.000** rad·s⁻¹ |
| **RADIUS equation as written** | **20.000** rad·s⁻¹ |

**A factor-of-two spurious spin-up.** The $-\dot{\mathbf{J}}\boldsymbol\omega$ term forces conservation
of $\mathbf{h}=\mathbf{J}\boldsymbol\omega$, which is the physics of *a skater pulling their arms in* —
internal redistribution — not of mass ejection. Every material element retains its own angular
velocity when it leaves; the remaining body keeps spinning at the same rate with less angular
momentum.

**This is the exact rotational analogue of the error RS-004 §3.1 identifies and rejects for
translation.** The specification argues carefully that treating departing mass as vanishing is wrong
for linear momentum, and then commits that error for angular momentum three sections later. The
internal inconsistency is what makes this finding decisive rather than a matter of taste.

`OBSERVATION`: the error is not small and would not have been caught by the specified tests.
V-VM-01 (Tsiolkovsky) checks only translation. V-EOM-05 checks conservation at **constant** mass. No
specified test exercised rotation with $\dot m \neq 0$. A new test is required — see §11.

### 5.3 Correction adopted

Adopt the boxed equation as the baseline, i.e. **remove $-\dot{\mathbf{J}}\boldsymbol\omega$**, under
a new explicit assumption:

> `A-VM-05` — ejected mass leaves co-rotating, with negligible velocity relative to the structure at
> its exit location. Under this assumption the angular-momentum flux exactly cancels
> $\dot{\mathbf{J}}\boldsymbol\omega$.

This is **simpler and more correct** — the audit brief's stated preference. It also cleanly separates
the remaining physics: with $u_{\text{exit}} \neq 0$ at a point offset from the CM, the exhaust carries
away transverse momentum and produces the genuine **jet damping** moment. That is now a properly
separate, still-omitted term rather than half of an entangled pair.

**$\mathbf{M}_{\text{jet}}$ was a placeholder** — an undefined symbol appearing in a boxed governing
equation. It is now either defined or absent, never both.

**Internal redistribution** (moving internal mass, $\dot{\mathbf{J}}\neq0$ with $\dot m=0$) is the case
where $-\dot{\mathbf{J}}\boldsymbol\omega$ *is* correct. RADIUS does not model it; if it ever does, the
term returns — with its own derivation.

### 5.4 Rotational dynamics otherwise — verified

Constant-mass torque-free integration of an asymmetric body ($\mathbf{J}=\text{diag}(120,300,260)$):
$\lVert\mathbf{h}\rVert$ drift $5.4\times10^{-16}$, kinetic energy drift $1.7\times10^{-14}$ over 8 s.
The gyroscopic term $-\boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega)$ is correct and
conservative. **Only the $\dot{\mathbf{J}}$ term was at fault.**

---

## 6. Centre of mass and inertia — **CONDITIONAL, assumptions made explicit**

| Question | Answer |
|---|---|
| Is the CM fixed relative to the body frame? | **No.** The body frame's *origin* is the instantaneous CM, so the CM is at the origin by definition — but it moves relative to the **structure** |
| Where is CM motion represented? | Algebraically, as $\mathbf{r}_{\text{ref}/\text{cm}}(t)$ from the mass model. Not a state |
| Does $\mathbf{p}^{I}$ represent the instantaneous CM? | **Yes** — and it is therefore a material-changing point during a burn. Now stated explicitly |
| Does mass loss move the CM? | Yes; this feeds the aerodynamic moment transfer and is stability-determining |
| Is $\mathbf{J}$ constant? | **No.** $\mathbf{J}(t)$ from the mass model |
| What causes $\mathbf{J}$ to vary? | Mass depletion only. Not redistribution — see `A-VM-05` |
| Is $\dot{\mathbf{J}}$ known from the state? | **No longer needed in the equations of motion** after F-1's correction. It remains a diagnostic |
| Inertia: algebraic function of mass, or a model? | An **inertia model** supplied by `MassProperties`, taking $(t, m)$. Making $\mathbf{J}$ a pure function of scalar mass would assume self-similar depletion, which is an unnecessary restriction |

**Consequence of F-1 worth noting:** removing $-\dot{\mathbf{J}}\boldsymbol\omega$ also removes the
open question in RS-008 §4 about whether a finite-difference $\dot{\mathbf{J}}$ inside an RK stage
would degrade the convergence order. That risk **disappears** with the term. A correction that
removes both an error and a hazard is a good sign it was the right correction.

---

## 7. Gravity — **VERIFIED, with F-7 recorded**

- Constant $g$ is a deliberate verification switch, not the default. Correct.
- $g(h)=g_0(R_E/(R_E+h))^2$ with direction fixed along $+\hat{z}_I$. **Consistent with the flat-Earth
  frame**: a field $g(z)\hat{z}$ is conservative, so this is a legitimate approximation, not an
  inconsistency. It is *not* a central inverse-square field — only the magnitude varies — and RS-001
  now says so.
- **Sign verified** by Case C: free fall accumulates $+z$ displacement. Correct for NED.

**`gravity(position)` rather than `gravity(altitude)` — independently evaluated and RETAINED.** Under
flat Earth only $h$ is used, so the wider signature buys nothing today. It is still correct: under
ECEF both the magnitude *and the direction* of gravity depend on full position, so the narrower
signature would have to change at every call site — including inside the dynamics core, the one module
the architecture most wants to leave untouched. The cost is one unused argument.

**F-7 (minor).** `A-FRM-02` absorbs the centrifugal contribution into measured $g$, then $g(h)$
scales the whole thing as inverse-square. The centrifugal part actually scales as $(R_E+h)$, i.e. it
*increases* with altitude. `CALCULATION`: at 30 km the mis-scaling is $\approx5\times10^{-4}$ m·s⁻²
($5\times10^{-5}$ of $g$), about 0.9 m of position error over 60 s of free fall — **three orders of
magnitude below the already-accepted Coriolis error** of ~730 m. Recorded in `assumptions.md`, not
corrected: fixing it would require splitting $g$ into gravitational and centrifugal parts, which is
work that belongs with the ECEF extension.

---

## 8. Atmosphere — **VERIFIED, F-6 corrected**

Numerical checks against the defining document's published values:

| Check | Result |
|---|---|
| Sea-level density $\rho=pM_0/(R^{*}T)$ | 1.22500 kg·m⁻³ ✓ |
| Sea-level speed of sound | 340.294 m·s⁻¹ ✓ |
| Pressure at 11 km geopotential | **22632.1 Pa** vs published 22632 ✓ |
| Temperature at 11 km | 216.65 K ✓ |
| Exponent $g_0M_0/(R^{*}L_b)$ dimensionless, troposphere | $-5.2559$ ✓ |
| Exponent sign behaviour for $L<0$ and $L>0$ | both give decreasing $p$ ✓ |

The layered formulation, constants and the recursive base-pressure scheme are correct.

**F-6.** The layer table lists $L_b$ in **K·km⁻¹** while the barometric formula requires **K·m⁻¹**. A
factor of 1000 in an exponent produces $p$ wrong by many orders of magnitude — loud rather than
subtle, but trivially avoidable. The table now carries both, and the unit conversion is explicit.

**Interface adequacy for the future aerodynamic model.** The atmosphere returns
$(\rho, p, T, a)$. **Dynamic viscosity $\mu$ is absent.** Not needed by the current model (constant
$C_A$, no Reynolds dependence), but any future coefficient set with Reynolds-number dependence would
require it. Recorded as a gap; the return is a structure, so adding $\mu$ (Sutherland's law, which is
in the same defining document) is non-breaking. **Not added now** — the audit brief says not to expand
the atmosphere model unnecessarily, and an unused quantity is one more thing to verify.

---

## 9. Aerodynamic interface — **VERIFIED (F-2, F-5 corrected). Q8 gate remains closed.**

### 9.1 F-2 — wind-frame sign error **[LOAD-BEARING]**

RS-001 §2.3 stated $\mathbf{T}_{BW}=\mathbf{R}_y(-\alpha)\mathbf{R}_z(\beta)$. RADIUS's own
definitions $\alpha=\arctan2(w,u)$, $\beta=\arcsin(v/V)$ force

$$\mathbf{v}^{B}=V\big(\cos\alpha\cos\beta,\;\sin\beta,\;\sin\alpha\cos\beta\big)$$

**Worked counter-example** ($\alpha=0$, $\beta=+30°$, $V=100$ m·s⁻¹):

| | $\mathbf{v}^{B}$ |
|---|---|
| Required by RADIUS's $\alpha,\beta$ definitions | $(86.603,\;+50.000,\;0)$ |
| RS-001 formula as written | $(86.603,\;\mathbf{-50.000},\;0)$ |
| **Correct** $\mathbf{T}_{BW}=\mathbf{R}_y(\alpha)\mathbf{R}_z(-\beta)$ | $(86.603,\;+50.000,\;0)$ |

The published formula produces $\beta = -30°$ where $+30°$ was specified — **the sideslip and
angle-of-attack senses were both inverted.** Checked over 500 random $(V,\alpha,\beta)$: the corrected
form is exact to $0.0$; the original is wrong by up to 1.8 $\times$ the speed.

**Consequence had it been implemented:** every sideslip-dependent side force and yawing moment would
have had the wrong sign — turning a statically stable vehicle into a divergent one, or vice versa,
while every individual number looked reasonable.

**V-FRM-05 would have caught it**, because the round-trip test builds $\mathbf{v}^B$ from
$\mathbf{T}_{BW}$ and recovers $\alpha,\beta$ from the independent `arctan2`/`arcsin` definitions. The
test design was sound; the documented formula was not. That is a point in favour of specifying tests
before code — but it does not excuse publishing a wrong equation, since an implementer may well write
the formula and the test to agree with each other.

### 9.2 F-5 — `arctan` vs `arctan2`

RS-001 §2.3 wrote $\alpha=\arctan(w/u)$; RS-007 §2 wrote $\arctan2(w,u)$ and explained why
(correctness through $u<0$, which occurs in tumbling and near apogee). RS-001 is now aligned.

### 9.3 Interface separation — verified

The interface cleanly separates environment state ($\rho,p,T,a$) · vehicle state · derived
$\alpha,\beta,\bar q$, Mach · coefficients · reference area $S$, length $d$, and **reference point**
with explicit transfer to the CM · forces · moments.

**Can a future traceable coefficient model be substituted without changing the dynamics kernel?**
**Yes** — verified structurally: the dynamics core consumes only $\mathbf{F}^{B}$ and
$\mathbf{M}^{B}_{\text{cm}}$ and has no knowledge of coefficients, Mach, or tables. Substituting a
tabulated Mach- and Reynolds-dependent model changes `radius/aerodynamics/` alone.

**Q8 gate remains NOT PASS.** No coefficient data was invented, and the missing traceable coefficient
source stands as the open limitation.

---

## 10. Numerical integration — **VERIFIED, methodology added**

- **State derivative compatible with RK4:** yes — $f(t,\mathbf{x})$ pure, no hidden state. ✓
- **Quaternion handling compatible:** yes, **once F-3 is fixed.** Before the fix it was undefined.
- **Mass evolution compatible:** yes; $\dot m$ is a smooth function of $(t,\mathbf{x})$ between events.
- **Events do not silently destroy order:** the specified restart-at-event scheme is correct, and
  V-NUM-06 tests it. Retained.
- **Normalisation does not invalidate the convergence test:** correct, and V-NUM-07 tests it rather
  than assuming it (§2.6).
- **Fixed-step determinism achievable:** yes — no data-dependent branching anywhere in the corrected
  formulation. F-3's fix is a division, not a conditional, which *preserves* this property; an
  in-stage `if norm != 1: normalize` would not have.

### Timestep selection methodology (replaces "$h=10^{-3}$ s")

$h=10^{-3}$ s is **not** a validated timestep and the audit does not bless it. The methodology:

1. **Estimate the fastest retained timescale.** From $\mathbf{J}$ and the aerodynamic moment
   derivative, the rotational mode $\omega_n \approx \sqrt{\bar q S d\,|C_{m\alpha}|/J_{yy}}$ at the
   highest $\bar q$ in the scenario. This is an estimate, not a measurement.
2. **Set a starting step** from an accuracy rule of $\ge 20$ steps per period, *not* from the RK4
   stability limit — for a 5 Hz mode these differ by a factor of nine.
3. **Run a refinement study on the actual scenario**: $h, h/2, h/4, h/8$; compute a Richardson error
   estimate against the finest run.
4. **Require the observed convergence order to be $4.0\pm0.2$** before trusting any error estimate. A
   wrong order means the error model does not apply and the study is invalid.
5. **Select the largest $h$** whose Richardson error is below the tolerance *declared in advance for
   that experiment*, then apply a safety factor of 2.
6. **Record $h$, the study, and the tolerance in the experiment manifest.** A step size inherited from
   another experiment without repeating this is not justified.
7. **Re-run when the fastest mode changes** — notably when actuator dynamics arrive at Phase 12.

The output of step 5 is per-experiment. There is no single correct RADIUS timestep.

---

## 11. Verification tests — classification and gaps

The ~60 specified tests were reviewed and classified. **Four were mis-categorised** and three tests
are **missing**.

### Mis-categorisations corrected

| Test | Was | Should be | Why |
|---|---|---|---|
| V-ATM-03 (comparison with published tables) | implied validation-adjacent | **Verification against an external reference** | The 1976 standard is an idealised annual mean. Agreement shows RADIUS implements *the standard*, not that the standard describes the air |
| V-STA-03, V-AER-01 (round trips) | "verification" | **Unit / property tests** | They check internal self-consistency and can pass under a uniformly wrong convention — exactly what F-2 demonstrates |
| V-EOM-05 (torque-free asymmetric) | analytical | **Numerical invariant test** | It has no closed form; it checks conserved quantities |
| V-AER-08 (coefficient provenance) | listed among physics tests | **Process/metadata test** | It verifies no physics |

### Tests that can pass despite a uniformly wrong convention

`OBSERVATION`, and the audit's central methodological point: **every round-trip and self-consistency
test in the suite has this weakness.** F-2 is the proof — a wrong $\mathbf{T}_{BW}$ paired with a
wrong inverse would have round-tripped perfectly.

The tests that cannot be fooled are those with **externally sourced or hand-computed** expected
values: V-FRM-08, V-ATT-01, V-ATM-03, V-EOM-06 (Tsiolkovsky), V-AER-05/06 (hand-computed moment
signs). These are load-bearing and must not be weakened into self-consistency checks.

### Tests required before implementation — new

| ID | Test | Catches |
|---|---|---|
| **V-EOM-09** | **Variable-mass torque-free spin.** Axisymmetric body, uniform depletion, no external moment ⟹ $\omega_z$ **constant**. Hand-computed | **F-1.** No existing test exercised rotation with $\dot m\neq0$ |
| **V-FRM-09** | $\mathbf{T}_{BI}(kq)$ orthonormal for $k\neq1$; $\mathbf{T}_{BI}(kq)=\mathbf{T}_{BI}(q)$ | **F-3.** RK-stage correctness |
| **V-FRM-10** | $\mathbf{T}(q_a\otimes q_b)=\mathbf{T}(q_b)\mathbf{T}(q_a)$, and that the reversed order **fails** | **F-4.** Composition order |

V-EOM-09 is the test whose absence allowed a factor-of-two error to reach a gate marked PASS.

Also required: **V-ATT-02 must use a non-principal rotation axis.** As specified it used a
principal-axis case, which cannot distinguish $q\otimes\tilde{\boldsymbol\omega}$ from
$\tilde{\boldsymbol\omega}\otimes q$ — the two commute there. The audit's own check needed
$\boldsymbol\omega=(0.37,-0.81,1.23)$ to separate them by $10^{12}$. RS-002's V-ATT-03 already covers
a non-principal axis; the requirement is now explicit rather than incidental.

---

## 12. AURA interface — **VERIFIED, no change**

- **Truth / estimated separation:** architecturally enforced — the estimator gets its own state
  vector. Correct, and it is the property that makes an eventual inference experiment meaningful.
- **No AURA terminology in the physics core:** verified. RADIUS says *perturbation*, not *fault* —
  a fault taxonomy is a modelling commitment RADIUS has not made. `provenance`, `seed` and `manifest`
  are generic research-engineering terms, not AURA-specific.
- **Sufficient exposure without dependency:** state trajectories, derived observables, parameters,
  environment, perturbations, seeds, configuration and provenance are all independently justified by
  RADIUS's own needs. No output exists solely for AURA.
- **RADIUS remains independently meaningful.** No import, schema, or dependency. Unchanged.

---

## 13. Source reconciliation

Convention differences were reconciled explicitly rather than assumed away; recorded in
`research/SOURCES.md`.

| Source | Convention difference | Reconciliation |
|---|---|---|
| SRC-006 Markley & Crassidis | Largely uses the **JPL/Shuster** quaternion convention (product order reversed relative to Hamilton) | RADIUS's $\dot q$ is **derived independently** (§2.2) and numerically confirmed, not adopted from this source. Cited for norm-drift and singularity discussion, which are convention-independent |
| SRC-003 NASA RP-1207 | Constant mass; integrates **body-axis** velocity | Matches RADIUS's Phase-4 baseline in physics but not in state choice. Used to cross-check the *rotational* equation and force build-up, not the translational state form |
| SRC-007 Eke | Variable-mass equations via Kane's method | Supports F-1's correction: the momentum-flux treatment is the point. Hardware content not used |
| SRC-008 U.S. Std Atm 1976 | Lapse rates tabulated per km | F-6: converted explicitly |

**No source was cited merely for containing a similar-looking equation.** Where the load-bearing
result is RADIUS's own derivation (§2.2, §5.2), that is stated.

---

## 14. Load-Bearing Corrections

1. **F-1** — Remove $-\dot{\mathbf{J}}\boldsymbol\omega$ from the rotational equation; adopt
   $\mathbf{J}(t)\dot{\boldsymbol\omega}+\boldsymbol\omega\times(\mathbf{J}(t)\boldsymbol\omega)=\mathbf{M}_{\text{ext}}$
   under new assumption `A-VM-05`. Define or remove $\mathbf{M}_{\text{jet}}$; it is no longer an
   undefined symbol in a governing equation. **ADR-0009.**
2. **F-2** — $\mathbf{T}_{BW}=\mathbf{R}_y(\alpha)\mathbf{R}_z(-\beta)$ in RS-001 §2.3.
3. **F-3** — $\mathbf{T}_{BI}(q)$ divided by $q\cdot q$, defined for non-unit $q$. New `A-NUM-05`.
4. **F-4** — Quaternion composition order stated in `NOTATION_AND_CONVENTIONS.md`.

## 15. Accepted Assumptions (retained deliberately)

`A-FRM-01` flat non-rotating Earth (quantified) · `A-FRM-02` centrifugal in measured $g$, with F-7's
mis-scaling recorded as negligible · `A-EOM-01` rigid body · `A-VM-02` quasi-static CM · **`A-VM-05`
(new)** co-rotating ejection with negligible relative exit velocity · `A-VM-03` jet damping omitted,
now a genuinely separate term · `A-AER-01` linear coefficients with a raising validity gate ·
`A-AER-03` coefficients arbitrary-illustrative · `A-ATM-02` 1976 gas constant used deliberately ·
`A-NUM-04` at most one event crossing per step.

## 16. Remaining Research Gaps

| Gap | Status after audit |
|---|---|
| **Traceable aerodynamic coefficient source** | **Open.** Q8 gate remains NOT PASS. No data invented |
| **Independent 6-DOF benchmark trajectory** | **Open.** RADIUS can be fully verified and remain unvalidated |
| **Jet damping magnitude** | **Open**, but now cleanly separated from $\dot{\mathbf{J}}$ rather than entangled with it — a better-posed question than before |
| CM-motion momentum term (`A-VM-02`) | Open, unquantified |
| Timestep adequacy | **Methodology now specified** (§10). $h$ becomes a per-experiment measured quantity |
| Dynamic viscosity in the atmosphere interface | Open; non-breaking to add when a Reynolds-dependent model arrives |
| SRC-010 bibliographic details | Open, still `(not verified)` |
| Atmosphere layer-table transcription | Partially closed: sea level and the 11 km boundary now verified against published values |

---

## 17. Gate Determination

**PASS WITH REQUIRED CORRECTIONS** — corrections applied in this commit.

| Gate criterion | Status |
|---|---|
| Frame conventions unambiguous | ✅ verified; F-2, F-4, F-5 corrected |
| Quaternion equation verified | ✅ derived independently and numerically confirmed against a non-degenerate case |
| Translational equations verified | ✅ four limiting cases, including a rotating-attitude case matching closed form |
| Rotational equations verified | ✅ **after F-1 correction** |
| Variable-mass assumptions explicit and sufficient | ✅ `A-VM-05` added; the entangled term pair resolved |
| Gravity convention verified | ✅ sign and interface confirmed; F-7 recorded as negligible |
| Numerical formulation defined | ✅ F-3 closed; timestep methodology specified |
| Critical verification tests specified | ✅ V-EOM-09, V-FRM-09, V-FRM-10 added |
| No unresolved mathematical blocker | ✅ for Phases 2–6. **Phase 8 remains blocked on data, not mathematics** |

**Phase 2 (`radius/math/`, `radius/frames/`) may begin.**

---

## 18. The single most important conclusion

> **The specification's most carefully argued section contained the error.**

RS-004 §3.1 reasons at length about why treating departing mass as vanishing is wrong for linear
momentum — and then, three sections later, does exactly that for angular momentum. The result was a
factor-of-two error in spin rate that no specified test would have caught, in a document that had
already passed a quality gate.

The gate did not fail through carelessness. It failed because **every rotational test was written for
constant mass**, so the variable-mass rotational equation was never exercised by anything. The
generalisable lesson for RADIUS is that a test suite must be checked for *coverage of the equations as
written*, not only for the correctness of each test — and that an argument made well in one place does
not propagate itself to the analogous case.
