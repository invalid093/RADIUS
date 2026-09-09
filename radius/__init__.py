"""RADIUS — Rocket Dynamics & Integrated Uncertainty Simulation.

A physics-based nonlinear 6-DOF aerospace vehicle dynamics, simulation and
uncertainty-analysis framework.

**Status: research / architecture phase.** This package currently contains only the
frame and quaternion mathematics needed to make the independently hand-derived Phase 2A
anchors in ``tests/test_frames.py`` executable. There is no dynamics engine, no
integrator, no atmosphere, no aerodynamics, no simulation and no vehicle model.

Nothing here is validated. The anchors that this code is written against are
*verification* evidence only: they establish that the documented conventions have been
implemented correctly, not that any model corresponds to reality. See
``docs/methodology/VERIFICATION_AND_VALIDATION.md``.

Conventions are fixed in ``docs/methodology/NOTATION_AND_CONVENTIONS.md`` and are
restated in each module that depends on them. Where code and that document disagree,
the code is wrong.
"""

# Recorded in every experiment manifest as `code.radius_version`
# (see docs/PROVENANCE.md section 3).
__version__ = "0.1.0"

__all__ = ["__version__"]
