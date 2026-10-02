# RADIUS

**Robust Aerospace Dynamics & Uncertainty Inference System**

*A physics-based nonlinear 6-DOF aerospace vehicle dynamics, simulation, and uncertainty-analysis
framework.*

> ### CLOSED — 2026-10-01
>
> **RADIUS is not under development.** It is published as a terminal record of what was built and
> verified, what was deliberately not built, and why the work stopped. **There is no simulator
> here, and nothing is validated.**
>
> **Read [`CLOSURE.md`](CLOSURE.md) first** — final inventory, the findings, and the reasons for
> closure. Decision: [ADR-0012](docs/decisions/ADR-0012-project-closure.md). Where anything below
> implies that work continues, `CLOSURE.md` governs.

**Maturity at closure: Research / Architecture** — foundations implemented and verified; 6-DOF
dynamics specified with verification anchors, not yet implemented. Reference-frame transformations
and quaternion algebra exist in `radius/` and are verified against hand-derived anchors. The
simulator itself does not: its equations are specified and carry frozen analytical anchors, but
one dynamics function exists — the rigid-body rotational derivative, verified against its
anchor — and no integrator, attitude propagation, translational dynamics, atmosphere or
aerodynamic code has been written. Nothing is validated. The label is unchanged by closure: it is
a claim about what the code does, and stopping work promotes nothing (ADR-0011 §4, ADR-0012 §3).

**What this repository is worth reading for** is the verification method and the defects it caught:
four specification errors found *before any code existed* — including one that no test could have
caught — five defects found in the project's own verification apparatus, and five methodological
results. All in [`CLOSURE.md`](CLOSURE.md) §4. See [Final status](#final-status).

---

## What RADIUS is

RADIUS is a computational framework for studying the nonlinear dynamics of a rigid, variable-mass
aerospace vehicle: its equations of motion, the reference frames and attitude representations those
equations are written in, the numerical methods used to integrate them, and the way uncertainty in
initial conditions, parameters and environment propagates through the resulting trajectory.

It is an **academic computational-engineering project**. It is a study of the mathematics and the
software architecture, not the design of any physical article. Vehicle parameters used for
development and testing are generic and non-operational, chosen because they exercise the numerics —
not because they describe anything real.

## Core objective

> Build an auditable and reproducible simulation environment in which the underlying physical model
> is independently verified — and its validity limits stated — *before* it is used as a test subject
> for reliability and uncertainty analysis.

The ordering matters. A simulator whose own numerical correctness is unestablished cannot support a
claim about uncertainty, because the analyst cannot separate uncertainty in the modelled system from
error in the model of it. RADIUS therefore treats verification as a prerequisite deliverable rather
than a closing formality.

## Scope

**In scope**

- rigid-body 6-DOF translational and rotational dynamics
- reference frames, coordinate transformations, and their conventions
- attitude representation (Euler angles, DCM, quaternion) and propagation
- numerical integration, step-size and error behaviour, deterministic execution
- generic atmosphere models
- generic aerodynamic force and moment models
- variable-mass dynamics as an abstract mathematical problem, with a generic external-force and
  mass-flow interface
- trajectory simulation and recorded state histories
- uncertainty propagation and Monte Carlo analysis
- verification and validation methodology
- reproducibility, provenance, software architecture

**Out of scope**

- design, optimisation or analysis of any real or operational vehicle
- propulsion hardware: construction, manufacture, chemistry, or performance tuning of a physical
  system. Propulsion enters RADIUS only as a mathematical external force and mass-flow rate
- targeting, deployment, or any operational procedure
- any claim of flight-readiness, operational validity, or suitability for use outside a study of
  the mathematics
- machine learning, learned surrogates, or data-driven uncertainty estimators (see `CLAUDE.md`)

## Relationship to AURA

RADIUS and [AURA](https://github.com/invalid093/aura) are **separate projects with separate
questions**.

| | RADIUS | AURA |
|---|---|---|
| Question | *How does the vehicle state evolve, and how accurately can we compute it?* | *What can be inferred from observations of a system, and how confident may we be?* |
| Domain | physics, dynamics, environment models, numerical integration, trajectory and state evolution; eventually navigation, guidance and control | uncertainty, reliability, diagnosability, fault analysis, statistical inference, experiment validity, provenance, evidence |
| Object of study | the vehicle | the inference procedure, and the experiment itself |

The intended long-run relationship is that **AURA treats RADIUS as a computational test subject** —
a system whose true state is known by construction, so that an inference method's performance can be
measured rather than asserted.

That relationship is **conceptual at this stage and deliberately unimplemented**. RADIUS does not
import AURA, does not depend on AURA's schemas, and must remain independently executable and
independently meaningful. RADIUS will expose plain, self-describing outputs (state trajectories,
configuration, seeds, provenance metadata); whether anything consumes them is not RADIUS's concern.
See `docs/architecture/AURA_INTERFACE.md`.

## Final status

**CLOSED 2026-10-01** at maturity **Research / Architecture** — foundations implemented and
verified; 6-DOF dynamics specified with verification anchors, not yet implemented
(`docs/methodology/PUBLICATION_POLICY.md` §11). Full account: [`CLOSURE.md`](CLOSURE.md).

| | |
|---|---|
| Researched | frames, attitude, state, equations of motion, numerical integration, atmosphere, aerodynamics, variable mass — `docs/research/` |
| Designed | software architecture, provenance, publication governance, conceptual AURA interface |
| Implemented | **foundations, plus one dynamics function** — reference-frame, Euler, quaternion→DCM and wind-frame transformations (`radius/frames.py`), the Hamilton quaternion product (`radius/math/quaternion.py`), and the rigid-body rotational **derivative** (`radius/dynamics/rotational.py`), each exercised by named tests. No integrator, attitude propagation, translational dynamics, atmosphere, aerodynamic, propulsion or trajectory code exists |
| Verified | **the frame and attitude conventions** — V-FRM-05, V-FRM-08, V-FRM-09, V-FRM-10, V-ATT-01 — **and the rotational derivative** against V-EOM-05, all versus hand-derived anchors. 135 tests run, 135 pass, 0 skipped |
| Verification anchors frozen | **V-EOM-01 … V-EOM-05** — exact analytical oracles for the translational and rotational equations of motion, frozen *before* the code they test (`tests/test_eom_anchors.py`). V-EOM-05 is now consumed by the rotational derivative |
| Validated | **nothing**, and no path to validation ever existed — no independent 6-DOF benchmark trajectory was found, and the scope boundary excludes the sources one would come from (`CLOSURE.md` §5) |
| Not built | no integrator, attitude propagation, translational dynamics, assembled state derivative, events, atmosphere, aerodynamics, propulsion, variable mass, trajectory, uncertainty propagation, navigation, guidance or control. Reached **step 2 of the 14-step order** below |

The specification passes its own [quality gate](docs/research/QUALITY_GATE.md) for Phases 2–6
(frames through analytical verification) and **does not pass** for Phase 8 (aerodynamics): there is no
traceable source for a coefficient set, so implementing it would produce results scoped to a
hypothetical vehicle. That gap is recorded rather than worked around, and the phase was never begun.

Explicitly:

- There is no simulator. There are no results. There are no figures. None were ever produced.
- Nothing here is validated. *Verification* ("did we implement the equations correctly?") and
  *validation* ("does the model represent reality well enough for the intended purpose?") are
  reported as distinct claims, and passing unit tests are never described as validation.
- RADIUS makes no claim of flight-ready, operationally valid, or real-world-deployable performance,
  and will not make one on the strength of self-consistent simulation.

## Repository structure

```
RADIUS/
├── README.md            this file
├── CLOSURE.md           terminal record: final state, findings, reasons for closure
├── CLAUDE.md            operating rules for the project
├── docs/
│   ├── PROVENANCE.md    the chain every published number must be traceable along
│   ├── assumptions.md   assumptions register; code cites an ID, never an inline comment alone
│   ├── research/        mathematical specification (frames, attitude, state, EOM, numerics, ...)
│   ├── architecture/    software architecture; conceptual AURA interface
│   ├── methodology/     notation and conventions; V&V strategy; publication policy
│   └── decisions/       ADRs — decisions with rationale, alternatives, and revisit criteria
├── radius/              implemented source: `frames.py`, `math/quaternion.py`,
│                        `dynamics/rotational.py`
├── tests/               verification tests, including the frozen analytical anchors
├── infrastructure/
│   └── publication_checklist.md   pre-push audit
├── research/
│   ├── SOURCES.md       reference record: what each source is used for
│   └── RESEARCH_LOG.md  dated decision log
└── handoffs/
    └── current_state.md final status inventory
```

**Start here:** [`docs/research/README.md`](docs/research/README.md) — the mathematical specification
and its quality-gate verdict.

`radius/`, `tests/` and `handoffs/` exist because the phases that fill them ran.
`experiments/`, `validation/` and `results/` were **never created**: a directory arrives with the
phase that fills it, and no such phase was reached. The tree describes what exists rather than what
was intended. See `docs/decisions/ADR-0001`.

## What is published here, and what is not

This repository is a **curated research record**, not a mirror of the working environment.

Published: source code, specifications, reports, ADRs, experiment definitions, configurations, seeds,
curated result tables, and the figures behind published claims. Not published: raw and intermediate
simulation output, Monte Carlo ensembles, per-run directories, debug plots, logs, caches, notebooks
that have not been cleaned and reviewed, and AI interaction records.

The reason is not tidiness. A result here is reproducible from **code + configuration + seed +
commit**, so publishing those is a stronger guarantee than publishing a snapshot of the output — and
burying the evidence under thousands of undocumented files makes a claim harder to check, not easier.

Policy: [`docs/methodology/PUBLICATION_POLICY.md`](docs/methodology/PUBLICATION_POLICY.md) ·
audit: [`infrastructure/publication_checklist.md`](infrastructure/publication_checklist.md) ·
rationale: [ADR-0008](docs/decisions/ADR-0008-publication-architecture.md).

## Implementation order

Research specification → frames and math utilities → state representation → equations of motion →
numerical integration → analytical verification → atmosphere → aerodynamics → variable-mass
abstraction → trajectory simulation → navigation → guidance/control → uncertainty propagation →
possible AURA interface.

**The project stopped at step 2.** The research specification is complete for Phases 2–6, frames and
math utilities are implemented and verified, one dynamics function exists, and the analytical
verification anchors for the equations of motion are frozen — four of the five never consumed by an
implementation. No step was skipped, and no subsystem was implemented before its mathematical
formulation, assumptions and verification strategy were documented. Steps 3 onward were not begun;
see [`CLOSURE.md`](CLOSURE.md) §6.

## Reproducing

The verification suite still runs, and still passes, from the repository root:

```bash
python -m unittest discover -s tests -t tests
```

135 tests, 135 pass, 0 skipped. There is no simulation to run. Dependencies are minimal (Python,
`numpy`, `PyYAML`), and the provenance and seeding machinery was specified but never exercised,
because no experiment was ever run.

Reproducibility is claimed precisely, not loosely: **bitwise-identical output on the same platform
and library versions** given the same commit, configuration and seed; **agreement within a stated
tolerance** across platforms. The stronger cross-platform claim would require pinned compiler flags
and a controlled BLAS, which RADIUS does not do. See [`docs/PROVENANCE.md`](docs/PROVENANCE.md) §5.

## Citation

There is no result here to cite, and there will not be. Refer to the repository itself:

> RADIUS — Rocket Dynamics & Integrated Uncertainty Simulation.
> `https://github.com/invalid093/RADIUS`, commit `<hash>`, accessed `<date>`.

Cite a specific commit. `main` is now terminal, so the distinction matters less than it did, but the
closure commit is the one that describes the project as a whole. No `CITATION.cff` is added: there is
no result worth citing.

## Licence

None. No licence is granted; this repository is published as a research record, not as reusable
software.
