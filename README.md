# RADIUS

**Rocket Dynamics & Integrated Uncertainty Simulation**

*A physics-based nonlinear 6-DOF aerospace vehicle dynamics, simulation, and uncertainty-analysis
framework.*

**Status: Research / Architecture** — foundations implemented and verified; 6-DOF dynamics
specified with verification anchors, not yet implemented. Reference-frame transformations and
quaternion algebra exist in `radius/` and are verified against hand-derived anchors. The
simulator itself does not: its equations are specified and carry frozen analytical anchors, but
no dynamics, integrator, atmosphere or aerodynamic code has been written. Nothing is validated.
The project is actively developed. See [Current status](#current-status).

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

## Current status

**Research / Architecture** — foundations implemented and verified; 6-DOF dynamics specified
with verification anchors, not yet implemented (`docs/methodology/PUBLICATION_POLICY.md` §11).

| | |
|---|---|
| Researched | frames, attitude, state, equations of motion, numerical integration, atmosphere, aerodynamics, variable mass — `docs/research/` |
| Designed | software architecture, provenance, publication governance, conceptual AURA interface |
| Implemented | **foundations only** — reference-frame, Euler, quaternion→DCM and wind-frame transformations (`radius/frames.py`) and the Hamilton quaternion product (`radius/math/quaternion.py`), each exercised by named tests. No dynamics, integrator, atmosphere, aerodynamic, propulsion or trajectory code exists |
| Verified | **the frame and attitude conventions only** — V-FRM-05, V-FRM-08, V-FRM-09, V-FRM-10, V-ATT-01, against hand-derived anchors. 94 tests run, 94 pass, 0 skipped |
| Verification anchors frozen | **V-EOM-01 … V-EOM-04** — exact analytical oracles for the translational and rotational equations of motion, frozen *before* the code they will test (`tests/test_eom_anchors.py`) |
| Validated | **nothing**, and no path to validation currently exists |

The specification passes its own [quality gate](docs/research/QUALITY_GATE.md) for Phases 2–6
(frames through analytical verification) and **does not pass** for Phase 8 (aerodynamics): there is no
traceable source for a coefficient set, so implementing it would produce results scoped to a
hypothetical vehicle. That gap is recorded rather than worked around.

Explicitly:

- There is no simulator yet. There are no results. There are no figures.
- Nothing here is validated. *Verification* ("did we implement the equations correctly?") and
  *validation* ("does the model represent reality well enough for the intended purpose?") are
  reported as distinct claims, and passing unit tests are never described as validation.
- RADIUS makes no claim of flight-ready, operationally valid, or real-world-deployable performance,
  and will not make one on the strength of self-consistent simulation.

## Repository structure

```
RADIUS/
├── README.md            this file
├── CLAUDE.md            operating rules for the project
├── docs/
│   ├── PROVENANCE.md    the chain every published number must be traceable along
│   ├── assumptions.md   assumptions register; code cites an ID, never an inline comment alone
│   ├── research/        mathematical specification (frames, attitude, state, EOM, numerics, ...)
│   ├── architecture/    software architecture; conceptual AURA interface
│   ├── methodology/     notation and conventions; V&V strategy; publication policy
│   └── decisions/       ADRs — decisions with rationale, alternatives, and revisit criteria
├── radius/              implemented source: `frames.py`, `math/quaternion.py`
├── tests/               verification tests, including the frozen analytical anchors
├── infrastructure/
│   └── publication_checklist.md   pre-push audit
├── research/
│   ├── SOURCES.md       reference record: what each source is used for
│   └── RESEARCH_LOG.md  dated decision log
└── handoffs/
    └── current_state.md concise project state for continuation
```

**Start here:** [`docs/research/README.md`](docs/research/README.md) — the mathematical specification
and its quality-gate verdict.

`radius/`, `tests/` and `handoffs/` exist because the phases that fill them have run.
`experiments/`, `validation/` and `results/` are **not created yet**: a directory arrives with the
phase that fills it, so the tree describes what exists rather than what is intended. See
`docs/decisions/ADR-0001`.

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

The project is at step 2. The research specification is complete for Phases 2–6, frames and math
utilities are implemented and verified, and the analytical verification anchors for the equations
of motion are frozen ahead of the code they will test. No step is skipped, and no subsystem is
implemented before its mathematical formulation, assumptions and verification strategy are
documented.

## Reproducing

The verification suite runs today, from the repository root:

```bash
python -m unittest discover -s tests -t tests
```

There is no simulation to run yet. Dependencies are kept minimal (Python, `numpy`, `PyYAML` unless
a further dependency is justified), every stochastic component will take an explicit seed, and
every result will trace to configuration + seed + commit.

Reproducibility is claimed precisely, not loosely: **bitwise-identical output on the same platform
and library versions** given the same commit, configuration and seed; **agreement within a stated
tolerance** across platforms. The stronger cross-platform claim would require pinned compiler flags
and a controlled BLAS, which RADIUS does not do. See [`docs/PROVENANCE.md`](docs/PROVENANCE.md) §5.

## Citation

There is no result here to cite yet. Until there is, refer to the repository itself:

> RADIUS — Rocket Dynamics & Integrated Uncertainty Simulation.
> `https://github.com/invalid093/RADIUS`, commit `<hash>`, accessed `<date>`.

Cite a specific commit, not the branch: the repository is under active development and `main` will
not say the same thing next week. A `CITATION.cff` will be added when there is a result worth
citing and the author has chosen how to be named.

## Licence

None. No licence is granted; this repository is published as a research record, not as reusable
software.
