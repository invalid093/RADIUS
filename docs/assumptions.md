# RADIUS — Assumptions Register

**Date:** 2026-09-09
**Rule:** No assumption may live only inside code. If code depends on one, it cites the ID here.
An assumption that is later tested moves to `VALIDATED` or `REFUTED` — it is **never silently
deleted**, because results whose manifests list it must remain traceable (`docs/PROVENANCE.md` §7).

| Status | Meaning |
|---|---|
| `OPEN` | Assumed, untested |
| `TO-VERIFY` | Assumed, with a specific action scheduled |
| `VALIDATED` | Tested and held |
| `REFUTED` | Tested and failed — consequences must be traced |

**Every assumption below is `OPEN` or `TO-VERIFY`.** `FACT`: the only implemented code is the
frame and quaternion utilities (`radius/frames.py`, `radius/math/quaternion.py`), and the tests
that would move an assumption to `VALIDATED` — those named in the **Action** column — belong to
subsystems that do not exist yet. `A-NUM-05` is the closest: V-FRM-09 establishes its observable
half only, which is recorded in `docs/methodology/VERIFICATION_AND_VALIDATION.md` §2 and is not
enough to change its status. No status below has changed.

**Revised 2026-09-09** by `docs/research/PRE_IMPLEMENTATION_MATHEMATICAL_AUDIT.md`: `A-VM-05` and
`A-NUM-05` added; `A-VM-03` re-scoped after the rotational equation was corrected (ADR-0009);
`A-FRM-02` extended with a quantified inconsistency.

The **Consequence** column is the important one. An assumption without a stated consequence is
decoration: it does not tell a reader what changes if it is wrong, which is the only reason to record
it.

---

## Reference frames — RS-001

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-FRM-01` | The NED frame at the reference point may be treated as **inertial**: Earth is flat and non-rotating | `OPEN` — **the most consequential assumption in RADIUS** | Coriolis and curvature errors enter every trajectory. Quantified in RS-001 §3: ~730 m over 100 s at 1000 m·s⁻¹; 196 m curvature drop at 50 km range | Validity domain (~10 km range, ~60 s) quoted with every result. Superseded by an ECEF/ECI extension, deferred |
| `A-FRM-02` | The centrifugal contribution is **already inside** the measured $g$ used | `OPEN` | Double-counting if a later change adds an explicit centrifugal term. **Audit finding F-7:** the centrifugal part scales as $(R_E+h)$ but `A-FRM-03`'s $g(h)$ scales all of $g$ as inverse-square. `CALCULATION`: $\approx5\times10^{-4}$ m·s⁻² at 30 km, ~0.9 m over 60 s — three orders below the accepted Coriolis error | Recorded, **not corrected**. Splitting $g$ belongs with the ECEF extension |
| `A-FRM-03` | Constant $g$ is used **only** as a deliberate switch enabling closed-form verification, not as a physical claim | `OPEN` (by construction) | If a *result* were produced with constant $g$ enabled, it would carry an unstated altitude error — 0.94 % at 30 km | Configuration flag recorded in every manifest |
| `A-FRM-04` | The convention set (NED $z$-down, right-handed, 3-2-1 Euler, Hamilton scalar-first $q_{BI}$, "to←from" transforms) is applied **uniformly** | `TO-VERIFY` | A uniformly-applied wrong convention is self-consistent and invisible to consistency tests | Hand-computed expected values: V-FRM-08, V-ATT-01 |

## Attitude — RS-002

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-ATT-01` | Post-step quaternion normalisation perturbs the solution by $O(h^{p+1})$ per step and so **preserves global 4th-order accuracy** | `TO-VERIFY` — argued in RS-002 §6, not measured | The integrator would not be 4th order, invalidating every convergence-based error estimate | V-NUM-07: measure order with normalisation on and off |
| `A-ATT-02` | Canonicalising $q_0 \ge 0$ only at output/comparison boundaries is sufficient to handle double cover | `OPEN` | Component-wise attitude comparisons would report spurious large errors | V-ATT-06 |

## State — RS-003

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-STA-01` | 14 states suffice: no actuator, controller, flexible-body, slosh or estimator states | `OPEN` (scope decision) | Any dynamics on those timescales is absent, not approximated. Actuator lag in particular changes the high-frequency response | Revisited at Phase 12 |
| `A-STA-02` | A single lumped scalar mass with a prescribed CM offset represents the vehicle adequately | `OPEN` | A multi-tank or shifting-load vehicle would need more states; CM offset would be wrong through the burn | Revisit if a multi-tank model is justified |

## Equations of motion — RS-004

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-EOM-01` | The vehicle is **rigid**: no aeroelasticity, no flexible modes, no slosh | `OPEN` — **not defended as physics**, accepted as a scope boundary | For a slender vehicle at high dynamic pressure this is likely false. Bending modes could couple with control and are entirely absent | Stated as a core limitation in every report |
| `A-EOM-02` | $\mathbf{J}$ is symmetric positive-definite, about the CM, in body axes, with products of inertia retained (not assumed diagonal) | `TO-VERIFY` | A non-PD or asymmetric tensor makes $\mathbf{J}^{-1}$ meaningless; assuming diagonal would drop the axis coupling that V-EOM-05 exists to test | V-VM-06 asserts symmetry and positive-definiteness every step |
| `A-EOM-03` | Gravity is a central inverse-square field in altitude only — no $J_2$ oblateness, no lateral variation, no third bodies | `OPEN` | Negligible at the altitudes the flat-Earth assumption permits; would matter for any extension | Bounded by `A-FRM-01`'s domain |
| `A-EOM-04` | **Gravity-gradient torque is neglected** | `OPEN` | Negligible for short atmospheric flight; not negligible for a long-duration orbital extension | Revisit with the ECI extension |

## Variable mass — RS-008

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-VM-01` | A force source's declared `force_body` and `mass_flow_rate` are **mutually consistent**. RADIUS does not enforce this — enforcing it would require modelling the exhaust, which is out of scope | `OPEN` (unenforceable contract) | An inconsistent source produces a vehicle whose momentum change does not match its mass loss: physically impossible, numerically silent | Both values recorded in the manifest so the inconsistency is detectable after the fact |
| `A-VM-02` | CM migration is **quasi-static**: its position enters the moment transfer, but momentum from the CM moving relative to the structure is neglected | `OPEN` — **magnitude unquantified** | Rotational response would be wrong by an unknown amount during rapid mass change | No claim may assert the term is small. Quantifying it is open |
| `A-VM-03` | **Jet damping is omitted.** Re-scoped 2026-09-09: it is the moment arising from **non-zero** exhaust velocity relative to the structure at an offset exit plane — now a single separable term, no longer entangled with $\dot{\mathbf{J}}\boldsymbol{\omega}$ | `OPEN` — **magnitude unbounded** | Simulated pitch/yaw damping is **optimistically low**: oscillations decay more slowly than reality, or fail to decay. Conservative for a stability study, non-conservative for a dispersion study | **No rotational-damping claim is supportable** until a reference bounds it. Highest-priority gap |
| **`A-VM-05`** | **Ejected mass leaves co-rotating, with negligible velocity relative to the structure at its exit location.** Under this assumption the angular-momentum flux **exactly cancels** $\dot{\mathbf{J}}\boldsymbol{\omega}$, so neither term appears in the rotational equation | `OPEN` (new, ADR-0009) | If the exhaust carries significant transverse relative momentum, the cancellation is only approximate and the residual **is** jet damping (`A-VM-03`). Note this is *not* an assumption that jet damping is small — it is what isolates jet damping as the whole remaining effect | V-EOM-09 / V-VM-10 verify the cancellation case. Bounding the residual needs the `A-VM-03` reference |
| `A-VM-04` | Mass depletion handled as an event, never a clamp; $m \le 0$ raises | `TO-VERIFY` | A clamp would silently create infinite propellant while producing plausible output | V-VM-03, V-VM-09 |

## Numerical methods — RS-005

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-NUM-01` | Fixed-step RK4 at $h = 10^{-3}$ s is adequate | `TO-VERIFY` — **a proposal, not a result** | Trajectory error larger than assumed, entering every downstream conclusion | V-NUM-01, V-NUM-02 measure it before any result is produced |
| `A-NUM-02` | The coupled system is **non-stiff** across the operating domain, including near mass depletion | `OPEN` — **unassessed** | An explicit method would need an uneconomically small step, or would go unstable | Examine stiffness when the mass model is first exercised |
| `A-NUM-03` | Reproducibility is bitwise on one platform, tolerance-based across platforms | `TO-VERIFY` | If same-platform bitwise determinism fails, the publication policy's argument for not publishing ensembles (ADR-0008) fails with it | V-NUM-03, V-NUM-04. **Load-bearing** |
| `A-NUM-04` | Event location by sign change assumes **at most one crossing per step** | `OPEN` | An even number of crossings inside a step is missed entirely — the event never fires and the trajectory continues through a discontinuity | Bounded by choosing $h$ small relative to event timescales; not currently checked |
| **`A-NUM-05`** | $\mathbf{T}_{BI}$ is evaluated as $[\text{formula}]/(q\cdot q)$, making it a proper rotation at the **non-unit quaternions that necessarily arise inside RK stages** | `TO-VERIFY` (new, audit finding F-3) | Using the raw formula scales every aerodynamic and propulsive force by $\lVert q\rVert^{2}$ inside stages 2–4. At $\lVert q\rVert=1.037$ the matrix is off orthonormality by 0.16 | V-FRM-09, V-NUM-09. The division is chosen over an in-stage normalisation because it introduces no branch and does not alter the stage function |

## Atmosphere — RS-006

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-ATM-01` | The layer table ($H_b$, $T_b$, $L_b$) is transcribed correctly | `TO-VERIFY` | Wrong density throughout a layer, propagating linearly into every aerodynamic force | **Check against SRC-008 directly before implementation.** V-ATM-03 compares against published tables; base pressures derived recursively so only $p_0$ is transcribed |
| `A-ATM-02` | $R^{*} = 8314.32$ J·kmol⁻¹K⁻¹ (1976 value) is used **deliberately**, not the current CODATA value | `OPEN` (intentional) | None, provided the intent is documented — the goal is to reproduce *that standard's* tables. Using a "better" constant would fail V-ATM-03 for the right reason and the wrong purpose | Cited by the atmosphere module |
| `A-ATM-03` | The atmosphere supplies thermodynamic state only — no wind, gusts, turbulence or humidity | `OPEN` | Real atmospheric variability absent. The 1976 standard is an annual mean, not any actual day | Wind enters through a separate interface (RS-007 §7). Stated as a limitation |

## Aerodynamics — RS-007

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| `A-AER-01` | Linear coefficients in $\alpha,\beta$ with rate damping are adequate for $\lvert\alpha\rvert,\lvert\beta\rvert < 10°$ | `OPEN` | Forces wrong outside the linear region; no stall, no high-$\alpha$ nonlinearity | **Validity gate raises** outside the envelope (RS-007 §6) rather than extrapolating |
| `A-AER-02` | Below $V_{\min} = 10^{-3}$ m·s⁻¹, returning exactly zero aerodynamic force is correct, and bounds the $d/2V$ damping divergence | `OPEN` | A discontinuity at the cutoff would inject a spurious impulse | V-AER-03; continuity across the cutoff not yet checked |
| `A-AER-03` | Coefficients are **arbitrary and illustrative** unless a `provenance` field says otherwise | `OPEN` — **and this is the weakest point in the specification** | Every aerodynamic result is scoped to "a hypothetical vehicle with the stated coefficients". No statement about any real configuration is licensed | Find a published generic set, or keep the scoping explicit. V-AER-08 enforces the provenance field |
| `A-AER-04` | Aerodynamic moments must be transferred from the geometric reference point to the **instantaneous CM** | `TO-VERIFY` | Omitting or mis-signing it makes static stability qualitatively wrong while every number looks reasonable | V-AER-05, V-AER-06 |
| `A-AER-05` | No Mach dependence in the initial model | `OPEN` | The model is invalid transonically — which for many trajectories is most of the flight | **Assess before producing results**, not after. May limit the initial model more than expected |
| `A-AER-06` | Aerodynamics is **quasi-steady**: forces depend on the instantaneous state, with no unsteady or history effects | `OPEN` | Rapid manoeuvres and post-stall behaviour would be misrepresented | Accepted as scope |

---

## How this register is used

- Code cites an ID at the point of dependence: `# A-VM-03: jet damping omitted`.
- Every experiment manifest lists the IDs its result depends on (`docs/PROVENANCE.md` §3), so that a
  refuted assumption can be traced to every result it touched.
- A refuted assumption moves to `REFUTED` with its consequences traced. It is not deleted.
- The consequence column, not the assumption text, is what a reviewer should read first.
