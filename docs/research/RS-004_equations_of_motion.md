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
| $J_{xx}, J_{yy}, \ldots$ | components of $\mathbf{J}$, resolved in $B$ | $B$ | kg·m² |
| $J_\parallel,\ J_\perp$ | principal moments about the symmetry axis and about any transverse axis — **axisymmetric bodies only** (ADR-0010, NOTATION §5.1). A RADIUS vehicle's symmetry axis is $x_B$: $J_{xx}=J_\parallel$, $J_{yy}=J_{zz}=J_\perp$ when principal axes coincide with $B$ | — | kg·m² |
| $\omega_\parallel$ | component of $\boldsymbol{\omega}$ along the symmetry axis; for a RADIUS vehicle, the roll rate $p$ | $B$ | rad·s⁻¹ |
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

> **Corrected 2026-09-09 (audit finding F-1).** This section previously carried a
> $-\dot{\mathbf{J}}\boldsymbol{\omega}$ term. That term is **wrong for mass ejection** — it models
> internal redistribution — and produced a factor-of-two spurious spin-up in a torque-free depleting
> body. The derivation below replaces it. See
> `PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md` §5 and ADR-0009.

Angular momentum about the centre of mass, resolved in $B$: $\mathbf{h}^{B} = \mathbf{J}\boldsymbol{\omega}$.

### 4.1 Why the constant-mass form is not simply reusable — the rotational case

The same open/closed-system care that §3.1 applies to linear momentum is required for angular
momentum, and the naive extension fails in the same way.

Differentiating $\mathbf{h}$ in the inertial frame and applying the transport theorem gives the
left-hand side

$$\left.\frac{d\mathbf{h}}{dt}\right|_{I} = \dot{\mathbf{J}}\boldsymbol{\omega} + \mathbf{J}\dot{\boldsymbol{\omega}} + \boldsymbol{\omega}\times(\mathbf{J}\boldsymbol{\omega})$$

Setting this equal to $\mathbf{M}_{\text{ext}}$ alone is the **rotational analogue of the
$\frac{d}{dt}(m\mathbf{v})=\mathbf{F}$ error rejected in §3.1**: it treats the departing mass as
vanishing, when in fact it leaves carrying angular momentum.

The right-hand side must therefore include the angular-momentum flux. Let mass leave **co-rotating,
with negligible velocity relative to the structure at its exit location** (`A-VM-05`). The angular
momentum it carries out per unit time, about the CM, is

$$\int \mathbf{r}\times(\boldsymbol{\omega}\times\mathbf{r})\,d\dot{m} \;=\; -\dot{\mathbf{J}}\boldsymbol{\omega}$$

so the balance reads

$$\dot{\mathbf{J}}\boldsymbol{\omega} + \mathbf{J}\dot{\boldsymbol{\omega}} + \boldsymbol{\omega}\times(\mathbf{J}\boldsymbol{\omega}) \;=\; \mathbf{M}_{\text{ext}} + \dot{\mathbf{J}}\boldsymbol{\omega}$$

**The $\dot{\mathbf{J}}\boldsymbol{\omega}$ terms cancel exactly**, leaving

$$\boxed{\;\dot{\boldsymbol{\omega}} = \mathbf{J}(t)^{-1}\Big[\mathbf{M}^{B}_{\text{aero}} + \mathbf{M}^{B}_{\text{prop}} - \boldsymbol{\omega}\times\big(\mathbf{J}(t)\boldsymbol{\omega}\big)\Big]\;}$$

The inertia tensor is evaluated at the instantaneous mass; its *rate* does not appear.

### 4.2 Why this is not merely a simplification

`CALCULATION` (pre-implementation audit, 2026-09-09). Torque-free axisymmetric body spinning at
$\omega_z = 10$ rad·s⁻¹ about its symmetry axis, depleting uniformly 1000 → 500 kg over 20 s with
inertia proportional to mass:

| | $\omega_z(20\ \text{s})$ |
|---|---|
| Truth — each element leaves carrying its own angular momentum | **10.000** rad·s⁻¹ |
| Previous formulation, retaining $-\dot{\mathbf{J}}\boldsymbol{\omega}$ | **20.000** rad·s⁻¹ |

> **Notation (ADR-0010).** $\omega_z$ in this calculation is the spin component about the symmetry
> axis, $\omega_\parallel$, written in a $z$-symmetric labelling — the canonical frame $P$ of NOTATION
> §5.1. For a RADIUS vehicle, whose symmetry axis is $x_B$, it is the roll rate $p$. The calculation
> and its result are unchanged.

Retaining the term forces conservation of $\mathbf{J}\boldsymbol{\omega}$ — the physics of a skater
pulling their arms in. That is **internal redistribution**, not ejection. When mass is ejected, every
material element keeps its own angular velocity, so the remaining body spins at the same rate with
less angular momentum.

`INTERPRETATION`: $-\dot{\mathbf{J}}\boldsymbol{\omega}$ **is** correct for redistribution
($\dot{\mathbf{J}}\neq0$ with $\dot m = 0$ — a moving internal mass). RADIUS does not model that. If
it ever does, the term returns, with its own derivation.

### 4.3 Term by term

| Term | Physical meaning | Status (vocabulary: ADR-0010) |
|---|---|---|
| $\mathbf{M}_{\text{aero}}$ | aerodynamic moment about the CM | **Specified** (RS-007). Not yet implemented; no traceable coefficient source (Q8, `A-AER-03`) |
| $\mathbf{M}_{\text{prop}}$ | moment from a thrust line not through the CM | **Specified** as an interface input (RS-008 §3.1). Not yet implemented |
| $-\boldsymbol{\omega}\times(\mathbf{J}\boldsymbol{\omega})$ | gyroscopic coupling. Source of coning and of intermediate-axis instability | **Specified. Verification anchor established** (V-EOM-04). Not yet implemented. The pre-implementation audit's own integration of this term was conservative — $\lVert\mathbf{h}\rVert$ drift $5\times10^{-16}$, energy drift $2\times10^{-14}$ over 8 s (audit §5.4) — an audit calculation, not a property of RADIUS code |
| angular-momentum flux of ejected mass | cancels $\dot{\mathbf{J}}\boldsymbol{\omega}$ under `A-VM-05` | **Analytically verified**: cancels exactly under `A-VM-05` (§4.1, ADR-0009), which is why neither term appears. Anchor V-EOM-09 planned |
| **jet damping** | arises only when the exhaust leaves with **non-zero** velocity relative to the structure, at a point offset from the CM. Opposes transverse rotation | **OMITTED.** `A-VM-03` |

### 4.4 On the omission of jet damping

It is now a genuinely separate term rather than half of an entangled pair — the second benefit of the
correction. Physically it is roughly proportional to the mass-flow rate and to the square of the
distance from the CM to the exit plane, opposing transverse angular rate, i.e. it **damps**.

Omitting it makes the simulated vehicle *less* damped in pitch and yaw than a real one: attitude
oscillations decay more slowly, or fail to decay. That is the conservative direction for a stability
study and the non-conservative direction for a dispersion study, and any result touching either must
say so.

`LIMITATION`: the magnitude of the omitted term remains **unbounded** — RADIUS does not know how
large the error is. Closing this needs a reference (`research/SOURCES.md`, gaps table). Until then no
claim about rotational damping is supportable.

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

| ID | Case | Configuration | Closed-form reference | Isolates | Status (ADR-0010) |
|---|---|---|---|---|---|
| V-EOM-01 | Force-free translation | $\mathbf{F}=0$, $g=0$ | $\mathbf{p}(t) = \mathbf{p}_0 + \mathbf{v}_0 t$ | integrator, position/velocity coupling | **Verification anchor established** (frozen oracle, `tests/test_eom_anchors.py`); not yet implemented |
| V-EOM-02 | Constant gravity | $g = g_0$, no aero, no thrust | parabola, exact | gravity sign and magnitude | **Verification anchor established** (frozen oracle, `tests/test_eom_anchors.py`); not yet implemented |
| V-EOM-03 | Constant non-zero body force at a fixed attitude | $\mathbf{F}^{B}\neq0$ constant, $g=0$, attitude a fixed parameter of the case, not a state | $\mathbf{a}^{I}=\frac{1}{m}\mathbf{T}_{IB}\mathbf{F}^{B}$; $\mathbf{v}(t)=\mathbf{v}_0+\mathbf{a}^{I}t$; $\mathbf{p}(t)=\mathbf{p}_0+\mathbf{v}_0t+\frac12\mathbf{a}^{I}t^2$ | the $\mathbf{T}_{IB}$ force path | **Verification anchor established** (frozen oracle, `tests/test_eom_anchors.py`); not yet implemented |
| V-EOM-10 | Torque-free, constant rate about a principal axis — *listed as V-EOM-03 until 2026-09-11* | $\mathbf{M}=0$, $\boldsymbol{\omega}_0 \parallel$ principal axis | $\boldsymbol{\omega}$ constant; $q(t)$ closed form | quaternion kinematics, gyroscopic term vanishing correctly | **Planned** — never frozen |
| V-EOM-04 | Torque-free axisymmetric coning | $J_\parallel \ne J_\perp$, $\boldsymbol{\omega}_0$ with non-zero transverse part. Frozen in two forms: RADIUS body axes (symmetry axis $x_B$) and the canonical frame $P$ (symmetry axis $z_P$), NOTATION §5.1 | the transverse $\boldsymbol{\omega}$ rotates relative to the body, about the positive symmetry axis, at $\lambda = \frac{J_\parallel - J_\perp}{J_\perp}\,\omega_\parallel$; $\omega_\parallel$ and $\lVert\boldsymbol{\omega}_\perp\rVert$ constant. In $B$: $\dot q = -\lambda r$, $\dot r = \lambda q$, $\omega_\parallel = p$ | the $\boldsymbol{\omega}\times\mathbf{J}\boldsymbol{\omega}$ term, quantitatively | **Verification anchor established** (frozen oracle, `tests/test_eom_anchors.py`); not yet implemented |
| V-EOM-05 | Torque-free asymmetric | principal moments $J_{xx} < J_{yy} < J_{zz}$, all distinct | no closed form; **invariants** $\lVert\mathbf{h}\rVert$ and $T=\frac{1}{2}\boldsymbol{\omega}\!\cdot\!\mathbf{J}\boldsymbol{\omega}$ conserved. Qualitatively: intermediate-axis instability | products of inertia, full tensor handling | **Planned** |
| V-EOM-06 | **Tsiolkovsky** | straight line, no gravity, no aero, constant $\mathbf{c}$ and $\dot m$ | $\Delta v = \lVert\mathbf{c}\rVert \ln\!\big(m_0/m_f\big)$, exact | **the variable-mass coupling**, quantitatively | **Planned** |
| V-EOM-07 | Thrust offset from CM | $\mathbf{M}_{\text{prop}} = \mathbf{r}\times\mathbf{F}_{\text{prop}}$ | angular acceleration $= \mathbf{J}^{-1}\mathbf{M}$ at $t=0$ | moment transfer, CM referencing | **Planned** |
| **V-EOM-09** | **Variable-mass torque-free spin** | axisymmetric, uniform depletion, $\mathbf{M}=0$, $\boldsymbol{\omega}_0$ along the symmetry axis ($x_B$) | $\omega_\parallel$ — the roll rate $p$ — **constant** (hand-computed) | **the variable-mass rotational equation.** Added by the audit | **Planned** |
| V-EOM-08 | Dimensional consistency | symbolic audit of every term | every term in $\dot{\mathbf{v}}$ is m·s⁻², every term in $\dot{\boldsymbol{\omega}}$ is rad·s⁻² | unit errors | **Planned** |

**Identifier history (ADR-0010).** Until 2026-09-11 this table listed *torque-free, constant rate
about a principal axis* as **V-EOM-03**. That case was never frozen and never tested. On 2026-09-10
the identifier V-EOM-03 was assigned to the frozen body-force anchor. An identifier names exactly one
claim and a frozen anchor is never renumbered, so the planned case is now **V-EOM-10**, unchanged in
content. Rows stay ordered by prerequisite, not by number. The V-EOM-04 entry was first written as
$J_x = J_y = J_t \ne J_z$ with $\lambda = \frac{J_z - J_t}{J_t}\omega_z$ — symmetry about $z$ — and is
restated above in the notation of ADR-0010; the frozen values did not change.

**V-EOM-09 exists because of a gate failure.** Every rotational test in the original suite ran at
constant mass, so the variable-mass rotational equation was exercised by nothing at all — which is how
a factor-of-two error passed a quality gate marked PASS. The generalisable lesson is that a suite must
be checked for *coverage of the equations as written*, not only for the correctness of each test.

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

`A-EOM-01` … `A-EOM-04`, `A-VM-01`, `A-VM-03`, `A-VM-05` — see `docs/assumptions.md`.

---

## 9. Open questions

1. **How large is the omitted jet-damping term?** Currently unbounded (§4). This is the largest known
   gap in the formulation and it blocks any rotational-damping claim.
2. ~~Should $\dot{\mathbf{J}}$ be computed analytically or by finite difference?~~ **Closed by the
   F-1 correction (2026-09-09):** $\dot{\mathbf{J}}$ no longer appears in the equations of motion, so
   the associated hazard — a finite-difference derivative nested inside an RK stage acting as a
   second, hidden discretisation — disappears with it. $\dot{\mathbf{J}}$ remains available as a
   diagnostic. A correction that removes both an error and a hazard is evidence it was the right
   correction.
3. Is the rigid-body assumption (`A-EOM-01`) tenable for a slender vehicle at high dynamic pressure?
   Almost certainly not in general. It is accepted as a scope boundary, not defended as physics.
4. RS-003 §3 chose inertial velocity partly to keep the variable-mass terms separable. That reasoning
   is argued, not demonstrated. A body-axis derivation reaching the same equations would be a genuine
   independent check, and is worth doing on paper before implementation.
