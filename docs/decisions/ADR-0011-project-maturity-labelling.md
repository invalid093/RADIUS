# ADR-0011 — Project maturity labelling: the project label is scoped, and is not the component status

**Date:** 2026-09-12 · **Status:** Accepted
**Amends:** `PUBLICATION_POLICY.md` §11 · **Complements:** ADR-0010 §5 (component status vocabulary) ·
**Supersedes:** nothing — ADR-0008 stands
**Evidence:** ADR-0010 "Affected documents"; the repository itself

## Context

ADR-0010 corrected documents that claimed **more** than existed. It also found, and deliberately did
not fix, the opposite fault: current documents claiming that **nothing** exists. README said
"Implemented: nothing — no source code exists" and "Verified: nothing — none written"; the handoff
snapshot, the assumptions register, the research index and three specification headers said the same.

Those statements stopped being true at Phase 2B. `radius/frames.py` and `radius/math/quaternion.py`
exist, and V-FRM-05, V-FRM-08, V-FRM-09, V-FRM-10 and V-ATT-01 exercise them; the suite runs 94 tests
with none skipped. The dynamics equations are specified and carry four frozen analytical anchors
(V-EOM-01 … V-EOM-04), but no dynamics, integrator, atmosphere, aerodynamic or trajectory code has
been written.

Correcting the statements needed a decision rather than an edit, because `PUBLICATION_POLICY.md` §11
assigns the project a single maturity label and defined **Research / Architecture** as "Specification
only. Nothing implemented". Under that definition RADIUS no longer qualified for its own label, and
the next labels up — **Experimental** ("implemented, unverified") and **Preliminary** ("implemented,
partially verified") — would each tell a reader the simulator exists.

## Decision

### 1. The label, stated scoped

RADIUS keeps the §11 label **Research / Architecture**, and every current-status statement carries it
with its scope:

> **Research / Architecture — foundations implemented and verified; 6-DOF dynamics specified with
> verification anchors, not yet implemented.**

The scoped form is what communicates, in one line: source code exists; some of it is verified; the
dynamics specification has verification anchors; the complete 6-DOF simulation does not exist; and
the project is under active development.

### 2. §11's first row is widened, not replaced

"Specification only. Nothing implemented" becomes "Specification, with at most foundational utilities
implemented and verified. The model the project exists to build is not implemented." The other four
labels are untouched.

### 3. Project label ≠ component status

The §11 table labels the **project** — specifically the model it exists to build. Terms, subsystems
and verification cases carry the finer component vocabulary of ADR-0010 §5. The two are not
interchangeable, and a document states which it is using. Collapsing them is what produced both
faults: the over-claims ADR-0010 corrected and the under-claims corrected here.

### 4. Promotion criteria, fixed in advance

| When | Label |
|---|---|
| Foundational utilities only, however well verified | **Research / Architecture** (scoped) |
| The 6-DOF model runs, unverified | **Experimental** |
| The 6-DOF model runs and part of it is verified against the anchors | **Preliminary** |
| The implementation is demonstrated to solve the intended equations, by stated tests | **Verified** |
| Adequate against independent reference data, for a stated purpose, to a stated tolerance | **Validated** |

Fixed now, before the results that would tempt a generous reading of them.

### 5. What may be corrected under this ADR

Only statements describing the **current** state. Dated records — ADRs, the pre-implementation audit,
the quality-gate verdict, research-log entries, earlier phase reports — are historically truthful and
are not rewritten. Where a historical document is *also* read as a current-status source, it gets the
smallest possible clarification instead.

## Alternatives considered

- **Promote the project to Preliminary.** Rejected: "implemented, partially verified" describes a
  simulator that exists and is partly checked. RADIUS has no simulator. This would be the exact
  misrepresentation §11 exists to prevent, in the flattering direction.
- **Invent a new label ("Foundations", "Alpha").** Rejected: the policy already defines a taxonomy,
  and a private sixth label would make RADIUS's maturity incomparable with its own policy.
- **Leave the statements alone.** Rejected: they are false, and §11 forbids misrepresenting maturity
  without limiting that to overstatement. A reader deciding whether the repository is worth reading
  is misled either way.
- **Drop the project label and publish only component statuses.** Rejected: a reader needs one
  honest summary before the detail, and the checklist audits the README against §11.

## Consequences

- The README, the handoff snapshot and any future status summary carry the scoped label, not a bare
  stage name.
- A phase that implements a subsystem updates its document's status line using the ADR-0010
  vocabulary, and does not touch the project label. Changing the project label requires meeting a row
  of the table in Decision 4.
- The pre-push checklist item "does `README.md` still state the project's actual maturity (policy
  §11)?" is now answerable against a definition that matches the repository.
- Cost: the project-level label is deliberately conservative, so a reader who reads only the label
  under-estimates what exists. The scope clause and the status table are what carry the detail.

## Affected documents

Corrected here (current-status statements only): `README.md`; `handoffs/current_state.md`;
`docs/assumptions.md` header; `docs/research/README.md`; `docs/methodology/NOTATION_AND_CONVENTIONS.md`
header; RS-001 and RS-002 headers; `docs/architecture/ARCHITECTURE.md` header;
`docs/methodology/PUBLICATION_POLICY.md` §11; `docs/methodology/VERIFICATION_AND_VALIDATION.md` §2.

Deliberately unchanged, as historical records: ADR-0001 … ADR-0010 (including ADR-0007's "RADIUS is
at Phase 1. Nothing is implemented"), `PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`, `QUALITY_GATE.md`,
RL-0001 … RL-0013. Unchanged because still true: `AURA_INTERFACE.md`, `docs/PROVENANCE.md` §8 (no
experiment has been run), and the RS-003 … RS-008 headers.

## Verification impact

**None.** No test, oracle, numerical literal, identifier, convention or assumption status changes:
94 executed / 94 passed / 0 failed / 0 skipped, before and after. Q8 remains open. Nothing under
`radius/` is touched, and no dependency is added.

## Revisit if

The 6-DOF model runs end to end — then Decision 4 selects the next label; a subsystem is implemented
and its document's status line needs the ADR-0010 vocabulary; or the policy's taxonomy is revised.
