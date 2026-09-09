"""Quaternion algebra — Hamilton convention, scalar-first.

Authoritative convention: ``docs/methodology/NOTATION_AND_CONVENTIONS.md`` section 4.
Restated here because a module that depends on a convention should state it, and
because the alternatives are all in circulation under the same name.

CONVENTIONS ENCODED
-------------------
* **Ordering: scalar first.** ``quat = (q0, q1, q2, q3) = (w, x, y, z)``.
  Scalar-last ``(x, y, z, w)`` is a *different* convention and is not accepted here.
* **Product: Hamilton**, i.e. ``ij = k``, ``jk = i``, ``ki = j``. **Not** the
  JPL/Shuster convention, in which the product order is reversed.

      (a0, av) (x) (b0, bv) = (a0*b0 - av.bv,  a0*bv + b0*av + av x bv)

* **Angles are in radians**; there are no angles in this module, but the constructors
  in :mod:`radius.frames` that produce quaternions consumed here take radians.
* **No hidden normalisation.** No function in this module normalises its input or its
  output. A quaternion of non-unit norm is returned unchanged, because the caller — an
  RK stage, for instance — may legitimately be working off the unit sphere and silently
  projecting back onto it would alter the function being integrated.

WHY COMPOSITION ORDER MATTERS HERE
----------------------------------
Matrices compose by adjacency, ``T_CA = T_CB @ T_BA``. Quaternions in this convention
**do not**::

    T(qa (x) qb) = T(qb) @ T(qa)

The orders are reversed relative to one another. This was audit finding F-4
(``docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`` section 2.5): an implementer
would reasonably assume the two match, and they do not. The behaviour is pinned by
V-ATT-01 case 3, which is the only test guarding it.

SCOPE
-----
Deliberately not a general-purpose quaternion library. There is no conjugate, inverse,
norm, SLERP, axis-angle, rotation-vector or integration API here, because nothing yet
requires one. Those arrive with the phase that needs them.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = ["quat_multiply"]

# Number of components in a scalar-first quaternion.
_QUAT_LEN = 4


def _as_quat(quat: ArrayLike, name: str) -> NDArray[np.float64]:
    """Coerce to a float64 length-4 array, or raise.

    The length check is not defensive clutter: a length-3 argument would otherwise
    broadcast or slice into something that runs and returns a plausible wrong answer,
    which is the failure mode this project is least willing to accept.
    """
    array = np.asarray(quat, dtype=np.float64)
    if array.shape != (_QUAT_LEN,):
        raise ValueError(
            f"{name} must be a scalar-first quaternion of shape (4,) ordered "
            f"(q0, q1, q2, q3); got shape {array.shape}."
        )
    return array


def quat_multiply(quat_a: ArrayLike, quat_b: ArrayLike) -> NDArray[np.float64]:
    """Hamilton product ``quat_a (x) quat_b``, scalar-first.

    Implements, term by term::

        scalar = a0*b0 - av . bv
        vector = a0*bv + b0*av + av x bv

    Parameters
    ----------
    quat_a, quat_b:
        Scalar-first quaternions ``(q0, q1, q2, q3)``. Need not be of unit norm.

    Returns
    -------
    The product, scalar-first. **Not** normalised.

    Notes
    -----
    The product is **not commutative**, and in this convention the composition of the
    corresponding rotations runs the other way: ``T(a (x) b) = T(b) @ T(a)``. See the
    module docstring. Swapping the arguments is a silent, plausible-looking error, which
    is why V-ATT-01 case 3 tests the composed value against a hand-computed literal
    rather than against a round trip.
    """
    a = _as_quat(quat_a, "quat_a")
    b = _as_quat(quat_b, "quat_b")

    a0, av = a[0], a[1:]
    b0, bv = b[0], b[1:]

    scalar = a0 * b0 - float(np.dot(av, bv))
    vector = a0 * bv + b0 * av + np.cross(av, bv)

    return np.concatenate(([scalar], vector))
