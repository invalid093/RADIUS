# ADR-0002 — RADIUS is independent of AURA

**Date:** 2026-09-09 · **Status:** Accepted

## Context

RADIUS and AURA are written by the same researcher and are intended to meet eventually: AURA studies
inference under uncertainty and needs a system whose true state is known by construction; RADIUS
produces exactly such a system. The obvious efficiency is to share code — AURA already has a
provenance module, a seed-derivation scheme, a Monte Carlo driver, an experiment registry and a
validity-gate mechanism, all of which RADIUS will eventually need in some form.

That efficiency is a trap, for three reasons.

1. **Scientific.** If AURA is to use RADIUS as a test subject, RADIUS must be an *independent*
   object of study. A simulator that imports its evaluator's schemas, gates and assumptions is not an
   independent test subject; shared code is a shared-mode failure, and an error in the common layer
   would corrupt the system and its evaluation identically and undetectably.
2. **Project-state.** AURA's own record shows its research question was terminated and its novelty
   gate returned FAIL; it has since been re-scoped to a research-engineering framework. Coupling a
   new project to a project that has already had its premise withdrawn once would inherit that
   instability for no benefit.
3. **Practical.** RADIUS is at Phase 1. A dependency taken now would be taken before RADIUS knows
   what it needs, which is how dependencies end up shaping designs rather than serving them.

## Decision

RADIUS does not depend on AURA in any way: no import, no shared package, no shared schema, no shared
configuration format assumption, no shared data model, no submodule, no vendored copy.

RADIUS must remain **independently executable and independently meaningful**: it must be possible to
clone RADIUS alone, run it, and obtain a scientifically interpretable result.

Where RADIUS needs a capability AURA also has — provenance, seeding, Monte Carlo, experiment
registry — RADIUS implements its own, sized to RADIUS's needs. Reading AURA's version to learn from
its design is encouraged; copying it wholesale is not, because RADIUS's requirements are not AURA's
and an oversized mechanism is a maintenance cost with no scientific return.

The eventual relationship is one-directional and loosely coupled: **RADIUS emits, AURA consumes.**
RADIUS writes plain, self-describing outputs — state trajectories, configuration, seeds, provenance
metadata — in a format documented for its own sake. Whether anything consumes them is not RADIUS's
concern, and no output format decision may be justified by "AURA needs it this way".

The interface is specified conceptually in `docs/architecture/AURA_INTERFACE.md` and is **not
implemented**.

## Alternatives considered

- **Share a common `provenance`/`seeds` package between both projects.** Rejected on the
  shared-mode-failure argument above. The duplicated code is perhaps a few hundred lines; the
  independence is the entire methodological premise of using RADIUS as a test subject.
- **Make RADIUS a subpackage of AURA.** Rejected. It would subordinate a physics project to a
  statistics project and make RADIUS's status depend on AURA's, which is precisely backwards: the
  physics must stand on its own before it can serve as ground truth for anything.
- **Depend on AURA now, decouple later if needed.** Rejected. Decoupling is reliably harder than not
  coupling, and the coupling would be established during the phase when RADIUS's own abstractions are
  still forming — the worst possible time to import someone else's.

## Consequences

- Some code will exist in both repositories in similar form. Accepted, and cheap at this scale.
- RADIUS cannot benefit automatically from improvements to AURA's infrastructure. Accepted; a good
  idea can be re-implemented deliberately, which is the point.
- If AURA later consumes RADIUS output, the coupling lives on **AURA's** side, in an adapter AURA
  owns. RADIUS's output format is then a published contract AURA reads, not a dependency RADIUS has.

## Revisit if

An AURA–RADIUS integration experiment is actually designed and registered, at which point the
direction and location of the coupling is re-decided explicitly — with the default remaining that the
adapter lives in AURA.
