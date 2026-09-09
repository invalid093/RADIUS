# RADIUS — Verification and Validation Strategy

**Status:** Strategy, designed before implementation. Nothing has been verified or validated.
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

`FACT`, 2026-09-09:

| | |
|---|---|
| Verified | **nothing** |
| Validated | **nothing** |
| Verification tests written | **none** — 60+ are *specified* across RS-001…RS-008 |
| Independent reference data held | **none** |

The last row is the important one, and it is a `LIMITATION` on the whole project: **RADIUS currently
has no path to validation of its trajectory output**, because it has no independent benchmark to
compare against. This is recorded in `research/SOURCES.md` as an open gap. Until it closes, RADIUS
can become a thoroughly verified implementation of a model whose fidelity to reality is entirely
unestablished — and it must say so.

---

## 3. Verification: four kinds

### 3.1 Analytical

The strongest evidence available, because the reference is exact and independent of the
implementation. Specified in RS-004 §7; anchors:

- **V-EOM-02** — constant gravity gives an exact parabola.
- **V-EOM-04** — torque-free axisymmetric coning at $\lambda = \frac{J_z-J_t}{J_t}\omega_z$; a
  *quantitative* check on the gyroscopic term.
- **V-EOM-06 / V-VM-01 — Tsiolkovsky.** $\Delta v = \lVert\mathbf{c}\rVert\ln(m_0/m_f)$: the only
  exact check on the variable-mass coupling, and derived independently of RADIUS's own derivation.
- **V-ATT-02** — closed-form quaternion under constant body rate.

**Conservation and symmetry checks** (V-EOM-05, V-NUM-08) deserve separate mention. An invariant is in
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
