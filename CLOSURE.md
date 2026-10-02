# RADIUS — Closure Report

**Date:** 2026-10-01 · **Decision:** [ADR-0012](docs/decisions/ADR-0012-project-closure.md) ·
**Development span:** commits `5b831ed` … `0015178`

> **Status: CLOSED.** RADIUS is complete as a terminal record and is not under development. No
> further phases are planned. The repository is published as a finished account of what was built
> and verified, what was deliberately not built, and why the work stopped.

This document is the single authoritative statement of final state. Where any other document in
this repository implies that work continues, this one governs.

**The project maturity label does not change on closure.** RADIUS remains **Research /
Architecture — foundations implemented and verified; 6-DOF dynamics specified with verification
anchors, not yet implemented** (`docs/methodology/PUBLICATION_POLICY.md` §11, ADR-0011). Closure is
a lifecycle state; maturity is a claim about what the code does. Stopping work does not promote the
latter, and ADR-0011 §4 fixed the promotion criteria in advance precisely so that this could not be
blurred at the end.

---

## 1. What this repository is, and is not

**It is** an account of applying verification-first discipline to nonlinear rigid-body dynamics: a
complete mathematical specification, an assumptions register, frozen hand-derived analytical
oracles, and a small amount of production code written against those oracles and mutation-tested
against them.

**It is not** a rocket simulator. There is no integrator, no attitude propagation, no translational
dynamics, no atmosphere, no aerodynamics, no trajectory, no uncertainty propagation, and no results.
It never produced a simulated trajectory, because the phase that would have produced one was never
reached.

**It is not validated**, and no path to validation ever existed (§5).

---

## 2. Final inventory — what exists

`FACT`, verified against the working tree at closure.

### Production code — 657 lines, 6 modules, 6 public functions

| Module | Public API | Verified by |
|---|---|---|
| `radius/frames.py` | `dcm_b_from_i_euler`, `quat_b_from_i_euler`, `dcm_b_from_i_quat`, `dcm_b_from_w` | V-FRM-05, V-FRM-08, V-FRM-09, V-FRM-10, V-ATT-01 |
| `radius/math/quaternion.py` | `quat_multiply` (Hamilton, scalar-first) | V-ATT-01 |
| `radius/dynamics/rotational.py` | `angular_acceleration_wrt_i_in_b` | V-EOM-05 |

The last of these is the whole of the dynamics: the rigid-body rotational **derivative**
ω̇ = J⁻¹[M_ext − ω×(Jω)], evaluated at one state. It is a derivative, not a step — nothing
integrates it.

### Verification suite — 3,432 lines, 135 tests, 0 skipped

| File | Tests | Contents |
|---|---|---|
| `tests/test_frames.py` | 31 | frame, Euler, quaternion and wind-frame convention anchors |
| `tests/test_eom_anchors.py` | 86 | the frozen exact oracles V-EOM-01 … V-EOM-05 |
| `tests/test_dynamics_rotational.py` | 18 | the production rotational derivative against V-EOM-05 |

```bash
python -m unittest discover -s tests -t tests
```

135 executed / 135 passed / 0 failed / 0 skipped. Standard library only; the anchor module imports
nothing from `radius`.

### Specification and governance — ~6,900 lines of Markdown

RS-001 … RS-008 (frames, attitude, state, equations of motion, integration, atmosphere,
aerodynamics, variable mass); a 31-entry assumptions register; notation and conventions; the V&V
strategy; the publication policy and pre-push checklist; the provenance chain; the architecture
document; twelve ADRs; a dated research log; the pre-implementation mathematical audit and its
thirteen-question quality gate.

### Frozen analytical anchors

**V-EOM-01** force-free translation · **V-EOM-02** constant-gravity ballistic · **V-EOM-03**
constant body force at a fixed attitude · **V-EOM-04** torque-free axisymmetric coning ·
**V-EOM-05** torque-free body whose body axes are not principal axes.

All five were frozen **before** the code they test. One of the five — V-EOM-05 — was ever consumed
by an implementation. The other four remain exact oracles awaiting code that does not exist.

---

## 3. What was verified

Six verification IDs, out of 65+ specified across RS-001 … RS-008: **V-FRM-05, V-FRM-08, V-FRM-09,
V-FRM-10, V-ATT-01, V-EOM-05.**

Each was hand-derived independently of the implementation, in exact rational arithmetic
(`fractions.Fraction`) over Pythagorean-triple angles so that the oracle carries no floating-point
error of its own, and frozen as literal expected values before the module under test was written.
The tests consume those literals; they never recompute them. An error shared between oracle and
implementation therefore cannot hide, which is the specific failure mode a test-first project is
otherwise most exposed to.

The rotational derivative additionally passed a mutation campaign: **16 required mutations, 16
detected, 0 escaped**, each run in a temporary tree with verification that the interpreter had
actually loaded the mutated file. Its tolerance, 1 × 10⁻¹² absolute, was derived from conditioning
rather than inherited — |ω̇| ≤ 40, cond(J) ≈ 4.64, unit round-off 2.22 × 10⁻¹⁶, hence ≲ 4 × 10⁻¹⁴
for a backward-stable solve. `FACT`: measured worst error **3.55 × 10⁻¹⁵**, exactly zero in two of
three cases.

`LIMITATION`. This is **verification** in the strict sense of `docs/methodology/`
`VERIFICATION_AND_VALIDATION.md` §1 — agreement between code and documented mathematics, with no
physical reality consulted. It establishes that six conventions and one equation were implemented
correctly. It establishes nothing whatever about whether those equations describe a rocket.

---

## 4. Findings

The substantive output of this project is a set of defects caught and a set of methodological
results. Both transfer; neither is specific to rocketry.

### 4.1 Errors found in the specification before any code existed

The pre-implementation mathematical audit
(`docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`) returned **PASS WITH REQUIRED
CORRECTIONS** and found four defects, all in the specification rather than in code, because no code
existed yet:

- **F-1, load-bearing.** The rotational equation carried a −J̇ω term. For an *ejecting* body that
  term models internal mass redistribution, not ejection, and produced a **factor-of-two spurious
  spin-up**. Removed; ADR-0009, assumption `A-VM-05`.
- **F-2.** A sign error in the wind-frame composition; sideslip β came out negated.
- **F-3.** T_BI was undefined at the non-unit quaternions that Runge–Kutta stages produce; it is now
  divided by q·q (`A-NUM-05`).
- **F-4.** Quaternion composition order is the reverse of matrix composition order; this was
  unstated, and is now stated.

`INTERPRETATION`, and the most useful result in this document: **F-1 was unreachable by testing.**
A test-first project that derives its oracle from its own specification encodes the specification's
error into the oracle and the code alike, and the test passes. Only an independent re-derivation
from first principles found it. Test-first discipline is necessary and is not sufficient; it must be
preceded by an audit of the mathematics that the tests will be written against.

### 4.2 Defects found in the project's own verification apparatus

More instructive than the physics errors, because these are failures of verification *design*:

- **V-EOM-02's supplied value was wrong.** The specified `p_z(3)` disagreed with independent
  derivation; the derived value 70 was frozen instead.
- **V-EOM-05 could not detect what it existed to detect.** As specified it used a *diagonal*
  inertia tensor — and a diagonal tensor is identically insensitive to products-of-inertia errors,
  which was the entire error class the anchor existed to catch. Repaired by reconfiguring it around
  a symmetric positive-definite tensor with all three products non-zero (determinant 163, prime,
  yet with integral ω̇ at the chosen states). An anchor can be exact, frozen, passing, and
  worthless.
- **An identifier collision.** Two distinct verification claims shared the ID V-EOM-03. Resolved by
  ADR-0010 without renumbering a frozen anchor.
- **A convention mismatch inside the specification.** RS-004's axisymmetric treatment presumed the
  symmetry axis was z, while the rest of the specification's own evidence — roll rate p, rolling
  moment L, the damping derivative C_lp, exhaust along −x̂_B, J_yy used as pitch inertia — implied
  x_B. ADR-0010 fixed x_B and preserved the z-symmetric form as a named analysis-only frame P.
- **Status language drifted in both directions.** Documents claimed more than existed (corrected by
  ADR-0010) and went on claiming that nothing existed after code did (corrected by ADR-0011).
  Misrepresentation of maturity is not only flattering.

### 4.3 Methodological findings

- **Sampling an anchor at convenient fractions of a period is blind to a family of errors.** In
  V-EOM-04, at the half-cycle a *reversed* coning sign is invisible — the difference is exactly
  zero — and λ′ = −3λ is invisible at both the quarter and the half cycle. An anchor sampled only at
  "nice" times passes a sign-reversed *and* a wrong-magnitude implementation. Fixed by adding a
  sample at the incommensurate time arctan(3/4).
- **A mutation that is a mathematical identity is not a detection and must not be counted as one.**
  Two mutations of the rotational derivative escape: transposing a *symmetric* J, and replacing the
  linear solve with an explicit inverse. Both are identities under this representation. They are
  recorded as structural blind spots. A mutation score that counted them as kills would be inflated
  by exactly the amount that makes mutation scores untrustworthy.
- **A tolerance should be derived, not inherited.** The translational anchors' 1 × 10⁻¹² does not
  transfer to a derivative evaluation, and was not assumed to; see §3.
- **The oracle must not share a derivation route with the implementation.** The anchors use exact
  rational arithmetic and import nothing from `radius`; the production function is cross-checked
  against two independent exact routes (adjugate inverse and Cramer's rule) which agree with each
  other exactly.
- **Thorough verification leaves validation entirely untouched.** 135 tests, 0 skipped, 16/16
  mutations caught — and not one statement about physical reality is thereby supported. The two
  words are not degrees of the same thing.

### 4.4 The findings that closed the project

`OBSERVATION`. Of the final five development phases, **three consecutive phases produced no new
capability.** They repaired an identifier collision, stale status language, and a defective anchor —
every one of them created by an earlier phase of this same project.

`CALCULATION`. At closure: 6,900 lines of specification and governance, 3,432 lines of tests, and
**657 lines of production code**. Documentation to production ≈ 10.5 : 1; tests to production
≈ 5.2 : 1.

`INTERPRETATION`. The governance apparatus had grown faster than the substance it governed and had
begun to consume the development budget. The rigour could not be relaxed to compensate, because the
rigour was the only thing distinguishing this project from a short script against an existing
simulator — so the cost per unit of progress was structural, not a matter of effort.

`INTERPRETATION`. The remaining scope — assembled state derivative, integrator, attitude
propagation, translational dynamics, variable mass, atmosphere, aerodynamics, event handling,
Monte Carlo uncertainty propagation — is an order of magnitude larger than what was completed, and
each piece carries the same anchor-derivation, mutation-testing and documentation cost as the one
function that was finished.

`LIMITATION`. **No systematic literature search was performed for RADIUS.** AURA's novelty audit
(TV-N1) has no equivalent here. The judgement that this work is not novel — that 6-DOF rigid-body
flight dynamics with Monte Carlo uncertainty is long-established, with mature open-source and
institutional implementations — is recorded as an **interpretation, not an audited finding**, and
no bibliographic claim is made in support of it. The project never asserted novelty, so nothing
published here depends on the question.

`LIMITATION`. **Methodological independence from AURA was never achieved.** Code independence held
completely and was audited: no import, no shared schema, no dependency, and AURA was never modified
(ADR-0002). But the apparatus — assumption registers with IDs cited from code, ADRs, frozen
verification anchors, component status vocabularies, scoped maturity labelling, deny-by-default
publication governance — is AURA's methodology transplanted to a new domain. ADR-0002 constrained
code and data; it never claimed intellectual independence, and in retrospect that independence was
not available.

---

## 5. What was never validated, and why

`FACT`. Nothing in this repository is validated. Three gaps were open at closure and are now
permanent:

1. **No independent 6-DOF benchmark trajectory was ever found.** Without one, the project could be
   verified arbitrarily thoroughly and remain entirely unvalidated — which is precisely what
   happened.
2. **No traceable aerodynamic coefficient set** (`A-AER-03`, open question Q8). The quality gate
   therefore **does not pass** for the aerodynamics phase, and that phase was correctly never
   begun. Implementing it would have produced numbers scoped to a hypothetical vehicle.
3. **Jet damping is omitted and its magnitude is unbounded** (`A-VM-03`). No rotational-damping
   claim was ever supportable.

`INTERPRETATION`. The first gap was not closable within this project's scope. Validation requires
independent reference data; the hard scope boundary in `CLAUDE.md` — no real or operational vehicle,
no propulsion hardware, no flight-readiness claim — excludes the sources from which such data would
come. The honest terminal state of the project as scoped was therefore always going to be *verified,
never validated*: a correct implementation of equations that nobody disputes. Recognising that
earlier would have been worth several phases.

Also left open at closure, unresolved: the V-EOM-10 / V-ATT-02 overlap in the closed-form q(t)
(ADR-0010); the unquantified centre-of-mass motion term (`A-VM-02`); the flat-Earth validity domain
as an estimate rather than a measurement; stiffness near mass depletion (`A-NUM-02`); the atmosphere
layer-table transcription check against its source; and the unverified bibliographic details of
SRC-010. Attitude propagation, the inertial precession rate, and the variable-mass rotational case
V-EOM-09 are unanchored.

---

## 6. What was not built

Explicitly, so that no reader has to infer it: no numerical integrator; no attitude or quaternion
propagation; no translational dynamics; no assembled state-derivative function; no 6-DOF
propagation loop; no event detection; no atmosphere model; no aerodynamic force or moment model; no
propulsion or variable-mass implementation; no trajectory simulation; no state recording; no
uncertainty propagation or Monte Carlo analysis; no navigation, guidance or control; no AURA
interface beyond a conceptual document. No `experiments/`, `validation/` or `results/` directory was
ever created, because no phase that would fill one was reached.

The project reached **step 2 of the 14-step implementation order** in `README.md`.

---

## 7. What a reader may and may not take from this

**May.** That the verification method is real and was executed properly: oracles derived
independently and frozen before implementation, exact rational arithmetic, mutation testing with
executed-file verification, tolerances derived from conditioning, identity mutations reported as
blind spots rather than counted as kills, and a pre-implementation audit that caught a load-bearing
specification error no test could have caught. The defect list in §4 is the usable content.

**May not.** That any rocket, vehicle or trajectory was simulated. That any model was validated.
That the physics implemented here is novel. That this repository is reusable software — no licence
is granted (ADR-0007), and no licence is added on closure.

---

## 8. If this is ever reopened

Closure is recorded as a decision with a revisit condition, not as a verdict about the subject
(ADR-0012). Reopening would be sound if any of the following changed:

- **An independent 6-DOF benchmark trajectory becomes available.** This is the binding constraint.
  It would convert the project from permanently unvalidatable to validatable, which is the only
  change that alters the terminal state described in §5.
- **The deliverable is reframed as the verification methodology itself**, with rigid-body dynamics
  as the case study rather than the product. That is a smaller and genuinely finishable scope, and
  §4 is most of its content already.
- **A traceable aerodynamic coefficient set is found**, closing Q8 and `A-AER-03`.

Reopening under the existing scope — continuing to implement equations against frozen anchors —
would reproduce §4.4 and is not recommended.

---

## 9. Pointers

| | |
|---|---|
| Closure decision | [ADR-0012](docs/decisions/ADR-0012-project-closure.md) |
| Final state snapshot | [`handoffs/current_state.md`](handoffs/current_state.md) |
| All decisions | [`docs/decisions/`](docs/decisions/README.md) — twelve ADRs |
| Dated decision log | [`research/RESEARCH_LOG.md`](research/RESEARCH_LOG.md) — RL-0001 … RL-0017 |
| Mathematical specification | [`docs/research/README.md`](docs/research/README.md) — RS-001 … RS-008 |
| The audit that found F-1 | [`docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`](docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md) |
| V&V strategy and anchor detail | [`docs/methodology/VERIFICATION_AND_VALIDATION.md`](docs/methodology/VERIFICATION_AND_VALIDATION.md) |
| Assumptions register | [`docs/assumptions.md`](docs/assumptions.md) — 31 entries |

The historical record in this repository is **not rewritten to make the project look finished.**
Dated documents — the ADRs, the audit, the quality gate, the research log — remain exactly as
written, including the statements that were true when written and are superseded now. Where such a
document reads as a current-status source, it carries a pointer to this file instead of an edit.
