# RADIUS — Verification and Validation Strategy

**Status:** Strategy, written before implementation. The frame and attitude conventions are now
**verified** against hand-derived anchors (section 2). Nothing is **validated**, and no dynamics,
integrator, atmosphere or aerodynamic code exists to verify.
**Sources:** SRC-011 (Oberkampf & Roy), SRC-012 (AIAA G-077-1998), SRC-013 (NASA-STD-7009)

---

## 1. The distinction, and why RADIUS enforces it

**Verification** — *did we implement and solve the equations correctly?*
A comparison between the code and the mathematics. Entirely internal: no physical reality is
consulted.

**Validation** — *does the model represent reality well enough for the intended purpose?*
A comparison between the model and the world. Requires **independent reference data**, a **stated
purpose**, and a **stated tolerance**. Without all three the word does not apply.

These are community-standard definitions (SRC-012) and RADIUS adopts them in meaning.

**Why this is a binding rule rather than terminology.** "Validated" is the word that converts a
research prototype into something people rely on. Applied to a model that has only passed its own
tests, it makes a claim about reality on the strength of self-consistency — and self-consistency is
perfectly compatible with being uniformly wrong. Every convention error in
`docs/methodology/NOTATION_AND_CONVENTIONS.md` has that property: applied consistently, it passes
every internal check.

So: **passing tests is verification evidence only.** Where no independent reference data exists, the
correct statement is *"verified, not validated"*, and the limitation is reported rather than elided.

---

## 2. Current status

`FACT`, 2026-09-09 (updated when the first tests began passing; the previous version of
this table said "verification tests written: none", which stopped being true at Phase 2B):

| | |
|---|---|
| Implemented | `radius/frames.py` (frame, Euler, quaternion→DCM and wind-frame transformations) and `radius/math/quaternion.py` (Hamilton product) — and nothing else. No dynamics, integrator, atmosphere, aerodynamic or trajectory code exists |
| Verified | **the frame and attitude conventions only** — V-FRM-05, V-FRM-08, V-FRM-09, V-FRM-10, V-ATT-01, against hand-derived anchors. Nothing else |
| Validated | **nothing** |
| Verification tests written | **117**: 117 passing, 0 failing, **0 skipped** — against 65+ test IDs *specified* across RS-001…RS-008 (not like-for-like: one specified ID is usually several test methods) |
| Frozen analytical anchors, awaiting an implementation to consume them | **V-EOM-01**, **V-EOM-02**, **V-EOM-03** (translational), **V-EOM-04** and **V-EOM-05** (rotational) — established as exact oracles; no translational or rotational dynamics code exists |
| Independent reference data held | **none** |

### Translational EOM analytical anchors

Frozen **before** any translational dynamics implementation exists, in
`tests/test_eom_anchors.py`. Governing equation: RS-004 §3.4, on the state of RS-003 §6.

| Anchor | Case | Closed form | Frozen oracle |
|---|---|---|---|
| **V-EOM-01** | Force-free straight-line translational limit | `v(t) = v0`, `p(t) = p0 + v0 t` | `p0=(12,−7,31)`, `v0=(35,−11,8)`, `t=4` → `v=(35,−11,8)`, `p=(152,−51,63)` |
| **V-EOM-02** | Constant-gravity ballistic translational limit | `v(t) = v0 + (0,0,g0 t)`, `p(t) = p0 + v0 t + (0,0,g0 t²/2)` | `p0=(10,20,100)`, `v0=(40,−15,−25)`, `g0=10`, `t=3` → `v=(40,−15,5)`, `p=(130,−25,70)` |
| **V-EOM-03** | Constant non-zero **body** force at a fixed known attitude | `a = (1/m) T_IB F^B`, `v(t) = v0 + a t`, `p(t) = p0 + v0 t + a t²/2` | attitude `(φ,θ,ψ)` with `(cos,sin) = (4/5,3/5), (3/5,4/5), (4/5,−3/5)`; `F^B=(−375,−250,500)` N, `m=5` kg → `a=(−64,−77,90)`; `p0=(5,15,−25)`, `v0=(10,−30,20)`, `t=4` → `v=(−246,−338,380)`, `p=(−467,−721,775)` |

> **These are analytical verification anchors for limiting cases. They do not constitute
> validation against flight data, a high-fidelity trajectory benchmark, or validation of
> the complete 6-DOF model.**

Both cases set `F_aero^B = F_prop^B = 0`, so the term `T_IB (F_aero + F_prop)` vanishes
identically. **The force-free construction intentionally removes dependence on the
body-to-inertial force transformation**, which is anchored separately (V-FRM-08,
V-ATT-01), so that a failure localises to the inertial translational equation.

`LIMITATION`, asserted rather than assumed in the test file: the same construction makes
V-EOM-01 and V-EOM-02 structurally **blind** to a body/inertial confusion in the force
path, because they contain no force path. Gravity-sign and missing-½ errors are likewise
invisible to V-EOM-01, which has no gravity.

**V-EOM-03 closes the force-path gap.** It carries a constant non-zero body force at a
fixed attitude and no gravity, so the three anchors between them cover the gravity path
and the force path without either masking the other.

**The attitude in V-EOM-03 is a parameter of the analytical case, not a state being
integrated** — no quaternion, Euler angle or angular rate is propagated, and no
rotational equation appears. Rotational dynamics were entirely unanchored when V-EOM-03
was frozen; V-EOM-04, below, is the first rotational anchor.

*Case selection for V-EOM-03 was driven by discrimination analysis, not assumption.* Two
constructions were rejected because each silently voids a required mutation: `m = 1`
makes "multiply by mass instead of divide" invisible (`1/1 == 1*1`), and equal body-force
components make "permute the force components" invisible. Both exclusions are asserted as
tests, so a later simplification cannot quietly drain the anchor of its power. The
attitude uses Pythagorean triples, giving a DCM whose entries are exact rationals over
125 with **no zero entries** — a zero entry is somewhere a mutation can hide.

Mutation evidence (2026-09-10, executed file verified per run): control 32/32 pass; a
transposed DCM, a reversed Euler composition, a flipped attitude sign, a force-component
swap, a force-sign reversal, a mass multiplication, a missing ½, and both trap
constructions were each detected. Discrimination margins in acceleration run from 34 to
2160 m·s⁻², and the smallest margin anywhere in the anchor is 1 m from a unit
initial-position perturbation.

`LIMITATION` on V-EOM-03 itself: mutations "T_BI used instead of T_IB" and "transpose of
the intended DCM" are **the same mutation**, since `T_IB` is *defined* as `T_BI`
transposed. Recorded rather than counted twice.

`FACT`: the value supplied for V-EOM-02's `p_z(3)` when this anchor was commissioned was
55; independent derivation gives **70**, and 70 is what is frozen. The discrepancy is
documented in the test module. Freezing 55 would have installed an arithmetically false
oracle permanently.

### Rotational EOM analytical anchor — V-EOM-04

> **Reconciled 2026-09-11 by ADR-0010.** This section now writes $J_\parallel$, $J_\perp$ and
> $\omega_\parallel$ (NOTATION §5.1) where it first wrote $J_z$, $J_t$ and $\omega_z$, and names the
> canonical principal frame $P$ in which the $z$-symmetric form is expressed. The findings recorded
> when the anchor was frozen are kept below, marked resolved. **No frozen value changed.**

**V-EOM-04 — Torque-free axisymmetric coning.** The first rotational anchor, frozen in
`tests/test_eom_anchors.py` on 2026-09-10, **before** any rotational dynamics implementation exists.
Governing equation: RS-004 §4.1 / ADR-0009 at constant inertia and zero moment,
$\mathbf{J}\dot{\boldsymbol\omega} + \boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega) = 0$,
with the skew form of NOTATION §5.

**Frozen in two forms of one solution.**

| Form | Symmetry axis | Inertia |
|---|---|---|
| Canonical principal frame $P$ | $z_P$ | $\mathbf{J}^{P} = \mathrm{diag}(J_\perp, J_\perp, J_\parallel)$ |
| RADIUS body axes | $x_B$ | $\mathbf{J}^{B} = \mathrm{diag}(J_\parallel, J_\perp, J_\perp)$ |

The two forms are related by $x_P = y_B$, $y_P = z_B$, $z_P = x_B$, a cyclic relabelling whose
correctness the anchor tests. A full-tensor implementation must pass both. The canonical oracle is
also a legitimate body-frame input, for a body whose symmetry axis happens to be $z_B$.

`CALCULATION` — derived independently (2026-09-10) and executed as tests. In $P$:

$$J_\perp\dot\omega_{x_P} + (J_\parallel-J_\perp)\,\omega_{y_P}\omega_{z_P} = 0,\qquad
J_\perp\dot\omega_{y_P} - (J_\parallel-J_\perp)\,\omega_{x_P}\omega_{z_P} = 0,\qquad
J_\parallel\dot\omega_{z_P} = 0$$

so $\omega_\parallel = \omega_{z_P}$ is constant, $\dot\omega_{x_P} = -\lambda\omega_{y_P}$ and
$\dot\omega_{y_P} = \lambda\omega_{x_P}$, with $\lambda = \frac{J_\parallel-J_\perp}{J_\perp}\,\omega_\parallel$, and

$$\omega_{x_P}(t) = \omega_{x_P,0}\cos\lambda t - \omega_{y_P,0}\sin\lambda t,\qquad
\omega_{y_P}(t) = \omega_{y_P,0}\cos\lambda t + \omega_{x_P,0}\sin\lambda t.$$

In RADIUS body axes the same solution reads $\dot q = -\lambda r$, $\dot r = \lambda q$, with
$\omega_\parallel = p$.

Cross-check: with $u = \omega_{x_P} + i\omega_{y_P}$, $\dot u = i\lambda u$, so $u(t) = u_0 e^{i\lambda t}$ —
the same solution. A third, numerical check was run as a scratchpad analysis and **not
committed**: integrating the full nonlinear equations, without assuming $\omega_\parallel$ constant,
reproduced the closed form to $1.3\times10^{-13}$ rad·s⁻¹ at every sample, while the
reversed-sign form missed by up to 10 rad·s⁻¹.

**What $\lambda$ is.** "Coning rate" names at least three different quantities:

| Symbol | Rate of | Seen from | Value in the frozen case | Verified by V-EOM-04 |
|---|---|---|---|---|
| $\lambda = \frac{J_\parallel-J_\perp}{J_\perp}\omega_\parallel$ | the transverse $\boldsymbol\omega$ vector, positive right-handed about the positive symmetry axis ($+z_P$; $+x_B$ on a RADIUS vehicle) | the **body** axes | $-2$ rad·s⁻¹ | **yes** |
| $\sigma = -\lambda$ | the body, relative to the plane containing $\mathbf{h}$ and the symmetry axis | that plane | $+2$ rad·s⁻¹ | only through the exact identity $\boldsymbol\omega = \mathbf{h}/J_\perp + \sigma\,\hat{\mathbf{e}}_\parallel$ |
| $\lVert\mathbf{h}\rVert/J_\perp$ | the symmetry axis precessing about the fixed angular momentum | **inertial** space | $\sqrt{30}\approx5.48$ rad·s⁻¹ | **no** — needs attitude propagation |

**On the formula as originally stated — recorded, not silently replaced.** RS-004 §7 and §3.1
below first gave $\lambda = \frac{J_z-J_t}{J_t}\omega_z$. `FINDING` (2026-09-10): that formula is
**correct in magnitude and sign** for the body-frame rate of the transverse angular velocity, with
positive sense right-handed about the symmetry axis. It was **incomplete** as stated. It gave no sign
reference, and $\sigma = -\lambda$, the other natural reference, has the opposite sign. It did not say
it is a body-frame rate rather than the inertial precession rate. And it presumes symmetry about
$z$. **Resolved by ADR-0010:** it is now written axis-independently as
$\lambda = \frac{J_\parallel-J_\perp}{J_\perp}\omega_\parallel$, with its sign reference (NOTATION §5.1,
RS-004 §7).

`FINDING` (2026-09-10) — **axis labelling.** RS-004 §7, RS-004 §4.2, ADR-0009 and V-EOM-09 all
described a body "spinning at $\omega_z$ about its symmetry axis", but NOTATION §3 puts $x_B$ along
the vehicle's **longitudinal** axis, so a RADIUS vehicle is axisymmetric about $x_B$. The z-symmetric
case remains a valid test of the equation, which does not care which axis is special, and was frozen
as specified. The $x_B$-symmetric form a RADIUS vehicle will have was frozen beside it,
$\mathbf{J} = \mathrm{diag}(2, 6, 6)$, $\boldsymbol\omega_0 = (3, 2, -5)$, same $\lambda$. It was
obtained by the cyclic relabelling $(x,y,z)\to(y,z,x)$, a proper rotation. Relabelling by swapping
two axes is a reflection; it flips the cross product and is shown to **fail**, which is the
handedness check.

**Resolved by ADR-0010:**
- The physical symmetry axis is $x_B$.
- The $z$-symmetric form is the named, analysis-only canonical frame $P$, mapped to $B$ by exactly
  that relabelling.
- V-EOM-04 is therefore **both** a mathematically correct canonical-frame benchmark and, through its
  frozen $x_B$ form, a representation of the RADIUS vehicle's axis convention.
- Neither form is a representative vehicle state.
- RS-004 §4.2, §7 and RS-008's V-VM-10 now state the axis. ADR-0009 and the audit are dated records
  and are read through ADR-0010's migration rules.

| Frozen case | |
|---|---|
| Inertia | $J_\perp = 6$, $J_\parallel = 2$ kg·m² (prolate, $J_\parallel/J_\perp = 1/3$); test identifiers `J_PERP`, `J_PARALLEL` (named `J_T`, `J_Z` until ADR-0010) |
| Initial rate | frame $P$: $\boldsymbol\omega_0^{P} = (2, -5, 3)$ rad·s⁻¹; body axes: $\boldsymbol\omega_0^{B} = (p, q, r) = (3, 2, -5)$ rad·s⁻¹ |
| $\lambda$ | $-2$ rad·s⁻¹: the transverse rate **regresses** relative to the body |
| Sample times | $0,\ \pi/4,\ \pi/2,\ \arctan(3/4)$ s, i.e. $\lambda t = 0,\ -\pi/2,\ -\pi,\ -2\arctan(3/4)$ |
| $\boldsymbol\omega^{P}$ at the samples | $(2,-5,3)$, $(-5,-2,3)$, $(-2,5,3)$, $(-\tfrac{106}{25},-\tfrac{83}{25},3)$ |
| $\dot{\boldsymbol\omega}^{P}$ at the samples | $(-10,-4,0)$, $(-4,10,0)$, $(10,4,0)$, $(-\tfrac{166}{25},\tfrac{212}{25},0)$ |
| $\boldsymbol\omega^{B}$ at the samples | $(3,2,-5)$, $(3,-5,-2)$, $(3,-2,5)$, $(3,-\tfrac{106}{25},-\tfrac{83}{25})$ |
| $\dot{\boldsymbol\omega}^{B}$ at the samples | $(0,-10,-4)$, $(0,-4,10)$, $(0,10,4)$, $(0,-\tfrac{166}{25},\tfrac{212}{25})$ |
| Invariants | $\lVert\boldsymbol\omega_\perp\rVert^2 = 29$, $\lVert\mathbf{h}\rVert^2 = 1080$, $2T = 192$ |

All values are exact rationals; no floating-point tolerance is used in the anchor. The
translational `FUTURE_COMPARISON_TOL` does **not** transfer: a rotational implementation must
integrate numerically, so its tolerance must come from a measured convergence study (RS-005,
V-NUM-01) in the phase that builds it.

*Case selection was driven by exact discrimination analysis over ten candidates and 26
mutations.* Each rejected construction voids at least one mutation:

| Rejected construction | What it hides |
|---|---|
| $J_\parallel = J_\perp$ | λ = 0; eleven mutations invisible |
| zero transverse rate | 21 mutations invisible |
| $J_\parallel/J_\perp = \tfrac12$ | the sign-slipped small-nutation inertial precession rate $-\frac{J_\parallel}{J_\perp}\omega_\parallel$ equals λ |
| $J_\parallel/J_\perp = 2$ | omitting the ratio |
| $J_\perp = 1$ | omitting the division |
| $\omega_\parallel = 1$ | omitting $\omega_\parallel$ |
| a zero transverse component | a symmetrically coupled solution |
| equal transverse components | a swap, at $t=0$ |

The avoidances are asserted, and each trap is demonstrated, as tests.

`LIMITATION` — blind spots, recorded rather than hidden:

- **Samples at multiples of π/2 alias.** A wrong rate $\lambda' = -3\lambda$ — exactly
  $\frac{J_\perp-J_\parallel}{J_\parallel}\omega_\parallel$, with numerator and denominator both wrong —
  coincides with λ at the quarter- **and** half-cycle samples. It is caught only by the
  $\arctan(3/4)$ sample, which is incommensurate with π, and by $\dot{\boldsymbol\omega}(0)$. That is
  why that sample exists.
- The half-cycle sample alone is also blind to $\lambda\to-\lambda$ and to both wrong-coupling
  forms tested.
- Some wrong rates ($\omega_\parallel$ omitted, $\lVert\mathbf{h}\rVert/J_\perp$, a perturbed
  $\omega_{\parallel,0}$) land on no exactly representable phase at any sample. They are detected
  **exactly** only through $\dot{\boldsymbol\omega}(0)$; a future comparison of sampled trajectories
  would detect them in floating point only.
- $\frac{J_\perp-J_\parallel}{J_\perp}\omega_\parallel$ is numerically $-\lambda$, and a phase of $\lambda t/2$
  is here the same function as $-\frac{J_\parallel}{J_\perp}\omega_\parallel$. Each pair is counted once.

**Mutation evidence, 2026-09-10.** The harness ran on a temporary copy, the executed file was
verified on every run, and the repository file was never modified.
- Control: 63/63 pass in the module.
- A deliberately incorrect frozen $\boldsymbol\omega(\pi/4)$ fails 15 tests.
- Every one of 19 further mutations is detected (failure counts in parentheses):
  - reversed λ literal (24);
  - oracle builder rotating the wrong way (12);
  - λ from the wrong denominator (22);
  - λ with $\omega_\parallel$ omitted (24);
  - frozen transverse components (12);
  - swapped initial components (24);
  - a reversed component sign (24);
  - a perturbed initial rate (24);
  - a wrong frozen $\omega_\parallel$ (12);
  - a non-zero $\dot\omega_\parallel$ (7);
  - the phase of $\arctan(4/3)$ frozen instead of $\arctan(3/4)$ (7);
  - a reversed frozen derivative (13);
  - the spherical trap (29);
  - the zero-transverse trap (26);
  - the $J_\parallel/J_\perp = \tfrac12$ trap (27);
  - the $J_\perp = 1$ trap (29);
  - a left-handed skew form (26);
  - an $x_B$-symmetric literal built by reflection (1).
- No mutation caused a failure outside the V-EOM-04 classes.

**Re-verified 2026-09-11 after the ADR-0010 rename.**
- **Mutation harness:** re-run with its targets updated to the new identifiers. Control 63/63; each
  of the 20 runs gave **exactly** the failure count recorded above.
- **Syntax tree:** the module's tree before and after is identical once the renames are reversed and
  string text is blanked; the renames covered names, attributes, arguments and `subTest` keyword
  labels.
- **Counts:** the module's 713 numeric literals, 144 assertion calls and 63 test methods are
  unchanged.

**What V-EOM-04 does not establish:** quaternion attitude propagation, the inertial precession
rate, numerical integration, translational coupling, variable mass (V-EOM-09), products of
inertia (V-EOM-05), or a complete 6-DOF simulation. It verifies an angular-velocity closed form
for one limiting case; it validates nothing.

`FINDING` (2026-09-10) — **identifier collision.** RS-004 §7 defined **V-EOM-03** as *torque-free,
constant rate about a principal axis*, while the frozen V-EOM-03 above is the body-force anchor named
by its commissioning brief. The RS-004 case was unanchored and its identifier ambiguous.
**Resolved by ADR-0010:** V-EOM-03 stays with the frozen body-force anchor. The never-frozen
principal-axis case is renumbered **V-EOM-10**, and RS-004 §7 records its former number.

`FINDING` (2026-09-10) — **status wording.** RS-004 §4.3 marked the gyroscopic term, and the
aerodynamic and propulsive moments, "**Implemented**", while RS-004's own header and this document
record that no dynamics code exists. **Resolved by ADR-0010:** RS-004 §4.3 now reads *Specified*,
*Verification anchor established*, *Analytically verified* and *Not yet implemented*. **Implemented**
is reserved for production code that exists and passes named tests. ADR-0010 also lists stale
*under*-claims elsewhere — README, the handoff snapshot, the assumptions header, three specification
headers — for a maturity-label decision by the researcher.

### Products-of-inertia anchor — V-EOM-05

**V-EOM-05 — torque-free rigid body whose body axes are *not* principal axes.** Frozen
2026-09-12 in `tests/test_eom_anchors.py`, before any rotational dynamics implementation exists.

`FINDING` (2026-09-11, recorded in `handoffs/current_state.md` §6) — **the previous configuration could
not test its own claim.** RS-004 §7 specified the case with *principal moments $J_{xx}<J_{yy}<J_{zz}$,
all distinct*, which is a **diagonal** tensor, while listing "products of inertia, full tensor
handling" as what it isolates. The three products are then identically zero, so zeroing $J_{xy}$,
$J_{xz}$ or $J_{yz}$, or diagonalising $\mathbf{J}$, left the case bit-identical. The defect was in
the case, not the equation. **Resolved by this repair**, which changes the configuration and leaves
the governing equation, every other anchor and the ADR-0010 conventions untouched.

**What it verifies.** For $\mathbf{J}\dot{\boldsymbol\omega} + \boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega) = 0$
(RS-004 §4.1, ADR-0009), the **instantaneous** angular acceleration
$\dot{\boldsymbol\omega} = -\mathbf{J}^{-1}[\boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega)]$ at two
frozen states, plus the invariant rates. An asymmetric torque-free body has **no elementary
closed-form trajectory** — the solution runs on Jacobi elliptic functions — so no trajectory is frozen
and none should be.

**Coordinate convention.** The tensor is resolved in **body axes** $B$ (NOTATION §5.1), with
$\mathbf{J} = [[J_{xx}, J_{xy}, J_{xz}], [J_{xy}, J_{yy}, J_{yz}], [J_{xz}, J_{yz}, J_{zz}]]$ and the
products entering $\mathbf{J}\boldsymbol\omega$ with a **plus** sign; RADIUS does not use the
leading-minus definition. This case says nothing about the $x_B$ symmetry-axis convention of
ADR-0010: an axisymmetric vehicle is the special case in which the products vanish. Here they
deliberately do not, which is what an asymmetric body — or a symmetric one whose structure is
misaligned with the body frame — actually looks like.

| Frozen case | |
|---|---|
| $\mathbf{J}$ (kg·m²) | $[[8, -1, -2],\ [-1, 7, -3],\ [-2, -3, 5]]$ |
| Symmetric | yes, asserted entry by entry |
| Positive definite | leading minors $(8,\ 55,\ 163)$, all $>0$ (Sylvester) |
| Triangle inequalities | minors of $S=(\operatorname{tr}\mathbf{J}/2)\mathbf{I}-\mathbf{J}$ are $(2,\ 5,\ 7)$, all $>0$ |
| Principal moments | $\approx(2.0205,\ 8.6111,\ 9.3684)$, condition number $\approx4.64$; eigenvectors nowhere near the body axes |
| Products of inertia | $J_{xy}=-1$, $J_{xz}=-2$, $J_{yz}=-3$ — non-zero, distinct, and **not all of one sign** |
| State 0 | $\boldsymbol\omega=(4,-6,7)$ → $\mathbf{J}\boldsymbol\omega=(24,-67,45)$ → RHS $(-199,12,124)$ → $\dot{\boldsymbol\omega}=(-18,9,23)$ |
| State 1 | $\boldsymbol\omega=(7,-5,-8)$ → $\mathbf{J}\boldsymbol\omega=(77,-18,-39)$ → RHS $(-51,343,-259)$ → $\dot{\boldsymbol\omega}=(-12,31,-38)$ |
| Invariants | state 0: $\lVert\mathbf{h}\rVert^{2}=7090$, $2T=813$; state 1: $7774$, $941$ |
| Invariant rates | $\mathbf{h}\cdot(\mathbf{J}\dot{\boldsymbol\omega}) = 0$ and $\boldsymbol\omega\cdot(\mathbf{J}\dot{\boldsymbol\omega}) = 0$, exactly, at both states |

Every frozen number is an integer although $\det\mathbf{J}=163$ is prime — itself a check, since
almost any transcription slip makes $\dot{\boldsymbol\omega}$ fractional.

**A tensor can be symmetric and positive definite and still not be a body.** The principal moments
must also satisfy $J_i + J_j \ge J_k$, which holds exactly when $S$ above is positive semidefinite.
$[[10,2,1],[2,8,3],[1,3,6]]$ is symmetric positive definite and **fails** that test; it is asserted as
a counter-example so the check cannot quietly be dropped.

**The oracle was calculated twice, by different routes** (`CALCULATION`, 2026-09-12), and the two
agree exactly: (A) adjugate-over-determinant inverse with generic matrix helpers; (B) Cramer's rule
with every determinant written out as an explicit scalar expression, sharing no helper with (A). Both
are re-executed as tests. Substituting the frozen $\dot{\boldsymbol\omega}$ back into
$\mathbf{J}\dot{\boldsymbol\omega}$ reproduces the right-hand side exactly, at both states.

**How the products of inertia change the answer.** Deleting them — keeping the same diagonal —
gives $\dot{\boldsymbol\omega} = (-21/2,\ -12,\ -24/5)$ at state 0 instead of $(-18, 9, 23)$, a
max-norm difference of $139/5 = 27.8$ rad·s⁻²; at state 1, $(10, 24, -7)$ instead of $(-12, 31, -38)$,
a difference of $31$ rad·s⁻². Each product matters individually: zeroing $J_{xy}$, $J_{xz}$, $J_{yz}$
shifts $\dot{\boldsymbol\omega}$ by $157/10$, $4218/203$ and $5841/247$ rad·s⁻² respectively.

*Case selection was driven by mutation analysis.* A candidate whose three products were all
**positive** was rejected: "replace each product by its absolute value" is then the identity
operation and escapes undetected. The chosen tensor has all three negative, so that mutation flips
all three and is caught with a margin of $922/17$ rad·s⁻².

**Mutation evidence** (2026-09-12; temporary copy, executed file verified per run, repository file
never modified): **27 mutations, 27 detected, 0 escaped**; control clean. Tensor: each product zeroed
(19/18/18 tests fail), each product sign-flipped (18/18/17), all products deleted (25), products
replaced by $|\cdot|$ (19), a non-symmetric $\mathbf{J}$ (17), a tensor violating the triangle
inequality (22). Equation: minus sign dropped (12), inverse omitted (12), cross term dropped from the
residual (2), residual sign reversed (2), Cramer oracle sign error (2), diagonalisation helper made a
no-op (3), triangle matrix using $\operatorname{tr}$ instead of $\operatorname{tr}/2$ (1), wrong
leading-minor formula (2). Frozen values: each of $\dot{\boldsymbol\omega}_0$, $\dot{\boldsymbol\omega}_1$,
$\mathbf{h}_0$, the right-hand side and the products gap (13/5/2/3/2). State: $\boldsymbol\omega_0$
permuted (13), one component negated (13), one component zeroed (14), state 1 duplicated from state 0 (7).

`LIMITATION` — **structural blind spots**, which are properties of the equation rather than of this
case, and are asserted as facts so they are not mistaken for coverage:

- **Transposing $\mathbf{J}$ is undetectable**, because $\mathbf{J}$ is symmetric: the mutation is the
  identity operation. No case built on a symmetric tensor can catch it.
- **$\boldsymbol\omega \to -\boldsymbol\omega$ leaves $\dot{\boldsymbol\omega}$ unchanged**, because the
  right-hand side is quadratic in $\boldsymbol\omega$.
- **$\mathbf{J} \to k\mathbf{J}$ leaves $\dot{\boldsymbol\omega}$ unchanged**, because $\mathbf{J}^{-1}$
  and $\mathbf{J}$ cancel — the case cannot police the *scale* of an inertia tensor, only its shape.
- Dropping the minus sign, reversing the cross-product order, and writing
  $\mathbf{J}\dot{\boldsymbol\omega} = +\boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega)$ are **one**
  mutation numerically, not three. Counted once.
- Being an instantaneous anchor, it cannot see errors that only appear after integration: time
  stepping, attitude propagation, or any error preserving the derivative at these two states.

**What V-EOM-05 does not establish:** a trajectory, an integrator, attitude propagation, variable
mass, or a complete 6-DOF simulation. **No production rotational-dynamics implementation exists** for
it to test; the anchor is frozen so that one can be written against it.

### Traceability — audit findings to their guarding anchors

The two load-bearing corrections from the pre-implementation audit have named,
independent anchors rather than being covered incidentally:

| Finding | Assumption | Anchor | Guards |
|---|---|---|---|
| **F-3** | `A-NUM-05` | **V-FRM-09** | `dcm_b_from_i_quat` is scale-invariant *and* agrees with an independently derived DCM. Uses a non-unit, non-axis-aligned quaternion whose exact rational DCM is hand-derived |
| **F-4** | — | **V-FRM-10** | `T(qa ⊗ qb) = T(qb) T(qa)`. Both sides pinned to literals; the reversed order is pinned to a *second* literal, so the wrong answer is anchored too |
| **F-2** | — | **V-FRM-05** → `radius.frames.dcm_b_from_w` | `T_BW = R_y(α) R_z(−β)`, **implemented and verified**. The corrected relationship was **independently re-derived** rather than assumed: inverting the definitions of α and β forces the first column of `T_BW` to be `(cos α cos β, sin β, sin α cos β)`, which the corrected form satisfies and the superseded `R_y(−α)R_z(β)` contradicts. Anchors at (α=0, β=30°) and (α=30°, β=60°), each pinned as a literal, with the superseded and reversed-order matrices pinned too |

**V-FRM-05 verifies a coordinate-transformation convention, not an aerodynamic model.**
No coefficient, force or moment appears in it or in `dcm_b_from_w`. Implementing the
transform establishes that the *convention* is encoded correctly; it says nothing about
whether any aerodynamic model is physically valid, and it leaves the Q8 gate (no
traceable aerodynamic coefficient source, `A-AER-03`) exactly where it was — **open**.

Mutation evidence for `dcm_b_from_w` (2026-09-09, module path verified inside the
interpreter running the suite): the correct form passes 31/31; the wrong sideslip sign,
the superseded `R_y(−α)R_z(β)`, and the active/passive transpose each fail 4 tests; the
reversed composition order fails 3 — three rather than four because case A (α=0) cannot
distinguish composition order, which the anchor asserts explicitly.

`LIMITATION` on V-FRM-09: it establishes the observable half of `A-NUM-05`
(scale invariance) but **cannot** establish that the implementation divides rather than
normalising — the two are the same mathematical map, agreeing to 5.6e-16 over 2000
random inputs. Branch-freedom is a source property, verified by reading, not by testing.
Recorded so that a passing V-FRM-09 is not read as full coverage of `A-NUM-05`.

The **"independent reference data held: none"** row above is the important one, and it is a
`LIMITATION` on the whole project: **RADIUS currently has no path to validation of its trajectory
output**, because it has no independent benchmark to compare against. This is recorded in `research/SOURCES.md` as an open gap. Until it closes, RADIUS
can become a thoroughly verified implementation of a model whose fidelity to reality is entirely
unestablished — and it must say so.

---

## 3. Verification: four kinds

### 3.1 Analytical

The strongest evidence available, because the reference is exact and independent of the
implementation. Specified in RS-004 §7; anchors:

- **V-EOM-01, V-EOM-02, V-EOM-03** — force-free straight line; constant gravity giving an
  exact parabola; and a constant non-zero body force at a fixed attitude, which is the one
  that exercises the `T_IB` force transformation. **Frozen as exact oracles** in
  `tests/test_eom_anchors.py`; see §2.
- **V-EOM-04** — torque-free axisymmetric coning at
  $\lambda = \frac{J_\parallel-J_\perp}{J_\perp}\omega_\parallel$ (first written
  $\frac{J_z-J_t}{J_t}\omega_z$ with symmetry about $z$; reconciled by ADR-0010); a *quantitative*
  check on the gyroscopic term. **Frozen as an exact oracle** in the canonical frame $P$ and in
  RADIUS body axes, symmetry axis $x_B$ (§2). λ is the **body-frame** transverse rate, positive
  right-handed about the positive symmetry axis — not the inertial precession rate.
- **V-EOM-06 / V-VM-01 — Tsiolkovsky.** $\Delta v = \lVert\mathbf{c}\rVert\ln(m_0/m_f)$: the only
  exact check on the variable-mass coupling, and derived independently of RADIUS's own derivation.
- **V-ATT-02** — closed-form quaternion under constant body rate.

**Conservation and symmetry checks** (V-EOM-05, V-NUM-08) deserve separate mention. V-EOM-05 is
now frozen (§2) and carries exact invariants for V-NUM-08 to measure drift against. An invariant is in
one respect a *stronger* test than a trajectory match: it must hold at every step, for every initial
condition, without a reference solution existing at all.

### 3.2 Numerical

Properties of the method rather than of the physics.

- **V-NUM-01, order of accuracy.** The single most informative test in the suite: measured log-log
  slope of error against $h$, requiring 4 for RK4 and 1 for Euler. It detects a large class of subtle
  errors — a mis-signed term often leaves a plausible trajectory but a wrong convergence rate. The
  roundoff floor must be identified and excluded from the fit (RS-005 §5), or the study reports a
  spurious flattening as a defect.
- **V-NUM-03, determinism.** Load-bearing for the publication policy (ADR-0008), not a nicety.
- **V-NUM-06**, order preserved *across* an event — where order of accuracy quietly dies.
- **V-ATT-05**, norm drift with normalisation **off** behaving as predicted. A suite that only checks
  the corrected system cannot distinguish "the correction works" from "there was nothing to correct".

### 3.3 Dimensional

Every term in every equation, audited symbolically: every term in $\dot{\mathbf{v}}$ is m·s⁻², every
term in $\dot{\boldsymbol\omega}$ is rad·s⁻². Cheap, and catches a whole class of error that
otherwise surfaces as a mysterious factor.

### 3.4 Regression

Once a reference case is verified, it is frozen with a tolerance so that later changes cannot
silently alter behaviour. Reference trajectories are small, carry full metadata, and live under
`validation/reference/` (the one re-inclusion in the `.gitignore`'s bulk-array denial).

A regression test **is not** verification evidence. It establishes that behaviour has not changed —
including, if the original was wrong, that it is still wrong in the same way.

---

## 4. Test ordering

Prerequisites first, so a failure localises:

```
math/quaternion  →  frames  →  state  →  attitude propagation
    →  translational dynamics  →  rotational dynamics
    →  integrator order  →  events  →  variable mass
    →  atmosphere  →  aerodynamics  →  coupled trajectory
```

A coupled-trajectory failure with everything upstream passing points at the coupling. A
coupled-trajectory failure with quaternion tests also failing points at the quaternions. The ordering
is what makes the second diagnosis available.

---

## 5. Validation: what it would require

Not achievable today. Recorded so the requirement is concrete rather than aspirational.

| Need | Status |
|---|---|
| An independent published 6-DOF benchmark: stated initial conditions, parameters, and reference output | **Not found.** The binding gap |
| A stated purpose — "adequate for what?" | Not yet stated, because there is no result to scope |
| A stated tolerance, declared **before** comparison | Not yet stated |
| A traceable aerodynamic coefficient set | **Not found** (`A-AER-03`) |
| Bounds on omitted physics — jet damping, CM-motion momentum | **Unbounded** (`A-VM-03`, `A-VM-02`) |

The last row is decisive. Validating a model with unbounded modelling error measures the error, not
the model.

**A near-term partial exception.** V-ATM-03 compares the atmosphere implementation against the
published U.S. Standard Atmosphere tables. That is a comparison against an external document, which
makes it stronger than internal consistency — but the 1976 standard is itself an idealised annual
mean, so agreement verifies that RADIUS implements *the standard*, not that the standard describes
the air. It is verification against an external reference: a real intermediate category, and it must
be described as such rather than promoted to validation.

---

## 6. Credibility reporting

Following the spirit of SRC-013 (NASA-STD-7009), a RADIUS result is reported with, not as, a number:

verification status · validation status · input pedigree (where parameters came from, including
`arbitrary-illustrative`) · uncertainty in the result · robustness (sensitivity to step size, seed,
parameters) · use history · limitations.

**RADIUS does not claim compliance with NASA-STD-7009.** Compliance is a formal process this project
has not undertaken; claiming it would be false. The standard is used as a checklist for what a
credible result report contains.

---

## 7. Rules that hold regardless of results

- A result that looks too good is a **hypothesis about a bug** until investigated. An error falling
  faster than the method's order, or a conservation law satisfied to machine precision where it should
  not be, gets investigated before it gets reported.
- A falsified prediction appears in the summary and the conclusions, not a footnote.
- Test tolerances are declared **before** the test is run. A tolerance loosened after seeing a failure
  is documented as such, with the reason, or it is not changed.
- A gate that cannot be evaluated **raises**; it never returns a pass. If $\alpha$ is `NaN`, the
  validity gate does not silently succeed.
- Verification tests are published with the claim they support. A claim of verification without the
  tests is an assertion.
