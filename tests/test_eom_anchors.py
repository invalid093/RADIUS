"""V-EOM-01, V-EOM-02, V-EOM-03 — frozen analytical anchors for the translational EOM.

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
