# ADR-0010 — Dynamics specification conventions: verification-ID ownership, symmetry axis, axisymmetric inertia notation, status vocabulary

**Date:** 2026-09-11 · **Status:** Accepted
**Amends:** RS-004 §2, §4.2, §4.3, §7 · RS-008 (V-VM-10) · `NOTATION_AND_CONVENTIONS.md` §3, §5, §8 ·
`VERIFICATION_AND_VALIDATION.md` §2, §3.1 · **Supersedes:** nothing — ADR-0003 and ADR-0009 stand ·
**Evidence:** `VERIFICATION_AND_VALIDATION.md` §2, findings recorded when V-EOM-04 was frozen

## Context

Three inconsistencies in the dynamics specification were found on 2026-09-10 while the first
rotational verification anchor, V-EOM-04, was being frozen. They were recorded as `FINDING`s rather
than fixed in place, because each needed a decision rather than an edit. All three must be settled
before any rotational-dynamics code is written, since that code, its inputs and its acceptance tests
would inherit them.

**1. One verification identifier, two claims.** RS-004 §7 (2026-09-09) listed **V-EOM-03** as
*torque-free, constant rate about a principal axis*. That case was never frozen and never tested. On
2026-09-10, V-EOM-03 was assigned to a different claim — *a constant non-zero body force at a fixed
known attitude* — frozen as an exact oracle in `tests/test_eom_anchors.py` (commit `341bb97`) and
recorded in the V&V document. The identifier then named two different things.

**2. Two incompatible symmetry axes.** `NOTATION_AND_CONVENTIONS.md` §3, RS-001 §2.2 and ADR-0003 put
$x_B$ along the vehicle's **longitudinal** axis. RS-004 §7 wrote V-EOM-04 as
$J_x = J_y = J_t \neq J_z$ with $\lambda = \frac{J_z-J_t}{J_t}\omega_z$ — symmetry about $z$ — and
RS-004 §4.2, ADR-0009, V-EOM-09 and RS-008's V-VM-10 describe a body "spinning at $\omega_z$ about its
symmetry axis". As mathematics this is valid for any rigid body. As a description of a RADIUS
vehicle it is wrong: $z_B$ is the **yaw** axis, a transverse axis. And the symbol $J_z$ reads as
$J_{zz}$, the moment about $z_B$ — which on a RADIUS vehicle is exactly a *transverse* moment. The
same letter would mean opposite things in the analytical case and on the vehicle.

**3. "Implemented" with no code behind it.** RS-004 §4.3 marked the aerodynamic moment, the
propulsive moment and the gyroscopic term **Implemented**, while RS-004's own header, the V&V
document and the repository record that no dynamics code exists. The word was being used to mean
"included in the formulation". No status vocabulary was defined anywhere.

## Decisions

### 1. Verification-identifier ownership

**Rule.** One identifier names exactly one verification claim, for the life of the project.
Identifiers are never reused. A **frozen** anchor is never renumbered. A **planned** case that must
give up its identifier takes the next unused number, and the old number is recorded against it.

| ID | Claim | Status | Why |
|---|---|---|---|
| **V-EOM-03** | Constant non-zero body force at a fixed known attitude | Verification anchor established (frozen 2026-09-10) | the only claim ever frozen under this identifier; cited by tests, the V&V record and published commit history |
| **V-EOM-10** | Torque-free, constant rate about a principal axis — *listed as V-EOM-03 in RS-004 §7 from 2026-09-09 to 2026-09-11* | Planned — never frozen, never tested | content unchanged; renamed only |

The three categories stay distinct: **completed anchors** V-EOM-01, 02, 03, 04; **planned cases**
V-EOM-05, 06, 07, 08, 09, 10; **renamed case** V-EOM-10 alone. The next new V-EOM case is V-EOM-11.

### 2. The physical symmetry axis is $x_B$

For an axisymmetric RADIUS vehicle the symmetry axis is **$x_B$**. When its principal axes coincide
with $B$:

$$\mathbf{J}^{B} = \mathrm{diag}(J_\parallel,\ J_\perp,\ J_\perp)$$

and, with $\boldsymbol\omega^{B}_{B/I} = (p,q,r)$ and moments $(L,M,N)$ (NOTATION §5–6):

$$J_\parallel\,\dot p = L,\qquad J_\perp\,\dot q + (J_\parallel - J_\perp)\,p\,r = M,\qquad J_\perp\,\dot r - (J_\parallel - J_\perp)\,p\,q = N$$

Torque-free: $p$ is constant, $\dot q = -\lambda r$, $\dot r = \lambda q$, with
$\lambda = \frac{J_\parallel - J_\perp}{J_\perp}\,p$. The transverse rate $(q, r)$ rotates relative
to the body at $\lambda$, positive right-handed about $+x_B$ (from $+y_B$ toward $+z_B$).
`CALCULATION`, 2026-09-11: confirmed in exact rational arithmetic against
$\mathbf{J}\dot{\boldsymbol\omega} + \boldsymbol\omega\times(\mathbf{J}\boldsymbol\omega) = \mathbf{M}$
over 1000 random cases, with moments.

This is **normative** for every vehicle description, mass-property input, planned verification case
and report. It does **not** introduce an axis-specific equation. The rotational equation stays
full-tensor (RS-004 §4, `A-EOM-02`), so production code is axis-agnostic by construction. The
convention governs what is fed to that code and how its output is read. An implementation that
hard-codes a symmetry axis does not conform.

### 3. Notation for axisymmetric inertia

| Symbol | Meaning | Scope |
|---|---|---|
| $J_\parallel$ | principal moment of inertia about the **symmetry axis** | axisymmetric bodies only |
| $J_\perp$ | principal moment of inertia about **any transverse axis** | axisymmetric bodies only |
| $\omega_\parallel$, $\boldsymbol\omega_\perp$ | component of $\boldsymbol\omega$ along the symmetry axis, and the transverse remainder | for a RADIUS vehicle, $\omega_\parallel = p$ and $\boldsymbol\omega_\perp = (0, q, r)$ |
| $J_{xx}, J_{yy}, J_{zz}, J_{xy}, J_{xz}, J_{yz}$ | components of the inertia tensor **resolved in $B$** | always; already used this way in RS-005 §4 ($J_{yy}$, pitch) |

For an aligned axisymmetric RADIUS vehicle, $J_{xx} = J_\parallel$ and $J_{yy} = J_{zz} = J_\perp$.
The body-frame transverse rate is written axis-independently as

$$\lambda = \frac{J_\parallel - J_\perp}{J_\perp}\,\omega_\parallel,\qquad \text{positive right-handed about the positive symmetry axis.}$$

**$J_t$ and $J_z$ are retired** for axisymmetric moments. The new symbols are not cosmetic. Without
them, "z" names the symmetry axis in the analytical case and a transverse axis on the vehicle, and
$\lambda$ cannot be written without tying it to one labelling. In code the frozen V-EOM-04 oracle
uses `J_PARALLEL` and `J_PERP`, renamed from `J_Z` and `J_T`; values unchanged.

### 4. Canonical principal frame $P$ — retained, named, analysis-only

Analytical derivations may relabel the principal axes so that the symmetry axis is the third one.
That relabelling is named the **canonical principal frame $P$**: axes $x_P, y_P, z_P$, symmetry axis
$z_P$, $\mathbf{J}^{P} = \mathrm{diag}(J_\perp, J_\perp, J_\parallel)$. In it,
$u = \omega_{x_P} + i\,\omega_{y_P}$ obeys $\dot u = i\lambda u$ with $\omega_\parallel = \omega_{z_P}$.

**Mapping to RADIUS body axes**, for a vehicle whose principal axes coincide with $B$:

$$x_P = y_B,\qquad y_P = z_B,\qquad z_P = x_B,\qquad\text{so}\qquad \boldsymbol\omega^{P} = (q,\ r,\ p)$$

This is a **cyclic** relabelling. The matrix of $P$'s axes expressed in $B$ has determinant $+1$, so
$P$ is right-handed, cross products are preserved, and torque-free solutions map to torque-free
solutions (checked exactly, 2026-09-11). **A relabelling that swaps two axes is a reflection**. It
reverses every cross product and is forbidden; V-EOM-04 contains a test showing that such a
relabelling fails the Euler equations.

Rules for $P$:

- It is **not a simulation frame.** No production module uses it, no output is expressed in it, and
  it is not one of the frames of NOTATION §3.
- Any quantity derived in $P$ is **mapped to $B$** before it is compared with RADIUS.
- A document that uses $P$ says so and cites this mapping.
- If the principal axes are **not** aligned with $B$ (non-zero products of inertia), $P$ is related to
  $B$ by the principal-axis rotation of $\mathbf{J}$, and the simple mapping above does not apply.

### 5. Implementation-status vocabulary

For any term, subsystem or verification case:

| Status | Means | Evidence required |
|---|---|---|
| **Specified** | written in `docs/research/` in symbolic form, with frames, units and assumptions | the document |
| **Analytically verified** | an independent derivation or closed-form check has been performed and recorded | a `CALCULATION` record |
| **Verification anchor established** | an exact expected result is frozen as executable tests, awaiting an implementation | named tests in `tests/` |
| **Planned** | named, with no frozen oracle and no code | an entry in a registry |
| **Partially implemented** | production code exists for part of the specified scope | the module, the part, and its tests named |
| **Implemented** | production code exists in `radius/` **and passes its named verification tests** | the module and tests named |
| **Not yet implemented** | explicit negative; may accompany any of the above | — |
| **Omitted** | deliberately excluded from the model — a modelling status, orthogonal to the rest | an assumption ID |

A statement that a term is *part of the model* is **Specified**, never **Implemented**. Production
code that exists but is unverified is "implemented, unverified" and may not be called **Implemented**
alone.

This vocabulary labels **components**. The **project** maturity label is governed by
`PUBLICATION_POLICY.md` §11 and is not changed by this ADR.

## Alternatives considered

- **Keep $z$ as the symmetry axis and document a relabelling (brief option B, as the normative
  convention).** Rejected. RADIUS already treats $x_B$ as the vehicle axis everywhere else, in
  documents that were audited independently of this question:
  - the roll/pitch/yaw rates and moment signs of NOTATION §5–6 put roll, $p$ and $L$, about $x_B$;
  - RS-007 §3 puts axial force along $-x_B$ and roll damping $C_{lp}$ about $x_B$, and gives the
    pitching and yawing moments the same linear form ($C_{mlpha}$, $C_{mq}$; $C_{neta}$, $C_{nr}$);
  - RS-004 §3.1 has the exhaust velocity pointing roughly along $-\hat{x}_B$;
  - RS-005 §4 uses $J_{yy}$ as the transverse pitch inertia.

  Making $z$ the symmetry axis for rotational dynamics alone would put two incompatible pictures of
  one vehicle into one specification. The $z$-symmetric form is retained only as the named frame $P$.
- **Use $x_B$ everywhere and delete the $z$-symmetric form (brief option A, strictly).** Rejected. The
  frozen V-EOM-04 canonical oracle is mathematically correct. Its two frozen forms are themselves a
  check: an implementation with a symmetry axis silently hard-coded fails one of them. Rewriting
  frozen values to make documentation look uniform is exactly what the verification record forbids.
- **Keep $J_t$, $J_z$ and add a mapping sentence.** Rejected: $J_z$ still reads as $J_{zz}$ at every
  point of use, and a mapping sentence is not present at every point of use.
- **Give the body-force anchor a new number instead.** Rejected: it would renumber a *frozen*
  claim, one cited by tests and published history, in order to preserve a plan that never produced a
  test.
- **Merge the principal-axis case into V-ATT-02.** Rejected in this ADR as a scope change. V-ATT-02
  prescribes $\boldsymbol\omega$ and tests kinematics. V-EOM-10 tests that the *dynamics* keep
  $\boldsymbol\omega$ constant when $\boldsymbol\omega_0$ lies along a principal axis of an
  asymmetric $\mathbf{J}$. The overlap in $q(t)$ is recorded, not resolved.
- **Replace "Implemented" with "Included".** Rejected: that is just another undefined word. A status
  must say what evidence exists.

## Consequences

What future implementation must follow:

- Axisymmetric vehicle mass properties are supplied in $B$ with $x_B$ as the symmetry axis. For an
  aligned body $J_{xx} = J_\parallel$ and $J_{yy} = J_{zz} = J_\perp$, and its spin rate is $p$.
- Rotational code takes the full tensor and **must pass both frozen forms of V-EOM-04**. The
  canonical-frame oracle is also a legitimate $B$-frame input for a body whose symmetry axis happens
  to be $z_B$, so it runs through the same code unchanged. The $x_B$ form is the RADIUS vehicle.
- New documents use $J_\parallel$, $J_\perp$, $\omega_\parallel$ and $\lambda$ as defined here, and
  $J_{xx}\ldots$ for tensor components in $B$.
- Status words follow Decision 5. Any claim of **Implemented** names the module and the tests.

Costs, stated:

- In the aligned case one number has two names ($J_{xx}$ and $J_\parallel$); the reader must know the
  mapping. NOTATION §5.1 states it once.
- Documents dated before 2026-09-11 keep the old notation. They are historical records and are not
  rewritten; they are read through the migration rules below.
- The V-EOM-04 test identifiers changed. Anything that quoted `J_Z` or `J_T` must be read with the
  mapping above.

## Affected documents

**Synchronised in this change:**

| Document | Change |
|---|---|
| `docs/research/RS-004_equations_of_motion.md` | §2 symbols; §4.2 notation note; §4.3 status column; §7 registry — status column, V-EOM-03 row, V-EOM-10, V-EOM-04 in the new notation and both forms, tensor notation in V-EOM-05, symmetry axis in V-EOM-09, identifier history |
| `docs/research/RS-008_variable_mass_abstraction.md` | V-VM-10 row: symmetry axis stated |
| `docs/methodology/NOTATION_AND_CONVENTIONS.md` | §3 pointer; new §5.1 — inertia notation, the $x_B$ convention, frame $P$ and its mapping; one §8 naming rule |
| `docs/methodology/VERIFICATION_AND_VALIDATION.md` | V-EOM-04 section in the new notation, both frozen forms, findings marked resolved; §3.1 entry |
| `docs/architecture/ARCHITECTURE.md` | §6: one sentence that read as a claim of implementation |
| `tests/test_eom_anchors.py` | V-EOM-04 identifiers and commentary only — see Verification impact |
| `docs/decisions/README.md` | index |
| `research/RESEARCH_LOG.md` | RL-0013 |

**Historical, deliberately not edited** — read with the migration rules below: ADR-0009 (ADRs are
never edited); `PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md` §5; RESEARCH_LOG RL-0012; `QUALITY_GATE.md`
§11 (whose "V-EOM-01…09" was accurate on its date); `handoffs/current_state.md` (a dated snapshot).

**Found stale, not edited — for the researcher.** Several *current* status statements
**under**-claim:

- README "Implemented: nothing — no source code exists", "Verified: nothing — none written" and
  "the project is at step 1";
- `handoffs/current_state.md` §2;
- the header of `docs/assumptions.md` ("Nothing is implemented");
- `docs/research/README.md`'s opening;
- the headers of NOTATION, RS-001 and RS-002.

In fact `radius/frames.py` and `radius/math/quaternion.py` exist and are verified by V-FRM-05, 08,
09, 10 and V-ATT-01. Correcting these statements implies revisiting the project maturity label,
which `PUBLICATION_POLICY.md` §11 makes a governance decision, so they are flagged rather than
edited. **No statement anywhere claims that production dynamics exist.**

## Verification impact

- **NOTATION §9 change control.** This ADR **adds** NOTATION §5.1 and one naming rule to §8; it
  changes **no** existing convention of §1–8 — frames, units, transformation direction, Euler
  sequence, quaternion convention and moment signs all stand. It therefore invalidates **no**
  reference data: no stored reference trajectory exists, and no frozen expected value changes.
- **No numerical or analytical oracle in V-EOM-01, 02, 03 or 04 changes.** Every frozen literal is
  identical. No test is added, removed or weakened.
- **V-EOM-04 test file.** Identifiers are renamed: `J_Z`→`J_PARALLEL`, `J_T`→`J_PERP`, with the
  matching local names. Commentary now states frame $P$ and this ADR. Checked by comparing the syntax
  tree before and after, with renames reversed and string literals blanked; by the full suite; and
  by re-running the V-EOM-04 mutation harness.
- **Interpretation of V-EOM-04**, now explicit. Its canonical form is a mathematically correct
  benchmark in frame $P$. Its frozen $x_B$ form — the cyclic image of the canonical form —
  represents the RADIUS vehicle's axis convention. It is therefore **both**, through its two forms.
  Neither is a representative vehicle state: the nutation is deliberately large.
- **V-EOM-03** is unchanged. **V-EOM-10** is planned; no test exists or is added.

## Migration and historical record

- "**V-EOM-03**" in any document or record dated **2026-09-09** refers to the principal-axis case
  now numbered **V-EOM-10**. From **2026-09-10** it refers to the body-force anchor. RS-004 §7 carries
  a note; git history retains the earlier table.
- "**$J_t$, $J_z$, $\omega_z$**" in a document dated before 2026-09-11, when describing an
  axisymmetric body, mean $J_\perp$, $J_\parallel$, $\omega_\parallel$ in a $z$-symmetric labelling,
  i.e. frame $P$. For a RADIUS vehicle, $\omega_z$ there is the roll rate $p$. No number in those
  documents changes.
- The three findings in `VERIFICATION_AND_VALIDATION.md` §2 stay where they were recorded, marked
  **resolved by ADR-0010**, so the record shows both the defect and its resolution.

## Revisit if

A vehicle configuration needs a symmetry axis other than $x_B$, or principal axes not aligned with
$B$. A non-axisymmetric analytical case needs its own canonical frame. The project maturity label
changes. Or an implementation shows that the full-tensor rotational code needs axis-specific handling.
