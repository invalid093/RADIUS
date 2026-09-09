# ADR-0003 — Reference frames, notation and sign conventions

**Date:** 2026-09-09 · **Status:** Accepted · **Detail:** RS-001, `docs/methodology/NOTATION_AND_CONVENTIONS.md`

## Context

Most 6-DOF defects are not errors of physics. They are two parts of a codebase disagreeing about what
a symbol means: a transformation applied in the wrong direction, a quaternion in the other community's
convention, a moment taken about the wrong point, an angle in the wrong unit. Such an error is
invisible to internal consistency checks, because a *uniformly applied* wrong convention is
self-consistent.

The conventions therefore have to be fixed once, in one authoritative place, before any code exists.

## Decision

1. **Frames.** $I$ — a flat-Earth, non-rotating NED frame treated as inertial, origin at a surface
   reference point, $x$ North, $y$ East, $z$ **Down**. $B$ — body, origin at the *instantaneous centre
   of mass*, $x$ forward, $y$ right, $z$ down. $W$ — wind, derived, never integrated. $E$ — ECEF,
   **deferred and named as deferred**, accessed through an interface so its introduction is a
   substitution.
2. **Units.** SI everywhere internally; radians. Degrees only at boundaries, with a `_deg` suffix on
   the configuration key, converted once in a named function.
3. **Notation.** Every vector states both the frame it is *resolved in* and the frame it is
   *differentiated in*. Code names carry both: `v_cm_wrt_i_in_b`.
4. **Transformations.** Passive, subscripts read "to ← from": $\mathbf{v}^B=\mathbf{T}_{BI}\mathbf{v}^I$.
   Code writes `T_b_from_i`.
5. **Euler.** 3-2-1 sequence, $\mathbf{T}_{BI}=\mathbf{R}_x(\phi)\mathbf{R}_y(\theta)\mathbf{R}_z(\psi)$,
   with the elementary matrices written out explicitly.
6. **Quaternion.** **Hamilton product, scalar-first, $q\equiv q_{BI}$**, with $\mathbf{T}_{BI}(q)$
   given in closed form.
7. **Moments** are about the instantaneous centre of mass unless a reference point is named, and any
   function returning a moment states its reference point in its signature.

**The flat non-rotating Earth assumption is quantified, not asserted** (RS-001 §3): Coriolis,
centrifugal, curvature and gravity-variation errors are each estimated, yielding a provisional
validity domain of roughly 10 km range and 60 s duration.

## Alternatives considered

- **ENU / $z$-up.** Rejected: NED is the aerospace convention, and the literature RADIUS
  cross-checks against uses it. Mixing would guarantee sign confusion at the seam.
- **JPL quaternion convention.** Rejected — not on merit (both are self-consistent) but because one
  must be chosen and stated. Hamilton is the more common choice in flight-dynamics texts RADIUS uses.
- **Leaving the ECEF frame undefined entirely.** Rejected: the *interface* is fixed now (gravity takes
  a position, not an altitude) so the extension does not touch every call site. Only the frame's
  detailed definition is deferred.
- **Defining ECEF now.** Rejected as speculation about a design that has not been done.
- **A units library or typed frames.** Rejected: adds a dependency and does not cover the
  frame-relationship errors that actually occur. Verbose naming plus hand-computed tests covers more,
  at the cost of verbosity.

## Consequences

- Names are long. Accepted — the alternative is a class of error that internal tests cannot detect.
- Changing any convention invalidates every verification test and every stored reference trajectory.
  Such a change requires a superseding ADR naming the invalidated data.
- The flat-Earth domain must be quoted with every result until the ECEF extension exists.
- **Hand-computed expected values (V-FRM-08, V-ATT-01) are mandatory**, because they are the only
  test class that catches a uniformly applied wrong convention.

## Revisit if

The ECEF/ECI extension is undertaken; or a subsystem needs a frame this set does not provide.
