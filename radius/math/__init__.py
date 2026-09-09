"""Mathematical primitives for RADIUS.

Currently only quaternion algebra (``radius.math.quaternion``), which is the minimum
required by the Phase 2A frame and attitude anchors.

Note on the package name: this package is named ``math`` and therefore shadows the
standard library module of the same name *only* for code that imports it by its full
path. Python 3 uses absolute imports by default, so a plain ``import math`` anywhere in
RADIUS still resolves to the standard library. Nothing in this package imports the
standard library ``math`` module, so the question does not arise here.
"""

__all__: list[str] = []
