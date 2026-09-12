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

**NEXT STEP.** Revisit only on explicit researcher instruction. Before any release presented as
final, the licence must be settled explicitly along with every third-party dependency's licence and
required notices.

---

## 2026-09-09 · RL-0005 — Deny-by-default publication architecture adopted before any data exists

**DECISION.** A three-layer publication architecture: a policy classifying every artifact into five
classes (`docs/methodology/PUBLICATION_POLICY.md`); a `.gitignore` rewritten to deny each class of
generated artifact wholesale and re-include named curated exceptions; and a pre-push audit procedure
covering the working tree and the git history separately
(`infrastructure/publication_checklist.md`). Provenance requirements specified in
`docs/PROVENANCE.md`. GitHub secret scanning and push protection enabled.

**RATIONALE.** Three pressures make the case-by-case default wrong. Monte Carlo output is enormous
and individually worthless — the ensemble statistic is the result, not any trajectory in it.
Generated artifacts are self-justifying: a file that exists feels like it should be kept. And Git's
costs are permanent and delayed — a large blob or a leaked secret persists in every clone and is not
fixed by deleting the file later. The policy therefore had to be written before the first large run,
while none of the artifacts exist and none of them are anyone's work yet.

A blocklist `.gitignore` was rejected: it fails silently on the artifact class nobody anticipated,
which is precisely the class that causes the accident. Deny-by-default fails toward not publishing.

**EVIDENCE.** `docs/decisions/ADR-0008-publication-architecture.md`. The `.gitignore` was tested
against dummy artifacts (`CALCULATION`, 2026-09-09): curated result files, figures and figure scripts
are trackable; bulk `.npz`, per-run directories, scratch, logs, `.env`, stray notebooks and agent
directories are all denied. One inconsistency was found and fixed in that test — notebooks under
`notebooks/` were trackable despite the policy stating they require an explicit force-add.

**IMPACT.** Publishing an artifact now takes deliberate effort, which is the mechanism rather than a
side effect. It also makes the determinism guarantee load-bearing: because ensembles are not
published, V-NUM-03 (bitwise determinism from config + seed) is what makes their absence legitimate.
`infrastructure/` was created ahead of the ADR-0001 schedule because the checklist is content with a
documented purpose — an instance of that principle, not an exception to it.

**NEXT STEP.** Resume the mathematical specification (RS-002 onward) under these rules.

---

## 2026-09-09 · RL-0006 — Conventions fixed before any equation is written

**DECISION.** NED with $z$ **down**; all frames right-handed; passive transformations with subscripts
reading "to ← from"; Euler 3-2-1; **Hamilton product, scalar-first quaternion** $q_{BI}$; SI and
radians internally with degrees only at boundaries; moments about the instantaneous centre of mass
unless a reference point is named. Fixed in one authoritative document.

**RATIONALE.** Most 6-DOF defects are not errors of physics but two modules disagreeing about what a
symbol means. Such an error is invisible to internal consistency checks, because a *uniformly applied*
wrong convention is self-consistent. It follows that hand-computed expected values are the only test
class that can catch it — which is why V-FRM-08 and V-ATT-01 are mandatory rather than optional.

**EVIDENCE.** ADR-0003; SRC-005 (Shuster) documents the competing quaternion conventions that make
this necessary. The quaternion-to-DCM formula was checked symbolically against a pure-yaw rotation
during specification (`CALCULATION`).

**IMPACT.** Changing any convention later invalidates every verification test and every stored
reference trajectory, and requires a superseding ADR naming the invalidated data.

**NEXT STEP.** Frames and mathematical utilities (Phase 2).

---

## 2026-09-09 · RL-0007 — Flat non-rotating Earth accepted, and quantified rather than asserted

**DECISION.** The NED frame is treated as inertial for Phases 1–10, with a provisional validity domain
of roughly 10 km range and 60 s duration. Gravity varies inverse-square with altitude from the start;
constant $g$ is retained only as a switch enabling closed-form verification.

**RATIONALE.** The verification programme rests on comparing against closed-form analytical solutions,
and those exist for constant gravity in a non-rotating frame but not once the frame rotates. Starting
flat establishes that the integrator and the rigid-body equations are correct *before* introducing
effects that make correctness unfalsifiable by hand.

**EVIDENCE.** RS-001 §3 (`CALCULATION`, 2026-09-09): neglected Coriolis acceleration $\le 2\Omega_E V$
gives ~730 m over 100 s at 1000 m·s⁻¹; curvature drop $d^2/2R_E$ is 196 m at 50 km range; gravity is
0.94 % low at 30 km if held constant. These are estimates of neglected terms, **not measured errors** —
measuring them would need a rotating-Earth implementation, which does not exist.

**IMPACT.** The validity domain must be quoted with every result until an ECEF/ECI extension exists.
Because the altitude correction is cheap and exact, holding $g$ constant was rejected as a default.

**NEXT STEP.** ECEF extension deferred; the gravity interface takes a position, not an altitude, so
the extension is a substitution rather than a rewrite.

---

## 2026-09-09 · RL-0008 — Quaternion attitude; Euler ruled out at the initial condition

**DECISION.** Quaternion as the integrated attitude state; DCM computed on demand and never stored;
Euler angles at input/output only. Norm maintained by post-step renormalisation, explicitly **not**
inside RK stages.

**RATIONALE.** The general arguments for quaternions are well known and were not decisive on their
own. What was decisive is RADIUS-specific: in a 3-2-1 sequence the Euler singularity is at
$\theta=\pm90°$, which for an aircraft is an aerobatic edge case but for a **vertically launched
vehicle is the initial condition of the most obvious test case the project will run**. Choosing a
different sequence moves the singularity rather than removing it, and makes the representation's
validity a function of the trajectory.

Normalising *inside* an RK stage would change the stage function from the $f$ the Butcher tableau's
order conditions were derived for, silently invalidating the method's order — a plausible trajectory
with the wrong convergence rate. Recorded so it is not done.

**EVIDENCE.** ADR-0004, RS-002. The claim that post-step normalisation preserves fourth order is
argued in RS-002 §6 and registered as `A-ATT-01` — a **prediction to be tested by V-NUM-07**, not a
result.

**IMPACT.** No singularity at any attitude. Branch-free, division-free kinematics, which supports the
determinism guarantee. Double cover forces geodesic-angle comparison rather than component-wise
differences.

**NEXT STEP.** Phase 3.

---

## 2026-09-09 · RL-0009 — Inertial velocity chosen over the body-axis convention

**DECISION.** The 14-element state integrates **inertial** velocity, against the aerospace convention
of body-axis $(u,v,w)$. Mass is an integrated state, not a prescribed function of time.

**RATIONALE.** Three reasons, the second decisive. The translational equation loses its transport term
$-\boldsymbol\omega\times\mathbf{v}$, whose sign error would be small and plausible rather than
obvious. **Verification localises**: free-fall and ballistic references are exact and
attitude-independent in inertial velocity, whereas in body axes the same physical test must be
expressed through the attitude history, coupling the translational test to the rotational
implementation — so a failure no longer says which is broken. And the variable-mass momentum-flux term
separates cleanly from frame-rotation terms, which is a known failure mode in variable-mass
derivations.

The conventional choice's advantage is smaller than it appears: $\alpha,\beta$ need air-relative body
velocity, so the transformation is evaluated every derivative call either way.

**EVIDENCE.** ADR-0005, RS-003 §3. `INTERPRETATION` — an argued design choice, not a measured result.

**IMPACT.** $u,v,w$ must be computed for aerodynamics and for comparison with literature. The two
formulations are analytically equivalent, so switching later invalidates no physics — only regenerable
reference trajectories.

**NEXT STEP.** Phases 3–4.

---

## 2026-09-09 · RL-0010 — Fixed-step RK4; adaptive stepping deferred on determinism grounds

**DECISION.** Fixed-step classical RK4, with explicit Euler retained as a verification comparator.
Dormand–Prince RK5(4) evaluated and deferred with a stated revisit condition. Events located by
bisection with restart.

**RATIONALE.** Requirements were ranked before methods were considered, and determinism was placed
above efficiency. This is not fastidiousness: the publication policy declines to publish Monte Carlo
ensembles *because they are regenerable*, which is true only if regeneration is exact. Adaptive
stepping makes the step sequence depend on a floating-point comparison against a tolerance, so a
last-bit difference can flip an accept/reject decision and the runs diverge. It also makes order of
accuracy — the most informative verification test available — much harder to measure, because $h$
stops being an input.

Euler is kept precisely because its expected slope is *different*: if RK4 and Euler both measured 4,
the harness would be measuring something other than the integrator.

**EVIDENCE.** ADR-0006, RS-005. SRC-009 for the rejected method. `CALCULATION`: for a 5 Hz mode,
stability permits $h<90$ ms while a 20-steps-per-period accuracy rule demands $\le10$ ms — a factor of
nine, which is why the stability bound is never the step-selection criterion.

**IMPACT.** V-NUM-03 (determinism) becomes load-bearing for ADR-0008: if it fails, the argument for
not publishing ensembles fails with it. The proposed $h=10^{-3}$ s is a **proposal, not a result**.

**NEXT STEP.** Phase 5, then the analytical verification cases.

---

## 2026-09-09 · RL-0011 — Quality gate: PASS for Phases 2–6, NOT PASS for aerodynamics

**DECISION.** The thirteen-question specification gate was evaluated. Phases 2–6 (frames, math, state,
equations of motion, integration, analytical verification) **pass** and implementation may begin.
Phase 8 (aerodynamics) **does not pass**. Phase 7 (atmosphere) passes conditional on checking the
layer table against SRC-008.

**RATIONALE.** Question 8 — how forces and moments are represented — is only partially answered. There
is **no traceable source for an aerodynamic coefficient set**, so every aerodynamic result would be
scoped to "a hypothetical vehicle with the stated coefficients"; and the initial model has no Mach
dependence, which may make it invalid across most of a typical trajectory. Per the gate rule, the
correct action is to continue researching that subsystem rather than implement it and discover the
problem afterwards.

**EVIDENCE.** `docs/research/QUALITY_GATE.md`. Three quantities are recorded as **unbounded**: jet
damping (`A-VM-03`), CM-motion momentum (`A-VM-02`), and the flat-Earth validity bound (an estimate of
neglected terms, not a measurement).

**IMPACT.** Implementation proceeds through Phase 6. No aerodynamic claim will be supportable until
the coefficient-provenance gap closes, and no rotational-damping claim is supportable at all while jet
damping is unbounded.

**NEXT STEP.** Phase 2 — `radius/math/` and `radius/frames/` with their verification tests, starting
with the hand-computed convention tests V-FRM-08 and V-ATT-01. In parallel, search for a published
generic aerodynamic coefficient set and for an independent 6-DOF benchmark trajectory.


---

## 2026-09-09 · RL-0012 — Pre-implementation mathematical audit: four defects, one load-bearing

**DECISION.** Before writing any Phase 2 code, the whole specification was independently audited as a
*candidate* rather than as settled. Verdict **PASS WITH REQUIRED CORRECTIONS**; corrections applied.
The load-bearing one removes the $-\dot{\mathbf{J}}\boldsymbol{\omega}$ term from the rotational
equation (ADR-0009).

**RATIONALE.** The specification had already passed a quality gate, which is precisely why it needed
an adversarial re-reading: a gate that has returned PASS is the least likely thing to be re-examined,
and the earlier gate had checked that each answer *existed* rather than that the answers were
*consistent with each other* and *covered by tests*.

**EVIDENCE.** `docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`. Numerical checks run as audit
artifacts (`CALCULATION`, 2026-09-09):

- **F-1 (load-bearing).** Torque-free axisymmetric body depleting 1000 → 500 kg: the specified
  equation gives $\omega_z = 20.0$ rad·s⁻¹ where the truth is $10.0$. The
  $-\dot{\mathbf{J}}\boldsymbol{\omega}$ term forces conservation of $\mathbf{J}\boldsymbol{\omega}$ —
  a skater pulling their arms in — which is internal *redistribution*, not ejection. It is the exact
  rotational analogue of the $\frac{d}{dt}(m\mathbf{v})=\mathbf{F}$ error that RS-004 §3.1 identifies
  and rejects for translation, three sections earlier. Analytically, the angular-momentum flux of
  co-rotating ejected mass is $-\dot{\mathbf{J}}\boldsymbol{\omega}$, so the two cancel exactly.
- **F-2.** $\mathbf{T}_{BW}=\mathbf{R}_y(-\alpha)\mathbf{R}_z(\beta)$ contradicted RADIUS's own
  $\alpha,\beta$ definitions: at $\beta=+30°$ it returns $\beta=-30°$. Corrected to
  $\mathbf{R}_y(\alpha)\mathbf{R}_z(-\beta)$.
- **F-3.** $\mathbf{T}_{BI}(q)$ was undefined at the non-unit quaternions RK stages necessarily
  produce; $\mathbf{T}_{BI}(kq)=k^2\mathbf{T}_{BI}(q)$, so the raw formula scales every force by
  $\lVert q\rVert^2$ inside stages 2–4. Fixed by dividing by $q\cdot q$.
- **F-4.** Quaternion composition order is the **reverse** of matrix composition order
  ($\mathbf{T}(q_a\otimes q_b)=\mathbf{T}(q_b)\mathbf{T}(q_a)$) and this was stated nowhere.

**What survived.** Frame conventions, the quaternion kinematic equation (re-derived independently and
confirmed against a **non-principal** axis, which separates the competing product orders by $10^{12}$
where a principal-axis test cannot separate them at all), translational dynamics across four limiting
cases, the gyroscopic term, and the atmosphere model against published values at sea level and 11 km.

**IMPACT.** RS-001, RS-002, RS-003, RS-004, RS-005, RS-006, RS-008 and the notation document amended;
`A-VM-05` and `A-NUM-05` registered; `A-VM-03` re-scoped; six tests added (V-EOM-09/V-VM-10,
V-FRM-09, V-FRM-10, V-ATT-02b, V-NUM-09, V-ATM-09). A timestep-selection *methodology* replaces the
bare proposal of $h=10^{-3}$ s. Two hazards disappeared with the removed term: the analytic-vs-finite-
difference $\dot{\mathbf{J}}$ question, and the risk of a nested discretisation inside an RK stage.

**The generalisable finding**, recorded because it will recur: *every rotational test in the original
suite ran at constant mass*, so the variable-mass rotational equation was exercised by nothing. A test
suite must be audited for **coverage of the equations as written**, not only for the correctness of
each test. And an argument made well in one section does not propagate itself to the analogous case in
another.

**NEXT STEP.** Phase 2 — `radius/math/` and `radius/frames/`, beginning with the hand-computed
convention tests. Q8 (aerodynamic coefficients) remains NOT PASS; the audit deliberately did not close
it by inventing data.

---

## 2026-09-11 · RL-0013 — Dynamics conventions reconciled before any rotational code

**DECISION.** ADR-0010:

1. V-EOM-03 remains the frozen body-force anchor. The never-frozen principal-axis case once listed
   under that number is renumbered V-EOM-10.
2. The symmetry axis of an axisymmetric RADIUS vehicle is $x_B$.
3. Axisymmetric moments are $J_\parallel$ and $J_\perp$, and the body-frame transverse rate is
   $\lambda = \frac{J_\parallel-J_\perp}{J_\perp}\omega_\parallel$; $J_t$ and $J_z$ are retired.
4. A $z$-symmetric labelling survives only as the named, analysis-only canonical principal frame $P$,
   mapped to $B$ by $x_P=y_B$, $y_P=z_B$, $z_P=x_B$.
5. Status words have defined meanings, and **Implemented** requires production code that passes named
   tests.

**RATIONALE.** Each defect was harmless on paper and expensive in code:

- **Identifier.** An identifier naming two claims breaks the chain from requirement to test.
- **Symmetry axis.** The rotational specification put the symmetry axis on $z$, while the
  specification's own rates, moment signs, aerodynamic channels, exhaust direction and pitch inertia
  $J_{yy}$ all treat $x_B$ as the vehicle axis. That would have reached a mass-property input as a
  silent axis swap. $J_z$ would also have been read as $J_{zz}$, a transverse moment on this vehicle.
- **Status.** "Implemented" with no code behind it is the kind of maturity misstatement the
  publication policy forbids.

The axis was decided on the specification's own evidence, not on which choice needed fewer edits.
The $z$-symmetric form was kept, named, because the frozen oracle is correct as mathematics and its
two forms together catch a hard-coded axis.

**EVIDENCE.** `CALCULATION`, 2026-09-11, in exact rational arithmetic:

- The body-axis Euler equations for $\mathbf{J}^B=\mathrm{diag}(J_\parallel,J_\perp,J_\perp)$ with
  moments, and the frame-$P$ form, agree with
  $\mathbf{J}\dot{\boldsymbol\omega}+\boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega)=\mathbf{M}$ over
  1000 random cases.
- The $P\to B$ mapping has determinant $+1$ and carries torque-free solutions to torque-free solutions.

The V-EOM-04 identifier rename was checked three ways:

- the syntax tree is identical once renames are reversed and strings blanked;
- numeric literals, assertion calls and test methods are unchanged (713, 144, 63);
- the mutation harness, re-run, gives the same failure count for every one of its 20 runs.

**IMPACT.**

- **Synchronised:** RS-004 (§2, §4.2, §4.3, §7), RS-008 (V-VM-10), NOTATION (§3 pointer, new §5.1, a
  §8 naming rule), the V&V record (V-EOM-04 findings marked resolved), ARCHITECTURE §6, the ADR index
  and the V-EOM-04 test identifiers.
- **Unchanged:** no frozen numerical value, and no convention of NOTATION §1–8; no reference data is
  invalidated.
- **Flagged, not edited:** stale *under*-claims of implementation status — README, the handoff
  snapshot, the assumptions header and three specification headers still say no code exists, while
  `radius/frames.py` and `radius/math/quaternion.py` do and are verified. These are left for a
  maturity-label decision (PUBLICATION_POLICY §11).

**NEXT STEP.** Researcher decision on the project maturity label, followed by correction of the stale
status statements ADR-0010 lists, so that the public record neither over- nor under-states what
exists before rotational dynamics code is written.

---

## 2026-09-12 · RL-0014 — Project maturity label scoped; stale "nothing exists" statements corrected

**DECISION.** ADR-0011. RADIUS keeps the **Research / Architecture** label of PUBLICATION_POLICY §11,
stated with its scope — *foundations implemented and verified; 6-DOF dynamics specified with
verification anchors, not yet implemented*. §11's first row is widened to admit verified foundational
utilities, project-level maturity and ADR-0010's component status are declared distinct vocabularies,
and the criteria for the next label are fixed in advance. Current-status statements claiming that no
source code exists were corrected; dated records were not.

**RATIONALE.** §11 forbids misrepresenting maturity and does not limit that to overstatement. Since
Phase 2B the README had told a reader that nothing was implemented and nothing verified, while
`radius/frames.py` and `radius/math/quaternion.py` were carrying 94 passing tests. The obvious repair
— promoting the project to **Preliminary** — would have been the opposite error, because that label
says a model exists and is partly verified, and RADIUS has no simulator. Scoping the existing label
was the only option that states both facts at once. Fixing the promotion criteria now, before there
are results to flatter, is the same discipline the project applies to tolerances.

**EVIDENCE.** `FACT`, 2026-09-12: `radius/` contains `frames.py` and `math/quaternion.py` and nothing
else; `python -m unittest discover -s tests -t tests` reports **94 executed / 94 passed / 0 failed /
0 skipped**; V-FRM-05, V-FRM-08, V-FRM-09, V-FRM-10 and V-ATT-01 exercise those modules; V-EOM-01 …
V-EOM-04 are frozen oracles with no implementation to consume them; no dynamics, integrator,
atmosphere, aerodynamic, propulsion or trajectory code exists.

**IMPACT.**

- **Corrected** (current statements only): README; `handoffs/current_state.md`; the assumptions
  register header; the research index; the NOTATION, RS-001, RS-002 and ARCHITECTURE headers;
  PUBLICATION_POLICY §11; the V&V status table, which now carries an explicit **Implemented** row.
- **Unchanged:** every ADR from 0001 to 0010, the pre-implementation audit, the quality-gate verdict,
  RL-0001 … RL-0013, all V-EOM oracles and identifiers, the ADR-0010 notation, every test, and every
  assumption status. Q8 remains open.
- No production code was touched and no dependency added.

**NEXT STEP.** Await review. Begin the next scientific phase only after this documentation
reconciliation is accepted; do not start V-EOM-05 unless explicitly authorised.

---

## 2026-09-12 · RL-0015 — V-EOM-05 repaired: a verification case that could not test its own claim

**DECISION.** V-EOM-05 is reconfigured as *a torque-free rigid body whose body axes are not principal
axes*: a symmetric positive-definite inertia tensor in $B$ with all three products of inertia
non-zero, two frozen states, and an exact instantaneous $\dot{\boldsymbol\omega}$. The identifier, the
governing equation, the ADR-0010 conventions and every other anchor are unchanged. No ADR was
written: this is an anchor repair inside the existing conventions, not a new decision.

**RATIONALE.** The case as specified used principal moments on the body axes — a diagonal tensor —
while claiming to isolate products of inertia and full-tensor handling. A diagonal tensor has no
products of inertia, so the three mutations the case existed to catch (zero $J_{xy}$, zero $J_{xz}$,
zero $J_{yz}$) and the "diagonalise $\mathbf{J}$" shortcut all reproduced it exactly. A test that
cannot fail under the error it targets is not testing for it. RS-004 §4.3 had the physics right all
along — "the products of inertia are exactly what couple the axes" — so only the case needed changing.

**EVIDENCE.** `CALCULATION`, 2026-09-12, exact rational arithmetic.

- $\mathbf{J} = [[8,-1,-2],[-1,7,-3],[-2,-3,5]]$: leading minors $(8,55,163)$ give positive
  definiteness; minors $(2,5,7)$ of $(\operatorname{tr}\mathbf{J}/2)\mathbf{I}-\mathbf{J}$ give the
  strict triangle inequalities. Both are necessary: $[[10,2,1],[2,8,3],[1,3,6]]$ is positive definite
  and is **not** a physically realisable body, and it is frozen as a counter-example.
- $\boldsymbol\omega=(4,-6,7) \Rightarrow \dot{\boldsymbol\omega}=(-18,9,23)$;
  $\boldsymbol\omega=(7,-5,-8) \Rightarrow \dot{\boldsymbol\omega}=(-12,31,-38)$. Computed twice by
  independent routes — adjugate inverse, and Cramer's rule written out as scalar expressions — which
  agree exactly, and both re-executed as tests.
- Deleting the products changes $\dot{\boldsymbol\omega}$ by $139/5$ and $31$ rad·s⁻² at the two
  states, which is the discrimination the previous configuration lacked entirely.
- Mutation harness: **27 mutations, 27 detected, 0 escaped**, control clean.
- A candidate tensor with all-positive products was **rejected**: it makes "replace each product by
  its absolute value" an identity operation.

**IMPACT.** 23 tests added (94 → 117 executed, 117 passed, 0 skipped). `tests/test_eom_anchors.py`
gains a V-EOM-05 section; RS-004 §7 gains the repaired row and a note recording what was wrong;
the V&V document gains the anchor's derivation, mutation table and blind spots. V-EOM-01 … V-EOM-04
are byte-identical apart from two lines of module docstring. No production code, no dependency, no
identifier and no existing oracle changed. Q8 remains open.

**Structural blind spots recorded, not claimed away:** transposing a symmetric $\mathbf{J}$ is a
no-op; $\boldsymbol\omega\to-\boldsymbol\omega$ leaves $\dot{\boldsymbol\omega}$ unchanged because the
right-hand side is quadratic; $\mathbf{J}\to k\mathbf{J}$ leaves it unchanged because the inverse
cancels the tensor, so the case constrains the *shape* of an inertia tensor and not its scale.

**NEXT STEP.** Stop and await review before beginning production rotational dynamics.
