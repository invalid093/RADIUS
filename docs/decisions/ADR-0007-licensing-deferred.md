# ADR-0007 — No licence at this stage

**Date:** 2026-09-09 · **Status:** Accepted

## Context

The repository is public. A public repository without a licence file grants no rights: default
copyright applies and no reuse is permitted. Adding a permissive licence is the conventional default
for a public research repository, and is often done reflexively.

RADIUS is at Phase 1. Nothing is implemented, nothing is verified, and the scope boundary
(`CLAUDE.md`) explicitly excludes any claim of real-world applicability.

## Decision

**No licence file is added**, and no statement is made that implies the code or documentation is
freely reusable. The README states this plainly rather than leaving it to inference.

The repository is published as a **research record**: something to be read and audited, not something
to be depended upon.

Adding a licence later requires an explicit instruction from the researcher.

## Alternatives considered

- **MIT or Apache-2.0 now.** Rejected, for now. Licensing is a decision about downstream use, and
  downstream use of an unverified dynamics model is exactly what the project does not want to
  encourage at this stage. The decision is also one-way in practice: a licence granted is difficult
  to withdraw from copies already taken.
- **A no-derivatives documentation licence.** Rejected as premature; it answers a question nobody has
  asked yet and adds a compliance surface for no benefit.

## Consequences

- Others may read the repository but may not reuse it. That is the intended state.
- Anyone wishing to reuse anything must ask, which is an acceptable cost at this stage and gives the
  researcher a chance to state the verification status first.

## Revisit if

The researcher decides to invite reuse or contribution, or the framework reaches a verification state
where reuse would not be irresponsible.
