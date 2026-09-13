"""Rigid-body rotational dynamics — the instantaneous angular-acceleration derivative.

Authoritative equation: ``docs/research/RS-004_equations_of_motion.md`` section 4.1, as
corrected by ADR-0009. Notation and the inertia convention: ADR-0010 and
``docs/methodology/NOTATION_AND_CONVENTIONS.md`` section 5.1. Restated below, because a
silently mismatched inertia convention is the defect class this module is most exposed to.

THE EQUATION IMPLEMENTED
------------------------
For a rigid body of constant inertia, with all quantities resolved in the body frame ``B``
and moments taken about the instantaneous centre of mass::

    J wdot + w x (J w) = M_ext          =>      wdot = J^-1 [ M_ext - w x (J w) ]

This module evaluates the right-hand side **once**, at one state. It is a derivative, not
a step: nothing here integrates, propagates attitude, advances time, or touches mass.

CONVENTIONS ENCODED
-------------------
**Inertia tensor, body axes, products of inertia with a PLUS sign** (ADR-0010, and the
V-EOM-05 anchor that pins it)::

    J = [[J_xx, J_xy, J_xz],
         [J_xy, J_yy, J_yz],
         [J_xz, J_yz, J_zz]]

so that ``(J w)_x = J_xx w_x + J_xy w_y + J_xz w_z``. Some texts store products of inertia
already negated; RADIUS does not, and this module performs no conversion. A caller supplying
the other convention gets a silently wrong answer — which is why the convention is stated
here, in NOTATION section 5.1, and in the frozen anchor.

**The full tensor is used.** Nothing here assumes principal axes, diagonality, or the
axisymmetric special case ``diag(J_par, J_perp, J_perp)`` of a RADIUS vehicle. The products
of inertia are exactly what couple the axes (RS-004 section 4.3), and V-EOM-05's
products-of-inertia tests fail if they are dropped.

**Angular velocity** is ``w = omega^B_{B/I} = (p, q, r)``, rad/s, of the body frame relative
to the inertial frame, resolved in body axes (NOTATION section 5).

**Moments** are about the **instantaneous centre of mass**, in body axes, N·m (NOTATION
section 6). A moment about any other point must be transferred before it is passed here.

WHAT IS DELIBERATELY ABSENT
---------------------------
* **No inertia-rate term.** ``Jdot w`` does not appear: under ``A-VM-05`` the angular-momentum
  flux of co-rotating ejected mass cancels it exactly (ADR-0009). For a depleting vehicle the
  caller passes ``J`` evaluated at the instantaneous mass; this function neither knows nor
  cares how ``J`` was obtained.
* **No jet damping** (``A-VM-03``, omitted, magnitude unbounded) and no aerodynamic or
  propulsive moment model. Those produce ``M_ext``; they are not this function's business.
* **No integration, no attitude propagation, no state vector.** Those belong to RS-005 and to
  modules that do not exist yet.

VALIDATION — WHAT IS AND IS NOT CHECKED
---------------------------------------
Checked: shapes, finiteness, and that ``J`` is non-singular — the *mathematical* requirement
for the solve to mean anything.

**Not checked: symmetry, positive definiteness, or the triangle inequalities on the principal
moments.** Those are the *physical* requirements for a tensor to be a rigid body's, they are
properties of the mass model rather than of this evaluation, and RADIUS has not yet defined a
production validation policy for them: ``A-EOM-02`` is still ``TO-VERIFY`` and V-VM-06 — the
test that asserts symmetry and positive definiteness every step — belongs to the
mass-properties interface of RS-008, which does not exist. This limitation is recorded rather
than papered over with an ad-hoc check invented here. A caller that supplies a physically
impossible tensor gets the mathematically correct answer for that tensor.

VERIFICATION STATUS
-------------------
Verified against **V-EOM-05**, the products-of-inertia anchor frozen in
``tests/test_eom_anchors.py`` before this module existed, whose expected values were derived
independently (twice, by an adjugate inverse and by Cramer's rule) from the specification and
not from this code. ``tests/test_dynamics_rotational.py`` consumes those frozen values; it
does not recompute them. That is **verification**, not validation: it establishes that the
documented equation is implemented correctly, and says nothing about physical reality.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = ["angular_acceleration_wrt_i_in_b"]

_VEC_SHAPE = (3,)
_TENSOR_SHAPE = (3, 3)


def _as_vector(value: ArrayLike, name: str) -> NDArray[np.float64]:
    """Coerce to a finite float64 ``(3,)`` array, or raise."""
    array = np.asarray(value, dtype=np.float64)
    if array.shape != _VEC_SHAPE:
        raise ValueError(
            f"{name} must be a 3-vector resolved in body axes, shape (3,); "
            f"got shape {array.shape}."
        )
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite; got {array!r}.")
    return array


def _as_inertia(value: ArrayLike) -> NDArray[np.float64]:
    """Coerce to a finite float64 ``(3, 3)`` array, or raise."""
    array = np.asarray(value, dtype=np.float64)
    if array.shape != _TENSOR_SHAPE:
        raise ValueError(
            "inertia_about_cm_in_b must be the full 3x3 inertia tensor about the centre "
            f"of mass, resolved in body axes; got shape {array.shape}. A 3-vector of "
            "principal moments is not accepted: the products of inertia are part of the "
            "argument (ADR-0010, NOTATION section 5.1)."
        )
    if not np.all(np.isfinite(array)):
        raise ValueError(f"inertia_about_cm_in_b must be finite; got {array!r}.")
    return array


def angular_acceleration_wrt_i_in_b(
    inertia_about_cm_in_b: ArrayLike,
    omega_wrt_i_in_b: ArrayLike,
    moment_about_cm_in_b: ArrayLike,
) -> NDArray[np.float64]:
    """Angular acceleration ``wdot`` of ``B`` relative to ``I``, resolved in body axes.

    Solves, for one state::

        J wdot = M_ext - w x (J w)

    Parameters
    ----------
    inertia_about_cm_in_b:
        ``(3, 3)`` inertia tensor about the instantaneous centre of mass, resolved in body
        axes, kg·m². Products of inertia are stored **positive** — see the module docstring.
        Used as given: symmetry and positive definiteness are not checked.
    omega_wrt_i_in_b:
        ``(3,)`` angular velocity of ``B`` relative to ``I``, resolved in body axes, rad/s.
    moment_about_cm_in_b:
        ``(3,)`` external moment **about the centre of mass**, resolved in body axes, N·m.
        Pass zeros for the torque-free case; there is no default, because a silently omitted
        moment is precisely the error that would make a torque-free test pass a model that
        ignores its moment input.

    Returns
    -------
    ``(3,)`` angular acceleration in rad/s², a new array. No input is modified.

    Raises
    ------
    ValueError
        If any argument has the wrong shape or is non-finite, or if the inertia tensor is
        singular. A singular tensor has no unique ``wdot``: returning a number anyway would
        be inventing one, which the repository's standing rule forbids (RS-006 section 4).

    Notes
    -----
    The linear system is **solved**, not inverted: ``J^-1`` is never formed. For a 3x3 system
    the difference is small but real — a solve is backward-stable and costs less rounding
    than forming an inverse and multiplying by it — and the two are exactly equivalent
    mathematically, which is what the anchor checks.

    The cross product follows the right-handed convention of NOTATION section 5, so
    ``w x (J w)`` is the gyroscopic term that transfers angular momentum between body axes.
    It is the term that makes a torque-free asymmetric body tumble, and dropping it is the
    first mutation V-EOM-05 catches.

    Deterministic and branch-free for every valid input: the same arguments produce bitwise
    identical output, which the reproducibility guarantee of ``docs/PROVENANCE.md`` section 5
    depends on. The validation above rejects inputs outside the domain; it never alters the
    arithmetic for inputs inside it.
    """
    inertia = _as_inertia(inertia_about_cm_in_b)
    omega = _as_vector(omega_wrt_i_in_b, "omega_wrt_i_in_b")
    moment = _as_vector(moment_about_cm_in_b, "moment_about_cm_in_b")

    angular_momentum = inertia @ omega                     # h = J w
    gyroscopic = np.cross(omega, angular_momentum)         # w x h   (NOTATION section 5)
    right_hand_side = moment - gyroscopic                  # r = M_ext - w x (J w)

    try:
        return np.linalg.solve(inertia, right_hand_side)
    except np.linalg.LinAlgError as exc:                   # singular tensor
        raise ValueError(
            "inertia_about_cm_in_b is singular, so J wdot = M - w x (J w) has no unique "
            "solution. A singular inertia tensor is not a rigid body's: it implies zero "
            "resistance to rotation about some axis."
        ) from exc
