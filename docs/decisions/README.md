# Architecture Decision Records

An ADR records a decision that would be expensive or confusing to reverse silently: something a
reader six months from now would otherwise have to reverse-engineer from the code.

Every ADR states **Context**, **Decision**, **Alternatives considered** (with the reason each was
rejected), **Consequences** — including the bad ones — and **Revisit if**, a concrete condition that
would reopen the question.

An ADR is never edited to look correct in hindsight. A decision that turns out wrong is superseded by
a new ADR that says so, and the original stays.

| ID | Title | Status | Date |
|---|---|---|---|
| [ADR-0001](ADR-0001-repository-structure.md) | Repository structure and deferred implementation tree | Accepted | 2026-09-09 |
| [ADR-0002](ADR-0002-independence-from-aura.md) | RADIUS is independent of AURA | Accepted | 2026-09-09 |
| [ADR-0007](ADR-0007-licensing-deferred.md) | No licence at this stage | Accepted | 2026-09-09 |
| [ADR-0008](ADR-0008-publication-architecture.md) | Publication architecture and data governance | Accepted | 2026-09-09 |

ADR-0003 to ADR-0006 are reserved for the mathematical decisions of the research phase (frames and
conventions, attitude representation, state vector, integrator) and are written when that research
concludes, not before.
