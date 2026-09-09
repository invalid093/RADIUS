# RADIUS — Research Specification Quality Gate

**Purpose.** Before substantial implementation begins, the specification must let another aerospace
engineer answer thirteen questions by reading the repository. This document answers them, points at
the evidence, and — where an answer is incomplete — says so.

**Gate rule:** a question that cannot be answered clearly means *continue researching that subsystem*,
not *implement it and find out*.

> **Re-examined 2026-09-09** by `PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`, which found **four
> defects this gate did not catch** — one of them a factor-of-two error in the variable-mass
> rotational equation (Q4). The verdict below stands *after* those corrections. The gate's failure
> mode is recorded in §15: it checked that each specified test was correct, not that the specified
> tests **covered the equations as written**. No rotational test ran with $\dot m \neq 0$.

**Verdict:** **PASS for Phases 2–6** (frames, math utilities, state, equations of motion, integration,
analytical verification). **NOT PASS for Phase 8** (aerodynamics) — see Q8 and §14.

---

### 1. What is the state?

$\mathbf{x} = [\mathbf{p}^{I},\ \mathbf{v}^{I},\ q_{BI},\ \boldsymbol{\omega}^{B},\ m] \in \mathbb{R}^{14}$
— inertial position and velocity, attitude quaternion, body angular velocity, mass. The manifold is
$\mathbb{R}^{13}\times S^{3}$, not $\mathbb{R}^{14}$: 13 degrees of freedom plus one constraint.

Time is not a state; the inertia tensor is not a state. Actuator, controller, flexible-body and
estimator states are deliberately absent, with the phase each would arrive in recorded.

→ **RS-003**, ADR-0005. **Answered.**

### 2. What coordinate frames are used?

$I$ (flat-Earth NED, treated as inertial), $B$ (body, origin at the instantaneous CM), $W$ (wind,
derived, never integrated), $E$ (ECEF — deferred, and named as deferred rather than sketched).

All right-handed, orthonormal, $z$ down. Each has a stated origin, axis definition, and — the part
usually omitted — a statement of what it is assumed inertial *with respect to*.

→ **RS-001**, ADR-0003. **Answered.**

### 3. What are the transformation conventions?

Passive transformations, subscripts read "to ← from": $\mathbf{v}^B = \mathbf{T}_{BI}\mathbf{v}^I$.
Euler 3-2-1 (yaw, pitch, roll) with the elementary matrices written out. Quaternion: **Hamilton
product, scalar-first, $q_{BI}$**, with $\mathbf{T}_{BI}(q)$ given explicitly and checked against a
pure-yaw case during specification.

The notation distinguishes the frame a vector is *resolved in* from the frame it is *differentiated
in* — the omission that produces missing transport terms.

→ **NOTATION_AND_CONVENTIONS.md**, ADR-0003. **Answered.**

### 4. What equations govern the state?

$$\dot{\mathbf{p}}^{I}=\mathbf{v}^{I},\quad
m\dot{\mathbf{v}}^{I}=\mathbf{T}_{IB}[\mathbf{F}^{B}_{\text{aero}}+\mathbf{F}^{B}_{\text{prop}}]+mg(h)\hat z_I,\quad
\dot q=\tfrac12\boldsymbol{\Omega}(\boldsymbol\omega)q$$
$$\mathbf{J}(t)\dot{\boldsymbol\omega}+\boldsymbol\omega\times\big(\mathbf{J}(t)\boldsymbol\omega\big)=\mathbf{M}_{\text{ext}},\quad
\dot m=-\dot m_{\text{out}}$$

Every term is named, attributed, and marked implemented or omitted. Both variable-mass equations are
**derived rather than assumed**: the translational form with the two common wrong versions explained,
and the rotational form showing that the angular-momentum flux cancels $\dot{\mathbf{J}}\boldsymbol\omega$
exactly under `A-VM-05`. Jet damping is **omitted and defined** — no longer an undefined symbol inside
a governing equation.

→ **RS-004**. **Answered — after correction.** The rotational equation as originally gated contained
a $-\dot{\mathbf{J}}\boldsymbol\omega$ term that is wrong for mass ejection (it models internal
redistribution) and produced a factor-of-two spurious spin-up. Corrected by ADR-0009; the
$\dot{\mathbf{J}}\boldsymbol\omega$ terms cancel exactly under `A-VM-05`.

### 5. What assumptions are being made?

31 registered assumptions across eight groups, each with an ID, a status, a **consequence if wrong**,
and an action. Code will cite IDs at the point of dependence; experiment manifests will list the IDs
each result depends on.

The heaviest: `A-FRM-01` (flat non-rotating Earth — *quantified*), `A-EOM-01` (rigid body — accepted
as scope, not defended as physics), `A-VM-03` (jet damping omitted — **magnitude unbounded**),
`A-AER-03` (coefficients arbitrary and illustrative).

→ **docs/assumptions.md**. **Answered.**

### 6. How is attitude represented?

Quaternion internally; DCM computed on demand and never stored; Euler angles at input/output only.
The decisive argument is that a 3-2-1 Euler singularity at $\theta=\pm90°$ is the **nominal**
condition for a vertically launched vehicle, not an edge case. Norm maintained by post-step
normalisation, explicitly **not** inside RK stages.

→ **RS-002**, ADR-0004. **Answered.**

### 7. How is the system integrated numerically?

Fixed-step classical RK4, with explicit Euler retained as a verification comparator and Dormand–Prince
RK5(4) evaluated and deferred with a stated revisit condition. Requirements were ranked before methods
were considered: determinism and measurable order of accuracy above raw efficiency.

Events located by bisection, with restart across discontinuities. Proposed $h=10^{-3}$ s, flagged as a
**proposal, not a result**.

→ **RS-005**, ADR-0006. **Answered.**

### 8. How are forces and moments represented?

Body-axis coefficients $(C_A, C_Y, C_N, C_l, C_m, C_n)$ with dynamic pressure and reference
dimensions; a linear-in-$\alpha,\beta$ initial model with rate damping; explicit transfer of moments
from the geometric reference point to the instantaneous CM; a validity gate that **raises** outside
$|\alpha|,|\beta| < 10°$ and raises on `NaN`.

**Incompletely answered.** Two gaps:

- **No traceable coefficient source** (`A-AER-03`). Every aerodynamic result would be scoped to "a
  hypothetical vehicle with the stated coefficients".
- **No Mach dependence** (`A-AER-05`), which may make the model invalid across most of a typical
  trajectory — assessed as a risk, not yet quantified.

→ **RS-007**. **Partially answered — this is what blocks Phase 8.**

### 9. How is atmospheric behaviour represented?

Two models: an exponential baseline (a verification instrument, not a physical model) and the U.S.
Standard Atmosphere 1976 layered model to 84.852 km geopotential, with equations, constants and layer
table given. Base pressures are derived recursively from $p_0$ rather than transcribed, so a
transcription error appears as a detectable discontinuity. Out-of-domain altitude **raises**.

Caveat recorded: the layer table values must be checked against SRC-008 directly before
implementation (`A-ATM-01`).

→ **RS-006**. **Answered, with one verification action outstanding.**

### 10. How is variable mass abstracted?

Two interfaces: `ExternalForceSource` (force, moment, mass-flow rate, active flag) and
`MassProperties` (mass, inertia, inertia rate, CM offset). No hardware content of any kind —
propulsion enters as three numbers per evaluation.

Depletion is an **event**, never a clamp; $m \le 0$ raises. CM migration feeds the aerodynamic moment
transfer. `A-VM-01` states the unenforceable consistency contract between declared force and declared
mass flow, and records both in the manifest so violations are detectable.

→ **RS-008**. **Answered.**

### 11. How will each subsystem be verified?

Approximately 65 specific tests are specified with pass criteria, before any code exists:
V-FRM-01…10, V-ATT-01…08 (plus V-ATT-02b), V-STA-01…05, V-EOM-01…09, V-NUM-01…09, V-ATM-01…09,
V-AER-01…09, V-VM-01…10. Ordered so failures localise.

**Five were added by the pre-implementation audit** — V-EOM-09/V-VM-10 (variable-mass spin),
V-FRM-09 (non-unit quaternion in RK stages), V-FRM-10 (quaternion composition order), V-ATT-02b
(non-principal rotation axis, which a principal-axis test provably cannot replace), V-NUM-09 and
V-ATM-09. Each catches a defect the original suite could not.

Anchors: Tsiolkovsky (variable mass), torque-free coning (gyroscopic term), order-of-accuracy slope
(integrator), U.S. Standard Atmosphere table comparison (atmosphere), and hand-computed rotations
(conventions — the only test class that catches a *uniformly applied* wrong convention).

→ **VERIFICATION_AND_VALIDATION.md** and each RS document. **Answered.**

### 12. What claims can and cannot currently be made?

**Can be made:** none about behaviour. Nothing is implemented. The only supportable claims today are
about the specification itself — that it exists, that it fixes the conventions, and that it names its
own gaps.

**Cannot be made, and will not be made even after Phases 2–6 succeed:**

- that RADIUS is **validated** — no independent reference data exists, and passing tests is
  verification only;
- any statement about a **real vehicle** — coefficients are arbitrary, the vehicle is hypothetical;
- any claim of **flight-readiness or operational suitability**;
- any claim about **rotational damping** — jet damping is omitted with unbounded magnitude
  (`A-VM-03`);
- any accuracy claim beyond the flat-Earth validity domain (~10 km range, ~60 s), and that bound is
  itself an estimate of neglected terms rather than a measurement.

→ **Answered, and this is the answer the project most needs to keep saying.**

### 13. How could RADIUS eventually interface with AURA?

RADIUS emits documented, self-describing output; AURA reads it through an adapter that lives **in
AURA**. RADIUS never imports AURA, never depends on its schemas, and no RADIUS design decision may be
justified by AURA's needs. Four preconditions are stated, all currently unmet — the binding one being
that a specific question requiring the combination must exist first.

→ **AURA_INTERFACE.md**, ADR-0002. **Answered — and the answer is "not yet, and here is what would
have to be true".**

---

## 15. What this gate missed, and why

`OBSERVATION`. The first pass of this gate returned PASS for Phases 2–6 while four defects were
present, one of them changing a governing equation. The cause is worth recording because it
generalises:

- **Q11 asked whether each subsystem had verification tests.** It did not ask whether the tests
  *exercised the equations as written*. Every rotational test ran at constant mass, so the
  variable-mass rotational equation was tested by nothing at all.
- **Q3 and Q6 confirmed the conventions were stated.** They did not confirm the stated conventions
  were *mutually consistent*: the wind-frame composition contradicted the $\alpha,\beta$ definitions
  three lines below it.
- **Q7 confirmed the integrator was specified.** It did not ask what $\mathbf{T}_{BI}$ does at the
  non-unit quaternions an RK stage necessarily produces.

The pattern: the gate checked that each answer *existed*, not that the answers were *consistent with
each other* or *covered by tests*. Future gate evaluations must ask both.

## 14. Gate verdict

**PASS for Phases 2–6.** State, frames, conventions, attitude, equations of motion, numerical
integration and their verification are specified to the level required. Implementation may begin, in
the documented order.

**NOT PASS for Phase 8 (aerodynamics).** Q8 is incomplete: no traceable coefficient source, and the
Mach-dependence gap is unassessed. The audit did **not** close this by inventing coefficient data. Per the gate rule, the correct action is to continue researching
that subsystem — searching for a published generic coefficient set, and assessing whether a
Mach-independent model is usable at all — rather than implementing it and discovering the problem
afterwards.

Phase 7 (atmosphere) may proceed once the layer table is checked against SRC-008.

**Three unbounded quantities** are recorded rather than glossed: jet damping (`A-VM-03`), CM-motion
momentum (`A-VM-02`), and the flat-Earth validity bound (an estimate, not a measurement). Each
constrains what may eventually be claimed, and each is named in `docs/assumptions.md` with its
consequence.
