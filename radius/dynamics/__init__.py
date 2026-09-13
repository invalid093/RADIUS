"""Equations of motion for RADIUS.

Currently only the rigid-body rotational derivative
(:func:`radius.dynamics.rotational.angular_acceleration_wrt_i_in_b`), which evaluates

    wdot = J^-1 [ M_ext - w x (J w) ]

at one state. That is the whole of this package: there is no translational derivative, no
mass equation, no assembled state-derivative function, and no integrator. Those belong to
RS-004 and RS-005 and to the phases that implement them.

The equation is RS-004 section 4.1 as corrected by ADR-0009, and the inertia convention is
ADR-0010. Verified against the V-EOM-05 anchor, which was frozen before this package
existed; see ``docs/methodology/VERIFICATION_AND_VALIDATION.md``.
"""

__all__: list[str] = []
