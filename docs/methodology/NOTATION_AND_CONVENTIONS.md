# RADIUS — Notation, Units and Sign Conventions

**Status:** Specification. Nothing here is implemented.
**Authority:** This document is the single place where these conventions are fixed. Every other
document and every module defers to it. If code and this document disagree, the code is wrong.

Most 6-DOF bugs are not errors of physics. They are two modules disagreeing about what a symbol
means — a transformation applied in the wrong direction, a quaternion in the other community's
convention, a moment taken about the wrong point. The purpose of this document is to make those
disagreements impossible to have silently.

---

## 1. Units

**SI throughout, without exception, everywhere inside the simulation.**

| Quantity | Unit | Symbol |
|---|---|---|
| Length, position | metre | m |
| Time | second | s |
| Mass | kilogram | kg |
| Velocity | metre per second | m·s⁻¹ |
| Acceleration | metre per second squared | m·s⁻² |
| Angle | **radian** | rad |
| Angular velocity | radian per second | rad·s⁻¹ |
| Force | newton | N |
| Moment | newton-metre | N·m |
| Moment of inertia | kilogram metre squared | kg·m² |
| Pressure | pascal | Pa |
| Density | kilogram per cubic metre | kg·m⁻³ |
| Temperature | kelvin | K |

**Degrees are not used internally.** They may appear in a configuration file or a plot axis. A
configuration value in degrees carries an explicit `_deg` suffix in its key name, and is converted
at the configuration boundary — once, visibly, in a named function. A quantity named without a unit
suffix is in SI.

Rationale: mixed-unit codebases fail at the seam, and the seam is invisible. Putting the unit in the
name of every non-SI value makes the seam a lexical property that a reader and a linter can both
see.

---

## 2. Vectors, frames, and the resolution/differentiation distinction

A vector is a physical object; its *components* exist only relative to a frame. Two separate facts
must be stated for every vector-valued quantity:

1. **Which frame its components are resolved in.**
2. **With respect to which frame it is differentiated** (for derivatives).

Conflating these is the standard source of missing Coriolis and transport terms.

### Notation

$$\mathbf{x}^{F}_{A/B}$$

- superscript $F$ — the frame the components are **resolved in**
- subscript $A/B$ — the quantity is *of* $A$ **relative to** $B$

Examples:

| Symbol | Meaning |
|---|---|
| $\mathbf{p}^{I}_{c/O}$ | position of the vehicle centre of mass $c$ relative to origin $O$, resolved in the inertial frame |
| $\mathbf{v}^{B}_{c/I}$ | velocity of the centre of mass relative to the inertial frame, resolved in **body** axes |
| $\boldsymbol{\omega}^{B}_{B/I}$ | angular velocity of the body frame relative to the inertial frame, resolved in body axes |

In code, this becomes an explicit name: `v_cm_wrt_i_in_b`, not `v`. Verbose names are the price of
not having a type system that tracks frames; the price is worth paying.

### Transport theorem

For any vector $\mathbf{a}$ and frames $I$, $B$ with relative angular velocity
$\boldsymbol{\omega}_{B/I}$:

$$\left.\frac{d\mathbf{a}}{dt}\right|_{I} = \left.\frac{d\mathbf{a}}{dt}\right|_{B} + \boldsymbol{\omega}_{B/I} \times \mathbf{a}$$

Every appearance of a cross-product term in the equations of motion traces to this identity. Where
one appears in RADIUS code, the comment cites this section.

---

## 3. Frames

All frames are **right-handed** and **orthonormal**. Detailed definitions, origins and validity
limits are in `docs/research/RS-001_reference_frames.md`. Summary:

| Tag | Name | Origin | Axes |
|---|---|---|---|
| $I$ | Inertial (initially: flat-Earth, non-rotating) | fixed reference point on the surface | $x$ North, $y$ East, $z$ **Down** |
| $B$ | Body | vehicle instantaneous centre of mass | $x$ forward along the vehicle longitudinal axis, $y$ out the right side, $z$ down (completing right-handed) |
| $W$ | Wind | vehicle centre of mass | $x$ along the air-relative velocity vector |
| $E$ | ECEF (deferred) | Earth centre | rotates with the Earth |

**$z$ is down.** This is the aerospace NED convention. It means positive altitude is *negative* $z$,
and gravity is $+z$. This is a frequent source of sign errors and is therefore stated here, tested by
V-FRM-03, and never re-litigated per module.

**Altitude** $h$ is a separate, explicitly named scalar, $h = -p^{I}_{z}$ under the flat-Earth
assumption. Code never uses a raw $z$ component where altitude is meant.

---

## 4. Rotations and transformation direction

### Direction convention: subscripts read "to ← from"

$$\mathbf{v}^{B} = \mathbf{T}_{BI}\,\mathbf{v}^{I}$$

$\mathbf{T}_{BI}$ transforms **from** $I$ **to** $B$. Consequently
$\mathbf{T}_{IB} = \mathbf{T}_{BI}^{\mathsf{T}} = \mathbf{T}_{BI}^{-1}$, and the chain rule composes
by adjacency: $\mathbf{T}_{CA} = \mathbf{T}_{CB}\mathbf{T}_{BA}$.

In code the name is `T_b_from_i`, never `T_bi`, because the underscore-form cannot be misread.

### Passive, not active

$\mathbf{T}_{BI}$ re-expresses the *same* physical vector in different axes. It does **not** rotate a
vector within a fixed frame. Every rotation object in RADIUS is passive. If an active rotation is
ever needed, it is constructed explicitly as the transpose at the point of use, with a comment.

### Euler angles: 3-2-1 sequence

Attitude of $B$ relative to $I$ is described by yaw $\psi$, pitch $\theta$, roll $\phi$, applied in
the order **yaw about $z$, then pitch about the new $y$, then roll about the new $x$**:

$$\mathbf{T}_{BI}(\phi,\theta,\psi) = \mathbf{R}_{x}(\phi)\,\mathbf{R}_{y}(\theta)\,\mathbf{R}_{z}(\psi)$$

with the elementary passive rotations

$$\mathbf{R}_{x}(\phi)=\begin{bmatrix}1&0&0\\0&\cos\phi&\sin\phi\\0&-\sin\phi&\cos\phi\end{bmatrix},\quad
\mathbf{R}_{y}(\theta)=\begin{bmatrix}\cos\theta&0&-\sin\theta\\0&1&0\\\sin\theta&0&\cos\theta\end{bmatrix},\quad
\mathbf{R}_{z}(\psi)=\begin{bmatrix}\cos\psi&\sin\psi&0\\-\sin\psi&\cos\psi&0\\0&0&1\end{bmatrix}$$

Ranges: $\phi \in (-\pi,\pi]$, $\theta \in [-\pi/2, \pi/2]$, $\psi \in (-\pi,\pi]$.

Euler angles are an **output and configuration-input representation only**. They are never the
integrated state. See RS-002.

### Quaternions: Hamilton convention, scalar-first

This is the convention that most often differs between communities (SRC-005). RADIUS fixes it here.

- **Ordering:** scalar first. $q = (q_0,\; \mathbf{q}_v) = (q_0, q_1, q_2, q_3)$.
- **Product:** Hamilton, i.e. $ij = k$, $jk = i$, $ki = j$. **Not** the JPL/Shuster convention, in
  which the product order is reversed.

$$(a_0,\mathbf{a}_v)\otimes(b_0,\mathbf{b}_v) = \big(a_0 b_0 - \mathbf{a}_v\!\cdot\!\mathbf{b}_v,\;\; a_0\mathbf{b}_v + b_0\mathbf{a}_v + \mathbf{a}_v\times\mathbf{b}_v\big)$$

- **Meaning:** $q \equiv q_{BI}$ encodes the same transformation as $\mathbf{T}_{BI}$, via

$$\mathbf{T}_{BI}(q) = (q_0^2 - \mathbf{q}_v\!\cdot\!\mathbf{q}_v)\,\mathbf{I}_3 + 2\,\mathbf{q}_v\mathbf{q}_v^{\mathsf{T}} - 2q_0\,[\mathbf{q}_v\times]$$

  where $[\mathbf{a}\times]$ is the skew-symmetric matrix with $[\mathbf{a}\times]\mathbf{b} = \mathbf{a}\times\mathbf{b}$.

- **Rotation operator.** RADIUS's $\mathbf{T}_{BI}(q)$ is the **transpose** of the conventional
  Hamilton *active* rotation matrix (note the sign of the $-2q_0[\mathbf{q}_v\times]$ term above). It
  therefore corresponds to

  $$\tilde{\mathbf{v}}^{B} = q^{*} \otimes \tilde{\mathbf{v}}^{I} \otimes q$$

  and **not** to $q\otimes\tilde{\mathbf{v}}\otimes q^{*}$. Both appear in the literature under the
  name "Hamilton convention", so the operator is stated rather than left to be inferred.

- **Composition order is REVERSED relative to matrices.** Matrices compose by adjacency
  ($\mathbf{T}_{CA}=\mathbf{T}_{CB}\mathbf{T}_{BA}$); quaternions in this convention do not:

  $$\mathbf{T}(q_a \otimes q_b) = \mathbf{T}(q_b)\,\mathbf{T}(q_a)$$

  An implementer would reasonably assume the two orders match. They do not. Confirmed numerically in
  the pre-implementation audit and pinned by test V-FRM-10.

- **Evaluation at non-unit $q$.** Inside an RK stage the quaternion block is **necessarily** not of
  unit norm. Since $\mathbf{T}_{BI}(kq) = k^{2}\,\mathbf{T}_{BI}(q)$, the raw formula is not a rotation
  there — at $k=1.037$ it is off orthonormality by 0.16. RADIUS therefore defines, for all $q\neq0$:

  $$\mathbf{T}_{BI}(q) = \frac{(q_0^2-\mathbf{q}_v\!\cdot\!\mathbf{q}_v)\,\mathbf{I}_3 + 2\,\mathbf{q}_v\mathbf{q}_v^{\mathsf{T}} - 2q_0\,[\mathbf{q}_v\times]}{q\cdot q}$$

  This is a division, not a normalisation: it evaluates the same smooth $f$ the integrator's order
  conditions assume, and introduces no branch — an in-stage `if norm != 1: normalise` would break
  both properties. Registered as `A-NUM-05`, pinned by V-FRM-09.

- **Sign ambiguity:** $q$ and $-q$ represent the same attitude. RADIUS canonicalises to $q_0 \ge 0$
  **at output and comparison boundaries only** — never during integration, where forcing the sign
  would introduce a discontinuity in a continuous state.

- **Norm:** $\lVert q \rVert = 1$ is a constraint, not an output. Its numerical maintenance is
  specified in RS-005.

**Independently audited 2026-09-09.** $\mathbf{T}_{BI}(q)$ was compared against
$\mathbf{T}_{BI}(\phi,\theta,\psi)$ built from the elementary matrices, over 2000 random attitudes:
maximum element error $5.6\times10^{-16}$. See
`docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md` §2.

**Consistency check performed.** Substituting a pure yaw quaternion
$q = (\cos\frac{\psi}{2},0,0,\sin\frac{\psi}{2})$ into $\mathbf{T}_{BI}(q)$ above yields exactly
$\mathbf{R}_z(\psi)$ as defined in §4. `CALCULATION` — performed symbolically during specification,
2026-09-09. It is re-established as an executable test (V-FRM-04) rather than relied on as a
document assertion.

---

## 5. Angular velocity and its skew form

$$\boldsymbol{\omega}^{B}_{B/I} = (p,\; q,\; r)^{\mathsf{T}}$$

- $p$ — roll rate, about $x_B$, positive right-wing-down
- $q$ — pitch rate, about $y_B$, positive nose-up
- $r$ — yaw rate, about $z_B$, positive nose-right

$$[\boldsymbol{\omega}\times] = \begin{bmatrix}0&-r&q\\ r&0&-p\\ -q&p&0\end{bmatrix}$$

**Symbol collision warning.** $q$ is used both for pitch rate and, conventionally, for dynamic
pressure. RADIUS writes dynamic pressure as $\bar{q}$ in documents and `q_bar` in code, and pitch
rate as `q_body`. Neither is ever written bare as `q`. The quaternion is `quat`, never `q`.

---

## 6. Forces, moments and the moment reference point

- Forces are resolved in $B$ unless stated: $\mathbf{F}^{B}$.
- Moments are resolved in $B$ and are taken **about the instantaneous centre of mass**, unless a
  different point is named explicitly.

This matters more for RADIUS than for a constant-mass simulator: as propellant depletes, the centre
of mass moves, while aerodynamic coefficients are conventionally referenced to a *fixed* geometric
point. Any moment supplied about a reference point $r$ must be transferred:

$$\mathbf{M}^{B}_{\text{cm}} = \mathbf{M}^{B}_{r} + \big(\mathbf{r}^{B}_{r/\text{cm}}\big) \times \mathbf{F}^{B}$$

Any module returning a moment states its reference point in its signature and docstring. A moment
without a stated reference point is an error. See RS-007 §4 and assumption `A-AER-04`.

### Sign conventions

- Positive $L$, $M$, $N$ (roll, pitch, yaw moments) act about $+x_B$, $+y_B$, $+z_B$ respectively,
  by the right-hand rule.
- Aerodynamic **drag** is defined positive opposing the air-relative velocity, i.e. it contributes
  $-D\,\hat{x}_W$.
- Aerodynamic **lift** is positive upward in the wind frame, contributing $-L\,\hat{z}_W$
  (since $z_W$ is down).
- **Control-surface deflection** sign convention is deferred to the phase that introduces actuators,
  and must be fixed by an ADR before any control code is written. It is *not* assumed here.

---

## 7. Constants

Constants are defined once, in configuration, never duplicated in a module.

| Symbol | Value | Unit | Note |
|---|---|---|---|
| $g_0$ | 9.806 65 | m·s⁻² | standard gravity; the *defined* constant used by the standard atmosphere |
| $R^{*}$ | 8 314.32 | J·(kmol·K)⁻¹ | universal gas constant **as specified in the U.S. Standard Atmosphere 1976** (SRC-008) |
| $M_0$ | 28.9644 | kg·kmol⁻¹ | sea-level mean molecular weight of air, 1976 standard |
| $\gamma$ | 1.40 | — | ratio of specific heats, 1976 standard |
| $r_0$ | 6 356 766 | m | effective Earth radius for geopotential altitude, 1976 standard |
| $\Omega_E$ | 7.292 115 × 10⁻⁵ | rad·s⁻¹ | Earth rotation rate — used only to *quantify the error* of the non-rotating assumption |

**Deliberate inconsistency, recorded.** $R^{*} = 8314.32$ differs from the current CODATA value
(≈ 8314.462 J·kmol⁻¹K⁻¹). RADIUS uses the 1976 value **inside the atmosphere model only**, because
the goal there is to reproduce that standard's published tables exactly; using a "better" constant
would make the verification test fail for the right reason and the wrong purpose. This is registered
as assumption `A-ATM-02`, and the atmosphere module cites it.

---

## 8. Naming rules for code

Not yet binding — no code exists — but fixed now so the first module obeys them.

| Rule | Example |
|---|---|
| Vectors carry frame and relationship | `v_cm_wrt_i_in_b` |
| Transformations read "to ← from" | `T_b_from_i` |
| Non-SI configuration keys carry the unit | `initial_pitch_deg` |
| Dynamic pressure is never `q` | `q_bar` |
| Quaternion is never `q` | `quat_b_from_i` |
| Rates carry the axis meaning | `p_body`, `q_body`, `r_body` |
| A moment names its reference point | `moment_about_cm_in_b` |

---

## 9. Change control

Changing any convention in this document invalidates every verification test and every stored
reference trajectory. Such a change requires an ADR, and the ADR must state which reference data is
being invalidated. Conventions are cheap to choose once and expensive to change; that asymmetry is
the reason this document exists.
