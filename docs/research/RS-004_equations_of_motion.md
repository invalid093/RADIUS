# RS-004 — Equations of Motion

**Status:** Specification. Not implemented, not verified.
**Depends on:** RS-001, RS-002, RS-003, `docs/methodology/NOTATION_AND_CONVENTIONS.md`

---

## 1. Scope of this document

The complete nonlinear equations governing the 14-element state of RS-003, written symbolically, with
every variable, frame, unit, sign convention and assumption stated. The objective is **not** to obtain
equations that look correct. It is to produce a formulation another engineer can audit term by term
and say precisely which physical effect each term is, and which are absent.

Every term below is either derived here or explicitly attributed. Where a term is *omitted*, it is
named and registered, because an unnamed omission is indistinguishable from an error.

---

## 2. Symbols

| Symbol | Meaning | Frame | Unit |
|---|---|---|---|
| $\mathbf{p}^{I}$ | position of the centre of mass | $I$ | m |
| $\mathbf{v}^{I}$ | velocity of the CM relative to $I$ | $I$ | m·s⁻¹ |
| $q \equiv q_{BI}$ | attitude, Hamilton, scalar-first | — | — |
| $\boldsymbol{\omega} \equiv \boldsymbol{\omega}^{B}_{B/I}$ | angular velocity of $B$ relative to $I$ | $B$ | rad·s⁻¹ |
| $m$ | total instantaneous vehicle mass | — | kg |
| $\mathbf{J}$ | inertia tensor about the CM | $B$ | kg·m² |
| $\mathbf{F}$ | resultant external force | as marked | N |
| $\mathbf{M}$ | resultant external moment **about the CM** | $B$ | N·m |
| $\mathbf{T}_{BI}(q)$ | transformation $I \to B$ | — | — |
| $\mathbf{c}$ | exhaust velocity **relative to the vehicle** | $B$ | m·s⁻¹ |
| $g(h)$ | gravitational acceleration magnitude | — | m·s⁻² |

The inertia tensor is written $\mathbf{J}$, not $\mathbf{I}$, throughout RADIUS — $\mathbf{I}$ is the
identity matrix and the collision is a genuine source of confusion in dense expressions.

---

## 3. Translational dynamics

### 3.1 Why the constant-mass form is not simply reusable

For a constant-mass particle, $\mathbf{F} = m\mathbf{a}$. For a variable-mass body the naive
extensions are **both wrong**:

- $\mathbf{F} = \frac{d}{dt}(m\mathbf{v})= m\dot{\mathbf{v}} + \dot m \mathbf{v}$ is wrong. It treats
  the departing mass as vanishing, when it in fact leaves carrying momentum. The resulting
  $\dot m \mathbf{v}$ term is frame-dependent, which is by itself proof that the equation is not a
  law of physics.
- $\mathbf{F} = m(t)\dot{\mathbf{v}}$ with $\mathbf{F}$ containing only aerodynamics and gravity is
  wrong in the other direction: it omits the momentum flux entirely, so a vehicle expelling mass does
  not accelerate.

The correct statement comes from applying momentum conservation to a **closed** system — the vehicle
plus the mass it is about to expel — and then rewriting it for the open system. The result (SRC-007;
cross-checked against SRC-002):

$$\boxed{\;m\,\dot{\mathbf{v}}^{I} \;=\; \mathbf{F}^{I}_{\text{aero}} \;+\; \mathbf{F}^{I}_{\text{grav}} \;+\; \mathbf{F}^{I}_{\text{prop}}\;}$$

where the **propulsive force** is the momentum flux

$$\mathbf{F}^{B}_{\text{prop}} = \dot m\,\mathbf{c}, \qquad \dot m < 0$$

**Sign check** (`CALCULATION`): $\dot m < 0$ for mass loss, and $\mathbf{c}$ points *aft* (roughly
$-\hat{x}_B$). A negative scalar times an aft-pointing vector gives a **forward** force, of magnitude
$|\dot m|\,\lVert\mathbf{c}\rVert$. This is the expected result and the expected magnitude. The check
is recorded because getting this sign wrong produces a vehicle that decelerates under thrust — a
failure that is obvious in a plot and invisible in an equation.

So $m\dot{\mathbf{v}} = \mathbf{F}$ *is* the right shape, provided $\mathbf{F}$ includes the momentum
flux as an explicit term. The $\dot m \mathbf{v}$ term does **not** appear.

### 3.2 RADIUS's abstraction

Consistent with the scope boundary in `CLAUDE.md`, RADIUS does **not** model how a propulsive force is
physically produced. The interface (RS-008) supplies, per call:

- a force $\mathbf{F}^{B}_{\text{prop}}$,
- a mass-flow rate $\dot m$,
- optionally a moment $\mathbf{M}^{B}_{\text{prop}}$.

The equations above are documented so that the *meaning* of the supplied force is unambiguous — it is
the momentum flux $\dot m\mathbf{c}$ (plus any pressure contribution the supplier chooses to include)
— and so that a supplier providing a force inconsistent with its declared mass flow is committing an
identifiable error rather than an untraceable one. This is registered as `A-VM-01`.

### 3.3 Gravity

$$\mathbf{F}^{I}_{\text{grav}} = m\,g(h)\;\hat{z}_I, \qquad
g(h) = g_0\left(\frac{R_E}{R_E + h}\right)^{2}$$

$\hat{z}_I$ is **down** (RS-001), so gravity is $+z$ with no sign flip anywhere. Constant $g$
($g \equiv g_0$) is a configurable option used only to enable the closed-form verification cases of
§7 — see RS-001 §3.4 and `A-FRM-03`.

The centrifugal contribution is absorbed into measured $g$ (`A-FRM-02`); it must not be added
separately.

### 3.4 Assembled

$$\dot{\mathbf{p}}^{I} = \mathbf{v}^{I}$$

$$\dot{\mathbf{v}}^{I} = \frac{1}{m}\,\mathbf{T}_{IB}(q)\Big[\mathbf{F}^{B}_{\text{aero}} + \mathbf{F}^{B}_{\text{prop}}\Big] \;+\; g(h)\,\hat{z}_I$$

Aerodynamic and propulsive forces are naturally body-referenced and are transformed once; gravity is
naturally inertial and is added directly. One transformation per derivative evaluation.

---

## 4. Rotational dynamics

Angular momentum about the centre of mass, resolved in $B$: $\mathbf{h}^{B} = \mathbf{J}\boldsymbol{\omega}$.

Differentiating in the inertial frame and applying the transport theorem
(`NOTATION_AND_CONVENTIONS.md` §2):

$$\left.\frac{d\mathbf{h}}{dt}\right|_{I} = \dot{\mathbf{J}}\boldsymbol{\omega} + \mathbf{J}\dot{\boldsymbol{\omega}} + \boldsymbol{\omega}\times(\mathbf{J}\boldsymbol{\omega}) = \mathbf{M}^{B}$$

so

$$\boxed{\;\dot{\boldsymbol{\omega}} = \mathbf{J}^{-1}\Big[\mathbf{M}^{B}_{\text{aero}} + \mathbf{M}^{B}_{\text{prop}} - \boldsymbol{\omega}\times(\mathbf{J}\boldsymbol{\omega}) - \dot{\mathbf{J}}\boldsymbol{\omega} + \mathbf{M}^{B}_{\text{jet}}\Big]\;}$$

Term by term:

| Term | Physical meaning | Status in RADIUS |
|---|---|---|
| $\mathbf{M}_{\text{aero}}$ | aerodynamic moment about the CM | **Implemented** (RS-007) |
| $\mathbf{M}_{\text{prop}}$ | moment from a thrust line not through the CM | **Implemented** via interface (RS-008) |
| $-\boldsymbol{\omega}\times(\mathbf{J}\boldsymbol{\omega})$ | gyroscopic coupling. Source of coning and of intermediate-axis instability | **Implemented** |
| $-\dot{\mathbf{J}}\boldsymbol{\omega}$ | moment from the inertia tensor changing as mass depletes | **Implemented** — $\dot{\mathbf{J}}$ from the mass model, by finite difference or analytically (RS-008 §4) |
| $\mathbf{M}_{\text{jet}}$ | **jet damping**: the expelled mass carries away angular momentum, opposing transverse rotation | **OMITTED.** Registered as `A-VM-03` |

**On the omission.** Jet damping is a genuine physical moment, roughly proportional to the mass flow
rate and the square of the distance from the CM to the exit plane, opposing transverse angular rate —
i.e. it acts as a **damping** term. Omitting it makes the simulated vehicle *less* damped in pitch and
yaw than a real one: attitude oscillations decay more slowly, or fail to decay. This is the
conservative direction for a stability study and the non-conservative direction for a dispersion
study, and any result touching either must say so.

`LIMITATION`: the magnitude of the omitted term is currently **unbounded** — RADIUS does not know how
large the error is. Closing this needs a reference (see `research/SOURCES.md`, gaps table). Until
then no claim about rotational damping is supportable.

**$\mathbf{J}$ is a full symmetric tensor**, not assumed diagonal. Assuming principal axes would
impose a symmetry the vehicle may not have, and the products of inertia are exactly what couple the
axes. $\mathbf{J}^{-1}$ is precomputed per evaluation, not per element.

---

## 5. Attitude kinematics

$$\dot q = \tfrac{1}{2}\,\boldsymbol{\Omega}(\boldsymbol{\omega})\,q$$

with $\boldsymbol{\Omega}$ as derived in RS-002 §4. Norm maintenance is an integrator concern, not a
dynamics concern, and is specified in RS-005.

---

## 6. Mass

$$\dot m = -\dot m_{\text{out}}(t, \mathbf{x}), \qquad \dot m_{\text{out}} \ge 0$$

supplied by the interface of RS-008. Depletion is handled as an **event** (RS-005 §6), not a clamp.

---

## 7. Analytical verification cases

These exist *because* the equations were written to make them possible. Each isolates a subset of
terms so that a failure localises. Ordered so that each test's prerequisites are already verified.

| ID | Case | Configuration | Closed-form reference | Isolates |
|---|---|---|---|---|
| V-EOM-01 | Force-free translation | $\mathbf{F}=0$, $g=0$ | $\mathbf{p}(t) = \mathbf{p}_0 + \mathbf{v}_0 t$ | integrator, position/velocity coupling |
| V-EOM-02 | Constant gravity | $g = g_0$, no aero, no thrust | parabola, exact | gravity sign and magnitude |
| V-EOM-03 | Torque-free, constant rate about a principal axis | $\mathbf{M}=0$, $\boldsymbol{\omega}_0 \parallel$ principal axis | $\boldsymbol{\omega}$ constant; $q(t)$ closed form | quaternion kinematics, gyroscopic term vanishing correctly |
| V-EOM-04 | Torque-free axisymmetric coning | $J_x = J_y = J_t \ne J_z$, $\boldsymbol{\omega}_0$ off-axis | transverse $\boldsymbol{\omega}$ rotates in body axes at $\lambda = \frac{J_z - J_t}{J_t}\omega_z$; $\omega_z$ and $\lVert\boldsymbol{\omega}_t\rVert$ constant | the $\boldsymbol{\omega}\times\mathbf{J}\boldsymbol{\omega}$ term, quantitatively |
| V-EOM-05 | Torque-free asymmetric | $J_x < J_y < J_z$, all distinct | no closed form; **invariants** $\lVert\mathbf{h}\rVert$ and $T=\frac{1}{2}\boldsymbol{\omega}\!\cdot\!\mathbf{J}\boldsymbol{\omega}$ conserved. Qualitatively: intermediate-axis instability | products of inertia, full tensor handling |
| V-EOM-06 | **Tsiolkovsky** | straight line, no gravity, no aero, constant $\mathbf{c}$ and $\dot m$ | $\Delta v = \lVert\mathbf{c}\rVert \ln\!\big(m_0/m_f\big)$, exact | **the variable-mass coupling**, quantitatively |
| V-EOM-07 | Thrust offset from CM | $\mathbf{M}_{\text{prop}} = \mathbf{r}\times\mathbf{F}_{\text{prop}}$ | angular acceleration $= \mathbf{J}^{-1}\mathbf{M}$ at $t=0$ | moment transfer, CM referencing |
| V-EOM-08 | Dimensional consistency | symbolic audit of every term | every term in $\dot{\mathbf{v}}$ is m·s⁻², every term in $\dot{\boldsymbol{\omega}}$ is rad·s⁻² | unit errors |

**V-EOM-06 is the important one.** It is the only test that checks the variable-mass translational
coupling against an exact analytical result, and it does so with a formula independent of the
derivation in §3 — Tsiolkovsky follows from momentum conservation directly. A sign error in
$\mathbf{F}_{\text{prop}} = \dot m\mathbf{c}$ fails it immediately and unmistakably.

**V-EOM-05 deserves its place** despite having no closed form. Conserved quantities are a *stronger*
test than a trajectory match in one respect: they must hold at every step, for every initial
condition, and they are sensitive to exactly the term (the full inertia tensor coupling) that a
diagonal-inertia shortcut would break. The qualitative intermediate-axis instability is a bonus check
that the nonlinearity is present rather than linearised away.

**What these tests do not establish.** All of them are **verification**. None is validation: every one
compares RADIUS against mathematics, not against reality. No test here licenses any statement about
how a physical vehicle would behave. See `docs/methodology/VERIFICATION_AND_VALIDATION.md`.

---

## 8. Assumptions registered

`A-EOM-01` … `A-EOM-04`, `A-VM-01`, `A-VM-03` — see `docs/assumptions.md`.

---

## 9. Open questions

1. **How large is the omitted jet-damping term?** Currently unbounded (§4). This is the largest known
   gap in the formulation and it blocks any rotational-damping claim.
2. Should $\dot{\mathbf{J}}$ be computed analytically from the mass model or by finite difference?
   Finite difference is simpler and introduces a truncation error into a term that is already small;
   analytical is exact but couples the dynamics module to the mass model's internals. Deferred to
   RS-008 §4, with the note that a finite-difference $\dot{\mathbf{J}}$ inside an RK stage is a
   second, hidden discretisation and needs its own error assessment.
3. Is the rigid-body assumption (`A-EOM-01`) tenable for a slender vehicle at high dynamic pressure?
   Almost certainly not in general. It is accepted as a scope boundary, not defended as physics.
4. RS-003 §3 chose inertial velocity partly to keep the variable-mass terms separable. That reasoning
   is argued, not demonstrated. A body-axis derivation reaching the same equations would be a genuine
   independent check, and is worth doing on paper before implementation.
