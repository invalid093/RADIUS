# RADIUS — Current State

**Date:** 2026-09-09 · **Commit:** see `git log -1` · **Branch:** `main`
**Phase:** 1 of 14 — Research / Architecture (specification **audited**, corrections applied)

Concise, factual, self-contained. Per `docs/methodology/PUBLICATION_POLICY.md` §7 this file contains
no conversation history, no reasoning traces, no logs.

---

## 1. What RADIUS is

An academic computational aerospace-engineering project studying nonlinear 6-DOF vehicle dynamics,
numerical methods and uncertainty propagation. A **mathematical and software** study, not a vehicle
design project. Hard scope boundary in `CLAUDE.md`: no real or operational vehicle design, no
propulsion hardware content, no targeting or deployment procedures, no flight-readiness claim.
Propulsion enters only as a generic force and mass-flow abstraction.

Independent of AURA (ADR-0002): no import, no shared schema, no dependency.

---

## 2. Status — precise

| | |
|---|---|
| Researched | Frames, attitude, state, equations of motion, integration, atmosphere, aerodynamics, variable mass |
| Designed | Software architecture; provenance; publication governance; conceptual AURA interface |
| **Implemented** | **Nothing.** No source code exists |
| **Verified** | **Nothing.** ~65 tests are *specified*; none written. The specification itself has been audited (see below) |
| **Validated** | **Nothing**, and no path to validation currently exists — no independent benchmark has been found |

---

## 3. Completed

**Repository.** Created locally and at `https://github.com/invalid093/RADIUS` (public). Four commits
pushed. Git identity uses a GitHub `noreply` address. Secret scanning and push protection enabled.

**Governance (ADR-0008).** Five-class publication policy; deny-by-default `.gitignore` tested against
dummy artifacts; pre-push audit checklist covering working tree and history separately; provenance
chain and counter-based seed derivation specified.

**Specification.** `docs/methodology/NOTATION_AND_CONVENTIONS.md` plus RS-001 … RS-008, a 31-entry
assumptions register, an architecture document, a V&V strategy, and the thirteen-question quality
gate. Nine ADRs.

**Pre-implementation mathematical audit** (`docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`).
Verdict **PASS WITH REQUIRED CORRECTIONS**; corrections applied. Verified correct by independent
derivation and numerical check: frame conventions, quaternion kinematics (against a non-principal
axis), translational dynamics across four limiting cases, the gyroscopic term, the atmosphere model
against published values. Four defects found and fixed:

- **F-1 (load-bearing).** $-\dot{\mathbf{J}}\boldsymbol{\omega}$ removed from the rotational equation
  — it models internal redistribution, not ejection, and gave a **factor-of-two** spurious spin-up.
  ADR-0009, `A-VM-05`.
- **F-2.** Wind-frame composition sign error; $\beta$ came out negated.
- **F-3.** $\mathbf{T}_{BI}$ undefined at the non-unit quaternions RK stages produce; now divided by
  $q\cdot q$. `A-NUM-05`.
- **F-4.** Quaternion composition order is the reverse of matrix composition order; now stated.

---

## 4. Decisions in force

| | Decision | ADR |
|---|---|---|
| Frames | Flat-Earth NED as inertial, $z$ down; body at instantaneous CM; wind derived; ECEF deferred | 0003 |
| Conventions | Passive "to←from" transforms; Euler 3-2-1; **Hamilton, scalar-first** quaternion $q_{BI}$; SI/radians | 0003 |
| Attitude | Quaternion integrated; DCM on demand; Euler at boundaries; post-step normalisation only | 0004 |
| State | 14 elements: $[\mathbf{p}^I, \mathbf{v}^I, q, \boldsymbol\omega^B, m]$ on $\mathbb{R}^{13}\times S^3$; **inertial** velocity; mass a state | 0005 |
| Integration | Fixed-step RK4; Euler as comparator; adaptive deferred on determinism grounds; bisection events | 0006 |
| Variable mass | Rotational equation is $\mathbf{J}\dot{\boldsymbol\omega}+\boldsymbol\omega\times\mathbf{J}\boldsymbol\omega=\mathbf{M}$; inertia-rate term removed | **0009** |
| Licence | None | 0007 |
| Publication | Deny-by-default; curated record only | 0008 |

---

## 5. Quality gate verdict

**PASS — Phases 2–6.** Frames, math utilities, state, equations of motion, integration, analytical
verification. Implementation may begin.

**NOT PASS — Phase 8 (aerodynamics).** No traceable coefficient source; Mach-dependence gap
unassessed.

**Conditional — Phase 7 (atmosphere).** Proceed once the layer table is checked against the U.S.
Standard Atmosphere 1976 document directly.

---

## 6. Open questions, by severity

**Blocking a claim:**

1. **Jet damping omitted, magnitude unbounded** (`A-VM-03`). Simulated pitch/yaw damping is
   optimistically low. **No rotational-damping claim is supportable.**
2. **No traceable aerodynamic coefficient set** (`A-AER-03`). All aerodynamic results would be scoped
   to a hypothetical vehicle.
3. **No independent 6-DOF benchmark trajectory found.** Without one, RADIUS can be thoroughly verified
   and remain entirely unvalidated.

**Unquantified:**

4. CM-motion momentum term neglected (`A-VM-02`), magnitude unknown.
5. Flat-Earth validity domain (~10 km, ~60 s) is an estimate of neglected terms, not a measurement.
6. Stiffness of the coupled system near mass depletion (`A-NUM-02`) unassessed.

**To be tested by the first tests written:**

7. Does post-step quaternion normalisation preserve 4th-order accuracy (`A-ATT-01`)? V-NUM-07.
7b. Does the corrected variable-mass rotational equation behave as derived (`A-VM-05`)? **V-EOM-09** —
   the test whose absence let a factor-of-two error pass a gate.
8. Is $h=10^{-3}$ s adequate (`A-NUM-01`)? V-NUM-02, now under the timestep-selection methodology of
   RS-005 §4 rather than as a bare proposal.
9. Does same-platform bitwise determinism hold (`A-NUM-03`)? V-NUM-03 — **load-bearing for ADR-0008**.

**To verify before implementing:**

10. Atmosphere layer table transcription (`A-ATM-01`) against SRC-008.
11. Bibliographic details for SRC-010, currently marked `(not verified)`.

---

## 7. Next action

**Phase 2 — `radius/math/` and `radius/frames/`, with their verification tests.**

Start with the **hand-computed convention tests V-FRM-08, V-ATT-01, V-FRM-09, V-FRM-10 and
V-ATT-02b**, before the modules they test. They are the only test class that can catch a uniformly
applied wrong convention, which internal consistency checks cannot detect by construction — as the
audit's F-2 finding demonstrated concretely.

Then in order: RS-003 state module, RS-004 dynamics, RS-005 integrator, RS-004 §7 analytical cases.
Do not skip to aerodynamics — the gate does not pass.

In parallel, and not blocking: search for a published generic aerodynamic coefficient set, and for an
independent 6-DOF benchmark trajectory.

---

## 8. Environment

Python 3.13, `numpy`, `PyYAML`. No further dependency without a recorded reason. Nothing to run yet.
