# RADIUS — Research and Decision Log

Chronological, append-only. Each entry records a decision that changed the direction of the work,
in the form:

**DATE · DECISION · RATIONALE · EVIDENCE · IMPACT · NEXT STEP**

Entries are not edited after the fact. A decision that turns out to be wrong gets a later entry
saying so.

---

## 2026-09-09 · RL-0001 — Project created; scope fixed as academic computational aerospace engineering

**DECISION.** RADIUS is created as an academic computational aerospace-engineering project studying
nonlinear 6-DOF vehicle dynamics, numerical methods and uncertainty propagation. A hard scope
boundary is written into `CLAUDE.md`: no real or operational vehicle design, no propulsion hardware
content, no targeting or deployment procedures, no flight-readiness claim. Propulsion enters only as
a mathematical external-force and mass-flow abstraction.

**RATIONALE.** The interesting and defensible content of this project is mathematical and
computational: how the equations are formulated, how frames and conventions are made unambiguous, how
integration error behaves, and how uncertainty propagates. None of that requires — or is improved
by — hardware specificity. Writing the boundary down at project creation is cheaper than negotiating
it repeatedly later, and it makes any drift visible as a violation rather than a gradual slide.

**EVIDENCE.** Design decision, not an empirical result. `ASSUMPTION`/`INTERPRETATION` class.

**IMPACT.** Determines what the variable-mass work can and cannot contain (see RL-0008): the mass and
force abstraction is developed as a mathematical interface, and the physical realisation of such a
force is out of scope permanently, not deferred.

**NEXT STEP.** Repository foundation, then the mathematical specification.

---

## 2026-09-09 · RL-0002 — Only directories with content are created

**DECISION.** The implementation tree (`radius/`, `tests/`, `validation/`, `experiments/`,
`results/`, `infrastructure/`, `handoffs/`) is not created yet; the path layout is fixed by ADR-0001
so documents can reference it, but each directory appears in the commit that first fills it.

**RATIONALE.** An empty tree of ten subsystem directories asserts an organisation the project has not
earned and misrepresents its state — the one thing the README exists to state accurately.

**EVIDENCE.** `docs/decisions/ADR-0001-repository-structure.md`.

**IMPACT.** A reader browsing the repository today sees documentation and nothing else, which is
correct.

**NEXT STEP.** Phase 2 creates `radius/frames/` and `tests/`.

---

## 2026-09-09 · RL-0003 — RADIUS takes no dependency on AURA

**DECISION.** No import, schema, configuration format, submodule or vendored copy. Capabilities AURA
also has (provenance, seeding, Monte Carlo, experiment registry) are implemented independently in
RADIUS, sized to RADIUS's needs.

**RATIONALE.** If AURA is eventually to use RADIUS as a test subject, RADIUS must be an independent
object of study; shared code is a shared-mode failure that would corrupt the system and its evaluator
identically and undetectably. Separately, AURA's own record shows a terminated research question and
a failed novelty gate, so coupling to it would import instability for no benefit.

**EVIDENCE.** `docs/decisions/ADR-0002-independence-from-aura.md`; AURA's `FINDINGS.md` and TV-N1
audit, read in the read-only audit preceding this project's creation.

**IMPACT.** Some duplication is accepted. Any eventual coupling lives on AURA's side as an adapter,
not in RADIUS.

**NEXT STEP.** Keep the AURA interface conceptual (`docs/architecture/AURA_INTERFACE.md`).

---

## 2026-09-09 · RL-0004 — No licence

**DECISION.** No licence file; the README states that no reuse rights are granted.

**RATIONALE.** Licensing is a decision about downstream use, and downstream use of an unimplemented,
unverified dynamics model is the thing the project least wants to encourage. The decision is
effectively one-way once copies exist.

**EVIDENCE.** `docs/decisions/ADR-0007-licensing-deferred.md`.

**IMPACT.** Repository is readable and auditable but not reusable.

**NEXT STEP.** Revisit only on explicit researcher instruction.
