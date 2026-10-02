# ADR-0012 — RADIUS is closed: development stops, and the repository becomes a terminal record

**Date:** 2026-10-01 · **Status:** Accepted
**Supersedes:** nothing. ADR-0001 … ADR-0011 stand as written
**Complements:** ADR-0011 (maturity labelling) · ADR-0002 (independence from AURA) · ADR-0007 (no licence)
**Evidence:** `CLOSURE.md` §4; the repository itself; `research/RESEARCH_LOG.md` RL-0013 … RL-0016
**Decided by:** the researcher

## Context

RADIUS reached step 2 of its 14-step implementation order. Frames, attitude and quaternion
mathematics are implemented and verified; five analytical anchors (V-EOM-01 … V-EOM-05) are frozen;
and one production dynamics function exists — the rigid-body rotational derivative, verified against
V-EOM-05 and mutation-tested (RL-0016). The suite runs 135 tests, none skipped. Nothing is
validated.

Three observations prompted the question of whether to continue.

**The last three capability-bearing phases bore no capability.** ADR-0010 repaired a verification-ID
collision and a symmetry-axis convention mismatch; ADR-0011 repaired status language that claimed
nothing existed after code did; RL-0015 repaired V-EOM-05, an anchor that as specified could not
detect the error class it existed to catch. Each was necessary. Each was also repair of a defect
this project had created, not an extension of it.

**The ratios had inverted.** 6,900 lines of specification and governance and 3,432 lines of tests
support 657 lines of production code. `INTERPRETATION`: the apparatus had grown faster than the
substance it governed and had begun to consume the development budget — and the rigour could not be
relaxed to compensate, because the rigour was the project's only differentiator from a short script
against an existing simulator.

**No path to validation existed, and none could.** No independent 6-DOF benchmark trajectory was
found; no traceable aerodynamic coefficient set exists (`A-AER-03`, Q8, and the quality gate
correctly does not pass for that phase); jet damping is omitted with unbounded magnitude
(`A-VM-03`). Validation requires independent reference data, and the hard scope boundary in
`CLAUDE.md` excludes the sources from which such data would come. `INTERPRETATION`: the terminal
state of the project *as scoped* was always going to be "verified, never validated" — a correct
implementation of equations nobody disputes.

Two further matters belong in the record because they bear on what the project was.

`LIMITATION`. **Methodological independence from AURA was never achieved.** The code independence
ADR-0002 actually required held completely and was audited: no import, no shared schema, no
dependency, AURA never modified. But the apparatus — ID-cited assumption registers, ADRs, frozen
anchors, component status vocabularies, scoped maturity labelling, deny-by-default publication
governance — is AURA's methodology transplanted. ADR-0002 never claimed intellectual independence,
and it was not available.

`LIMITATION`. **No systematic literature search was run for RADIUS.** There is no TV-N1 equivalent
here. The judgement that this work is not novel is an interpretation, not an audited finding, and no
bibliographic claim is made for it. The project never asserted novelty, so nothing published depends
on the question. This ADR does **not** close a novelty gate, and must not be cited as though it had.

## Decision

### 1. Development stops

No further implementation phases. Specifically not begun: attitude propagation, the integrator,
translational dynamics, the assembled state derivative, atmosphere, aerodynamics, variable mass,
uncertainty propagation. The remaining frozen anchors V-EOM-01 … V-EOM-04 stay frozen and unconsumed.

### 2. The repository becomes a terminal record, and says so

`CLOSURE.md` at the repository root is the single authoritative statement of final state: inventory,
what was verified, what was never validated, the findings, and why the work stopped. Where any other
document implies work continues, `CLOSURE.md` governs. The open next-action in
`handoffs/current_state.md` is closed rather than left pointing at a phase that will not run — an
abandoned-looking repository misrepresents its own state as surely as an over-claiming one.

### 3. The maturity label does not change

RADIUS remains **Research / Architecture — foundations implemented and verified; 6-DOF dynamics
specified with verification anchors, not yet implemented**. Closure is a lifecycle state; the §11
label is a claim about what the code does. Stopping work promotes nothing. ADR-0011 §4 fixed the
promotion criteria in advance so that this could not be blurred at the end, and no row of that table
is met.

### 4. The historical record is not rewritten

ADRs, the pre-implementation audit, the quality-gate verdict and RL-0001 … RL-0016 remain exactly as
written, including statements that were true when written and are superseded now. Where such a
document also reads as a current-status source, it receives a pointer to `CLOSURE.md`, not an edit.
Public history is not rewritten to make the project look finished — the same rule that forbids
rewriting it to hide inconvenient development.

### 5. No licence is added

ADR-0007 stands. Closure is not publication for reuse, and a terminal repository is not thereby made
reusable software.

### 6. The findings are published, not just the status

`CLOSURE.md` §4 records what the project actually produced: four specification defects caught before
any code existed — including F-1, the −J̇ω term whose factor-of-two spurious spin-up **no test could
have caught**, because a test-first project derives its oracle from the same specification that
carries the error; five defects found in the project's own verification apparatus; and five
methodological results, of which the sharpest are that an anchor sampled at convenient fractions of
a period is blind to a family of sign and magnitude errors, and that a mutation which is a
mathematical identity must be recorded as a blind spot rather than counted as a kill.

That content is the project's output. Publishing the status without it would discard the result and
keep the bookkeeping.

## Alternatives considered

- **Continue to the integrator and attitude propagation.** Rejected: it repeats the cost structure
  in Context without changing the terminal state in §5 — more verified equations, still no
  validation, still no novelty claim available. The marginal return per phase had already been
  falling for several phases.
- **Relax the rigour to cover more ground.** Rejected, and the strongest rejection of the three. The
  rigour *is* the deliverable. A 6-DOF simulator built without it is a worse version of software
  that already exists; the specification-first, anchor-first, mutation-tested method is the only
  thing here that was worth the effort.
- **Leave the repository as it stands, without a closure document.** Rejected: the README promises a
  simulator, the handoff points at a next phase, and the maturity label says dynamics are "not yet
  implemented". A reader would find a project that appears abandoned mid-stride rather than concluded
  — a misrepresentation of state, which §11 forbids without limiting itself to overstatement.
- **Delete the repository, or make it private.** Rejected: the findings in `CLOSURE.md` §4 are the
  usable output, and a negative result published is worth more than a negative result withdrawn.
  AURA's precedent applies — its novelty gate returning FAIL is one of its more credible artifacts.
- **Reframe the scope now, to the verification methodology with dynamics as the case study.**
  Rejected *as part of closure*, though recorded in `CLOSURE.md` §8 as the soundest basis for
  reopening. Rewriting the project's framing at termination would retrofit a research question onto
  work already done, which is the one thing the researcher's authority over the question exists to
  prevent.

## Consequences

- The repository is honest about being finished, and the §4 findings are discoverable from the root
  rather than buried in a research log.
- Four exact analytical oracles (V-EOM-01 … V-EOM-04) are published and unconsumed. They remain
  correct and usable by anyone implementing these equations; they are simply not exercised here.
- The open questions in `handoffs/current_state.md` §6 become permanent, recorded gaps rather than
  a work queue. Q8 stays open; it is not closed by abandonment.
- Cost, stated plainly: the project stops without having simulated anything, and the verification
  method it demonstrates is evidenced on six verification IDs out of 65+ specified. The
  demonstration is real but narrow, and `CLOSURE.md` §7 says so rather than letting the test count
  imply breadth.
- `radius/` continues to run and continues to pass. Nothing is deleted on closure.

## Affected documents

Created: `CLOSURE.md`; this ADR.
Updated (current-status statements and the open next-action only): `README.md`;
`handoffs/current_state.md`; `radius/__init__.py`; `docs/architecture/ARCHITECTURE.md` header;
`docs/methodology/VERIFICATION_AND_VALIDATION.md` §2; `docs/decisions/README.md`;
`research/RESEARCH_LOG.md` (RL-0017).

Deliberately unchanged as historical records: ADR-0001 … ADR-0011;
`PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`; `QUALITY_GATE.md`; RL-0001 … RL-0016;
`docs/methodology/PUBLICATION_POLICY.md` §11 (the taxonomy is unchanged because the label is);
RS-001 … RS-008; `docs/assumptions.md`; `AURA_INTERFACE.md`.

## Verification impact

**None.** No test, oracle, numerical literal, identifier, convention or assumption status changes:
**135 executed / 135 passed / 0 failed / 0 skipped**, before and after. Nothing under `radius/` is
modified except the package docstring. No dependency is added or removed.

## Revisit if

An independent 6-DOF benchmark trajectory becomes available — the binding constraint, and the only
change that alters the terminal state in `CLOSURE.md` §5; or the deliverable is deliberately reframed
as the verification methodology itself, with rigid-body dynamics as the case study rather than the
product; or a traceable aerodynamic coefficient set is found, closing Q8 and `A-AER-03`.

Reopening under the existing scope — continuing to implement equations against frozen anchors —
would reproduce the Context above, and is not recommended.
