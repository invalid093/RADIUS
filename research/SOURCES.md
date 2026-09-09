# RADIUS — Source Record

Every source RADIUS relies on, what it is used for, and what kind of claim it supports.

**Verification status.** Bibliographic details marked ✅ were checked against the publisher, the
issuing body, or NTRS on 2026-09-09. Anything unchecked is marked `(not verified)` and must not be
cited as if it were. No source is listed here that has not been located.

**Copyright.** This file records citation metadata and links only. No source text is reproduced in
this repository. Summaries in the specification documents are original.

**Support class** — what the source is being used to support:
`EQ` equations · `ARCH` architecture · `NUM` numerical methods · `V&V` verification/validation
methodology · `DATA` reference data.

---

## Flight dynamics and equations of motion

### SRC-001 — Stevens, Lewis & Johnson, *Aircraft Control and Simulation* (3rd ed.) ✅

| | |
|---|---|
| Authors | Brian L. Stevens, Frank L. Lewis, Eric N. Johnson |
| Publisher | Wiley, 3rd edition, 2015 |
| ISBN | 978-1-118-87098-3 |
| Class | `EQ`, `ARCH` |

**Used for.** The general nonlinear 6-DOF rigid-body equations of motion in body axes; the
relationship between body-axis velocity, Euler angles and quaternion kinematics; the structure of a
flight simulation (state derivative function, force/moment build-up, integrator) that RADIUS's
architecture follows.

**Relevant sections.** Ch. 1 (kinematics, frames, attitude) and Ch. 2 (rigid-body EOM, aerodynamic
force and moment build-up). *Page-level references not yet verified against a copy — recorded as
chapter-level only.*

---

### SRC-002 — Zipfel, *Modeling and Simulation of Aerospace Vehicle Dynamics* (3rd ed.) ✅

| | |
|---|---|
| Author | Peter H. Zipfel |
| Publisher | AIAA Education Series, 3rd edition, 2014, 661 pp. |
| ISBN | 978-1-62410-250-9 · DOI 10.2514/4.102509 |
| Class | `EQ`, `ARCH` |

**Used for.** Tensor/matrix notation discipline for frames — the practice of stating, for every
vector, both the frame it is *resolved in* and the frame it is *differentiated with respect to*.
RADIUS's notation convention (`docs/methodology/NOTATION_AND_CONVENTIONS.md`) is modelled on this
discipline. Also used for the treatment of rotating-Earth frames when RADIUS extends beyond the
flat-Earth assumption.

**Note.** A 4th edition exists (DOI 10.2514/4.107535). RADIUS cites the 3rd; if a claim depends on
edition-specific content, that is to be stated.

---

### SRC-003 — Duke, Antoniewicz & Krambeer, *Derivation and Definition of a Linear Aircraft Model* ✅

| | |
|---|---|
| Authors | Eugene L. Duke, Robert F. Antoniewicz, Keith D. Krambeer |
| Publication | NASA Reference Publication 1207, August 1988, 101 pp. |
| Organisation | NASA Ames Research Center, Dryden Flight Research Facility |
| Identifier | NTRS 19890005752 · <https://ntrs.nasa.gov/citations/19890005752> |
| Class | `EQ` |

**Used for.** An openly available, fully written-out derivation of the nonlinear rigid-body equations
and their observation variables, used as an **independent cross-check** on the equations RADIUS
writes down. Its scope — rigid aircraft, *constant mass*, flat non-rotating Earth, no assumption of
vehicle symmetry — matches RADIUS's Phase 4 baseline before the variable-mass extension, which makes
it a good audit reference for exactly the part RADIUS implements first.

**Why it matters that it is open.** A reader auditing RADIUS can obtain this document for free and
check the equations term by term. A textbook citation does not offer that.

---

### SRC-004 — Beard & McLain, *Small Unmanned Aircraft: Theory and Practice* ✅

| | |
|---|---|
| Authors | Randal W. Beard, Timothy W. McLain |
| Publisher | Princeton University Press, 2012 |
| ISBN | 978-0-691-14921-9 |
| Class | `EQ`, `ARCH` |

**Used for.** A compact, explicitly stated frame set (inertial / vehicle / vehicle-1 / vehicle-2 /
body / stability / wind) and the transformation chain between them, used as a cross-check that
RADIUS's frame definitions are complete and that no transformation is left implicit. Also a
reference for the separation of navigation, guidance and control concerns in later phases.

---

## Attitude representation

### SRC-005 — Shuster, *A Survey of Attitude Representations* ✅

| | |
|---|---|
| Author | Malcolm D. Shuster |
| Publication | *The Journal of the Astronautical Sciences*, Vol. 41, No. 4, Oct–Dec 1993, pp. 439–517 |
| Class | `EQ` |

**Used for.** The authoritative catalogue of attitude parameterisations and, critically, of the
**conventions that differ between communities** — Hamilton vs JPL quaternion products, scalar-first
vs scalar-last ordering, active vs passive rotation. RADIUS cites this as the reason its quaternion
convention is stated explicitly and pinned by a test rather than assumed. This is the single most
common source of silent sign errors in 6-DOF code.

---

### SRC-006 — Markley & Crassidis, *Fundamentals of Spacecraft Attitude Determination and Control* ✅

| | |
|---|---|
| Authors | F. Landis Markley, John L. Crassidis |
| Publisher | Springer, Space Technology Library Vol. 33, 2014 |
| ISBN | 978-1-4939-0801-1 · DOI 10.1007/978-1-4939-0802-8 |
| Class | `EQ`, `NUM` |

**Used for.** Quaternion kinematics, the numerical behaviour of quaternion propagation, norm drift
and renormalisation strategies, and the singularity structure of Euler-angle representations.

---

## Variable-mass dynamics

### SRC-007 — Eke, *Dynamics of Variable Mass Systems* ✅

| | |
|---|---|
| Author | Fidelis O. Eke |
| Publication | NASA technical report, NTRS accession 19980210404 |
| Identifier | <https://ntrs.nasa.gov/citations/19980210404> |
| Class | `EQ` |

**Used for.** The rigorous statement of translational and rotational equations for a general
variable-mass system, and specifically the **additional terms that a naive constant-mass derivation
omits**: the momentum-flux (thrust) term, the Coriolis-like term, the jet-damping moment, and the
moment arising from a time-varying inertia tensor.

RADIUS uses this to *name the terms it is not implementing*. The Phase 4 baseline omits jet damping
and inertia-rate moments; this source is what allows that omission to be registered as a specific,
identified assumption (`A-VM-03`, `A-VM-04`) rather than an unexamined gap.

**Scope note.** This source discusses design-relevant parameters (nozzle and chamber geometry,
propellant grain configuration). RADIUS uses **only** the abstract equations of motion from it. The
hardware-design content is outside RADIUS's scope and is not drawn on. See `CLAUDE.md`, hard scope
boundary.

**Related.** Eke & Mao, *On the Dynamics of Variable Mass Systems*, *International Journal of
Mechanical Engineering Education*, Vol. 30, No. 2, 2002, DOI 10.7227/IJMEE.30.2.4 — a Kane's-method
derivation of the same equations, useful as an independent cross-check. ✅

---

## Atmosphere

### SRC-008 — *U.S. Standard Atmosphere, 1976* ✅

| | |
|---|---|
| Issuing bodies | NOAA, NASA, USAF |
| Publication | October 1976 |
| Identifiers | NOAA-S/T 76-1562 · NASA-TM-X-74335 · NTRS 19770009539 |
| Links | <https://ntrs.nasa.gov/citations/19770009539> · <https://www.ngdc.noaa.gov/stp/space-weather/online-publications/miscellaneous/us-standard-atmosphere-1976/us-standard-atmosphere_st76-1562_noaa.pdf> |
| Class | `EQ`, `DATA` |

**Used for.** The defining equations and constants of the layered standard atmosphere below 86 km
(geopotential altitude, base temperatures and lapse rates, the barometric relations), and the
published property tables used as the **verification reference** for RADIUS's implementation.

**Important distinction.** Agreement with these tables is *verification* — evidence that RADIUS
implements the standard correctly. It is **not** validation, because the standard is itself an
idealised model and does not describe the atmosphere on any particular day. RADIUS states this
wherever atmosphere results are reported.

---

## Numerical methods

### SRC-009 — Dormand & Prince, *A family of embedded Runge-Kutta formulae* ✅

| | |
|---|---|
| Authors | J. R. Dormand, P. J. Prince |
| Publication | *Journal of Computational and Applied Mathematics*, Vol. 6, No. 1, 1980, pp. 19–26 |
| DOI | 10.1016/0771-050X(80)90013-3 |
| Class | `NUM` |

**Used for.** The RK5(4) embedded pair considered — and, for the initial phase, **rejected** — as
RADIUS's integrator. Cited in ADR-0006 as the alternative that was evaluated, with the reasons for
deferring it recorded.

---

### SRC-010 — Hairer, Nørsett & Wanner, *Solving Ordinary Differential Equations I: Nonstiff Problems*

| | |
|---|---|
| Authors | E. Hairer, S. P. Nørsett, G. Wanner |
| Publisher | Springer Series in Computational Mathematics, Vol. 8, 2nd revised edition |
| Year | 1993 `(not verified)` — edition and year not checked against the publisher |
| Class | `NUM` |

**Used for.** Order conditions for Runge–Kutta methods, local vs global error, the empirical
order-of-accuracy test that RADIUS uses as its principal integrator verification (V-NUM-01), and
linear stability regions.

**Status.** The content this supports is standard textbook material; the *bibliographic details*
above are recorded from memory and are marked unverified. Verify before the specification is cited
externally.

---

## Verification and validation methodology

### SRC-011 — Oberkampf & Roy, *Verification and Validation in Scientific Computing* ✅

| | |
|---|---|
| Authors | William L. Oberkampf, Christopher J. Roy |
| Publisher | Cambridge University Press, 2010 |
| ISBN | 978-0-521-11360-1 |
| Class | `V&V` |

**Used for.** The verification/validation distinction that `CLAUDE.md` makes binding; code
verification vs solution verification; the method of manufactured solutions; and the discipline of
stating a validation *purpose* and *tolerance* before claiming a model is adequate.

---

### SRC-012 — AIAA G-077-1998 (R2002), *Guide for the Verification and Validation of Computational Fluid Dynamics Simulations* ✅

| | |
|---|---|
| Issuing body | AIAA Computational Fluid Dynamics Committee on Standards |
| Publication | 1998, reaffirmed 2002 · DOI 10.2514/4.472855 |
| Class | `V&V` |

**Used for.** The community-standard definitions of verification ("does the computation represent
the conceptual model correctly") and validation ("does the computation represent the real world"),
which RADIUS adopts verbatim in meaning if not in wording.

**Scope note.** The guide is written for CFD. RADIUS is not CFD. It is cited for its definitions and
methodology, not its CFD-specific procedures.

---

### SRC-013 — NASA-STD-7009, *Standard for Models and Simulations* ✅

| | |
|---|---|
| Issuing body | NASA Office of the Chief Engineer |
| Current revision | **NASA-STD-7009B**, 5 March 2024 |
| Prior revision | NASA-STD-7009A w/ Change 1 |
| Links | <https://standards.nasa.gov/standard/NASA/NASA-STD-7009> |
| Class | `V&V` |

**Used for.** The idea that a simulation result should be reported together with an explicit
**credibility assessment** across several axes — verification, validation, input pedigree,
uncertainty, robustness, use history, management, people — rather than as a bare number.

**How RADIUS uses it.** As a checklist shaping what a RADIUS result report must contain. RADIUS does
**not** claim compliance with NASA-STD-7009; compliance is a formal process this project has not
undertaken, and claiming it would be false.

**Note.** Revision B (2024) supersedes A. Cite B unless a claim depends on A specifically.

---

## Gaps — sources RADIUS needs and does not yet have

Recorded so the gaps are visible rather than forgotten.

| Gap | Why it matters | Status |
|---|---|---|
| An independent published 6-DOF **benchmark trajectory** with stated initial conditions, parameters and reference output | Without one, RADIUS can verify its equations but cannot validate its integrated trajectory against anything external. This is the binding limitation on every claim RADIUS will be able to make | **Open — not found.** Searched only informally so far |
| A published **aerodynamic coefficient set** for a generic, non-operational configuration, in the open literature | Needed so the aerodynamic model is traceable rather than invented. If none is found, coefficients are declared *arbitrary and illustrative* and every result is scoped accordingly | **Open** |
| Verified bibliographic details for SRC-010 | Cited but unverified | **Open** |
| A reference for **jet damping** magnitude sufficient to bound the error of omitting it | Would convert assumption `A-VM-03` from "omitted, consequence unknown" to "omitted, consequence bounded" | **Open** |

A gap is closed by finding the source, not by deciding the question is unimportant.
