# ADR-0001 — Repository structure and deferred implementation tree

**Date:** 2026-09-09 · **Status:** Accepted

## Context

A research-oriented project structure was proposed containing a full implementation tree
(`radius/dynamics/`, `radius/frames/`, `radius/atmosphere/`, `radius/aerodynamics/`,
`radius/propulsion/`, `radius/actuators/`, `radius/navigation/`, `radius/guidance/`,
`radius/control/`, `radius/simulation/`) plus `experiments/`, `validation/`, `tests/`,
`infrastructure/`, `results/` and `handoffs/`.

RADIUS is in its research/architecture phase. None of those directories has content, and the
implementation order deliberately places navigation, guidance and control near the end.

There are two competing risks. Creating the whole tree now signals organisation the project has not
earned, and invites a reader to assume subsystems exist. Deferring directory creation churns paths
later, when documents already reference them.

## Decision

Create only the directories that have content today:

```
docs/research/        mathematical specification
docs/architecture/    software architecture, conceptual AURA interface
docs/methodology/     notation and conventions, V&V strategy
docs/decisions/       ADRs
research/             sources record, research log
```

The implementation tree is **not created** until the phase that fills it. Specifically:

- `radius/` and `tests/` arrive together in Phase 2 (frames and mathematical utilities), because the
  first module and its verification tests are written in the same step.
- `validation/` arrives in Phase 6 (analytical verification cases).
- `infrastructure/configuration/` arrives when the first parameter needs a home — expected Phase 7
  (atmosphere), the first subsystem with a table of constants.
- `experiments/` and `results/` arrive when there is a first experiment to register.
- `handoffs/` arrives when there is state to hand off.

The path layout above is fixed *now* by this ADR, so documents may reference those paths before the
directories exist without creating churn later. What is deferred is the empty directory, not the
decision about where things go.

`.gitignore` already anticipates `results/`, `validation/reference/` and
`research/research_log/`; that is intentional and costs nothing.

## Alternatives considered

- **Create the full tree with `.gitkeep` files.** Rejected. Fourteen empty directories, ten of them
  for subsystems whose mathematical formulation has not been written, would misrepresent the state of
  the project — the single thing the README is at pains to state accurately. This is the precise
  failure mode the project instruction "do not populate every directory with placeholder files merely
  for appearance" names.
- **Flat structure, defer all path decisions.** Rejected. The specification documents need to say
  where the module they specify will live, and retrofitting that would mean editing every document.

## Consequences

- A reader browsing the repository sees documentation and nothing else. That is an accurate
  representation of the current state and is the intended signal.
- Each phase's first commit creates its directory. That is visible in the history, which is a
  feature: the tree grows in the order the work was done.
- If the implementation order changes, this ADR is superseded rather than edited.

## Revisit if

The implementation order in the README changes, or a subsystem needs a home that this layout does not
provide.
