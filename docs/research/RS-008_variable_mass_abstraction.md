# RS-008 — Generic Variable-Mass and External-Force Abstraction

**Status:** Specification. Not implemented, not verified.
**Depends on:** RS-003, RS-004
**Primary source:** SRC-007 (Eke, *Dynamics of Variable Mass Systems*)

---

## 1. Scope — read this first

This document specifies a **mathematical abstraction** for studying variable-mass rigid-body dynamics.
It is not a propulsion document.

Per the hard scope boundary in `CLAUDE.md`, RADIUS contains **no** propulsion hardware content: no
construction, manufacture, chemistry, assembly, geometry, or performance tuning of any physical
system. Propulsion enters RADIUS as three numbers per evaluation — a force, a mass-flow rate, and
optionally a moment — supplied through an interface. *How* such a force might physically be produced
is out of scope and is not documented here.

SRC-007 is cited for its equations of motion only. Its design-relevant content (nozzle and chamber
geometry, propellant configuration) is not used.

The reason this boundary costs nothing scientifically: the interesting mathematics of variable-mass
dynamics — the momentum-flux term, the inertia-rate moment, jet damping, the CM shift — is entirely
independent of how the mass leaves. That is precisely what makes the abstraction correct rather than
merely convenient.

---

## 2. The mathematical problem

A rigid body of time-varying mass, expelling matter that carries momentum away. The distinctive
feature is that the "system" is **open**: mass crosses its boundary, so the conservation laws must be
applied to a closed system that momentarily contains the vehicle plus the mass about to leave.

The consequences, derived in RS-004 §3–4:

| Effect | Term | Status |
|---|---|---|
| Momentum flux ("thrust") | $\mathbf{F}_{\text{prop}} = \dot m\,\mathbf{c}$ | Supplied by interface |
| Moment from an offset thrust line | $\mathbf{r}\times\mathbf{F}_{\text{prop}}$ | Supplied, or computed from a declared offset |
| Inertia-rate moment | $-\dot{\mathbf{J}}\boldsymbol{\omega}$ | Computed from the mass model |
| Jet damping | $\mathbf{M}_{\text{jet}}$ | **Omitted** — `A-VM-03` |
| CM migration | $\mathbf{r}_{\text{ref}/\text{cm}}(t)$ | Computed from the mass model; feeds RS-007 §4 |

Notably absent: any $\dot m \mathbf{v}$ term. Its appearance in a derivation is a diagnostic that the
open/closed system distinction was mishandled (RS-004 §3.1).

---

## 3. Interfaces

Two interfaces, deliberately separate.

### 3.1 `ExternalForceSource`

```
force_body(t, state)   -> R^3   [N]      force in body axes
moment_body(t, state)  -> R^3   [N·m]    moment about the CM, in body axes (may be zero)
mass_flow_rate(t, state) -> float [kg/s] rate of mass LOSS, >= 0
is_active(t, state)    -> bool           whether the source is producing
```

**Contract.** A source declaring a non-zero `mass_flow_rate` and a `force_body` inconsistent with it
is committing an identifiable modelling error. RADIUS does not enforce consistency — enforcing it
would require RADIUS to know the exhaust velocity, which is exactly the hardware detail it declines to
model — but the contract is stated so the error is nameable. Registered as `A-VM-01`, and
`is_active` plus the declared flow rate are recorded in the result manifest so an inconsistent source
is detectable after the fact.

**Multiple sources** are summed. Each declares its own flow rate; the total is $\sum \dot m_{\text{out},i}$.

### 3.2 `MassProperties`

```
mass(t)               -> float   [kg]     total mass
inertia_body(t, m)    -> 3x3     [kg·m²]  inertia tensor about the CM, in body axes
inertia_rate_body(t, m) -> 3x3   [kg·m²/s]
cm_offset_body(t, m)  -> R^3     [m]      CM position relative to the geometric reference point
```

Separated from the force source because they answer different questions. A vehicle can have mass
properties without a force source (coasting), and the same mass model may serve several force
sources. Coupling them would make a coasting phase a special case of thrusting, which is backwards.

---

## 4. Inertia rate

$\dot{\mathbf{J}}$ enters the rotational equation directly (RS-004 §4). Two ways to obtain it:

- **Analytically**, from a differentiable mass model. Exact, and requires the mass model to be
  differentiable — a real constraint on what mass models are permitted.
- **By central finite difference** on $\mathbf{J}(t)$. Simple, model-agnostic, and introduces a
  truncation error.

**Decision: analytical where the mass model provides it; finite difference only as a documented
fallback.**

`HYPOTHESIS`, flagged for testing: a finite-difference $\dot{\mathbf{J}}$ evaluated **inside an RK
stage** is a second, nested discretisation. Its error does not necessarily behave like the
integrator's, and it could degrade the observed order of accuracy. If V-NUM-01 shows a slope below 4
once the mass model is active, this is the first hypothesis to test (RS-005 §11). Recording the
prediction now is what makes the eventual diagnosis fast rather than mysterious.

---

## 5. Centre-of-mass migration

As mass depletes, the CM moves relative to the vehicle geometry. Three consequences, all real:

1. **The body frame's origin moves** (RS-001 §2.2). The frame's *orientation* is structural; its
   origin tracks the CM.
2. **Aerodynamic moments must be transferred** to the moving CM (RS-007 §4). This is what determines
   static stability, and it changes through the burn.
3. **Thrust offset changes** even for a fixed thrust line, because the moment arm is measured from the
   CM.

`ASSUMPTION` `A-VM-02`: the CM shift is treated as **quasi-static** — its position enters the moment
transfer, but the momentum associated with the CM *moving relative to the structure*
($\ddot{\mathbf{r}}_{\text{cm}}$ terms) is neglected. Justified when the CM moves slowly compared with
the vehicle's rotational timescale. **Unquantified**: RADIUS does not currently know how large the
neglected term is, and no result may claim it is small.

---

## 6. Mass depletion

$m \to 0$ is a **discontinuous event**, handled per RS-005 §6, never a clamp.

On the depletion event: mass flow is set to zero, the associated force source is deactivated, and
integration restarts from the event state.

**Why not clamp.** A floor on $m$ produces a vehicle that keeps thrusting with constant mass — an
infinite propellant supply, silently violating mass conservation while producing entirely plausible
output. A clamp converts a loud failure into a quiet wrong answer, which is the worst available trade.

Guard: any evaluation with $m \le 0$ raises. It does not divide.

---

## 7. Verification tests this specification requires

| ID | Test | Passes if |
|---|---|---|
| V-VM-01 | **Tsiolkovsky** (= V-EOM-06): straight-line, no gravity, no aero, constant $\mathbf{c}$ and $\dot m$ | $\Delta v$ matches $\lVert\mathbf{c}\rVert\ln(m_0/m_f)$ to $<10^{-8}$ relative |
| V-VM-02 | Mass conservation: $\int \dot m_{\text{out}}\,dt$ equals the mass actually lost | $<10^{-10}$ relative |
| V-VM-03 | Depletion event fires at the analytically known time; mass never negative | within event tolerance; no $m\le0$ |
| V-VM-04 | Zero mass flow reduces exactly to the constant-mass equations | bitwise identical to the constant-mass path |
| V-VM-05 | $\dot{\mathbf{J}}$ analytical vs finite-difference agreement on a differentiable model | $<10^{-6}$ relative |
| V-VM-06 | Inertia tensor stays symmetric and positive-definite throughout a burn | no violation |
| V-VM-07 | Thrust offset produces the expected angular acceleration (= V-EOM-07) | matches $\mathbf{J}^{-1}\mathbf{M}$ |
| V-VM-08 | Order of accuracy preserved with the mass model active (tests the §4 hypothesis) | slope $4.0\pm0.2$ |
| V-VM-09 | $m \le 0$ raises rather than dividing | exception raised |

**V-VM-01** is the anchor: an exact analytical result, derived independently of RADIUS's own
derivation, that a sign error in $\mathbf{F}_{\text{prop}} = \dot m\mathbf{c}$ fails immediately.

**V-VM-04** is the cheapest high-value test here. It establishes that adding variable-mass capability
did not perturb the already-verified constant-mass path — the regression that is easiest to introduce
and hardest to notice.

---

## 8. Assumptions registered

`A-VM-01` … `A-VM-04` — see `docs/assumptions.md`.

---

## 9. Open questions

1. **How large is the omitted jet-damping moment (`A-VM-03`)?** Unbounded. RADIUS's damping is
   therefore optimistically low, and no rotational-damping claim is supportable. Closing this requires
   a reference (`research/SOURCES.md`, gaps table) and is the highest-priority gap in this document.
2. **How large is the neglected CM-motion momentum term (`A-VM-02`)?** Also unquantified.
3. Does the coupled variable-mass system become stiff near depletion? If mass approaches zero while
   force remains finite, acceleration diverges — the event handles the endpoint, but the approach to
   it may already demand steps smaller than the configured $h$. Unassessed.
4. Is a single lumped mass with a prescribed CM offset sufficient, or does a multi-body / multi-tank
   model become necessary? RS-003 §5 assumes the former. It is an assumption, not a result.
