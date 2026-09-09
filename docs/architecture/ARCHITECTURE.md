# RADIUS — Software Architecture

**Status:** Design. Not implemented.
**Depends on:** RS-001 … RS-008

---

## 1. The organising principle

> **The dynamics engine must be testable with everything else switched off.**

Every structural decision below follows from that. The analytical verification cases (RS-004 §7)
require running the equations of motion with no atmosphere, no aerodynamics, no mass flow and no
gravity — and getting an exact closed-form answer. If any of those is entangled with the equations,
the anchor tests cannot be written, and the project loses the only external check it currently has.

Secondary principle: **a failure should localise.** When a test fails, it should be obvious which
module is wrong. This is what makes small, purely-functional modules worth their overhead here.

---

## 2. Dependency direction

Dependencies point strictly downward. There are no cycles, and no upward imports.

```
                    experiment / CLI
                            │
                     simulation loop
                    (integrator, events, recording)
                            │
                  state derivative function
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
  force sources        mass model          environment
  (aero, external)                    (atmosphere, gravity, wind)
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
              frames · attitude · state · math
                            │
                    configuration
```

**The dynamics core knows nothing about aerodynamics.** It receives a force and a moment. It cannot
tell whether they came from an aerodynamic model, a test fixture returning zero, or a constant. That
is what makes V-EOM-01 through V-EOM-08 possible.

---

## 3. Modules

| Path | Contents | Specified by |
|---|---|---|
| `radius/math/` | quaternion algebra, skew-symmetric operator, rotations, safe `arccos`/`arcsin` guards | RS-002 |
| `radius/frames/` | frame definitions, $\mathbf{T}_{BI}(q)$, wind-frame construction, Euler conversions, altitude | RS-001 |
| `radius/state/` | the 14-element state: pack/unpack, named accessors, derived quantities, the block-wise error norm | RS-003 |
| `radius/dynamics/` | the state derivative function; translational, rotational and mass equations | RS-004 |
| `radius/atmosphere/` | exponential and U.S. Standard 1976 models behind one interface | RS-006 |
| `radius/aerodynamics/` | coefficient models, force/moment build-up, moment transfer, validity gate | RS-007 |
| `radius/propulsion/` | the **generic** `ExternalForceSource` interface and mass-flow abstraction. No hardware content | RS-008 |
| `radius/simulation/` | integrators, event detection and location, trajectory recording, run orchestration | RS-005 |
| `radius/config/` | YAML loading, unit conversion at the boundary, validation, config hashing | conventions §1 |
| `radius/provenance/` | manifest generation, seed derivation, commit capture | `docs/PROVENANCE.md` |

`radius/navigation/`, `radius/guidance/`, `radius/control/`, `radius/actuators/` are **named here and
not created**, per ADR-0001. Their place in the dependency graph is fixed (§6) so that adding them
does not restructure anything.

---

## 4. Interfaces

Small, explicit, and stated so that substitution is a substitution rather than a rewrite.

```
Environment
    atmosphere(h)              -> (rho, p, T, a)      raises outside its domain
    gravity(p_inertial)        -> R^3  [m/s^2]        inertial frame
    wind(t, p_inertial)        -> R^3  [m/s]          inertial frame

ForceSource                                            (see RS-008 §3.1)
    force_body(t, state)       -> R^3  [N]
    moment_body(t, state)      -> R^3  [N·m]  about the CM
    mass_flow_rate(t, state)   -> float [kg/s]  >= 0
    is_active(t, state)        -> bool

MassProperties                                         (see RS-008 §3.2)
    mass(t) · inertia_body(t,m) · inertia_rate_body(t,m) · cm_offset_body(t,m)

Integrator
    step(f, t, x, h)           -> x_next               deterministic, no hidden state

Event
    g(t, state)                -> float                zero crossing
    direction                  -> {+1, -1, 0}
    action(t, state)           -> state                applied at the located crossing
```

**`gravity` takes a position, not an altitude.** The flat-Earth model uses only the vertical
component, but taking the full position now is what makes the ECEF/ECI extension a substitution of one
implementation rather than a change to every call site. This is the one place where anticipating a
future need is worth the cost, because the alternative touches the dynamics core.

---

## 5. Purity and state ownership

- **The derivative function is pure.** `f(t, x, context) -> dx/dt`, with no mutation, no I/O, no
  hidden accumulator, no caching. It is called four times per RK4 step with *different* states, and a
  cache keyed on time rather than state would silently return values from the wrong stage — a bug
  that produces a plausible trajectory with the wrong convergence order.
- **No module-level mutable state.** Nothing is configured by import side effect.
- **No global RNG.** Every stochastic component takes a derived seed
  (`docs/PROVENANCE.md` §4).
- **Configuration is immutable after load**, hashed, and recorded in the manifest.
- **Units are converted once**, at the configuration boundary, in a named function.

---

## 6. Flow

Current, and all that is implemented through Phase 10:

```
configuration
  → initial state
  → [ environment → forces & moments → equations of motion
      → integrator → event check → next state ]  ×N
  → recorded trajectory
  → curated result + manifest
```

Later, without restructuring the above:

```
… → navigation (estimate) → guidance (command) → control (actuator command)
    → actuator model → forces & moments → …
```

Navigation, guidance and control sit **between** the state and the force sources. They consume
measurements and produce commands; they never touch the state directly.

**The estimator gets its own state vector, separate from the vehicle's** (RS-003 §7). This is
architectural, not a convention: a navigation module that can reach the true state will, eventually,
accidentally use it — and the resulting estimator looks excellent for reasons that have nothing to do
with the estimator. Keeping them separate is what makes the eventual AURA relationship meaningful,
because AURA's questions are precisely about what can be inferred *without* access to truth.

---

## 7. Testing structure

| Layer | What it establishes |
|---|---|
| Unit | one function, one property. Quaternion algebra, frame round trips, atmosphere layer continuity |
| Analytical | a subsystem against a closed-form solution. V-EOM-01…08, V-VM-01 |
| Numerical | properties of the method: order of accuracy, determinism, event location, invariant drift |
| Regression | frozen reference trajectories with tolerances, so behaviour changes are caught |
| Property | invariants over random inputs: $\mathbf{T}$ orthonormal, $\lVert q\rVert=1$, $\mathbf{J}$ positive-definite |

Ordered so each layer's prerequisites are verified before it runs. A failing analytical test whose
unit tests pass points at the composition; a failing unit test points at one function.

---

## 8. Dependencies

Python, `numpy`, `PyYAML`. Nothing else without a recorded reason.

**Why so few.** Every dependency is a reproducibility liability: a version whose behaviour changes,
a transitive tree that may not install in five years, and a floating-point implementation that may
differ across platforms. RADIUS's determinism claim (`docs/PROVENANCE.md` §5) is only as strong as its
dependency surface is small.

Notably **not** used: SciPy's ODE solvers. RADIUS implements RK4 itself — perhaps thirty lines —
because the integrator is a *subject of study* here, not a black box. An adaptive third-party solver
would take the determinism and order-of-accuracy properties out of the project's control, which is
exactly what RS-005 spent its length deciding.

---

## 9. What this architecture does not yet address

- **Performance.** Nothing here is optimised, and no performance requirement has been measured. Monte
  Carlo cost (R4 in RS-005 §1) is asserted to be acceptable and has not been demonstrated. A pure
  Python per-step derivative call may prove too slow for large ensembles; if so the fix is
  vectorisation across runs, not abandoning purity.
- **Parallelism.** Deliberately absent from the integration loop (determinism). Parallelism across
  independent Monte Carlo runs is safe — each has its own derived seed — and is the right place for it.
- **Persistence format.** Trajectory storage format is undecided; it interacts with the publication
  policy (bulk arrays are not published) and can wait until there is a trajectory.
