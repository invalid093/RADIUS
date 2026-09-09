"""Reference-frame transformations — passive, NED, 3-2-1 Euler, scalar-first quaternion.

Authoritative conventions: ``docs/methodology/NOTATION_AND_CONVENTIONS.md`` (section 4)
and ``docs/research/RS-001_reference_frames.md``. Restated below, because every one of
these has a plausible alternative in common use and a silently mismatched convention is
the defect class this module is most exposed to.

CONVENTIONS ENCODED
-------------------
**Frames.** ``I`` is the flat-Earth inertial frame: x North, y East, **z Down** (NED),
right-handed. ``B`` is the body frame: x forward, y out the right side, z down,
right-handed, origin at the instantaneous centre of mass.

**Passive transformations, read "to <- from".** ``T_b_from_i`` re-expresses the *same*
physical vector in different axes::

    v_B = T_b_from_i @ v_I

It does **not** rotate a vector within a fixed frame. The active rotation is the
transpose. Nothing in this module returns an active rotation.

**Angles are in radians**, always, with no degree-accepting variant. Degrees exist only
at configuration and reporting boundaries (NOTATION section 1).

**Euler: 3-2-1 sequence** — yaw ``psi`` about z, then pitch ``theta`` about the new y,
then roll ``phi`` about the new x::

    T_b_from_i(phi, theta, psi) = R_x(phi) @ R_y(theta) @ R_z(psi)

    R_x(a) = [[1, 0, 0], [0, cos a, sin a], [0, -sin a, cos a]]
    R_y(a) = [[cos a, 0, -sin a], [0, 1, 0], [sin a, 0, cos a]]
    R_z(a) = [[cos a, sin a, 0], [-sin a, cos a, 0], [0, 0, 1]]

Note the asymmetry: ``R_y`` carries ``-sin`` in its [0][2] entry where ``R_x`` and
``R_z`` carry ``+sin``. That is correct, not a typo, and it is the single most commonly
mis-transcribed entry of the three.

**Quaternion: Hamilton, scalar-first,** ``quat_b_from_i = (q0, q1, q2, q3)``. The
matrix built here is the transpose of the conventional Hamilton *active* rotation
matrix — note the sign of the ``-2 q0 [qv x]`` term — so it corresponds to
``v~_B = quat* (x) v~_I (x) quat`` and not to ``quat (x) v~ (x) quat*``.

**Non-unit quaternions are supported by division, not normalisation.** See
:func:`dcm_b_from_i_quat`.

INDEPENDENCE OF THE TWO PATHS
-----------------------------
:func:`dcm_b_from_i_euler` builds the matrix directly from the elementary matrices
above. It does **not** route through the quaternion. This is deliberate and required:
the Phase 2A anchors check both the Euler path and the quaternion path against the
*same* hand-derived literals, and that only has value if the two paths are genuinely
independent. An ``Euler -> quaternion -> DCM`` implementation of ``Euler -> DCM`` would
make a shared convention error invisible to those tests.

VERIFICATION STATUS
-------------------
Verified against the hand-derived anchors V-FRM-08 and V-ATT-01 in
``tests/test_frames.py``, which were written before this module existed and whose
expected values are derived from the specification, not from this code. That is
**verification** — evidence the documented equations are implemented correctly. It is
not validation, and nothing here supports a claim about physical reality.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = [
    "dcm_b_from_i_euler",
    "dcm_b_from_i_quat",
    "quat_b_from_i_euler",
]

_QUAT_LEN = 4


# --------------------------------------------------------------------------------------
# Elementary passive rotations, written out exactly as documented.
#
# These are private: callers compose attitudes through the public functions below, so
# there is exactly one place where the 3-2-1 order is decided.
# --------------------------------------------------------------------------------------
def _r_x(angle_rad: float) -> NDArray[np.float64]:
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[1.0, 0.0, 0.0],
                     [0.0, c, s],
                     [0.0, -s, c]])


def _r_y(angle_rad: float) -> NDArray[np.float64]:
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[c, 0.0, -s],
                     [0.0, 1.0, 0.0],
                     [s, 0.0, c]])


def _r_z(angle_rad: float) -> NDArray[np.float64]:
    c, s = np.cos(angle_rad), np.sin(angle_rad)
    return np.array([[c, s, 0.0],
                     [-s, c, 0.0],
                     [0.0, 0.0, 1.0]])


def dcm_b_from_i_euler(
    phi_rad: float, theta_rad: float, psi_rad: float
) -> NDArray[np.float64]:
    """Direction cosine matrix ``T_b_from_i`` from 3-2-1 Euler angles.

    Parameters
    ----------
    phi_rad:
        Roll, about the body x axis. Radians.
    theta_rad:
        Pitch, about the (once-rotated) y axis. Radians.
    psi_rad:
        Yaw, about the inertial z axis. Radians.

    Returns
    -------
    ``(3, 3)`` passive transformation such that ``v_B = T @ v_I``.

    Notes
    -----
    Built directly as ``R_x(phi) @ R_y(theta) @ R_z(psi)`` — see the module docstring on
    why this must not be routed through the quaternion representation.

    No singularity guard is applied. The 3-2-1 parameterisation is singular at
    ``|theta| = pi/2``, but that singularity belongs to the *extraction* of Euler angles
    from an attitude, not to their use as an input: this function is perfectly
    well-defined at ``theta = pi/2``, and V-ATT-01 case 2 and case 3 exercise it there.
    Euler angles are an input and reporting representation only; they are never the
    integrated state (RS-002, ADR-0004).
    """
    return _r_x(phi_rad) @ _r_y(theta_rad) @ _r_z(psi_rad)


def quat_b_from_i_euler(
    phi_rad: float, theta_rad: float, psi_rad: float
) -> NDArray[np.float64]:
    """Attitude quaternion ``quat_b_from_i`` from 3-2-1 Euler angles, scalar-first.

    Parameters
    ----------
    phi_rad, theta_rad, psi_rad:
        Roll, pitch, yaw in radians, as for :func:`dcm_b_from_i_euler`.

    Returns
    -------
    ``(4,)`` scalar-first quaternion ``(q0, q1, q2, q3)``, of unit norm to within
    floating-point rounding. Not explicitly normalised: the half-angle expressions are
    unit by construction, and dividing by a norm that is already 1 to within a few ULP
    would add rounding rather than remove it.

    Notes
    -----
    Equivalent to the Hamilton product ``q_yaw (x) q_pitch (x) q_roll`` — note the
    order, which follows from ``T(qa (x) qb) = T(qb) @ T(qa)`` (see
    :mod:`radius.math.quaternion`). The closed form below is used rather than three
    products because it is the standard expression and is cheaper; V-ATT-01 case 3
    checks it against the explicitly composed product, so the equivalence is tested
    rather than assumed.

    Returns the representative with the sign the half-angle formulas produce. It is not
    canonicalised to ``q0 >= 0``: canonicalisation belongs at output and comparison
    boundaries only, never where a continuous quantity might later be integrated
    (RS-002 section 7).
    """
    c_phi, s_phi = np.cos(phi_rad / 2.0), np.sin(phi_rad / 2.0)
    c_theta, s_theta = np.cos(theta_rad / 2.0), np.sin(theta_rad / 2.0)
    c_psi, s_psi = np.cos(psi_rad / 2.0), np.sin(psi_rad / 2.0)

    return np.array([
        c_psi * c_theta * c_phi + s_psi * s_theta * s_phi,
        c_psi * c_theta * s_phi - s_psi * s_theta * c_phi,
        c_psi * s_theta * c_phi + s_psi * c_theta * s_phi,
        s_psi * c_theta * c_phi - c_psi * s_theta * s_phi,
    ])


def dcm_b_from_i_quat(quat: ArrayLike) -> NDArray[np.float64]:
    """Direction cosine matrix ``T_b_from_i`` from a scalar-first quaternion.

    Implements, for all ``quat != 0``::

        T = [ (q0^2 - qv.qv) I + 2 qv qv^T - 2 q0 [qv x] ] / (quat . quat)

    Parameters
    ----------
    quat:
        Scalar-first quaternion ``(q0, q1, q2, q3)``. **Need not be of unit norm.**

    Returns
    -------
    ``(3, 3)`` passive transformation such that ``v_B = T @ v_I``. Orthonormal with
    determinant ``+1`` for any non-zero input.

    Raises
    ------
    ValueError
        If ``quat`` is not shape ``(4,)``, or if ``quat . quat`` is zero. The zero
        quaternion represents no attitude and the specification defines this formula
        only for ``quat != 0``; returning a number anyway would be inventing a
        convention. Raising follows the repository's standing rule that a quantity
        asked for outside its stated domain raises rather than being clamped or
        extrapolated (RS-006 section 4).

    Notes
    -----
    **The division by ``quat . quat`` is the point, and it is a division, not a
    normalisation.** Inside a Runge-Kutta stage the quaternion block is *necessarily*
    off the unit sphere, and because ``T(k*quat) = k^2 T(quat)``, the undivided formula
    is not a rotation there — it would scale every aerodynamic and propulsive force by
    ``||quat||^2`` in stages 2 through 4 of every step. This was audit finding F-3,
    registered as assumption ``A-NUM-05`` and pinned by the non-unit case of V-ATT-01.

    Normalising the input instead would be wrong for two separate reasons: it changes
    the function being integrated, which invalidates the integrator's order conditions;
    and a conditional normalisation introduces a branch, which the determinism guarantee
    in ``docs/PROVENANCE.md`` section 5 depends on not existing.

    The zero-norm check *is* a branch, but a different kind: it rejects an input outside
    the domain rather than altering the operation for inputs inside it. For every valid
    quaternion the arithmetic executed is identical and branch-free.

    Because the expression is quadratic in ``quat``, ``quat`` and ``-quat`` give exactly
    the same matrix — the double cover — with no special handling.
    """
    q = np.asarray(quat, dtype=np.float64)
    if q.shape != (_QUAT_LEN,):
        raise ValueError(
            f"quat must be a scalar-first quaternion of shape (4,) ordered "
            f"(q0, q1, q2, q3); got shape {q.shape}."
        )

    norm_sq = float(np.dot(q, q))
    if norm_sq == 0.0:
        raise ValueError(
            "The zero quaternion does not represent an attitude: T_b_from_i(quat) is "
            "defined only for quat != 0 (NOTATION_AND_CONVENTIONS.md section 4). "
            "Returning a matrix here would be inventing a convention."
        )

    q0, qv = q[0], q[1:]
    skew = np.array([[0.0, -qv[2], qv[1]],
                     [qv[2], 0.0, -qv[0]],
                     [-qv[1], qv[0], 0.0]])

    unscaled = (
        (q0 * q0 - float(np.dot(qv, qv))) * np.eye(3)
        + 2.0 * np.outer(qv, qv)
        - 2.0 * q0 * skew
    )
    return unscaled / norm_sq
