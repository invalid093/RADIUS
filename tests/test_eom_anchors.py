"""V-EOM-01 to V-EOM-05 — frozen analytical anchors for the equations of motion.

WHAT THIS FILE IS
-----------------
Three closed-form limiting cases of the translational equations of motion, frozen as
exact numerical oracles **before any translational dynamics implementation exists**.
There is no ``radius/dynamics.py``, and this file deliberately does not create one, call
one, or propose an API for one.  Nothing here imports from ``radius``.

The intended chain is::

    closed-form mathematics  ->  frozen analytical oracle  ->  future implementation
                                                           ->  acceptance test

Only the first two links exist today.  These tests establish that the frozen values are
arithmetically correct and that they have discriminating power; they do not verify any
code, because there is none to verify.

**V-EOM-04** adds the first *rotational* anchor -- torque-free axisymmetric coning --
frozen before any rotational dynamics implementation exists.  It lives in its own
section below, with its own derivation, and shares only the exact-arithmetic helpers.

**V-EOM-05** is the products-of-inertia anchor: a torque-free body whose body axes are
NOT principal axes, so the off-diagonal terms of the inertia tensor genuinely drive the
answer.  It freezes an instantaneous angular acceleration, not a trajectory -- an
asymmetric torque-free body has no elementary closed form.

GOVERNING EQUATION (RS-004, already audited)
--------------------------------------------
::

    m vdot^I = T_IB (F_aero^B + F_prop^B) + m g(h) zhat_I

**V-EOM-01 and V-EOM-02** set ``F_aero^B = F_prop^B = 0``, so the transformation term
vanishes **identically**.  That is intentional: it isolates the inertial translational
equation from the body-to-inertial force transformation, which is covered by its own
anchors (V-FRM-08, V-ATT-01).  The cost of that isolation is stated honestly in
:class:`TestEomAnchorDiscrimination` — with no force path, those two anchors are
structurally incapable of detecting a body/inertial mix-up.

**V-EOM-03 closes exactly that gap**: a constant *non-zero* body force at a fixed known
attitude, so the ``T_IB`` force-transformation path is exercised while the problem stays
analytically solvable.  It carries no gravity, so the three anchors between them cover
the gravity path and the force path without either masking the other.

FRAME CONVENTION
----------------
NED: **+x North, +y East, +z DOWN** (RS-001).  Gravity therefore acts along **+z**, and
a *negative* ``v_z`` means the body is moving **upward**.  This is not ENU and is not an
upward-positive Cartesian frame.

A CORRECTION TO THE VALUES THIS PHASE WAS GIVEN
-----------------------------------------------
The Phase 2F brief specified the V-EOM-02 result as ``p(3) = (130, -25, 55)``.
**Independent derivation gives ``(130, -25, 70)``, and 70 is the value frozen here.**

    p_z(3) = p0_z + v0_z t + g0 t^2 / 2
           = 100  + (-25)(3) + (10)(9)/2
           = 100  - 75       + 45
           = 70

Confirmed three ways: exact rational arithmetic, term-by-term expansion, and a physical
check — starting 100 m below the origin moving upward at 25 m/s under 10 m/s^2 of
downward gravity, the body rises 31.25 m in the first 2.5 s, falls 1.25 m in the
remaining 0.5 s, and so nets a 30 m rise, taking z from 100 to 70.  A value of 55 would
require an initial upward speed of 30 m/s rather than the specified 25 m/s.

The brief's ``v(3) = (40, -15, 5)`` and both x and y components of ``p(3)`` are correct;
only ``p_z`` was wrong.  Adopting 55 would have frozen an arithmetically false oracle
into the repository permanently, which is precisely the failure the "derive
independently" rule exists to prevent.  Flagged for the researcher: if the intended
scenario was different (``v0_z = -30`` would give 55), one literal changes and the
derivation above changes with it.

PRECISION
---------
Every quantity is a small integer, chosen so the closed forms evaluate exactly.  The
integrity checks below use :class:`fractions.Fraction`, so they are exact rational
arithmetic with no floating-point tolerance at all.  The frozen values are also all
exactly representable in binary64, so a future implementation can be compared against
them with a tolerance of 1e-12 — justified below in ``FUTURE_COMPARISON_TOL``.
V-EOM-04 is the exception: its values are exact rationals, not all representable in
binary64, and that tolerance does not transfer to it (see its section).

Run from the repository root::

    python -m unittest discover -s tests -t tests
"""

from fractions import Fraction
import unittest

# --------------------------------------------------------------------------------------
# Tolerance for a FUTURE implementation to be compared against these anchors.
# Unused by this file, which is exact; recorded here so the number is justified once,
# where the anchors live, rather than invented later at the point of use.
#
# The anchor magnitudes are O(100) and a propagation step is O(10) double-precision
# operations, so the honest error budget is ~1e-14 absolute. 1e-12 leaves two orders of
# headroom for accumulated round-off, and sits twelve orders below the SMALLEST
# discrimination margin demonstrated in this file (1.0, from a unit perturbation of the
# initial position). It cannot hide any error these anchors exist to catch.
FUTURE_COMPARISON_TOL = 1e-12


def _v(*components):
    """Exact rational 3-vector."""
    return tuple(Fraction(c) for c in components)


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _scale(k, a):
    return tuple(Fraction(k) * x for x in a)


# ======================================================================================
# Frozen anchor data.
#
# Plain containers, not TestCases: the values are the artifact, and keeping them out of
# a TestCase means a future acceptance test can import them without also inheriting and
# re-running the integrity checks below.
# ======================================================================================
class VEOM01ForceFreeStraightLine:
    """V-EOM-01 — force-free straight-line motion.

    DERIVATION (independent of any implementation)
    ----------------------------------------------
    With ``F_aero^B = F_prop^B = 0`` and ``g = 0`` the governing equation reduces to
    ``m vdot^I = 0``.  Mass is non-zero, so::

        vdot^I = 0            =>   v^I(t) = v0
        pdot^I = v^I          =>   p^I(t) = p0 + v0 t

    Uniform motion in a straight line.  No gravity term, no force term, and no frame
    transformation appears anywhere in the solution.
    """

    P0 = _v(12, -7, 31)          # m,      inertial
    V0 = _v(35, -11, 8)          # m/s,    inertial
    G0 = Fraction(0)             # m/s^2,  gravity switched off
    T = Fraction(4)              # s

    # Frozen oracle. Hand-derived from the closed forms above:
    #   v(4) = v0                                   = (35, -11, 8)
    #   p(4) = p0 + v0*4
    #        = (12 + 140, -7 - 44, 31 + 32)         = (152, -51, 63)
    V_EXPECTED = _v(35, -11, 8)
    P_EXPECTED = _v(152, -51, 63)


class VEOM02ConstantGravityBallistic:
    """V-EOM-02 — constant-gravity ballistic motion.

    DERIVATION (independent of any implementation)
    ----------------------------------------------
    With ``F_aero^B = F_prop^B = 0`` and ``g(h) = g0`` constant, and with +z DOWN::

        vdot^I = (0, 0, g0)
        v^I(t) = v0 + (0, 0, g0 t)
        p^I(t) = p0 + v0 t + (0, 0, g0 t^2 / 2)

    The sign of the vertical term is the point of this anchor: gravity is **+z** in NED.
    """

    P0 = _v(10, 20, 100)         # m,      inertial
    V0 = _v(40, -15, -25)        # m/s,    inertial; negative v_z means moving UPWARD
    G0 = Fraction(10)            # m/s^2,  downward, i.e. +z
    T = Fraction(3)              # s

    # Frozen oracle. Hand-derived from the closed forms above:
    #   v(3) = (40, -15, -25 + 10*3)                = (40, -15, 5)
    #   p(3) = (10 + 120, 20 - 45, 100 - 75 + 45)   = (130, -25, 70)
    #
    # See the module docstring: the brief for this phase stated p_z = 55. That is
    # arithmetically wrong; 70 is the derived value and the one frozen here.
    V_EXPECTED = _v(40, -15, 5)
    P_EXPECTED = _v(130, -25, 70)


# ======================================================================================
# Closed forms, written here once, independently of the frozen values above.
# ======================================================================================
def _closed_form_velocity(v0, g0, t):
    """v(t) = v0 + (0, 0, g0 t)."""
    return _add(v0, (Fraction(0), Fraction(0), g0 * t))


def _closed_form_position(p0, v0, g0, t):
    """p(t) = p0 + v0 t + (0, 0, g0 t^2 / 2)."""
    return _add(_add(p0, _scale(t, v0)),
                (Fraction(0), Fraction(0), g0 * t * t / 2))


class TestEomAnchorIntegrity(unittest.TestCase):
    """The frozen values satisfy the stated closed forms, in exact arithmetic.

    This is an **anchor-integrity** check, not verification of anything: there is no
    implementation, and both sides live in this file.  What it catches is a transcription
    slip between the derivation and the frozen literal — which is not hypothetical, since
    exactly such a slip was caught in the value this phase was handed (module docstring).

    Exact rational arithmetic throughout: no tolerance, no floating point.
    """

    def test_v_eom_01_frozen_values_satisfy_the_closed_form(self):
        case = VEOM01ForceFreeStraightLine
        self.assertEqual(
            _closed_form_velocity(case.V0, case.G0, case.T), case.V_EXPECTED,
            "V-EOM-01: with g = 0 the velocity must be unchanged from v0.",
        )
        self.assertEqual(
            _closed_form_position(case.P0, case.V0, case.G0, case.T), case.P_EXPECTED,
            "V-EOM-01: p(t) = p0 + v0 t.",
        )

    def test_v_eom_02_frozen_values_satisfy_the_closed_form(self):
        case = VEOM02ConstantGravityBallistic
        self.assertEqual(
            _closed_form_velocity(case.V0, case.G0, case.T), case.V_EXPECTED,
            "V-EOM-02: v(t) = v0 + (0, 0, g0 t).",
        )
        self.assertEqual(
            _closed_form_position(case.P0, case.V0, case.G0, case.T), case.P_EXPECTED,
            "V-EOM-02: p(t) = p0 + v0 t + (0, 0, g0 t^2 / 2). If this fails at p_z, "
            "check the module docstring: the value 55 given in the Phase 2F brief is "
            "arithmetically wrong and 70 is correct.",
        )

    def test_v_eom_02_vertical_sign_is_ned_not_enu(self):
        """A named, separate assertion because the sign is the whole point of V-EOM-02.

        +z is DOWN, so gravity increases v_z. The body starts with v_z = -25 (moving
        upward) and must end with v_z = +5 (moving downward) after 3 s.
        """
        case = VEOM02ConstantGravityBallistic
        self.assertLess(case.V0[2], 0, "v0_z must be negative: the body starts rising.")
        self.assertGreater(
            case.V_EXPECTED[2], 0,
            "V-EOM-02: after 3 s under +z gravity the body must be descending "
            "(v_z > 0). A negative value would mean gravity is acting upward, i.e. the "
            "frame has been read as ENU.",
        )
        self.assertEqual(
            case.V_EXPECTED[2] - case.V0[2], case.G0 * case.T,
            "V-EOM-02: the change in v_z must be exactly g0 * t.",
        )

    def test_frozen_values_are_exactly_representable_in_binary64(self):
        """Justifies FUTURE_COMPARISON_TOL: the anchors introduce no representation
        error of their own, so any discrepancy a future implementation shows is the
        implementation's."""
        for case in (VEOM01ForceFreeStraightLine, VEOM02ConstantGravityBallistic):
            for name in ("P0", "V0", "P_EXPECTED", "V_EXPECTED"):
                for component in getattr(case, name):
                    with self.subTest(case=case.__name__, field=name, value=component):
                        self.assertEqual(
                            Fraction(float(component)), component,
                            "Anchor values must be exact in binary64.",
                        )


class TestEomAnchorDiscrimination(unittest.TestCase):
    """What these anchors can and cannot detect.

    Each mutation is applied to the closed form and compared against the frozen oracle.
    Where a mutation is mathematically **invisible** to an anchor, that is asserted
    rather than glossed over: an anchor's blind spots are part of its specification, and
    an unrecorded blind spot is how a defect reaches a gate marked PASS.
    """

    CASE_1 = VEOM01ForceFreeStraightLine
    CASE_2 = VEOM02ConstantGravityBallistic

    @staticmethod
    def _sep(a, b):
        return max(abs(x - y) for x, y in zip(a, b))

    # -- 1. gravity sign reversed --------------------------------------------------
    def test_discriminates_reversed_gravity_sign(self):
        case = self.CASE_2
        p_wrong = _closed_form_position(case.P0, case.V0, -case.G0, case.T)
        v_wrong = _closed_form_velocity(case.V0, -case.G0, case.T)
        self.assertEqual(p_wrong[2], -20, "sanity: reversed gravity gives p_z = -20")
        self.assertGreaterEqual(
            self._sep(p_wrong, case.P_EXPECTED), 90,
            "V-EOM-02 must detect a reversed gravity sign (margin 90 m).",
        )
        self.assertGreaterEqual(
            self._sep(v_wrong, case.V_EXPECTED), 60,
            "V-EOM-02 must detect a reversed gravity sign in velocity (margin 60 m/s).",
        )

    def test_reversed_gravity_is_invisible_to_v_eom_01(self):
        """INVISIBLE, by construction: V-EOM-01 sets g = 0, and -0 = 0."""
        case = self.CASE_1
        self.assertEqual(
            _closed_form_position(case.P0, case.V0, -case.G0, case.T), case.P_EXPECTED,
            "V-EOM-01 cannot detect a gravity sign error; it has no gravity. Only "
            "V-EOM-02 guards the sign.",
        )

    # -- 2. NED read as ENU ---------------------------------------------------------
    def test_discriminates_ned_read_as_enu(self):
        """Reading the frame as ENU puts gravity along -z (up is +z there).

        Numerically this coincides with mutation 1, which is the honest statement: these
        anchors detect an ENU misreading *through the gravity direction only*. The
        x<->y relabelling that also distinguishes NED from ENU has no numerical
        consequence in either case, because neither has a lateral force, so a pure axis
        relabelling is invisible to both.
        """
        case = self.CASE_2
        p_enu = _closed_form_position(case.P0, case.V0, -case.G0, case.T)
        self.assertGreaterEqual(
            self._sep(p_enu, case.P_EXPECTED), 90,
            "V-EOM-02 must detect gravity applied in the ENU (upward) sense.",
        )

    # -- 3. incorrect position derivative -------------------------------------------
    def test_discriminates_incorrect_position_derivative(self):
        """Mutation: pdot = 0 instead of pdot = v, so position never advances."""
        for label, case in (("V-EOM-01", self.CASE_1), ("V-EOM-02", self.CASE_2)):
            with self.subTest(anchor=label):
                self.assertGreaterEqual(
                    self._sep(case.P0, case.P_EXPECTED), 100,
                    f"{label} must detect a position that does not integrate velocity.",
                )

    # -- 4. missing 1/2 factor -------------------------------------------------------
    def test_discriminates_missing_one_half_factor(self):
        case = self.CASE_2
        p_wrong = _add(_add(case.P0, _scale(case.T, case.V0)),
                       (Fraction(0), Fraction(0), case.G0 * case.T * case.T))
        self.assertEqual(p_wrong[2], 115, "sanity: without the 1/2 factor p_z = 115")
        self.assertGreaterEqual(
            self._sep(p_wrong, case.P_EXPECTED), 45,
            "V-EOM-02 must detect a missing 1/2 in the g t^2 term (margin 45 m).",
        )

    def test_missing_one_half_factor_is_invisible_to_v_eom_01(self):
        """INVISIBLE, by construction: with g = 0 the quadratic term is absent, so the
        factor multiplying it cannot be wrong."""
        case = self.CASE_1
        p_wrong = _add(_add(case.P0, _scale(case.T, case.V0)),
                       (Fraction(0), Fraction(0), case.G0 * case.T * case.T))
        self.assertEqual(p_wrong, case.P_EXPECTED)

    # -- 5. incorrect initial position ----------------------------------------------
    def test_discriminates_incorrect_initial_position(self):
        for label, case in (("V-EOM-01", self.CASE_1), ("V-EOM-02", self.CASE_2)):
            with self.subTest(anchor=label):
                perturbed = _add(case.P0, _v(1, 0, 0))
                p_wrong = _closed_form_position(perturbed, case.V0, case.G0, case.T)
                self.assertGreaterEqual(
                    self._sep(p_wrong, case.P_EXPECTED), 1,
                    f"{label} must detect a 1 m error in the initial position. This is "
                    "the smallest discrimination margin in this file and is what sets "
                    "the scale for FUTURE_COMPARISON_TOL.",
                )

    # -- 6. incorrect initial velocity ----------------------------------------------
    def test_discriminates_incorrect_initial_velocity(self):
        for label, case in (("V-EOM-01", self.CASE_1), ("V-EOM-02", self.CASE_2)):
            with self.subTest(anchor=label):
                perturbed = _add(case.V0, _v(0, 0, 1))
                v_wrong = _closed_form_velocity(perturbed, case.G0, case.T)
                p_wrong = _closed_form_position(case.P0, perturbed, case.G0, case.T)
                self.assertGreaterEqual(
                    self._sep(v_wrong, case.V_EXPECTED), 1,
                    f"{label} must detect a 1 m/s error in the initial velocity.",
                )
                self.assertGreaterEqual(
                    self._sep(p_wrong, case.P_EXPECTED), case.T,
                    f"{label}: the same error must move the position by v_err * t.",
                )

    # -- 7. incorrect time dependence -----------------------------------------------
    def test_discriminates_incorrect_time_dependence(self):
        """Mutation: the linear term becomes quadratic, p0 + v0 t^2."""
        for label, case in (("V-EOM-01", self.CASE_1), ("V-EOM-02", self.CASE_2)):
            with self.subTest(anchor=label):
                p_wrong = _add(_add(case.P0, _scale(case.T * case.T, case.V0)),
                               (Fraction(0), Fraction(0),
                                case.G0 * case.T * case.T / 2))
                self.assertGreaterEqual(
                    self._sep(p_wrong, case.P_EXPECTED), 100,
                    f"{label} must detect a wrong power of t in the linear term.",
                )

    # -- 8. body-frame quantities used as inertial ----------------------------------
    def test_body_inertial_confusion_is_invisible_by_construction(self):
        """INVISIBLE, and deliberately so.

        Both anchors set ``F_aero^B = F_prop^B = 0``, so the term ``T_IB (F_aero + F_prop)``
        is ``T_IB @ 0 = 0`` for **every** attitude.  There is no frame transformation
        anywhere in either solution, so no confusion between body-frame and
        inertial-frame *forces* can change the answer.

        This is the intended isolation, not an oversight: it is what lets these anchors
        localise a failure to the inertial translational equation rather than to the
        already-anchored frame transformations.  The consequence is recorded because it
        is a real limitation — **a separate anchor carrying a non-zero body force at a
        known attitude is required to guard the force-transformation path**, and it does
        not exist yet.
        """
        zero_force = (Fraction(0), Fraction(0), Fraction(0))
        # Arbitrary matrices standing in for any T_IB. Written here rather than imported,
        # so this file stays independent of radius/.
        for attitude in ([[0, 1, 0], [-1, 0, 0], [0, 0, 1]],
                         [[0, 0, -1], [-1, 0, 0], [0, 1, 0]],
                         [[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
            with self.subTest(attitude=attitude):
                transformed = tuple(
                    sum(Fraction(attitude[i][k]) * zero_force[k] for k in range(3))
                    for i in range(3)
                )
                self.assertEqual(
                    transformed, zero_force,
                    "The force term must vanish identically for any attitude.",
                )


# ======================================================================================
# V-EOM-03 — constant non-zero body force at a fixed known attitude
# ======================================================================================
#
# WHY THIS ANCHOR EXISTS
# ----------------------
# V-EOM-01 and V-EOM-02 both set the body force to zero, so the term
# ``T_IB (F_aero + F_prop)`` is ``T_IB @ 0 = 0`` for every attitude.  That isolation is
# deliberate, but it leaves the structural blind spot recorded in
# ``TestEomAnchorDiscrimination.test_body_inertial_confusion_is_invisible_by_construction``:
# **with zero applied force, an incorrect body-to-inertial force transformation cannot
# be detected.**  V-EOM-03 closes exactly that gap and nothing else.
#
# GOVERNING CASE
# --------------
#     m vdot^I = T_IB F^B          (gravity zero, propulsion zero, mass constant)
#     a^I      = (1/m) T_IB F^B    constant, so
#     v^I(t)   = v0 + a^I t
#     p^I(t)   = p0 + v0 t + a^I t^2 / 2
#
# THE ATTITUDE IS A PARAMETER OF THE TEST CASE, NOT A STATE BEING INTEGRATED.
# No quaternion, Euler angle or angular rate is propagated here, and no rotational
# equation appears.  The attitude is fixed by construction so that the force
# transformation can be exercised without depending on rotational dynamics.
# ======================================================================================


def _r_x(cos_a, sin_a):
    """Elementary passive rotation, transcribed from NOTATION_AND_CONVENTIONS.md sec 4."""
    return [[Fraction(1), Fraction(0), Fraction(0)],
            [Fraction(0), cos_a, sin_a],
            [Fraction(0), -sin_a, cos_a]]


def _r_y(cos_a, sin_a):
    return [[cos_a, Fraction(0), -sin_a],
            [Fraction(0), Fraction(1), Fraction(0)],
            [sin_a, Fraction(0), cos_a]]


def _r_z(cos_a, sin_a):
    return [[cos_a, sin_a, Fraction(0)],
            [-sin_a, cos_a, Fraction(0)],
            [Fraction(0), Fraction(0), Fraction(1)]]


def _matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)]


def _matvec(a, v):
    return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))


def _transpose(a):
    return [[a[j][i] for j in range(3)] for i in range(3)]


def _t_bi_from_euler(cph, sph, cth, sth, cps, sps):
    """T_BI = R_x(phi) R_y(theta) R_z(psi), the documented 3-2-1 composition."""
    return _matmul(_r_x(cph, sph), _matmul(_r_y(cth, sth), _r_z(cps, sps)))


def _closed_form_velocity_constant_accel(v0, accel, t):
    return tuple(v + a * t for v, a in zip(v0, accel))


def _closed_form_position_constant_accel(p0, v0, accel, t, half=Fraction(1, 2)):
    return tuple(p + v * t + half * a * t * t for p, v, a in zip(p0, v0, accel))


class VEOM03BodyForceFixedAttitude:
    """V-EOM-03 — constant body force at a fixed attitude. Frozen oracle.

    CASE SELECTION — CHOSEN BY ANALYSIS, NOT ASSUMED
    ------------------------------------------------
    Candidate cases were scored against all eleven required mutations before this one was
    fixed.  Two candidate constructions were **rejected because they silently void a
    required mutation**:

    * ``m = 1`` makes "multiply by mass instead of dividing" invisible, since 1/1 == 1*1.
      Hence ``m = 5 kg``.
    * Equal body-force components make "body-force component permutation" invisible.
      Hence three distinct, non-zero components with mixed signs.

    A third, not on the required list but avoided anyway: equal Euler angles would make an
    angle permutation invisible, so the three angles are distinct.

    ATTITUDE.  Chosen from Pythagorean triples so that **every DCM entry is an exact
    rational** — no radicals, no floating point, and the whole oracle auditable by hand:

        phi   : cos = 4/5, sin =  3/5   (+36.8699 deg)
        theta : cos = 3/5, sin =  4/5   (+53.1301 deg)
        psi   : cos = 4/5, sin = -3/5   (-36.8699 deg)

    All three differ; theta lies inside the documented [-90, +90] deg range.  The
    resulting T_BI has **no zero entries**, which matters: a zero entry is somewhere a
    mutation can hide.

        T_BI = R_x(phi) R_y(theta) R_z(psi)
             = (1/125) [[  60,  -45, -100],
                        [ 108,   44,   45],
                        [  19, -108,   60]]

        T_IB = T_BI^T
             = (1/125) [[  60,  108,   19],
                        [ -45,   44, -108],
                        [-100,   45,   60]]

    FORCE AND MASS.  ``F^B = (-375, -250, 500) N`` and ``m = 5 kg``, giving, by hand:

        125 * T_IB F^B / 125
            = (60(-3) + 108(-2) + 19(4),
               -45(-3) +  44(-2) - 108(4),
              -100(-3) +  45(-2) +  60(4))  * 125 / 125
            = (-180 - 216 + 76,  135 - 88 - 432,  300 - 90 + 240)
            = (-320, -385, 450) N

        a^I = (1/5)(-320, -385, 450) = (-64, -77, 90) m/s^2

    Three distinct non-zero acceleration components with mixed signs.  Every value in
    this anchor is an exact integer.

    NOT A VALIDATION.  This anchor verifies a translational force transformation and a
    closed-form constant-acceleration propagation.  It does not validate a 6-DOF dynamics
    implementation, an aerodynamic model, or anything physical.
    """

    # Attitude, as exact cosine/sine pairs. Degrees given only for the reader.
    COS_PHI, SIN_PHI = Fraction(4, 5), Fraction(3, 5)      # +36.8699 deg
    COS_THETA, SIN_THETA = Fraction(3, 5), Fraction(4, 5)  # +53.1301 deg
    COS_PSI, SIN_PSI = Fraction(4, 5), Fraction(-3, 5)     # -36.8699 deg

    # Hand-derived DCM, written as integers over 125 so the literal stays readable.
    _D = Fraction(1, 125)
    T_BI_EXPECTED = [[_D * 60, _D * -45, _D * -100],
                     [_D * 108, _D * 44, _D * 45],
                     [_D * 19, _D * -108, _D * 60]]
    T_IB_EXPECTED = [[_D * 60, _D * 108, _D * 19],
                     [_D * -45, _D * 44, _D * -108],
                     [_D * -100, _D * 45, _D * 60]]

    MASS = Fraction(5)                    # kg. NOT 1 -- see the class docstring.
    F_BODY = _v(-375, -250, 500)          # N, body axes; three distinct non-zero values
    A_EXPECTED = _v(-64, -77, 90)         # m/s^2, inertial

    P0 = _v(5, 15, -25)                   # m,   inertial
    V0 = _v(10, -30, 20)                  # m/s, inertial
    T = Fraction(4)                       # s

    # v(4) = v0 + 4a = (10 - 256, -30 - 308, 20 + 360)
    V_EXPECTED = _v(-246, -338, 380)
    # p(4) = p0 + 4 v0 + 8 a = (5 + 40 - 512, 15 - 120 - 616, -25 + 80 + 720)
    P_EXPECTED = _v(-467, -721, 775)


class TestVEOM03AnchorIntegrity(unittest.TestCase):
    """The frozen V-EOM-03 oracle is internally consistent, in exact arithmetic.

    The derivation chain runs strictly:

        published convention -> independently written DCM -> transformed force
                             -> acceleration -> closed-form velocity and position

    Nothing here imports ``radius``; the elementary rotations above are transcribed from
    the specification, not copied from ``radius/frames.py``.  Copying production code and
    calling it an independent oracle would defeat the purpose of the anchor.
    """

    C = VEOM03BodyForceFixedAttitude

    def test_dcm_literal_matches_the_independently_composed_product(self):
        composed = _t_bi_from_euler(self.C.COS_PHI, self.C.SIN_PHI,
                                    self.C.COS_THETA, self.C.SIN_THETA,
                                    self.C.COS_PSI, self.C.SIN_PSI)
        self.assertEqual(
            composed, self.C.T_BI_EXPECTED,
            "V-EOM-03: the frozen T_BI literal must equal R_x(phi) R_y(theta) R_z(psi) "
            "built from the documented elementary matrices.",
        )

    def test_dcm_is_exactly_orthonormal_with_unit_determinant(self):
        t_bi = self.C.T_BI_EXPECTED
        identity = [[Fraction(1 if i == j else 0) for j in range(3)] for i in range(3)]
        self.assertEqual(_matmul(t_bi, _transpose(t_bi)), identity,
                         "V-EOM-03: T_BI must be exactly orthonormal (rational).")
        det = (t_bi[0][0] * (t_bi[1][1] * t_bi[2][2] - t_bi[1][2] * t_bi[2][1])
               - t_bi[0][1] * (t_bi[1][0] * t_bi[2][2] - t_bi[1][2] * t_bi[2][0])
               + t_bi[0][2] * (t_bi[1][0] * t_bi[2][1] - t_bi[1][1] * t_bi[2][0]))
        self.assertEqual(det, 1, "V-EOM-03: det(T_BI) must be exactly +1.")

    def test_t_ib_literal_is_the_transpose_of_t_bi(self):
        self.assertEqual(self.C.T_IB_EXPECTED, _transpose(self.C.T_BI_EXPECTED),
                         "V-EOM-03: T_IB is by definition the transpose of T_BI.")

    def test_acceleration_matches_the_transformed_force_over_mass(self):
        accel = tuple(x / self.C.MASS
                      for x in _matvec(self.C.T_IB_EXPECTED, self.C.F_BODY))
        self.assertEqual(
            accel, self.C.A_EXPECTED,
            "V-EOM-03: a^I = (1/m) T_IB F^B must equal the frozen (-64, -77, 90).",
        )

    def test_velocity_and_position_match_the_closed_forms(self):
        c = self.C
        self.assertEqual(
            _closed_form_velocity_constant_accel(c.V0, c.A_EXPECTED, c.T),
            c.V_EXPECTED, "V-EOM-03: v(t) = v0 + a t.")
        self.assertEqual(
            _closed_form_position_constant_accel(c.P0, c.V0, c.A_EXPECTED, c.T),
            c.P_EXPECTED, "V-EOM-03: p(t) = p0 + v0 t + a t^2 / 2.")

    def test_v_eom_03_frozen_values_are_exactly_representable(self):
        c = self.C
        for name in ("F_BODY", "A_EXPECTED", "P0", "V0", "V_EXPECTED", "P_EXPECTED"):
            for component in getattr(c, name):
                with self.subTest(field=name, value=component):
                    self.assertEqual(Fraction(float(component)), component)

    def test_anchor_rejects_a_deliberately_incorrect_oracle(self):
        """Required integrity check: the tests above must actually be capable of failing.

        A frozen oracle that agrees with the closed form no matter what it contains would
        be worthless.  Perturbing one component of the acceleration by 1 m/s^2, or one
        component of the force by 1 N, must break the agreement.
        """
        c = self.C
        bad_accel = _add(c.A_EXPECTED, _v(1, 0, 0))
        self.assertNotEqual(
            _closed_form_velocity_constant_accel(c.V0, bad_accel, c.T), c.V_EXPECTED,
            "A wrong acceleration must not satisfy the frozen velocity oracle.")
        self.assertNotEqual(
            _closed_form_position_constant_accel(c.P0, c.V0, bad_accel, c.T),
            c.P_EXPECTED,
            "A wrong acceleration must not satisfy the frozen position oracle.")
        bad_force = _add(c.F_BODY, _v(0, 1, 0))
        self.assertNotEqual(
            tuple(x / c.MASS for x in _matvec(c.T_IB_EXPECTED, bad_force)),
            c.A_EXPECTED,
            "A wrong body force must not reproduce the frozen acceleration.")

    def test_case_construction_avoids_the_two_known_traps(self):
        """Guards the anchor's own discriminating power against a later 'tidy-up'.

        Both traps were found during case selection, and each silently voids a required
        mutation if violated.
        """
        self.assertNotEqual(
            self.C.MASS, 1,
            "V-EOM-03 requires m != 1: with m = 1, multiplying by mass and dividing by "
            "mass give identical results and that mutation becomes undetectable.")
        magnitudes = {abs(component) for component in self.C.F_BODY}
        self.assertEqual(
            len(magnitudes), 3,
            "V-EOM-03 requires three DISTINCT body-force magnitudes: with repeated "
            "components a permutation of the force is undetectable.")
        self.assertNotIn(Fraction(0), self.C.F_BODY,
                         "V-EOM-03 requires a fully non-axis-aligned body force.")
        self.assertNotIn(
            Fraction(0), [x for row in self.C.T_BI_EXPECTED for x in row],
            "V-EOM-03 requires an attitude whose DCM has no zero entries; a zero entry "
            "is somewhere a mutation can hide.")


class TestVEOM03Discrimination(unittest.TestCase):
    """What V-EOM-03 detects, with margins, against the eleven required mutations.

    Every wrong convention is built from the same independently transcribed elementary
    matrices, so each comparison is literal-against-literal rather than one
    implementation against another.
    """

    C = VEOM03BodyForceFixedAttitude

    def _observables(self, accel, p0=None, v0=None, half=Fraction(1, 2)):
        c = self.C
        p0 = c.P0 if p0 is None else p0
        v0 = c.V0 if v0 is None else v0
        return (accel,
                _closed_form_velocity_constant_accel(v0, accel, c.T),
                _closed_form_position_constant_accel(p0, v0, accel, c.T, half))

    def _assert_detected(self, label, accel, min_accel_margin):
        c = self.C
        a_w, v_w, p_w = self._observables(accel)
        margin = max(abs(x - y) for x, y in zip(a_w, c.A_EXPECTED))
        self.assertGreaterEqual(
            margin, min_accel_margin,
            f"V-EOM-03 must detect: {label} (acceleration margin {margin}).")
        self.assertNotEqual(v_w, c.V_EXPECTED, f"{label}: velocity must differ.")
        self.assertNotEqual(p_w, c.P_EXPECTED, f"{label}: position must differ.")

    def _accel_from(self, dcm, force=None, mass=None):
        c = self.C
        force = c.F_BODY if force is None else force
        mass = c.MASS if mass is None else mass
        return tuple(x / mass for x in _matvec(dcm, force))

    def test_1_and_2_t_bi_used_instead_of_t_ib_which_is_the_transpose(self):
        """Mutations 1 and 2 are the same mutation: T_IB is *defined* as T_BI
        transposed, so 'used T_BI' and 'transposed the intended DCM' are one error, not
        two.  Recorded rather than counted twice."""
        self._assert_detected("T_BI used where T_IB is required (= transpose)",
                              self._accel_from(self.C.T_BI_EXPECTED), 34)

    def test_3_reversed_euler_composition_order(self):
        c = self.C
        reversed_t_bi = _matmul(_r_z(c.COS_PSI, c.SIN_PSI),
                                _matmul(_r_y(c.COS_THETA, c.SIN_THETA),
                                        _r_x(c.COS_PHI, c.SIN_PHI)))
        self._assert_detected("reversed Euler composition R_z R_y R_x",
                              self._accel_from(_transpose(reversed_t_bi)), 90)

    def test_4_incorrect_euler_sign_convention(self):
        c = self.C
        # (a) active elementary matrices, i.e. every elementary rotation transposed.
        active = _matmul(_transpose(_r_x(c.COS_PHI, c.SIN_PHI)),
                         _matmul(_transpose(_r_y(c.COS_THETA, c.SIN_THETA)),
                                 _transpose(_r_z(c.COS_PSI, c.SIN_PSI))))
        self._assert_detected("active elementary rotations",
                              self._accel_from(_transpose(active)), 84)
        # (b) all three angles negated.
        negated = _t_bi_from_euler(c.COS_PHI, -c.SIN_PHI,
                                   c.COS_THETA, -c.SIN_THETA,
                                   c.COS_PSI, -c.SIN_PSI)
        self._assert_detected("all Euler angles negated",
                              self._accel_from(_transpose(negated)), 84)

    def test_5_body_force_components_permuted(self):
        c = self.C
        permuted = (c.F_BODY[2], c.F_BODY[0], c.F_BODY[1])
        self._assert_detected("body-force components cyclically permuted",
                              self._accel_from(c.T_IB_EXPECTED, force=permuted), 221)

    def test_6_body_force_sign_reversed(self):
        c = self.C
        negated_force = tuple(-x for x in c.F_BODY)
        self._assert_detected("body-force sign reversed",
                              self._accel_from(c.T_IB_EXPECTED, force=negated_force),
                              180)

    def test_7_multiplied_by_mass_instead_of_divided(self):
        c = self.C
        wrong = tuple(x * c.MASS for x in _matvec(c.T_IB_EXPECTED, c.F_BODY))
        self._assert_detected("multiplied by mass instead of dividing", wrong, 2160)

    def test_8_acceleration_sign_reversed(self):
        self._assert_detected("acceleration sign reversed",
                              tuple(-x for x in self.C.A_EXPECTED), 180)

    def test_9_missing_one_half_in_position_propagation(self):
        """Velocity is unaffected, so this is a position-only discriminator."""
        c = self.C
        _, v_w, p_w = self._observables(c.A_EXPECTED, half=Fraction(1))
        self.assertEqual(v_w, c.V_EXPECTED,
                         "the 1/2 factor appears only in the position term")
        margin = max(abs(x - y) for x, y in zip(p_w, c.P_EXPECTED))
        self.assertGreaterEqual(margin, 720,
                                "V-EOM-03 must detect a missing 1/2 (margin 720 m).")

    def test_10_incorrect_initial_position(self):
        c = self.C
        _, _, p_w = self._observables(c.A_EXPECTED, p0=_add(c.P0, _v(1, 0, 0)))
        self.assertEqual(max(abs(x - y) for x, y in zip(p_w, c.P_EXPECTED)), 1,
                         "V-EOM-03 must detect a 1 m initial-position error.")

    def test_11_incorrect_initial_velocity(self):
        c = self.C
        _, v_w, p_w = self._observables(c.A_EXPECTED, v0=_add(c.V0, _v(1, 0, 0)))
        self.assertEqual(max(abs(x - y) for x, y in zip(v_w, c.V_EXPECTED)), 1,
                         "V-EOM-03 must detect a 1 m/s initial-velocity error.")
        self.assertEqual(max(abs(x - y) for x, y in zip(p_w, c.P_EXPECTED)), c.T,
                         "the same error must displace position by v_err * t.")


# ======================================================================================
# V-EOM-04 — Torque-free axisymmetric coning.  The first ROTATIONAL anchor.
# ======================================================================================
#
# WHY THIS ANCHOR EXISTS
# ----------------------
# V-EOM-01..03 hold attitude fixed and contain no rotational equation, so until now the
# rotational dynamics had no verification of any kind.  V-EOM-04 anchors the gyroscopic
# term ``w x (J w)`` quantitatively, and nothing else.
#
# NOTATION AND FRAMES (ADR-0010) -- READ THIS FIRST
# -------------------------------------------------
#   J_par  (J_PARALLEL)   principal moment about the SYMMETRY axis
#   J_perp (J_PERP)       principal moment about any TRANSVERSE axis
#   w_par                 component of w along the symmetry axis
#
# The case is frozen in two forms of the same solution:
#
#   * CANONICAL PRINCIPAL FRAME P, symmetry axis z_P:  J^P = diag(J_perp, J_perp, J_par).
#     J_DIAG, OMEGA_0, OMEGA and OMEGA_DOT are components along (x_P, y_P, z_P), and
#     ``w_x, w_y, w_z`` in this section mean those components -- NOT body axes.  P is a
#     relabelling used for analysis only; it is not a simulation frame.
#   * RADIUS BODY AXES B, symmetry axis x_B (NOTATION sec 5.1):
#     J^B = diag(J_par, J_perp, J_perp) and w^B = (p, q, r).  The *_X_SYMMETRIC attributes.
#
#   P -> B:   x_P = y_B,   y_P = z_B,   z_P = x_B,   so  w^P = (q, r, p).
#
# That mapping is cyclic (determinant +1), so P is right-handed and cross products are
# preserved.  Swapping two axes instead is a reflection: it flips the cross product, and a
# test below shows it FAILS the Euler equations.  That is the handedness check.
#
# J_PARALLEL and J_PERP were named J_Z and J_T when this anchor was frozen (2026-09-10).
# ADR-0010 renamed them because "J_z" reads as J_zz, which on a RADIUS vehicle is a
# TRANSVERSE moment.  No value changed.  Because P's canonical oracle is also a legitimate
# body-frame input for a body whose symmetry axis happens to be z_B, a full-tensor
# implementation must pass both forms unchanged.
#
# GOVERNING EQUATION (RS-004 sec 4.1, ADR-0009) at constant inertia and zero moment:
#
#     J wdot + w x (J w) = 0         (skew form of NOTATION sec 5)
#
# DERIVATION -- performed here, not inherited, in frame P
# -------------------------------------------------------
# With J = diag(J_perp, J_perp, J_par), J w = (J_perp w_x, J_perp w_y, J_par w_z), and
#
#     w x (J w) = ( (J_par - J_perp) w_y w_z,  -(J_par - J_perp) w_x w_z,  0 )
#
# so the three Euler equations are
#
#     J_perp wdot_x + (J_par - J_perp) w_y w_z = 0    =>   wdot_x = -lambda w_y
#     J_perp wdot_y - (J_par - J_perp) w_x w_z = 0    =>   wdot_y = +lambda w_x
#     J_par  wdot_z                            = 0    =>   w_z = w_par is constant
#
#     lambda = ((J_par - J_perp) / J_perp) w_par      constant, because w_par is.
#
# In body axes B the same solution reads  qdot = -lambda r,  rdot = +lambda q,  w_par = p.
#
# Component solution (differentiate to check: it satisfies both transverse equations):
#
#     w_x(t) = w_x0 cos(lambda t) - w_y0 sin(lambda t)
#     w_y(t) = w_y0 cos(lambda t) + w_x0 sin(lambda t)
#
# Complex-variable cross-check.  With u = w_x + i w_y,
#     u_dot = -lambda w_y + i lambda w_x = i lambda (w_x + i w_y) = i lambda u,
# so u(t) = u0 exp(i lambda t), whose real and imaginary parts are the component solution
# above.  The two derivations agree; both are executed as tests below.
#
# WHAT lambda IS -- AND WHAT IT IS NOT
# ------------------------------------
# "Coning rate" is used for at least three different quantities.  This file keeps them
# apart:
#
#   lambda  = ((J_par-J_perp)/J_perp) w_par   the rate at which the transverse angular-
#                                     velocity vector rotates RELATIVE TO THE BODY, signed
#                                     by the right-hand rule about the POSITIVE SYMMETRY
#                                     AXIS (+z_P here: from +x_P toward +y_P; on a RADIUS
#                                     vehicle +x_B: from +y_B toward +z_B).  THIS is what
#                                     V-EOM-04 verifies.
#   sigma   = -lambda                 the rate at which the BODY rotates relative to the
#                                     plane containing H and the symmetry axis.  Same
#                                     magnitude, opposite sign: a "sign disagreement"
#                                     between two statements can be nothing more than this
#                                     change of reference.
#   |H|/J_perp                        the rate at which the symmetry axis precesses about
#                                     the inertially fixed angular momentum H, seen from
#                                     INERTIAL space.  A different magnitude.  Not
#                                     observable without attitude propagation, and NOT
#                                     verified here.
#
# They are linked by the exact decomposition  w = H/J_perp + sigma * (unit symmetry axis),
# tested below.
#
# HISTORY -- THE FORMULA AND THE AXIS AS FIRST SPECIFIED
# ------------------------------------------------------
# Before ADR-0010, RS-004 sec 7 wrote this case as J_x = J_y = J_t != J_z with
# lambda = ((J_z - J_t)/J_t) w_z, i.e. symmetry about z.  Building this anchor found that
# formula CORRECT in magnitude and sign for the body-frame rate, but incomplete: no sign
# reference, not distinguished from the inertial rate, and tied to a symmetry axis of z.
# It also found that NOTATION sec 3 puts x_B, not z_B, along the vehicle's longitudinal
# axis.  ADR-0010 resolved both: the physical symmetry axis is x_B, and the z-symmetric
# form is the canonical frame P.  Both forms were frozen from the start; only their names
# and this commentary changed.
#
# SCOPE.  This is an angular-velocity anchor only.  No quaternion, attitude, integrator or
# time-stepping appears.  It does not verify attitude propagation, numerical integration,
# translational dynamics, or a complete rigid-body simulation.
#
# TOLERANCE.  FUTURE_COMPARISON_TOL above was justified for CLOSED-FORM translational
# propagation and does NOT transfer to this anchor.  A rotational implementation must
# integrate numerically, so its comparison tolerance has to come from a measured
# convergence study (RS-005, V-NUM-01) in the phase that builds it.  No number is set here.
# ======================================================================================

def _skew_cross(w, b):
    """``w x b`` computed as ``[w x] b``, with ``[w x]`` transcribed from NOTATION sec 5."""
    p, q, r = w
    skew = [[0, -r, q],
            [r, 0, -p],
            [-q, p, 0]]
    return _matvec(skew, b)


def _diag_times(j_diag, w):
    """``J w`` for a diagonal inertia tensor given as its three principal moments."""
    return tuple(j * x for j, x in zip(j_diag, w))


def _torque_free_residual(j_diag, w, w_dot):
    """``J wdot + w x (J w)`` -- identically zero on any torque-free trajectory."""
    return _add(_diag_times(j_diag, w_dot), _skew_cross(w, _diag_times(j_diag, w)))


def _cmul(a, b):
    """Exact complex product; a complex number is a ``(real, imag)`` pair of Fractions."""
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _cpow_unit(z, n):
    """``z**n`` for ``|z| = 1`` and integer ``n``; a negative power uses the conjugate."""
    if n < 0:
        z, n = (z[0], -z[1]), -n
    out = (Fraction(1), Fraction(0))
    for _ in range(n):
        out = _cmul(out, z)
    return out


# (cos, sin) of 0, pi/2, pi, 3 pi/2 -- the only exact points needed besides atan(3/4).
_QUARTER_TURNS = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)),
                  (Fraction(-1), Fraction(0)), (Fraction(0), Fraction(-1)))


def _closed_form_transverse(w_x0, w_y0, cos_sin):
    """``(w_x, w_y)`` at the phase ``lambda t`` whose exact cosine and sine are given."""
    cos_p, sin_p = cos_sin
    return (w_x0 * cos_p - w_y0 * sin_p, w_y0 * cos_p + w_x0 * sin_p)


class VEOM04TorqueFreeAxisymmetricConing:
    """V-EOM-04 — torque-free axisymmetric coning. Frozen oracle.

    FRAMES.  J_DIAG, OMEGA_0, OMEGA and OMEGA_DOT are components in the canonical
    principal frame P (symmetry axis z_P; ADR-0010).  The *_X_SYMMETRIC attributes are the
    same case in RADIUS body axes, symmetry axis x_B.

    CASE SELECTION — CHOSEN BY ANALYSIS, NOT ASSUMED
    ------------------------------------------------
    Ten candidate constructions were scored, in exact arithmetic, against 26 mutations
    before this one was fixed.  Each rejected construction silently voids at least one:

    * ``J_par = J_perp`` (spherical): lambda = 0; eleven mutations become invisible, including
      the sign reversal and frozen transverse components.
    * ``w_x0 = w_y0 = 0``: every transverse mutation becomes invisible (21 of 26).
    * ``J_par/J_perp = 1/2``: ``(J_par/J_perp - 1) = -(J_par/J_perp)``, so the wrong formula
      ``-(J_par/J_perp) w_z`` -- a sign-slipped small-nutation INERTIAL precession rate --
      reproduces lambda exactly.  Of the three rates above, that confusion is the one most
      worth catching.
    * ``J_par/J_perp = 2``: ``(J_par - J_perp)/J_perp = 1``, so omitting the ratio is invisible.
    * ``J_perp = 1``: omitting the division by ``J_perp`` is invisible.
    * ``w_z = 1``: omitting ``w_z`` from lambda is invisible.
    * ``w_x0 = 0``: a symmetrically (wrongly) coupled solution is invisible.
    * ``w_x0 = w_y0``: swapping the transverse components is invisible at t = 0.

    Hence a prolate body (J_par < J_perp, as a slender vehicle is) with ``J_par/J_perp = 1/3``,
    neither moment equal to 1, ``w_z = 3``, and transverse components that are non-zero,
    unequal in magnitude and of opposite sign.

        J_perp = 6 kg m^2,  J_par = 2 kg m^2,  w0 = (2, -5, 3) rad/s
        lambda = ((2 - 6)/6)(3) = -2 rad/s

    lambda < 0: for a prolate body spinning positively, the transverse rate REGRESSES,
    rotating clockwise about +z_P (about +x_B in body axes) as seen relative to the body.

    SAMPLE TIMES — WHY FOUR, AND WHY ONE IS NOT A MULTIPLE OF PI
    -------------------------------------------------------------
    For |lambda| = 2 rad/s the sample times are ``0, pi/4, pi/2, atan(3/4)`` s, giving
    ``lambda t = 0, -pi/2, -pi, -2 atan(3/4)``, all with exact cosine and sine.

    Quarter- and half-cycle samples alone are NOT enough.  A rate ``lambda' = -3 lambda``
    lands on the same point as ``lambda`` at every multiple of pi/2, and that is exactly
    the mutation ``(J_perp - J_par)/J_par w_z`` (both numerator and denominator wrong).  The
    half-cycle sample is also blind to a plain sign reversal, since exp(i pi) =
    exp(-i pi).  ``atan(3/4)`` is incommensurate with pi, so no integer multiple of lambda
    other than lambda itself reaches the same point there.  The last phase is exact by the
    double-angle identities from tan = 3/4:

        cos(2a) = (1 - 9/16)/(1 + 9/16) = 7/25,   sin(2a) = (3/2)/(25/16) = 24/25

    and with lambda < 0 the frozen (cos, sin) of lambda t is (7/25, -24/25).

    FROZEN VALUES, BY HAND
    ----------------------
        t = 0         : w = ( 2, -5, 3)
        t = pi/4      : (cos, sin) = (0, -1)  ->  w = (0 - 5,  0 - 2, 3) = (-5, -2, 3)
        t = pi/2      : (cos, sin) = (-1, 0)  ->  w = (-2, 5, 3)
        t = atan(3/4) : w_x = 2(7/25) - (-5)(-24/25) = (14 - 120)/25 = -106/25
                        w_y = -5(7/25) + 2(-24/25)   = (-35 - 48)/25 = -83/25
                        w   = (-106/25, -83/25, 3)

        wdot = (-lambda w_y, lambda w_x, 0) = (2 w_y, -2 w_x, 0) at every sample.

    Invariants at every sample: |w_t|^2 = 29, |H|^2 = 1080, 2T = w.Jw = 192.
    (|H|/J_perp)^2 = 30, which is NOT lambda^2 = 4: the inertial precession rate and the
    body-frame transverse rate genuinely differ for this case, so confusing them is caught.

    Units: rad/s, rad/s^2, kg m^2.  A verification case, not a vehicle: the nutation is
    large (|w_t| > w_z) because that maximises the transverse discrimination margins.
    """

    J_PERP = Fraction(6)                # kg m^2, transverse moment (about x_P and y_P)
    J_PARALLEL = Fraction(2)            # kg m^2, symmetry axis z_P; NOT J_perp/2, NOT 2 J_perp
    J_DIAG = (J_PERP, J_PERP, J_PARALLEL)       # frame P
    OMEGA_0 = _v(2, -5, 3)              # rad/s, frame P; w_par = w_z != 1
    LAMBDA = Fraction(-2)               # rad/s = ((J_par - J_perp)/J_perp) w_par

    # Sample times in seconds, symbolic: exact phases exist; exact times do not.
    SAMPLE_TIMES_S = ("0", "pi/4", "pi/2", "atan(3/4)")
    # Exact (cos, sin) of lambda*t at each sample.
    COS_SIN = ((Fraction(1), Fraction(0)),
               (Fraction(0), Fraction(-1)),
               (Fraction(-1), Fraction(0)),
               (Fraction(7, 25), Fraction(-24, 25)))
    OMEGA = (_v(2, -5, 3),
             _v(-5, -2, 3),
             _v(-2, 5, 3),
             (Fraction(-106, 25), Fraction(-83, 25), Fraction(3)))
    OMEGA_DOT = (_v(-10, -4, 0),
                 _v(-4, 10, 0),
                 _v(10, 4, 0),
                 (Fraction(-166, 25), Fraction(212, 25), Fraction(0)))

    TRANSVERSE_RATE_SQ = Fraction(29)            # (rad/s)^2
    ANGULAR_MOMENTUM_SQ = Fraction(1080)         # (kg m^2 rad/s)^2
    TWICE_KINETIC_ENERGY = Fraction(192)         # kg m^2 (rad/s)^2
    INERTIAL_PRECESSION_RATE_SQ = Fraction(30)   # (|H|/J_perp)^2 -- NOT lambda^2

    # RADIUS body axes (NOTATION sec 5.1): symmetry axis x_B, J_xx = J_par, J_yy = J_zz = J_perp.
    # P -> B: x_P = y_B, y_P = z_B, z_P = x_B, so (p, q, r) = (w_zP, w_xP, w_yP).
    J_DIAG_X_SYMMETRIC = (J_PARALLEL, J_PERP, J_PERP)
    OMEGA_X_SYMMETRIC = (_v(3, 2, -5),
                         _v(3, -5, -2),
                         _v(3, -2, 5),
                         (Fraction(3), Fraction(-106, 25), Fraction(-83, 25)))
    OMEGA_DOT_X_SYMMETRIC = (_v(0, -10, -4),
                             _v(0, -4, 10),
                             _v(0, 10, 4),
                             (Fraction(0), Fraction(-166, 25), Fraction(212, 25)))


class TestVEOM04AnchorIntegrity(unittest.TestCase):
    """The frozen V-EOM-04 oracle is internally consistent, in exact arithmetic.

    The derivation chain runs strictly:

        project convention -> independently expanded Euler equations
                           -> independently solved closed form -> frozen values

    Nothing here imports ``radius``, and there is no production rotational-dynamics code
    to import.  Every test name carries ``v_eom_04`` so none can shadow another.
    """

    C = VEOM04TorqueFreeAxisymmetricConing

    def test_v_eom_04_gyroscopic_term_expands_to_the_derived_components(self):
        """Derivation step 1, executed: w x (J w) for J = diag(J_perp, J_perp, J_par)."""
        c = self.C
        probes = list(c.OMEGA) + [_v(7, 11, -13),
                                  (Fraction(1, 3), Fraction(-2, 7), Fraction(5, 2))]
        for j_perp, j_par in ((c.J_PERP, c.J_PARALLEL), (Fraction(9, 2), Fraction(11, 3))):
            for w in probes:
                with self.subTest(j_perp=j_perp, j_par=j_par, omega=w):
                    self.assertEqual(
                        _skew_cross(w, _diag_times((j_perp, j_perp, j_par), w)),
                        ((j_par - j_perp) * w[1] * w[2], -(j_par - j_perp) * w[0] * w[2], 0),
                        "V-EOM-04: the gyroscopic term must expand to "
                        "((J_par-J_perp) w_y w_z, -(J_par-J_perp) w_x w_z, 0).")

    def test_v_eom_04_lambda_literal_follows_from_inertia_and_spin(self):
        c = self.C
        self.assertEqual((c.J_PARALLEL - c.J_PERP) / c.J_PERP * c.OMEGA_0[2], c.LAMBDA,
                         "V-EOM-04: lambda = ((J_par - J_perp)/J_perp) w_z must equal -2 rad/s.")
        self.assertEqual(c.OMEGA[0], c.OMEGA_0)

    def test_v_eom_04_sample_phases_are_exact(self):
        """|lambda| t = 0, pi/2, pi, 2 atan(3/4) for |lambda| = 2; lambda < 0 negates sin.

        The last phase is built from its half-angle tangent, 3/4, by exact identities, so
        the symbolic time ``atan(3/4)`` and the frozen cosine and sine cannot drift apart
        (``atan(4/3)`` would give (-7/25, 24/25) instead).
        """
        c = self.C
        self.assertEqual(abs(c.LAMBDA), 2, "sample times are defined for |lambda| = 2")
        tau = Fraction(3, 4)
        double_angle = ((1 - tau * tau) / (1 + tau * tau), 2 * tau / (1 + tau * tau))
        magnitude_phases = (_QUARTER_TURNS[0], _QUARTER_TURNS[1], _QUARTER_TURNS[2],
                            double_angle)
        sign = -1 if c.LAMBDA < 0 else 1
        for k, (cos_p, sin_p) in enumerate(magnitude_phases):
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(c.COS_SIN[k], (cos_p, sign * sin_p))
                self.assertEqual(c.COS_SIN[k][0] ** 2 + c.COS_SIN[k][1] ** 2, 1)

    def test_v_eom_04_component_closed_form_reproduces_every_frozen_sample(self):
        c = self.C
        for k in range(4):
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                w_x, w_y = _closed_form_transverse(c.OMEGA_0[0], c.OMEGA_0[1], c.COS_SIN[k])
                self.assertEqual(c.OMEGA[k], (w_x, w_y, c.OMEGA_0[2]))

    def test_v_eom_04_complex_variable_solution_agrees_with_components(self):
        """u = w_x + i w_y: u(t) = u0 exp(i lambda t) and u_dot = i lambda u."""
        c = self.C
        u0 = (c.OMEGA_0[0], c.OMEGA_0[1])
        for k in range(4):
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                u = _cmul(u0, c.COS_SIN[k])
                self.assertEqual(u, c.OMEGA[k][:2],
                                 "V-EOM-04: u0 exp(i lambda t) must match the samples.")
                self.assertEqual(_cmul((Fraction(0), c.LAMBDA), u), c.OMEGA_DOT[k][:2],
                                 "V-EOM-04: u_dot must equal i lambda u.")

    def test_v_eom_04_omega_z_is_constant_at_every_sample(self):
        c = self.C
        for k in range(4):
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(c.OMEGA[k][2], c.OMEGA_0[2])
                self.assertEqual(c.OMEGA_DOT[k][2], 0)

    def test_v_eom_04_transverse_magnitude_is_constant_at_every_sample(self):
        c = self.C
        for k in range(4):
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(c.OMEGA[k][0] ** 2 + c.OMEGA[k][1] ** 2,
                                 c.TRANSVERSE_RATE_SQ)

    def test_v_eom_04_frozen_rates_satisfy_the_torque_free_euler_equations(self):
        c = self.C
        for k in range(4):
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(
                    _torque_free_residual(c.J_DIAG, c.OMEGA[k], c.OMEGA_DOT[k]), (0, 0, 0),
                    "V-EOM-04: J wdot + w x (J w) must vanish exactly.")

    def test_v_eom_04_frozen_rate_derivatives_are_the_derivative_of_the_closed_form(self):
        """d/dt of the closed form, taken by hand, against the frozen wdot literals."""
        c = self.C
        w_x0, w_y0, _ = c.OMEGA_0
        for k in range(4):
            cos_p, sin_p = c.COS_SIN[k]
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(
                    c.OMEGA_DOT[k],
                    (c.LAMBDA * (-w_x0 * sin_p - w_y0 * cos_p),
                     c.LAMBDA * (-w_y0 * sin_p + w_x0 * cos_p), 0))
                self.assertEqual(c.OMEGA_DOT[k],
                                 (-c.LAMBDA * c.OMEGA[k][1], c.LAMBDA * c.OMEGA[k][0], 0))

    def test_v_eom_04_transverse_rate_regresses_relative_to_the_body(self):
        """Rotation sense, as a sign: z-component of w_t(0) x w_t(pi/4).

        It equals sin(lambda t) |w_t|^2 = -29 < 0, i.e. rotation about -z_P (-x_B in body
        axes) relative to the body.  A prolate body (J_par < J_perp) with w_z > 0 must regress.
        """
        c = self.C
        w0, w1 = c.OMEGA[0], c.OMEGA[1]
        z_cross = w0[0] * w1[1] - w0[1] * w1[0]
        self.assertEqual(z_cross, c.COS_SIN[1][1] * c.TRANSVERSE_RATE_SQ)
        self.assertEqual(z_cross, -29)
        self.assertLess(c.J_PARALLEL, c.J_PERP)
        self.assertGreater(c.OMEGA_0[2], 0)

    def test_v_eom_04_angular_momentum_magnitude_and_kinetic_energy_are_conserved(self):
        c = self.C
        for k in range(4):
            h = _diag_times(c.J_DIAG, c.OMEGA[k])
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(sum(x * x for x in h), c.ANGULAR_MOMENTUM_SQ)
                self.assertEqual(sum(w * x for w, x in zip(c.OMEGA[k], h)),
                                 c.TWICE_KINETIC_ENERGY)

    def test_v_eom_04_body_rate_splits_into_inertial_precession_and_relative_spin(self):
        """w = H/J_perp + sigma zhat_P with sigma = -lambda: the three rates, kept apart."""
        c = self.C
        sigma = -c.LAMBDA
        for k in range(4):
            h = _diag_times(c.J_DIAG, c.OMEGA[k])
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(c.OMEGA[k],
                                 _add(_scale(Fraction(1) / c.J_PERP, h), (0, 0, sigma)))
        self.assertEqual(c.ANGULAR_MOMENTUM_SQ / c.J_PERP ** 2, c.INERTIAL_PRECESSION_RATE_SQ)
        self.assertNotEqual(c.INERTIAL_PRECESSION_RATE_SQ, c.LAMBDA ** 2,
                            "the inertial precession rate must differ from |lambda| here")

    def test_v_eom_04_x_body_symmetric_form_is_the_cyclic_relabelling(self):
        """RADIUS vehicles are symmetric about x_B (ADR-0010).  The cyclic relabelling P -> B
        is a proper rotation, so it must carry the solution to a solution with the SAME
        lambda."""
        c = self.C
        for k in range(4):
            w, w_dot = c.OMEGA[k], c.OMEGA_DOT[k]
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertEqual(c.OMEGA_X_SYMMETRIC[k], (w[2], w[0], w[1]))
                self.assertEqual(c.OMEGA_DOT_X_SYMMETRIC[k], (w_dot[2], w_dot[0], w_dot[1]))
                self.assertEqual(
                    _torque_free_residual(c.J_DIAG_X_SYMMETRIC, c.OMEGA_X_SYMMETRIC[k],
                                          c.OMEGA_DOT_X_SYMMETRIC[k]), (0, 0, 0))
        j_axial, j_perp = c.J_DIAG_X_SYMMETRIC[0], c.J_DIAG_X_SYMMETRIC[1]
        self.assertEqual((j_axial - j_perp) / j_perp * c.OMEGA_X_SYMMETRIC[0][0], c.LAMBDA)

    def test_v_eom_04_anchor_rejects_a_deliberately_incorrect_oracle(self):
        """Required integrity check: the oracle tests must be capable of failing."""
        c = self.C
        wrong_quarter = _v(5, 2, 3)          # the value a reversed coning sign gives
        w_x, w_y = _closed_form_transverse(c.OMEGA_0[0], c.OMEGA_0[1], c.COS_SIN[1])
        self.assertNotEqual((w_x, w_y, c.OMEGA_0[2]), wrong_quarter)
        self.assertNotEqual(
            _torque_free_residual(c.J_DIAG, c.OMEGA[1], _scale(-1, c.OMEGA_DOT[1])),
            (0, 0, 0), "a sign-reversed wdot must not satisfy the Euler equations")
        self.assertNotEqual((c.J_PARALLEL - c.J_PERP) / c.J_PERP * c.OMEGA_0[2], -c.LAMBDA)
        self.assertNotEqual(
            c.OMEGA[3][0] ** 2 + c.OMEGA[3][1] ** 2 + Fraction(1, 25),
            c.TRANSVERSE_RATE_SQ)

    def test_v_eom_04_case_construction_avoids_the_known_traps(self):
        """Guards the anchor's discriminating power against a later 'tidy-up'."""
        c = self.C
        w_x0, w_y0, w_z = c.OMEGA_0
        self.assertNotEqual(c.J_PARALLEL, c.J_PERP, "spherical body: lambda = 0")
        self.assertNotEqual(c.LAMBDA, 0)
        self.assertNotEqual(w_x0, 0, "w_x0 = 0 hides a symmetric-coupling error")
        self.assertNotEqual(w_y0, 0, "zero transverse rate hides every transverse error")
        self.assertNotEqual(abs(w_x0), abs(w_y0), "equal components hide a swap at t = 0")
        self.assertNotEqual(c.J_PERP, 1, "J_perp = 1 hides a missing division by J_perp")
        self.assertNotIn(w_z, (0, 1, -1), "w_z = 1 hides a missing w_z factor")
        self.assertNotIn(c.J_PARALLEL / c.J_PERP, (Fraction(1, 2), Fraction(2)),
                         "J_par/J_perp = 1/2 or 2 makes a wrong formula coincide with lambda")
        for k in range(4):
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                self.assertNotIn(0, c.OMEGA[k][:2],
                                 "a zero component is somewhere a mutation can hide")

    def test_v_eom_04_rejected_constructions_really_void_a_mutation(self):
        """Each rejected construction, demonstrated rather than asserted."""
        def lam(j_perp, j_par, w_z):
            return (j_par - j_perp) / j_perp * w_z

        F = Fraction
        self.assertEqual(-(F(3) / F(6)) * F(4), lam(F(6), F(3), F(4)),
                         "J_par/J_perp = 1/2: -(J_par/J_perp) w_z coincides with lambda")
        self.assertEqual(F(-2), lam(F(3), F(6), F(-2)),
                         "J_par/J_perp = 2: w_z alone coincides with lambda")
        self.assertEqual((F(1, 3) - F(1)) * F(3), lam(F(1), F(1, 3), F(3)),
                         "J_perp = 1: omitting the division by J_perp is invisible")
        self.assertEqual((F(6) - F(2)) / F(2), lam(F(2), F(6), F(1)),
                         "w_z = 1: omitting w_z is invisible")
        w_y0 = F(-5)
        for cos_p, sin_p in self.C.COS_SIN:
            true = _closed_form_transverse(F(0), w_y0, (cos_p, sin_p))
            symmetric = (F(0) * cos_p - w_y0 * sin_p, w_y0 * cos_p - F(0) * sin_p)
            self.assertEqual(true, symmetric,
                             "w_x0 = 0: a symmetrically coupled solution is invisible")
        # ...and none of them coincide for the case actually frozen.
        c = self.C
        j_perp, j_par, w_z = c.J_PERP, c.J_PARALLEL, c.OMEGA_0[2]
        for wrong in (-(j_par / j_perp) * w_z, w_z, (j_par - j_perp) * w_z, (j_par - j_perp) / j_perp):
            self.assertNotEqual(wrong, c.LAMBDA)


class TestVEOM04Discrimination(unittest.TestCase):
    """What V-EOM-04 detects, with exact margins, against mutations A-J and more.

    A mutated rate ``lambda'`` is evaluated EXACTLY at a sample only when its phase is an
    exactly representable point; elsewhere the helper returns ``None`` and the test relies
    on the derivative at t = 0, which is always exact and separates any lambda' != lambda.
    No floating point is used anywhere in this class.
    """

    C = VEOM04TorqueFreeAxisymmetricConing

    @staticmethod
    def _phase(multiple, k):
        """Exact (cos, sin) of ``multiple * lambda * t_k``, or None if not exact.

        ``lambda t_k = 0, -pi/2, -pi, -2 alpha`` with ``alpha = atan(3/4)``.
        """
        m = Fraction(multiple)
        if k == 0:
            return _QUARTER_TURNS[0]
        if k == 1:
            return _QUARTER_TURNS[int(-m) % 4] if m.denominator == 1 else None
        if (2 * m).denominator != 1:
            return None
        if k == 2:
            return _QUARTER_TURNS[int(-2 * m) % 4]
        return _cpow_unit((Fraction(4, 5), Fraction(-3, 5)), int(2 * m))

    def _rate_model(self, rate, w0=None):
        """Samples of the solution rotating at ``rate`` from ``w0`` (None = not exact)."""
        c = self.C
        w0 = c.OMEGA_0 if w0 is None else w0
        samples = []
        for k in range(4):
            cos_sin = self._phase(Fraction(rate) / c.LAMBDA, k)
            samples.append(None if cos_sin is None else
                           _closed_form_transverse(w0[0], w0[1], cos_sin) + (w0[2],))
        return samples

    def _margins(self, samples):
        """Max-norm distance from the frozen oracle at each sample (None = not exact)."""
        return [None if s is None else max(abs(x - y) for x, y in zip(s, self.C.OMEGA[k]))
                for k, s in enumerate(samples)]

    def _rate_derivative_margin(self, rate, w0=None):
        c = self.C
        w0 = c.OMEGA_0 if w0 is None else w0
        wrong = (-rate * w0[1], rate * w0[0], 0)
        return max(abs(x - y) for x, y in zip(wrong, c.OMEGA_DOT[0]))

    def test_v_eom_04_discrimination_harness_reproduces_the_frozen_oracle(self):
        """A harness that reports margins for everything would prove nothing."""
        c = self.C
        self.assertEqual(self._rate_model(c.LAMBDA), list(c.OMEGA))
        self.assertEqual(self._margins(self._rate_model(c.LAMBDA)), [0, 0, 0, 0])
        self.assertEqual(self._rate_derivative_margin(c.LAMBDA), 0)

    def test_v_eom_04_mutation_a_reversed_coning_sign(self):
        """Detected at pi/4 and atan(3/4). BLIND SPOT: the half-cycle sample cannot see
        it, because exp(i pi) = exp(-i pi); t = 0 trivially cannot either."""
        c = self.C
        self.assertEqual(self._margins(self._rate_model(-c.LAMBDA)),
                         [0, 10, 0, Fraction(48, 5)])
        self.assertEqual(self._rate_derivative_margin(-c.LAMBDA), 20)

    def test_v_eom_04_mutation_b_wrong_inertia_ratio(self):
        c = self.C
        j_perp, j_par, w_z = c.J_PERP, c.J_PARALLEL, c.OMEGA_0[2]
        # (J_perp - J_par)/J_perp: numerator reversed.  Numerically identical to mutation A.
        self.assertEqual((j_perp - j_par) / j_perp * w_z, -c.LAMBDA)
        # (J_par - J_perp)/J_par: wrong denominator, lambda' = 3 lambda.
        rate = (j_par - j_perp) / j_par * w_z
        self.assertEqual(self._margins(self._rate_model(rate)),
                         [0, 10, 0, Fraction(131232, 15625)])
        self.assertEqual(self._rate_derivative_margin(rate), 20)
        # (J_perp - J_par)/J_par: both wrong, lambda' = -3 lambda.  ALIASED: invisible at the
        # quarter AND half cycle; only atan(3/4) and the derivative catch it.
        rate = (j_perp - j_par) / j_par * w_z
        self.assertEqual(rate, -3 * c.LAMBDA)
        self.assertEqual(self._margins(self._rate_model(rate)),
                         [0, 0, 0, Fraction(90048, 15625)])
        self.assertEqual(self._rate_derivative_margin(rate), 40)
        # (J_par + J_perp)/J_perp: sign slip inside the difference.
        rate = (j_par + j_perp) / j_perp * w_z
        self.assertEqual(self._margins(self._rate_model(rate)),
                         [0, 7, 10, Fraction(5382, 625)])
        self.assertEqual(self._rate_derivative_margin(rate), 30)

    def test_v_eom_04_mutation_b_inertial_precession_rate_used_as_body_rate(self):
        c = self.C
        j_perp, j_par, w_z = c.J_PERP, c.J_PARALLEL, c.OMEGA_0[2]
        # Small-nutation inertial precession (J_par/J_perp) w_z, with either sign.
        self.assertEqual(self._margins(self._rate_model(j_par / j_perp * w_z)),
                         [0, None, 7, Fraction(221, 25)])
        self.assertEqual(self._rate_derivative_margin(j_par / j_perp * w_z), 15)
        self.assertEqual(self._margins(self._rate_model(-j_par / j_perp * w_z)),
                         [0, None, 7, Fraction(71, 25)])
        self.assertEqual(self._rate_derivative_margin(-j_par / j_perp * w_z), 5)
        # Exact inertial precession |H|/J_perp = sqrt(30) is irrational: compare |wdot(0)|^2
        # exactly, rate^2 |w_t|^2 = 30 * 29 against the frozen 116.
        self.assertEqual(c.INERTIAL_PRECESSION_RATE_SQ * c.TRANSVERSE_RATE_SQ, 870)
        self.assertEqual(sum(x * x for x in c.OMEGA_DOT[0]), 116)

    def test_v_eom_04_mutation_b_missing_factor(self):
        c = self.C
        j_perp, j_par, w_z = c.J_PERP, c.J_PARALLEL, c.OMEGA_0[2]
        # Ratio omitted: lambda' = w_z.
        self.assertEqual(self._margins(self._rate_model(w_z)),
                         [0, None, 7, Fraction(1027, 125)])
        self.assertEqual(self._rate_derivative_margin(w_z), 25)
        # Division by J_perp omitted: lambda' = (J_par - J_perp) w_z = 6 lambda.
        rate = (j_par - j_perp) * w_z
        self.assertEqual(self._margins(self._rate_model(rate)),
                         [0, 7, 10, Fraction(165884358, 244140625)])
        self.assertEqual(self._rate_derivative_margin(rate), 50)
        # w_z omitted: lambda' = -2/3.  No sample phase is exact; the derivative is.
        rate = (j_par - j_perp) / j_perp
        self.assertEqual(self._margins(self._rate_model(rate)), [0, None, None, None])
        self.assertEqual(self._rate_derivative_margin(rate), Fraction(20, 3))

    def test_v_eom_04_mutation_c_frozen_transverse_components(self):
        self.assertEqual(self._margins(self._rate_model(0)), [0, 7, 10, Fraction(156, 25)])
        self.assertEqual(self._rate_derivative_margin(0), 10)

    def test_v_eom_04_mutation_d_swapped_transverse_components(self):
        c = self.C
        swapped = [(w[1], w[0], w[2]) for w in c.OMEGA]
        self.assertEqual(self._margins(swapped), [7, 3, 7, Fraction(23, 25)])

    def test_v_eom_04_mutation_e_one_transverse_sign_reversed(self):
        c = self.C
        self.assertEqual(self._margins([(-w[0], w[1], w[2]) for w in c.OMEGA]),
                         [4, 10, 4, Fraction(212, 25)])
        self.assertEqual(self._margins([(w[0], -w[1], w[2]) for w in c.OMEGA]),
                         [10, 4, 10, Fraction(166, 25)])

    def test_v_eom_04_mutation_f_incorrect_omega_z_evolution(self):
        c = self.C
        w_x0, w_y0, w_z = c.OMEGA_0
        # w_z perturbed by 1 rad/s in the output only.
        self.assertEqual(self._margins([(w[0], w[1], w[2] + 1) for w in c.OMEGA]),
                         [1, 1, 1, 1])
        # w_z0 perturbed and propagated consistently into lambda (lambda' = -8/3).
        w0_bad = (w_x0, w_y0, w_z + 1)
        rate = (c.J_PARALLEL - c.J_PERP) / c.J_PERP * w0_bad[2]
        self.assertEqual(self._margins(self._rate_model(rate, w0_bad)), [1, None, None, None])
        self.assertEqual(self._rate_derivative_margin(rate, w0_bad), Fraction(10, 3))
        # w_z made to oscillate like a transverse component.
        self.assertEqual(
            self._margins([(w[0], w[1], w_z * cs[0]) for w, cs in zip(c.OMEGA, c.COS_SIN)]),
            [0, 3, 6, Fraction(54, 25)])
        # Wrong symmetry axis: J = diag(J_par, J_perp, J_perp) applied to this z-symmetric case.
        j_wrong = (c.J_PARALLEL, c.J_PERP, c.J_PERP)
        gyro = _skew_cross(c.OMEGA_0, _diag_times(j_wrong, c.OMEGA_0))
        w_dot_wrong = tuple(-g / j for g, j in zip(gyro, j_wrong))
        self.assertEqual(w_dot_wrong, (0, 4, Fraction(20, 3)))
        self.assertNotEqual(w_dot_wrong[2], 0, "the wrong axis makes w_z evolve")
        self.assertNotEqual(_torque_free_residual(j_wrong, c.OMEGA_0, c.OMEGA_DOT[0]),
                            (0, 0, 0))

    def test_v_eom_04_mutation_g_incorrect_initial_angular_velocity(self):
        c = self.C
        w_x0, w_y0, w_z = c.OMEGA_0
        for w0_bad in ((w_x0 + 1, w_y0, w_z), (w_x0, w_y0 + 1, w_z)):
            with self.subTest(w0=w0_bad):
                self.assertEqual(self._margins(self._rate_model(c.LAMBDA, w0_bad)),
                                 [1, 1, 1, Fraction(24, 25)])
                self.assertEqual(self._rate_derivative_margin(c.LAMBDA, w0_bad), 2)

    def test_v_eom_04_mutation_h_incorrect_time_dependence(self):
        c = self.C
        w_x0, w_y0, w_z = c.OMEGA_0
        # Phase lambda t / 2.  (Numerically the same function as -(J_par/J_perp) w_z here.)
        self.assertEqual(self._margins(self._rate_model(c.LAMBDA / 2)),
                         [0, None, 7, Fraction(71, 25)])
        # Cosine and sine exchanged in the closed form.
        exchanged = [(w_x0 * s - w_y0 * co, w_y0 * s + w_x0 * co, w_z)
                     for co, s in c.COS_SIN]
        self.assertEqual(self._margins(exchanged), [7, 7, 7, Fraction(217, 25)])
        # A value reported at the wrong sample time: every pair of samples must differ.
        gaps = [max(abs(x - y) for x, y in zip(c.OMEGA[i], c.OMEGA[j]))
                for i in range(4) for j in range(i + 1, 4)]
        self.assertEqual(min(gaps), Fraction(33, 25))

    def test_v_eom_04_incorrect_coupling_between_transverse_components(self):
        """Both fail at pi/4 and atan(3/4); both are invisible at the half cycle."""
        c = self.C
        w_x0, w_y0, w_z = c.OMEGA_0
        uncoupled = [(w_x0 * co, w_y0 * co, w_z) for co, _ in c.COS_SIN]
        self.assertEqual(self._margins(uncoupled), [0, 5, 0, Fraction(24, 5)])
        symmetric = [(w_x0 * co - w_y0 * s, w_y0 * co - w_x0 * s, w_z)
                     for co, s in c.COS_SIN]
        self.assertEqual(self._margins(symmetric), [0, 4, 0, Fraction(96, 25)])

    def test_v_eom_04_mutation_i_spherical_body_trap(self):
        """J_par = J_perp: lambda = 0, the gyroscopic term vanishes for EVERY w, and the
        frozen-transverse and sign-reversed mutations become the true solution."""
        c = self.C
        lam_spherical = (c.J_PERP - c.J_PERP) / c.J_PERP * c.OMEGA_0[2]
        self.assertEqual(lam_spherical, 0)
        self.assertEqual(-lam_spherical, lam_spherical)
        for w in c.OMEGA:
            self.assertEqual(_skew_cross(w, _diag_times((c.J_PERP, c.J_PERP, c.J_PERP), w)),
                             (0, 0, 0))
        self.assertNotEqual(_skew_cross(c.OMEGA_0, _diag_times(c.J_DIAG, c.OMEGA_0)),
                            (0, 0, 0), "the frozen case must exercise the term")

    def test_v_eom_04_mutation_j_zero_transverse_rate_trap(self):
        """w_x0 = w_y0 = 0: every transverse model collapses onto the same zero answer."""
        c = self.C
        w0_trap = (Fraction(0), Fraction(0), c.OMEGA_0[2])
        truth = self._rate_model(c.LAMBDA, w0_trap)
        for rate in (-c.LAMBDA, 0, 3 * c.LAMBDA, -3 * c.LAMBDA, 6 * c.LAMBDA):
            self.assertEqual(self._rate_model(rate, w0_trap), truth)
        self.assertEqual(_skew_cross(w0_trap, _diag_times(c.J_DIAG, w0_trap)), (0, 0, 0))

    def test_v_eom_04_left_handed_axis_relabelling_is_detected(self):
        """Swapping x and z is a reflection.  It flips the cross product, so the
        relabelled solution fails the Euler equations by exactly twice the gyroscopic
        term.  (The cyclic relabelling passes: see the integrity class.)"""
        c = self.C
        j_reflected = (c.J_PARALLEL, c.J_PERP, c.J_PERP)
        for k in range(4):
            w, w_dot = c.OMEGA[k], c.OMEGA_DOT[k]
            w_r, w_dot_r = (w[2], w[1], w[0]), (w_dot[2], w_dot[1], w_dot[0])
            with self.subTest(sample=c.SAMPLE_TIMES_S[k]):
                residual = _torque_free_residual(j_reflected, w_r, w_dot_r)
                self.assertNotEqual(residual, (0, 0, 0))
                self.assertEqual(residual,
                                 _scale(2, _skew_cross(w_r, _diag_times(j_reflected, w_r))))


# ======================================================================================
# V-EOM-05 — Torque-free rigid body whose BODY AXES ARE NOT PRINCIPAL AXES.
# ======================================================================================
#
# WHY THIS ANCHOR WAS REPAIRED
# ----------------------------
# RS-004 sec 7 originally configured V-EOM-05 as "principal moments J_xx < J_yy < J_zz,
# all distinct" while claiming the case isolates *products of inertia* and full-tensor
# handling.  Those two statements contradict each other: principal moments on the body
# axes mean a DIAGONAL tensor, whose three products of inertia are identically zero.  An
# implementation that dropped J_xy, J_xz and J_yz entirely, or that diagonalised J before
# using it, reproduced that case exactly.
#
# The defect was in the CASE, not in the equation: RS-004 sec 4.3 already requires a full
# symmetric tensor, "because the products of inertia are exactly what couple the axes".
# This anchor supplies a case in which they do.
#
# WHAT THIS ANCHOR IS -- AND IS NOT
# ---------------------------------
# A torque-free asymmetric body has NO elementary closed-form trajectory (the solution runs
# on Jacobi elliptic functions), so no trajectory is frozen here and none should be.  What
# is frozen is the INSTANTANEOUS angular acceleration at two known states, which is an
# exact rational quantity, plus the invariant-rate conditions that hold at any state:
#
#     J wdot + w x (J w) = 0      (RS-004 sec 4.1, ADR-0009, zero external moment)
#     wdot = -J^-1 [ w x (J w) ]
#
# A future implementation must reproduce wdot at both states from J and w alone.
#
# WHEN IS A TENSOR A REAL BODY?  THREE CONDITIONS, NOT TWO
# --------------------------------------------------------
# 1. symmetric;
# 2. positive definite -- Sylvester: leading principal minors all > 0;
# 3. the principal moments satisfy the triangle inequalities, J_i + J_j >= J_k.
#
# Condition 3 is the one that is easy to forget, and a tensor can satisfy 1 and 2 while
# failing it: diag-dominant [[10,2,1],[2,8,3],[1,3,6]] is symmetric positive definite, yet
# its principal moments violate the triangle inequality, so no rigid body has it.  The
# check is exact without computing eigenvalues: the eigenvalues of
#
#     S = (tr(J)/2) I - J
#
# are (J_i + J_j - J_k)/2, so S positive definite is equivalent to the strict triangle
# inequalities.  Both minor sets are asserted below.
#
# THE FROZEN CASE (kg m^2, rad/s, rad/s^2), chosen by mutation analysis
# ---------------------------------------------------------------------
#     J = [[ 8, -1, -2],
#          [-1,  7, -3],
#          [-2, -3,  5]]      symmetric; leading minors (8, 55, 163); det 163
#                             S minors (2, 5, 7) -> strict triangle inequalities
#                             principal moments ~ (2.0205, 8.6111, 9.3684),
#                             condition number ~ 4.64, and the eigenvectors lie nowhere
#                             near the body axes -- which is the entire point.
#
#     Diagonal entries 8, 7, 5 are distinct; products -1, -2, -3 are all non-zero with
#     distinct magnitudes; no value repeats anywhere in the tensor.
#
#     state 0:  w = ( 4, -6,  7)   ->   wdot = (-18,   9,  23)
#     state 1:  w = ( 7, -5, -8)   ->   wdot = (-12,  31, -38)
#
# Every frozen number is an integer even though det J = 163 is prime -- which is itself a
# check worth having, since almost any transcription slip makes wdot fractional.
#
# HAND DERIVATION, state 0 (reproduce it in a few lines of arithmetic)
# --------------------------------------------------------------------
#     J w  = ( 8(4) + (-1)(-6) + (-2)(7),
#             (-1)(4) +   7(-6) + (-3)(7),
#             (-2)(4) + (-3)(-6) +  5(7) )                    = ( 24, -67,  45)
#
#     w x (J w) = ( (-6)(45) - (7)(-67),
#                    (7)(24) - (4)(45),
#                    (4)(-67) - (-6)(24) )                    = ( 199, -12, -124)
#
#     so the right-hand side  -(w x (J w))                    = (-199,  12,  124)
#     and J wdot = (-199, 12, 124) is solved by wdot          = ( -18,   9,   23)
#
# The last step is checked in both directions below: the frozen wdot is substituted back
# into J wdot, and it is independently re-derived by Cramer's rule.
#
# CASE-SELECTION TRAP, found by analysis and asserted below
# ---------------------------------------------------------
# A tensor whose three products are all POSITIVE cannot detect the mutation "replace each
# product by its absolute value" -- that mutation is then the identity.  The chosen tensor
# has all three products negative, so |.| flips all three and is detected.  (A candidate
# with products (+1/2, +3, +1) was rejected for exactly this reason.)
#
# STRUCTURAL BLIND SPOTS -- properties of the equation, not of this case
# ----------------------------------------------------------------------
# * transposing J is a no-op, because J is symmetric;
# * w -> -w leaves wdot unchanged, because wdot is quadratic in w;
# * J -> kJ leaves wdot unchanged, because J^-1 and J cancel.
# All three are asserted below as facts, so that nobody later mistakes them for coverage.
#
# SCOPE.  This anchor verifies one instantaneous derivative, twice, and the invariant
# rates.  It does not verify a trajectory, an integrator, attitude propagation, variable
# mass, or a complete 6-DOF simulation.  No production rotational-dynamics implementation
# exists for it to test.
# ======================================================================================


def _det3(m):
    """Determinant of a 3x3 rational matrix, by cofactor expansion along the first row."""
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _leading_minors(m):
    """The three leading principal minors -- Sylvester's criterion for definiteness."""
    return (m[0][0], m[0][0] * m[1][1] - m[0][1] * m[1][0], _det3(m))


def _triangle_matrix(j):
    """``S = (tr(J)/2) I - J``; its eigenvalues are ``(J_i + J_j - J_k)/2``."""
    half_trace = (j[0][0] + j[1][1] + j[2][2]) / 2
    return [[(half_trace if i == k else Fraction(0)) - j[i][k] for k in range(3)]
            for i in range(3)]


def _inverse3(m):
    """Exact inverse as adjugate / determinant."""
    determinant = _det3(m)
    cofactor = [[(m[(i + 1) % 3][(k + 1) % 3] * m[(i + 2) % 3][(k + 2) % 3]
                  - m[(i + 1) % 3][(k + 2) % 3] * m[(i + 2) % 3][(k + 1) % 3])
                 for k in range(3)] for i in range(3)]
    return [[cofactor[k][i] / determinant for k in range(3)] for i in range(3)]


def _diagonalised(j):
    """``J`` with its products of inertia deleted -- NOT a principal-axis rotation."""
    return [[j[i][k] if i == k else Fraction(0) for k in range(3)] for i in range(3)]


def _full_torque_free_residual(j, w, w_dot):
    """``J wdot + w x (J w)`` for a full tensor; zero on any torque-free solution."""
    return _add(_matvec(j, w_dot), _skew_cross(w, _matvec(j, w)))


def _omega_dot_torque_free(j, w):
    """``wdot = -J^-1 [w x (J w)]`` -- the adjugate route."""
    return _matvec(_inverse3(j), _scale(-1, _skew_cross(w, _matvec(j, w))))


def _omega_dot_by_cramer(j, w):
    """The same derivative by Cramer's rule, written out as scalar expressions.

    Deliberately shares no helper with :func:`_omega_dot_torque_free`: no matrix product,
    no adjugate, no cross-product helper.  Two routes to one number is the point.
    """
    a11, a12, a13 = j[0][0], j[0][1], j[0][2]
    a22, a23 = j[1][1], j[1][2]
    a33 = j[2][2]
    p, q, r = w

    h1 = a11 * p + a12 * q + a13 * r          # J is symmetric: a21 = a12, a31 = a13,
    h2 = a12 * p + a22 * q + a23 * r          # a32 = a23
    h3 = a13 * p + a23 * q + a33 * r

    b1 = -(q * h3 - r * h2)                   # b = -(w x (J w))
    b2 = -(r * h1 - p * h3)
    b3 = -(p * h2 - q * h1)

    def d3(m11, m12, m13, m21, m22, m23, m31, m32, m33):
        return (m11 * (m22 * m33 - m23 * m32)
                - m12 * (m21 * m33 - m23 * m31)
                + m13 * (m21 * m32 - m22 * m31))

    determinant = d3(a11, a12, a13, a12, a22, a23, a13, a23, a33)
    return (d3(b1, a12, a13, b2, a22, a23, b3, a23, a33) / determinant,
            d3(a11, b1, a13, a12, b2, a23, a13, b3, a33) / determinant,
            d3(a11, a12, b1, a12, a22, b2, a13, a23, b3) / determinant)


class VEOM05NonPrincipalBodyAxes:
    """V-EOM-05 — torque-free body whose body axes are not principal axes. Frozen oracle.

    The tensor is resolved in **body axes** (NOTATION sec 5.1): `J_xx`, `J_yy`, `J_zz` on
    the diagonal and the products of inertia `J_xy`, `J_xz`, `J_yz` off it, with the
    standard sign convention in which the tensor is

        J = [[ Jxx, Jxy, Jxz], [ Jxy, Jyy, Jyz], [ Jxz, Jyz, Jzz]]

    and the products enter `J w` with a PLUS sign.  (Some texts define products of inertia
    with a leading minus; RADIUS does not.  The convention is fixed by this literal and by
    the hand derivation in the section comment above.)

    This case says nothing about the x_B symmetry-axis convention of ADR-0010: an
    axisymmetric vehicle is the *special* case in which the products vanish and
    `J_xx = J_parallel`, `J_yy = J_zz = J_perp`.  Here they deliberately do not vanish,
    which is what an asymmetric body, or a symmetric one whose structure is misaligned
    with the body frame, actually looks like.
    """

    J = [[Fraction(8), Fraction(-1), Fraction(-2)],
         [Fraction(-1), Fraction(7), Fraction(-3)],
         [Fraction(-2), Fraction(-3), Fraction(5)]]
    DETERMINANT = Fraction(163)
    LEADING_MINORS = (Fraction(8), Fraction(55), Fraction(163))
    TRIANGLE_MINORS = (Fraction(2), Fraction(5), Fraction(7))

    # state 0
    OMEGA_0 = _v(4, -6, 7)
    ANGULAR_MOMENTUM_0 = _v(24, -67, 45)
    RIGHT_HAND_SIDE_0 = _v(-199, 12, 124)          # -(w x (J w))
    OMEGA_DOT_0 = _v(-18, 9, 23)
    ANGULAR_MOMENTUM_SQ_0 = Fraction(7090)
    TWICE_KINETIC_ENERGY_0 = Fraction(813)
    OMEGA_DOT_IF_PRODUCTS_DELETED_0 = (Fraction(-21, 2), Fraction(-12), Fraction(-24, 5))
    PRODUCTS_GAP_0 = Fraction(139, 5)

    # state 1 — not a scalar multiple of state 0, so a hard-coded derivative fails
    OMEGA_1 = _v(7, -5, -8)
    ANGULAR_MOMENTUM_1 = _v(77, -18, -39)
    RIGHT_HAND_SIDE_1 = _v(-51, 343, -259)
    OMEGA_DOT_1 = _v(-12, 31, -38)
    ANGULAR_MOMENTUM_SQ_1 = Fraction(7774)
    TWICE_KINETIC_ENERGY_1 = Fraction(941)
    OMEGA_DOT_IF_PRODUCTS_DELETED_1 = _v(10, 24, -7)
    PRODUCTS_GAP_1 = Fraction(31)

    STATES = ((OMEGA_0, ANGULAR_MOMENTUM_0, RIGHT_HAND_SIDE_0, OMEGA_DOT_0,
               ANGULAR_MOMENTUM_SQ_0, TWICE_KINETIC_ENERGY_0,
               OMEGA_DOT_IF_PRODUCTS_DELETED_0, PRODUCTS_GAP_0),
              (OMEGA_1, ANGULAR_MOMENTUM_1, RIGHT_HAND_SIDE_1, OMEGA_DOT_1,
               ANGULAR_MOMENTUM_SQ_1, TWICE_KINETIC_ENERGY_1,
               OMEGA_DOT_IF_PRODUCTS_DELETED_1, PRODUCTS_GAP_1))


class TestVEOM05AnchorIntegrity(unittest.TestCase):
    """The frozen V-EOM-05 oracle is internally consistent, in exact arithmetic.

    Nothing here imports ``radius``, and no production rotational-dynamics code exists to
    import.  Every test name carries ``v_eom_05`` so none can shadow another.
    """

    C = VEOM05NonPrincipalBodyAxes

    def test_v_eom_05_inertia_tensor_is_symmetric(self):
        j = self.C.J
        for i in range(3):
            for k in range(3):
                with self.subTest(entry=(i, k)):
                    self.assertEqual(j[i][k], j[k][i],
                                     "V-EOM-05: the inertia tensor must be symmetric.")

    def test_v_eom_05_inertia_tensor_is_positive_definite(self):
        """Sylvester's criterion, exactly: every leading principal minor is positive."""
        minors = _leading_minors(self.C.J)
        self.assertEqual(minors, self.C.LEADING_MINORS)
        for order, minor in enumerate(minors, start=1):
            with self.subTest(order=order):
                self.assertGreater(minor, 0, "V-EOM-05: J must be positive definite.")
        self.assertEqual(_det3(self.C.J), self.C.DETERMINANT)

    def test_v_eom_05_inertia_tensor_satisfies_the_triangle_inequalities(self):
        """A symmetric positive-definite tensor is not automatically a real body.

        The principal moments must also satisfy J_i + J_j >= J_k, which holds exactly when
        ``S = (tr(J)/2) I - J`` is positive semidefinite.  Here it is strictly definite.
        """
        minors = _leading_minors(_triangle_matrix(self.C.J))
        self.assertEqual(minors, self.C.TRIANGLE_MINORS)
        for order, minor in enumerate(minors, start=1):
            with self.subTest(order=order):
                self.assertGreater(minor, 0)
        # ...and a tensor that passes positive definiteness yet fails this must be rejected.
        not_a_body = [[Fraction(10), Fraction(2), Fraction(1)],
                      [Fraction(2), Fraction(8), Fraction(3)],
                      [Fraction(1), Fraction(3), Fraction(6)]]
        self.assertTrue(all(x > 0 for x in _leading_minors(not_a_body)))
        self.assertFalse(all(x > 0 for x in _leading_minors(_triangle_matrix(not_a_body))),
                         "the counter-example must fail the triangle inequalities")

    def test_v_eom_05_products_of_inertia_are_non_zero_and_distinct(self):
        j = self.C.J
        products = (j[0][1], j[0][2], j[1][2])
        diagonal = (j[0][0], j[1][1], j[2][2])
        for name, value in zip(("J_xy", "J_xz", "J_yz"), products):
            with self.subTest(product=name):
                self.assertNotEqual(value, 0,
                                    "V-EOM-05 exists to exercise the products of inertia.")
        self.assertEqual(len({abs(x) for x in products}), 3)
        self.assertEqual(len(set(diagonal)), 3)
        self.assertEqual(len({abs(x) for x in products} | {abs(x) for x in diagonal}), 6)

    def test_v_eom_05_body_axes_are_not_principal_axes(self):
        """If a body axis were principal, ``J e`` would be parallel to ``e``."""
        for axis in range(3):
            basis = [Fraction(1) if i == axis else Fraction(0) for i in range(3)]
            image = _matvec(self.C.J, basis)
            off_axis = [image[i] for i in range(3) if i != axis]
            with self.subTest(axis="xyz"[axis]):
                self.assertNotEqual(off_axis, [Fraction(0), Fraction(0)],
                                    "V-EOM-05 requires body axes that are NOT principal.")

    def test_v_eom_05_frozen_angular_momentum_and_right_hand_side(self):
        for index, state in enumerate(self.C.STATES):
            w, h, rhs = state[0], state[1], state[2]
            with self.subTest(state=index):
                self.assertEqual(_matvec(self.C.J, w), h, "V-EOM-05: h = J w.")
                self.assertEqual(_scale(-1, _skew_cross(w, h)), rhs,
                                 "V-EOM-05: the right-hand side is -(w x (J w)).")

    def test_v_eom_05_frozen_derivative_satisfies_the_euler_equations(self):
        for index, state in enumerate(self.C.STATES):
            w, w_dot = state[0], state[3]
            with self.subTest(state=index):
                self.assertEqual(_full_torque_free_residual(self.C.J, w, w_dot), (0, 0, 0),
                                 "V-EOM-05: J wdot + w x (J w) must vanish exactly.")
                self.assertEqual(_matvec(self.C.J, w_dot), state[2],
                                 "V-EOM-05: J wdot must equal the frozen right-hand side.")

    def test_v_eom_05_derivative_matches_two_independent_calculations(self):
        """Adjugate inverse versus Cramer's rule -- no shared helper between them."""
        for index, state in enumerate(self.C.STATES):
            w, w_dot = state[0], state[3]
            with self.subTest(state=index):
                self.assertEqual(_omega_dot_torque_free(self.C.J, w), w_dot)
                self.assertEqual(_omega_dot_by_cramer(self.C.J, w), w_dot)

    def test_v_eom_05_invariant_rates_vanish_exactly(self):
        """``d|h|^2/dt = 2 h . (J wdot)`` and ``d(2T)/dt = 2 w . (J wdot)``, both zero."""
        for index, state in enumerate(self.C.STATES):
            w, h, w_dot, h_sq, twice_t = state[0], state[1], state[3], state[4], state[5]
            j_w_dot = _matvec(self.C.J, w_dot)
            with self.subTest(state=index):
                self.assertEqual(sum(x * y for x, y in zip(h, j_w_dot)), 0)
                self.assertEqual(sum(x * y for x, y in zip(w, j_w_dot)), 0)
                self.assertEqual(sum(x * x for x in h), h_sq)
                self.assertEqual(sum(x * y for x, y in zip(w, h)), twice_t)

    def test_v_eom_05_products_of_inertia_change_the_derivative(self):
        """The claim the original configuration could not support."""
        for index, state in enumerate(self.C.STATES):
            w, w_dot, deleted, gap = state[0], state[3], state[6], state[7]
            with self.subTest(state=index):
                without = _omega_dot_torque_free(_diagonalised(self.C.J), w)
                self.assertEqual(without, deleted)
                self.assertNotEqual(without, w_dot)
                self.assertEqual(max(abs(x - y) for x, y in zip(without, w_dot)), gap)

    def test_v_eom_05_the_two_states_are_independent(self):
        c = self.C
        self.assertNotEqual(c.OMEGA_DOT_0, c.OMEGA_DOT_1)
        ratios = {c.OMEGA_1[i] / c.OMEGA_0[i] for i in range(3)}
        self.assertGreater(len(ratios), 1,
                           "state 1 must not be a scalar multiple of state 0")
        for w in (c.OMEGA_0, c.OMEGA_1):
            self.assertNotIn(0, w)
            self.assertNotIn(1, [abs(x) for x in w])
            self.assertEqual(len({abs(x) for x in w}), 3)

    def test_v_eom_05_anchor_rejects_a_deliberately_incorrect_oracle(self):
        c = self.C
        wrong = _add(c.OMEGA_DOT_0, _v(1, 0, 0))
        self.assertNotEqual(_full_torque_free_residual(c.J, c.OMEGA_0, wrong), (0, 0, 0))
        self.assertNotEqual(_matvec(c.J, wrong), c.RIGHT_HAND_SIDE_0)
        bad_tensor = [row[:] for row in c.J]
        bad_tensor[0][1] = bad_tensor[1][0] = Fraction(0)
        self.assertNotEqual(_omega_dot_torque_free(bad_tensor, c.OMEGA_0), c.OMEGA_DOT_0)

    def test_v_eom_05_case_construction_avoids_the_known_trap(self):
        """All-positive products would make "replace products by |value|" a no-op."""
        c = self.C
        products = (c.J[0][1], c.J[0][2], c.J[1][2])
        absolute = [[abs(x) for x in row] for row in c.J]
        self.assertFalse(all(x > 0 for x in products))
        self.assertNotEqual(_omega_dot_torque_free(absolute, c.OMEGA_0), c.OMEGA_DOT_0,
                            "the |.| mutation must be visible, so the products must not "
                            "all share one sign")


class TestVEOM05Discrimination(unittest.TestCase):
    """What V-EOM-05 detects, with exact margins, and what it structurally cannot."""

    C = VEOM05NonPrincipalBodyAxes

    def _margin(self, tensor=None, omega=None):
        c = self.C
        tensor = c.J if tensor is None else tensor
        omega = c.OMEGA_0 if omega is None else omega
        wrong = _omega_dot_torque_free(tensor, omega)
        return max(abs(x - y) for x, y in zip(wrong, c.OMEGA_DOT_0))

    def _with_products(self, xy, xz, yz):
        c = self.C
        return [[c.J[0][0], xy, xz], [xy, c.J[1][1], yz], [xz, yz, c.J[2][2]]]

    def test_v_eom_05_harness_reproduces_the_frozen_oracle(self):
        self.assertEqual(self._margin(), 0)
        self.assertEqual(_omega_dot_torque_free(self.C.J, self.C.OMEGA_1), self.C.OMEGA_DOT_1)

    def test_v_eom_05_mutation_each_product_zeroed(self):
        c = self.C
        xy, xz, yz = c.J[0][1], c.J[0][2], c.J[1][2]
        zero = Fraction(0)
        self.assertEqual(self._margin(self._with_products(zero, xz, yz)), Fraction(157, 10))
        self.assertEqual(self._margin(self._with_products(xy, zero, yz)), Fraction(4218, 203))
        self.assertEqual(self._margin(self._with_products(xy, xz, zero)), Fraction(5841, 247))

    def test_v_eom_05_mutation_each_product_sign_flipped(self):
        c = self.C
        xy, xz, yz = c.J[0][1], c.J[0][2], c.J[1][2]
        self.assertEqual(self._margin(self._with_products(-xy, xz, yz)), Fraction(478, 17))
        self.assertEqual(self._margin(self._with_products(xy, -xz, yz)), Fraction(44))
        self.assertEqual(self._margin(self._with_products(xy, xz, -yz)), Fraction(486, 17))
        self.assertEqual(self._margin(self._with_products(-xy, -xz, -yz)), Fraction(922, 17))
        self.assertEqual(self._margin([[abs(x) for x in row] for row in c.J]),
                         Fraction(922, 17))

    def test_v_eom_05_mutation_products_swapped(self):
        c = self.C
        xy, xz, yz = c.J[0][1], c.J[0][2], c.J[1][2]
        self.assertEqual(self._margin(self._with_products(yz, xz, xy)), Fraction(864, 17))
        self.assertEqual(self._margin(self._with_products(xy, yz, xz)), Fraction(235, 56))

    def test_v_eom_05_mutation_tensor_diagonalised(self):
        self.assertEqual(self._margin(_diagonalised(self.C.J)), self.C.PRODUCTS_GAP_0)

    def test_v_eom_05_mutation_inertia_axes_permuted(self):
        c = self.C
        permuted = [[c.J[p][q] for q in (1, 2, 0)] for p in (1, 2, 0)]
        self.assertEqual(self._margin(permuted), Fraction(4386, 163))

    def test_v_eom_05_mutation_equation_sign_errors(self):
        """Three wrong equations that are numerically ONE mutation, recorded as such.

        Dropping the minus sign, reversing the cross-product order, and writing
        ``J wdot = +w x (J w)`` all produce ``+J^-1 [w x (J w)]`` -- the same wrong answer.
        """
        c = self.C
        wrong = _scale(-1, c.OMEGA_DOT_0)
        self.assertEqual(max(abs(x - y) for x, y in zip(wrong, c.OMEGA_DOT_0)), 46)
        no_cross = (Fraction(0), Fraction(0), Fraction(0))
        self.assertEqual(max(abs(x - y) for x, y in zip(no_cross, c.OMEGA_DOT_0)), 23)

    def test_v_eom_05_mutation_inverse_omitted(self):
        """``J`` applied where ``J^-1`` belongs."""
        c = self.C
        wrong = _matvec(c.J, c.RIGHT_HAND_SIDE_0)
        self.assertEqual(max(abs(x - y) for x, y in zip(wrong, c.OMEGA_DOT_0)), 1834)

    def test_v_eom_05_mutation_state_errors(self):
        c = self.C
        w = c.OMEGA_0
        self.assertEqual(self._margin(omega=(w[1], w[2], w[0])), Fraction(7363, 163))
        self.assertEqual(self._margin(omega=(-w[0], w[1], w[2])), Fraction(3392, 163))
        self.assertEqual(self._margin(omega=(w[0], Fraction(0), w[2])), Fraction(1692, 163))
        self.assertEqual(self._margin(omega=(w[0] + 1, w[1] - 1, w[2] + 2)),
                         Fraction(2185, 163))

    def test_v_eom_05_structural_blind_spots_are_recorded_not_claimed(self):
        """Three mutations this anchor CANNOT see, each a property of the equation."""
        c = self.C
        transposed = [[c.J[k][i] for k in range(3)] for i in range(3)]
        self.assertEqual(transposed, c.J, "J is symmetric, so transposing it is a no-op")
        self.assertEqual(self._margin(transposed), 0)

        negated = _scale(-1, c.OMEGA_0)
        self.assertEqual(_omega_dot_torque_free(c.J, negated), c.OMEGA_DOT_0)

        scaled = [[2 * x for x in row] for row in c.J]
        self.assertEqual(_omega_dot_torque_free(scaled, c.OMEGA_0), c.OMEGA_DOT_0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
