# RADIUS

**Rocket Dynamics & Integrated Uncertainty Simulation**

*A physics-based nonlinear 6-DOF aerospace vehicle dynamics, simulation, and uncertainty-analysis
framework.*

**Status: Research / Architecture Phase.** No simulation code has been written. Nothing in this
repository has been verified or validated. See [Current status](#current-status).

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

**Research / Architecture Phase.**

| | |
|---|---|
| Researched | in progress — see `docs/research/` |
| Designed | in progress — see `docs/architecture/` |
| Implemented | **nothing** |
| Verified | **nothing** |
| Validated | **nothing** |

Explicitly:

- There is no simulator yet. There are no results. There are no figures.
- Nothing here is validated. When implementation begins, *verification* ("did we implement the
  equations correctly?") and *validation* ("does the model represent reality well enough for the
  intended purpose?") will be reported as distinct claims, and passing unit tests will not be
  described as validation.
- RADIUS makes no claim of flight-ready, operationally valid, or real-world-deployable performance,
  and will not make one on the strength of self-consistent simulation.

## Repository structure

```
RADIUS/
├── README.md            this file
├── CLAUDE.md            operating rules for the project
├── docs/
│   ├── research/        mathematical specification (state, frames, attitude, EOM, numerics, ...)
│   ├── architecture/    software architecture; conceptual AURA interface
│   ├── methodology/     notation, units, sign conventions; V&V strategy
│   ├── decisions/       ADRs — decisions with rationale, alternatives, and revisit criteria
│   └── assumptions.md   assumptions register; code cites an ID, never an inline comment alone
└── research/
    ├── SOURCES.md       reference record: what each source is used for
    └── RESEARCH_LOG.md  dated decision log
```

Implementation directories (`radius/`, `experiments/`, `validation/`, `tests/`, `infrastructure/`,
`results/`, `handoffs/`) are **not created yet**. They arrive with the phase that fills them, so that
the tree describes what exists rather than what is intended. See `docs/decisions/ADR-0001`.

## Implementation order

Research specification → frames and math utilities → state representation → equations of motion →
numerical integration → analytical verification → atmosphere → aerodynamics → variable-mass
abstraction → trajectory simulation → navigation → guidance/control → uncertainty propagation →
possible AURA interface.

The project is at step 1. No step is skipped, and no subsystem is implemented before its
mathematical formulation, assumptions and verification strategy are documented.

## Reproducing

Nothing to run yet. When there is, dependencies will be kept minimal (Python, `numpy`, `PyYAML`
unless a further dependency is justified), every stochastic component will take an explicit seed, and
every result will trace to configuration + seed + commit.

## Licence

None. No licence is granted; this repository is published as a research record, not as reusable
software.
