# RS-001 — Reference Frames

**Status:** Specification. Not implemented, not verified.
**Depends on:** `docs/methodology/NOTATION_AND_CONVENTIONS.md`
**Decides:** ADR-0003

---

## 1. Why this comes first

No equation in RADIUS can be written down before the frames are fixed, because every term in the
equations of motion is either a quantity resolved in a frame or a term that exists *only because* a
frame rotates. A specification that names frames loosely produces code in which a missing transport
term is indistinguishable from a modelling choice.

Four things must be stated for each frame: **origin**, **axis directions**, **handedness**, and
**what it is assumed to be inertial with respect to**. The last is the one usually left out, and it
is the one that determines whether the equations are correct.

---

## 2. Frame set

### 2.1 $I$ — the computational inertial frame

**Phase 1–10 definition.** A frame whose origin is a fixed reference point on the Earth's surface
(the "launch point"), with axes

- $x_I$ — local North
- $y_I$ — local East
- $z_I$ — local Down (toward the Earth's centre at the origin)

right-handed, and **assumed non-rotating and non-accelerating**.

This is a *flat, non-rotating Earth* model. It is the North-East-Down (NED) frame, promoted to serve
as the inertial reference.

**This is an approximation, and it is the most consequential assumption in RADIUS.** It is
registered as `A-FRM-01`. Its consequences are quantified in §3 rather than waved at.

**Why start here.** The whole verification programme (RS-005, `docs/methodology/VERIFICATION_AND_VALIDATION.md`)
rests on comparing computed trajectories against closed-form analytical solutions. Closed-form
solutions exist for constant gravity in a non-rotating frame; they do not exist once the frame
rotates and gravity varies. Starting flat lets RADIUS establish that the integrator and the rigid-body
equations are correct *before* introducing effects that make correctness unfalsifiable by hand. The
sophistication is added afterwards, against a base that is known to work.

### 2.2 $B$ — body frame

- **Origin:** the vehicle's **instantaneous** centre of mass. Because mass depletes, this origin
  moves relative to the vehicle's geometry. The consequences are handled in RS-008 §5 and RS-007 §4.
- $x_B$ — forward, along the vehicle's longitudinal (reference) axis
- $y_B$ — out the right-hand side
- $z_B$ — down, completing the right-handed set

The body frame is rigidly attached to the vehicle structure in *orientation*; its *origin* tracks
the centre of mass. Distinguishing these is necessary: the rotational equations are written about the
centre of mass, but the geometry that generates aerodynamic forces is fixed to the structure.

### 2.3 $W$ — wind (air-relative) frame

- **Origin:** vehicle centre of mass
- $x_W$ — along the air-relative velocity vector $\mathbf{v}_{\text{rel}}$
- $z_W$ — in the vehicle plane of symmetry, perpendicular to $x_W$, positive "down"
- $y_W$ — completing the right-handed set

Related to $B$ through angle of attack $\alpha$ and sideslip $\beta$:

$$\mathbf{T}_{BW} = \mathbf{R}_y(\alpha)\,\mathbf{R}_z(-\beta)\qquad\text{(sign convention fixed in RS-007 §2 and tested by V-FRM-05)}$$

with, from $\mathbf{v}^{B}_{\text{rel}} = (u, v, w)$:

$$\alpha = \arctan2(w,\,u), \qquad \beta = \arcsin\!\left(\frac{v}{V}\right), \qquad V = \lVert\mathbf{v}_{\text{rel}}\rVert$$

equivalently $\mathbf{v}^{B}_{\text{rel}} = V\big(\cos\alpha\cos\beta,\;\sin\beta,\;\sin\alpha\cos\beta\big)$,
which is what fixes the composition above.

> **Corrected 2026-09-09 (audit finding F-2).** This document previously stated
> $\mathbf{T}_{BW} = \mathbf{R}_y(-\alpha)\mathbf{R}_z(\beta)$, which is sign-inconsistent with the
> definitions of $\alpha$ and $\beta$ immediately above: for $\alpha=0,\ \beta=+30°,\ V=100$ it
> returns $\mathbf{v}^{B} = (86.603,\,-50,\,0)$, i.e. $\beta=-30°$. Both the sideslip and
> angle-of-attack senses were inverted, which would have reversed every side force and yawing moment.
> `arctan` was also corrected to `arctan2` for consistency with RS-007 §2 (finding F-5). See
> `PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md` §9.1.

**Degenerate at $V = 0$**, and ill-conditioned for small $V$. Handling is specified in RS-007 §5;
it is not left to the implementer.

The wind frame is a *derived* frame. It is never integrated and never stored as state.

### 2.4 $E$ — Earth-centred Earth-fixed (deferred)

Not defined in detail here, because defining it now would be speculation about a design that has not
been done. What *is* fixed now is that the inertial frame is accessed through an interface (see
`docs/architecture/ARCHITECTURE.md` §4), so that replacing the flat-Earth $I$ with an ECI/ECEF pair
is a substitution rather than a rewrite.

Deferring the definition is a decision, recorded in ADR-0003. Pretending to define it now would be
worse than admitting it is deferred.

---

## 3. The flat non-rotating Earth assumption, quantified

`A-FRM-01` states that $I$ may be treated as inertial. Four distinct errors follow. Each is
quantified so the validity domain is a number, not an adjective.

`CALCULATION` — all figures below are order-of-magnitude estimates computed from the stated formulas
during specification (2026-09-09), using $\Omega_E = 7.292115\times10^{-5}$ rad·s⁻¹ and
$R_E \approx 6.371\times10^{6}$ m. They have not been checked against a rotating-Earth simulation,
because none exists. They are *estimates of neglected terms*, not measured errors.

### 3.1 Coriolis acceleration

$$\mathbf{a}_{\text{Cor}} = -2\,\boldsymbol{\Omega}_E \times \mathbf{v}$$

Magnitude bound $\lVert\mathbf{a}_{\text{Cor}}\rVert \le 2\Omega_E V$:

| $V$ (m·s⁻¹) | $\lVert a_{\text{Cor}}\rVert$ (m·s⁻²) | Position error over $t$, $\approx\frac{1}{2}at^2$ |
|---|---|---|
| 100 | 0.0146 | 7.3 m at $t=$ 30 s |
| 300 | 0.0437 | 79 m at $t=$ 60 s |
| 1000 | 0.146 | 729 m at $t=$ 100 s |

**Interpretation** (`INTERPRETATION`): the neglected Coriolis term is irrelevant for short, slow test
cases used to verify the integrator, and is *not* negligible for any trajectory with a range of tens
of kilometres. RADIUS must not be used for the latter class of problem while `A-FRM-01` stands.

### 3.2 Centrifugal acceleration

$\Omega_E^2 R_E \approx 3.4\times10^{-2}$ m·s⁻². This term is conventionally absorbed into *measured*
gravity: if $g$ is taken as the locally measured value rather than a Newtonian point-mass value, the
centrifugal term is already in it. RADIUS does this, and records it as `A-FRM-02` so that anyone
later adding an explicit centrifugal term knows not to double-count it.

`LIMITATION` (audit finding F-7, 2026-09-09). This interacts with §3.4: the centrifugal contribution
buried inside measured $g$ scales as $(R_E+h)$ — it *increases* with altitude — whereas §3.4 scales
the whole of $g$ as inverse-square. `CALCULATION`: the mis-scaling is $\approx5\times10^{-4}$ m·s⁻²
at 30 km ($5\times10^{-5}$ of $g$), about 0.9 m over 60 s of free fall — three orders of magnitude
below the accepted Coriolis error of §3.1. **Recorded, not corrected.** Separating $g$ into
gravitational and centrifugal parts is work that belongs with the ECEF extension.

### 3.3 Earth curvature

Treating the surface as a plane introduces a vertical geometry error over a horizontal range $d$ of
approximately $d^2/(2R_E)$:

| Range $d$ | Curvature drop |
|---|---|
| 1 km | 0.08 m |
| 10 km | 7.8 m |
| 50 km | 196 m |
| 100 km | 785 m |

Additionally, the direction of "down" is treated as fixed, whereas it rotates by $d/R_E$ over the
range — 0.45° at 50 km.

### 3.4 Gravity variation with altitude

Constant $g$ is assumed (`A-FRM-03`). The inverse-square variation gives
$g(h) = g_0\,\big(R_E/(R_E+h)\big)^2$:

| Altitude | $g(h)/g_0$ | Error if constant $g$ assumed |
|---|---|---|
| 1 km | 0.99969 | 0.03 % |
| 10 km | 0.99687 | 0.31 % |
| 30 km | 0.99065 | 0.94 % |

**Decision.** Because the altitude-dependent correction is *cheap, exact and analytically
differentiable*, RADIUS implements $g(h)$ inverse-square from the start, rather than constant $g$.
Constant $g$ is retained only as a selectable option, because several analytical verification cases
(RS-004 §7) have closed-form solutions *only* under constant $g$. So `A-FRM-03` is not an assumption
about physics; it is a switch used deliberately to make verification possible.

---

## 4. Validity domain

Summarising §3 into the statement that must accompany any RADIUS result while `A-FRM-01` stands:

> Trajectories with horizontal range below roughly 10 km and duration below roughly 60 s incur
> neglected-term errors at or below the ~10 m level. Beyond that, the flat non-rotating Earth
> assumption dominates the error budget and no accuracy claim is supportable.

`LIMITATION`. This bound is derived from the neglected-term estimates in §3, not measured. Measuring
it requires a rotating-Earth implementation to compare against, which does not exist. Until then the
bound is provisional and must be quoted as such.

---

## 5. Transformation chain

$$I \;\xrightarrow{\;\mathbf{T}_{BI}(q)\;}\; B \;\xrightarrow{\;\mathbf{T}_{WB}=\mathbf{T}_{BW}^{\mathsf{T}}\;}\; W$$

Only $\mathbf{T}_{BI}$ is derived from integrated state (the quaternion). $\mathbf{T}_{BW}$ is
derived algebraically from the state at each evaluation. There is exactly **one** function that
produces $\mathbf{T}_{BI}$, and it takes the quaternion; no other route to it exists in the codebase.

---

## 6. Verification tests this specification requires

| ID | Test | Passes if |
|---|---|---|
| V-FRM-01 | $\mathbf{T}_{BI}$ is orthonormal for random unit quaternions | $\lVert\mathbf{T}^{\mathsf{T}}\mathbf{T}-\mathbf{I}\rVert_\infty < 10^{-12}$ |
| V-FRM-02 | $\det \mathbf{T}_{BI} = +1$ (proper rotation, not a reflection) | $\lvert\det - 1\rvert < 10^{-12}$ |
| V-FRM-03 | Sign of "down": with zero attitude, gravity resolves to $(0,0,+g)$ in $B$ | exact |
| V-FRM-04 | Pure yaw quaternion reproduces $\mathbf{R}_z(\psi)$; likewise pitch and roll | $< 10^{-12}$ |
| V-FRM-05 | $\mathbf{T}_{BW}$ round trip: build $\mathbf{v}^B$ from $(V,\alpha,\beta)$, recover $(V,\alpha,\beta)$ | $< 10^{-12}$ relative |
| V-FRM-06 | Composition: $\mathbf{T}_{WI} = \mathbf{T}_{WB}\mathbf{T}_{BI}$ agrees with direct construction | $< 10^{-12}$ |
| V-FRM-07 | Euler → quaternion → DCM → Euler round trip over a grid avoiding $\lvert\theta\rvert>89°$ | angle error $< 10^{-10}$ rad |
| V-FRM-08 | Known-value spot checks: 90° yaw maps $\hat{x}_I \to -\hat{y}_B$ (hand-computed, hard-coded) | exact to $10^{-15}$ |
| **V-FRM-09** | $\mathbf{T}_{BI}(kq)$ for $k \neq 1$ is orthonormal and equals $\mathbf{T}_{BI}(q)$ — the non-unit quaternions that necessarily arise inside RK stages | $<10^{-12}$ |
| **V-FRM-10** | Composition order: $\mathbf{T}(q_a\otimes q_b) = \mathbf{T}(q_b)\mathbf{T}(q_a)$, **and** the reversed order demonstrably fails | equality $<10^{-12}$; reversed differs by $>10^{-3}$ |

V-FRM-08 is the important one. The others check internal consistency, and a codebase can be
self-consistently wrong. Only a hand-computed expected value catches a convention error that has been
applied uniformly.

That is not hypothetical. The wind-frame sign error corrected in §2.3 (audit finding F-2) would have
round-tripped perfectly through V-FRM-05 had the builder and the extractor been written to agree with
each other. V-FRM-09 and V-FRM-10 were added by the audit; both catch defects the original suite
could not.

---

## 7. Assumptions registered

`A-FRM-01`, `A-FRM-02`, `A-FRM-03`, `A-FRM-04` — see `docs/assumptions.md`.

---

## 8. Open questions

1. When the ECEF/ECI extension is designed, does the inertial-frame interface as sketched in
   ARCHITECTURE §4 actually suffice, or does gravity's dependence on position force a wider
   interface? Unresolved; will only be answerable when the extension is attempted.
2. Is the ~10 km / ~60 s validity bound in §4 realistic? It is an estimate of neglected terms, not a
   measurement, and it may be optimistic where errors accumulate through the aerodynamics rather than
   adding linearly.
