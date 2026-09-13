"""Production rotational derivative against the frozen V-EOM-05 anchor.

WHAT THIS FILE IS, AND WHAT IT DELIBERATELY IS NOT
---------------------------------------------------
This file tests ``radius.dynamics.rotational.angular_acceleration_wrt_i_in_b`` against the
values frozen in :mod:`test_eom_anchors` **before that module existed**. It imports those
values; it does not recompute them.

That distinction is the whole point. The anchor module derives the expected angular
acceleration twice, by an adjugate inverse and by Cramer's rule written out as scalar
expressions, in exact rational arithmetic, from the specification. If this file re-derived
the answer instead of consuming it, an algorithmic error shared between test and
implementation would be invisible — which is exactly the failure mode the anchors exist to
prevent. So: no matrix inverse, no linear solve, and no ``fractions`` arithmetic appears
below. The only computation performed here is the *forward* residual check of Test C, which
uses a different relation (multiply and add) from the one production uses (solve).

TOLERANCE — DERIVED, NOT INHERITED
----------------------------------
Phase 2H recorded that the translational anchors' 1e-12 does **not** transfer to rotational
work, and that a rotational tolerance must come from the numerical behaviour of the
implementation. This implementation performs no integration: it is one 3x3 linear solve in
binary64, so the tolerance follows from conditioning rather than from a convergence study.

    |wdot| for these cases          <= 40 rad/s^2
    condition number of J            ~ 4.64   (frozen in the anchor's documentation)
    unit round-off (binary64)         = 2.22e-16
    backward-stable solve: relative error ~ cond * eps  ~  1.0e-15
                           absolute error ~ 40 * 1.0e-15  ~  4e-14

``ABSOLUTE_TOLERANCE = 1e-12`` sits about 25x above that bound — enough headroom that a
different BLAS or a different numpy build cannot make a correct implementation fail — and 13
orders of magnitude **below** the smallest discrimination margin V-EOM-05 demonstrates
(157/10 = 15.7 rad/s^2, from zeroing a single product of inertia). It cannot hide any error
this anchor exists to catch. The measured error on this platform is reported in RL-0016 and
is far smaller again; the tolerance is set from the bound, not from the measurement, so that
it does not have to move when the measurement does.
"""

import unittest

import numpy as np

from radius.dynamics.rotational import angular_acceleration_wrt_i_in_b
from test_eom_anchors import VEOM05NonPrincipalBodyAxes as ANCHOR

# See the module docstring for the derivation. Absolute, in rad/s^2; no relative term is
# used, because every quantity here is O(1) to O(40) and a relative tolerance would only
# restate the same bound less clearly.
ABSOLUTE_TOLERANCE = 1e-12

# Test C — a non-zero external moment. Independently derived in exact rational arithmetic
# (2026-09-12) from M - w x (J w) and frozen here, so the moment path has its own oracle
# rather than borrowing the torque-free one:
#
#     J w             = (24, -67, 45)
#     w x (J w)        = (199, -12, -124)
#     r = M - w x (J w) = (11, -18, 14) - (199, -12, -124) = (-188, -6, 138)
#     J wdot = r       is solved by wdot = (-16, 8, 26)
#
# Cross-check by linearity: M was chosen as J k with k = (2, -1, 3), so wdot must exceed the
# torque-free (-18, 9, 23) by exactly k. It does.
MOMENT_ABOUT_CM = (11.0, -18.0, 14.0)
OMEGA_DOT_WITH_MOMENT = (-16.0, 8.0, 26.0)
MOMENT_LINEARITY_OFFSET = (2.0, -1.0, 3.0)

ZERO_MOMENT = (0.0, 0.0, 0.0)


def _f(values):
    """Frozen exact rationals -> float64 array. Conversion only; no arithmetic."""
    return np.asarray([float(x) for x in values], dtype=np.float64)


def _f2(rows):
    return np.asarray([[float(x) for x in row] for row in rows], dtype=np.float64)


class TestRotationalDerivativeAgainstVEOM05(unittest.TestCase):
    """The V-EOM-05 anchor, consumed as the acceptance gate for production code."""

    def setUp(self):
        self.inertia = _f2(ANCHOR.J)
        self.diagonalised = _f2([[x if i == k else 0 for k, x in enumerate(row)]
                                 for i, row in enumerate(ANCHOR.J)])

    def assert_close(self, actual, expected, message):
        self.assertLessEqual(
            float(np.max(np.abs(np.asarray(actual) - np.asarray(expected)))),
            ABSOLUTE_TOLERANCE, message)

    # -- Test A / B: the two frozen torque-free states -----------------------------------
    def test_matches_frozen_v_eom_05_state_0(self):
        result = angular_acceleration_wrt_i_in_b(
            self.inertia, _f(ANCHOR.OMEGA_0), ZERO_MOMENT)
        self.assert_close(result, _f(ANCHOR.OMEGA_DOT_0),
                          "production wdot must reproduce the frozen V-EOM-05 state 0 "
                          "oracle (-18, 9, 23).")

    def test_matches_frozen_v_eom_05_state_1(self):
        result = angular_acceleration_wrt_i_in_b(
            self.inertia, _f(ANCHOR.OMEGA_1), ZERO_MOMENT)
        self.assert_close(result, _f(ANCHOR.OMEGA_DOT_1),
                          "production wdot must reproduce the frozen V-EOM-05 state 1 "
                          "oracle (-12, 31, -38).")

    def test_consumes_the_anchor_rather_than_a_local_copy(self):
        """Traceability: the numbers compared against are the anchor's own literals."""
        self.assertEqual(tuple(float(x) for x in ANCHOR.OMEGA_DOT_0), (-18.0, 9.0, 23.0))
        self.assertEqual(tuple(float(x) for x in ANCHOR.OMEGA_DOT_1), (-12.0, 31.0, -38.0))
        self.assertEqual(tuple(float(x) for x in ANCHOR.OMEGA_0), (4.0, -6.0, 7.0))
        self.assertEqual(float(ANCHOR.J[0][1]), -1.0)

    # -- Test C: the external-moment path -------------------------------------------------
    def test_non_zero_external_moment(self):
        omega = _f(ANCHOR.OMEGA_0)
        result = angular_acceleration_wrt_i_in_b(self.inertia, omega, MOMENT_ABOUT_CM)
        self.assert_close(result, OMEGA_DOT_WITH_MOMENT,
                          "production wdot must reproduce the independently derived "
                          "non-zero-moment oracle (-16, 8, 26).")

    def test_non_zero_moment_satisfies_the_euler_equation_forward(self):
        """``J wdot + w x (J w) = M``, checked by multiplying — not by solving again."""
        omega = _f(ANCHOR.OMEGA_0)
        w_dot = angular_acceleration_wrt_i_in_b(self.inertia, omega, MOMENT_ABOUT_CM)
        residual = self.inertia @ w_dot + np.cross(omega, self.inertia @ omega)
        self.assert_close(residual, MOMENT_ABOUT_CM,
                          "the returned wdot must satisfy the Euler equation with the "
                          "supplied moment.")

    def test_moment_enters_linearly(self):
        """M = J k was chosen so the answer must exceed the torque-free one by exactly k."""
        omega = _f(ANCHOR.OMEGA_0)
        free = angular_acceleration_wrt_i_in_b(self.inertia, omega, ZERO_MOMENT)
        forced = angular_acceleration_wrt_i_in_b(self.inertia, omega, MOMENT_ABOUT_CM)
        self.assert_close(forced - free, MOMENT_LINEARITY_OFFSET,
                          "the moment path must be linear with the expected offset.")

    def test_zero_moment_is_not_silently_assumed(self):
        """A model ignoring its moment input would pass every torque-free test."""
        omega = _f(ANCHOR.OMEGA_0)
        free = angular_acceleration_wrt_i_in_b(self.inertia, omega, ZERO_MOMENT)
        forced = angular_acceleration_wrt_i_in_b(self.inertia, omega, MOMENT_ABOUT_CM)
        self.assertGreater(float(np.max(np.abs(forced - free))), 1.0)

    # -- Test D: products-of-inertia sensitivity ------------------------------------------
    def test_products_of_inertia_are_actually_consumed_state_0(self):
        omega = _f(ANCHOR.OMEGA_0)
        deleted = angular_acceleration_wrt_i_in_b(self.diagonalised, omega, ZERO_MOMENT)
        self.assert_close(deleted, _f(ANCHOR.OMEGA_DOT_IF_PRODUCTS_DELETED_0),
                          "with the products deleted, production must return the frozen "
                          "diagonalised comparison (-21/2, -12, -24/5).")
        full = angular_acceleration_wrt_i_in_b(self.inertia, omega, ZERO_MOMENT)
        self.assertGreater(float(np.max(np.abs(full - deleted))),
                           float(ANCHOR.PRODUCTS_GAP_0) - ABSOLUTE_TOLERANCE)

    def test_products_of_inertia_are_actually_consumed_state_1(self):
        omega = _f(ANCHOR.OMEGA_1)
        deleted = angular_acceleration_wrt_i_in_b(self.diagonalised, omega, ZERO_MOMENT)
        self.assert_close(deleted, _f(ANCHOR.OMEGA_DOT_IF_PRODUCTS_DELETED_1),
                          "with the products deleted, production must return the frozen "
                          "diagonalised comparison (10, 24, -7).")
        full = angular_acceleration_wrt_i_in_b(self.inertia, omega, ZERO_MOMENT)
        self.assertGreater(float(np.max(np.abs(full - deleted))),
                           float(ANCHOR.PRODUCTS_GAP_1) - ABSOLUTE_TOLERANCE)

    def test_each_product_of_inertia_changes_the_answer(self):
        """Not just "the products matter" collectively — each one individually."""
        omega = _f(ANCHOR.OMEGA_0)
        reference = angular_acceleration_wrt_i_in_b(self.inertia, omega, ZERO_MOMENT)
        for i, k, name in ((0, 1, "J_xy"), (0, 2, "J_xz"), (1, 2, "J_yz")):
            zeroed = self.inertia.copy()
            zeroed[i][k] = zeroed[k][i] = 0.0
            with self.subTest(product=name):
                result = angular_acceleration_wrt_i_in_b(zeroed, omega, ZERO_MOMENT)
                self.assertGreater(float(np.max(np.abs(result - reference))), 1.0)


class TestRotationalDerivativeContract(unittest.TestCase):
    """Purity, determinism, and the domain boundary."""

    def setUp(self):
        self.inertia = _f2(ANCHOR.J)
        self.omega = _f(ANCHOR.OMEGA_0)
        self.moment = np.asarray(MOMENT_ABOUT_CM, dtype=np.float64)

    # -- Test E: input purity --------------------------------------------------------------
    def test_does_not_mutate_its_inputs(self):
        inertia_before = self.inertia.copy()
        omega_before = self.omega.copy()
        moment_before = self.moment.copy()
        angular_acceleration_wrt_i_in_b(self.inertia, self.omega, self.moment)
        np.testing.assert_array_equal(self.inertia, inertia_before)
        np.testing.assert_array_equal(self.omega, omega_before)
        np.testing.assert_array_equal(self.moment, moment_before)

    def test_returns_a_new_array_each_call(self):
        first = angular_acceleration_wrt_i_in_b(self.inertia, self.omega, self.moment)
        second = angular_acceleration_wrt_i_in_b(self.inertia, self.omega, self.moment)
        self.assertIsNot(first, second)
        first[0] = 1234.0
        self.assertNotEqual(float(second[0]), 1234.0)

    # -- Test F: determinism ----------------------------------------------------------------
    def test_is_bitwise_deterministic(self):
        first = angular_acceleration_wrt_i_in_b(self.inertia, self.omega, self.moment)
        second = angular_acceleration_wrt_i_in_b(self.inertia, self.omega, self.moment)
        np.testing.assert_array_equal(first, second)

    def test_accepts_lists_and_tuples_identically_to_arrays(self):
        from_arrays = angular_acceleration_wrt_i_in_b(
            self.inertia, self.omega, self.moment)
        from_sequences = angular_acceleration_wrt_i_in_b(
            [[float(x) for x in row] for row in ANCHOR.J],
            tuple(float(x) for x in ANCHOR.OMEGA_0),
            list(MOMENT_ABOUT_CM))
        np.testing.assert_array_equal(from_arrays, from_sequences)

    # -- domain boundary --------------------------------------------------------------------
    def test_rejects_a_singular_inertia_tensor(self):
        singular = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        with self.assertRaises(ValueError):
            angular_acceleration_wrt_i_in_b(singular, self.omega, self.moment)

    def test_rejects_wrong_shapes(self):
        cases = {
            "principal moments as a 3-vector": ((8.0, 7.0, 5.0), self.omega, self.moment),
            "omega of length 4": (self.inertia, (1.0, 2.0, 3.0, 4.0), self.moment),
            "moment of length 2": (self.inertia, self.omega, (1.0, 2.0)),
        }
        for label, args in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    angular_acceleration_wrt_i_in_b(*args)

    def test_rejects_non_finite_inputs(self):
        cases = {
            "nan in omega": (self.inertia, (float("nan"), 0.0, 0.0), self.moment),
            "inf in moment": (self.inertia, self.omega, (float("inf"), 0.0, 0.0)),
        }
        for label, args in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(ValueError):
                    angular_acceleration_wrt_i_in_b(*args)

    def test_uses_the_full_tensor_not_only_its_diagonal(self):
        """A non-symmetric tensor is accepted and used as given — a recorded limitation.

        Symmetry and positive definiteness are *physical* requirements on the mass model
        (``A-EOM-02``, V-VM-06 of RS-008), not mathematical requirements of this solve, and
        RADIUS has not defined a production validation policy for them. This test pins the
        behaviour that is actually implemented, so the limitation is visible rather than
        assumed either way.
        """
        asymmetric = self.inertia.copy()
        asymmetric[0][1] = -4.0                      # breaks symmetry with J[1][0] = -1
        result = angular_acceleration_wrt_i_in_b(asymmetric, self.omega, self.moment)
        self.assertEqual(result.shape, (3,))
        self.assertTrue(bool(np.all(np.isfinite(result))))
