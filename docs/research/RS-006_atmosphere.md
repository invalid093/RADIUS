# RS-006 — Atmosphere Model

**Status:** Specification. Not implemented, not verified.
**Depends on:** RS-001 (altitude definition), `docs/methodology/NOTATION_AND_CONVENTIONS.md` §7
**Primary source:** SRC-008 — *U.S. Standard Atmosphere, 1976*

---

## 1. What the atmosphere model must supply

The aerodynamic model (RS-007) needs, as functions of altitude:

| Quantity | Symbol | Unit | Needed for |
|---|---|---|---|
| Density | $\rho$ | kg·m⁻³ | dynamic pressure — the dominant sensitivity |
| Pressure | $p$ | Pa | pressure-dependent force terms; completeness |
| Temperature | $T$ | K | speed of sound |
| Speed of sound | $a$ | m·s⁻¹ | Mach number, hence coefficient lookup |

Density is the one that matters most: aerodynamic force is linear in $\rho$ and $\rho$ varies by
roughly a factor of $e$ every 8 km. An error in the atmosphere model appears directly, and
proportionally, in every aerodynamic force.

---

## 2. Two models, for two different purposes

RADIUS implements **both**, deliberately.

### 2.1 Exponential atmosphere — the transparent baseline

$$\rho(h) = \rho_0 \exp\!\left(-\frac{h}{H_s}\right), \qquad \rho_0 = 1.225\ \text{kg·m}^{-3},\quad H_s \approx 8\,500\ \text{m}$$

One line, one parameter, everywhere differentiable, and **analytically integrable in certain
trajectory problems** — which is its entire purpose. It exists so that a closed-form or
semi-analytical reference solution is available for testing the *coupling* between atmosphere,
aerodynamics and dynamics. With the layered model there is no such reference, and a discrepancy
cannot be localised.

`LIMITATION`: it is a crude fit. It has no temperature structure, so no speed of sound, so no Mach
number. It is a verification instrument, not a physical model, and no result is reported from it.

### 2.2 U.S. Standard Atmosphere 1976 — the reference model

Piecewise-linear temperature profile in geopotential altitude, with hydrostatic pressure integration
per layer. Valid to 86 km geometric; RADIUS implements the region to 84.852 km geopotential, which
covers everything the flat-Earth assumption (`A-FRM-01`) permits anyway.

Chosen because it is **published, defining, and tabulated**: agreement with its tables is a
falsifiable check against an external document, which is the strongest form of verification available
to RADIUS at this stage.

---

## 3. Equations — U.S. Standard Atmosphere 1976

### 3.1 Geopotential altitude

$$H = \frac{r_0\,h}{r_0 + h}, \qquad r_0 = 6\,356\,766\ \text{m}$$

$H$ absorbs the variation of gravity with altitude into the vertical coordinate, so the hydrostatic
relation can use a constant $g_0$. `CALCULATION`: at $h = 30$ km, $H \approx 29.86$ km — a 0.47 %
difference. Ignoring the distinction is a common and quiet error, so the conversion is an explicit
named function and never inlined.

**Note on consistency:** $r_0$ here is the 1976 standard's *effective* radius for this purpose. It is
not the same quantity as the $R_E$ used for gravity in RS-001 §3.4, and the two must not be unified
"for tidiness" — they serve different definitions.

### 3.2 Layer structure

Within layer $b$, from base geopotential altitude $H_b$ with base temperature $T_b$ and lapse rate
$L_b$:

$$T(H) = T_b + L_b\,(H - H_b)$$

$$p(H) = \begin{cases}
p_b\left[\dfrac{T_b}{T_b + L_b (H - H_b)}\right]^{\frac{g_0 M_0}{R^{*} L_b}} & L_b \neq 0\\[2ex]
p_b\,\exp\!\left[\dfrac{-g_0 M_0 (H - H_b)}{R^{*} T_b}\right] & L_b = 0
\end{cases}$$

$$\rho = \frac{p\,M_0}{R^{*} T}, \qquad a = \sqrt{\frac{\gamma R^{*} T}{M_0}}$$

Constants per `NOTATION_AND_CONVENTIONS.md` §7: $g_0 = 9.80665$ m·s⁻², $R^{*} = 8314.32$
J·kmol⁻¹K⁻¹, $M_0 = 28.9644$ kg·kmol⁻¹, $\gamma = 1.40$.

### 3.3 Layer table

**Unit trap (audit finding F-6).** The table below lists $L_b$ in **K·km⁻¹**, the form in which it
is published. The barometric formulas of §3.2 require **K·m⁻¹**. The conversion is a factor of
$10^{-3}$ applied at load time, in a named function — a missed conversion puts a factor of 1000 in an
exponent and makes $p$ wrong by many orders of magnitude.

| $b$ | $H_b$ (km) | $T_b$ (K) | $L_b$ (K·km⁻¹) |
|---|---|---|---|
| 0 | 0 | 288.15 | −6.5 |
| 1 | 11 | 216.65 | 0.0 |
| 2 | 20 | 216.65 | +1.0 |
| 3 | 32 | 228.65 | +2.8 |
| 4 | 47 | 270.65 | 0.0 |
| 5 | 51 | 270.65 | −2.8 |
| 6 | 71 | 214.65 | −2.0 |
| — | 84.852 | 186.946 | (upper limit) |

**Base pressures $p_b$ are deliberately absent from this table.**

Only $p_0 = 101\,325$ Pa is an input. Every subsequent $p_b$ is computed by evaluating the layer
formula at the top of the preceding layer, at load time.

This is a design decision with a specific purpose: hard-coding eight base pressures means eight
opportunities for a transcription error, each producing a discontinuity at one layer boundary that is
easy to miss in a plot. Deriving them recursively means one transcribed constant, and any error in
the lapse table or the formula shows up as a *discontinuity*, which V-ATM-02 detects automatically.
The check becomes structural rather than a matter of proofreading.

`ASSUMPTION` `A-ATM-01`: the $T_b$ values are themselves transcribed and must be checked against
SRC-008. The recursion protects the pressures, not the temperatures.

---

## 4. Validity and behaviour outside it

| Condition | Behaviour |
|---|---|
| $H < 0$ (below sea level) | Layer 0 extrapolates smoothly; permitted, but flagged in output |
| $H > 84.852$ km | **Raises.** Does not extrapolate, does not clamp |
| Non-finite altitude | Raises |

**A model asked for a value outside its stated domain raises rather than returning a number.** This
follows the invariant RADIUS shares with AURA: *a check that cannot be evaluated must not return a
pass*. Clamping the density at the top of the table would let a diverging trajectory continue to
produce plausible numbers, which converts an obvious failure into a subtle one.

---

## 5. What the model is not

`LIMITATION`, and it must accompany any result depending on the atmosphere:

- It is an **idealised annual-mean standard**, not a forecast and not a description of the atmosphere
  on any particular day. Real density at a given altitude deviates substantially with latitude,
  season and weather.
- Therefore **agreement with the published tables is verification, not validation.** It shows RADIUS
  implements the standard correctly. It says nothing about whether the standard describes the air a
  vehicle would actually fly through.
- No wind, no gusts, no turbulence, no humidity. Wind enters as a separate interface in RS-007 §5;
  the atmosphere model supplies only thermodynamic state (`A-ATM-03`).

---

## 6. Verification tests this specification requires

| ID | Test | Passes if |
|---|---|---|
| V-ATM-01 | Sea-level values: $\rho = 1.225$ kg·m⁻³, $a = 340.29$ m·s⁻¹, $p = 101325$ Pa, $T = 288.15$ K | relative error $<10^{-5}$ |
| V-ATM-02 | **Continuity at every layer boundary**: $T$, $p$, $\rho$ evaluated from below and above | relative discontinuity $<10^{-12}$ |
| V-ATM-03 | Comparison against the SRC-008 published table at a set of altitudes spanning all layers | relative error $<10^{-4}$ (tolerance covers table rounding) |
| **V-ATM-09** | Lapse-rate unit conversion: the K·km⁻¹ table value reaches the formula as K·m⁻¹ | exponent for the troposphere $=-5.2559$ |
| V-ATM-04 | Geopotential/geometric conversion round trip | $<10^{-9}$ relative |
| V-ATM-05 | Monotonicity: $p$ and $\rho$ strictly decrease with altitude throughout the domain | no violation |
| V-ATM-06 | Out-of-domain altitude raises; does not clamp or extrapolate | exception raised |
| V-ATM-07 | Hydrostatic consistency: $dp/dH \approx -\rho g_0$ by finite difference | relative error $<10^{-4}$ |
| V-ATM-08 | Exponential model reproduces $\rho_0$ at $h=0$ and the correct scale height | analytic |

**Partially verified during the pre-implementation audit** (`CALCULATION`, 2026-09-09), against the
published values: sea-level $\rho = 1.22500$ kg·m⁻³ ✓, $a = 340.294$ m·s⁻¹ ✓; at 11 km geopotential
$T = 216.65$ K ✓ and $p = 22632.1$ Pa against a published 22632 ✓; troposphere exponent $-5.2559$ ✓.
The formulation and constants are correct. The remaining layers are still unchecked (`A-ATM-01`).

**V-ATM-03 is the one that matters.** It is a comparison against an external published document, and
it is the only check here that could fail because RADIUS misunderstood the standard rather than
mis-implemented its own intention. The others verify self-consistency, and self-consistency is
compatible with being uniformly wrong.

**V-ATM-07 is an independent check on the same thing by a different route** — the hydrostatic relation
is the physics the layer formulas were integrated from, so recovering it by finite differencing
confirms the exponents were transcribed correctly.

---

## 7. Assumptions registered

`A-ATM-01`, `A-ATM-02`, `A-ATM-03` — see `docs/assumptions.md`. `A-ATM-02` is the deliberate use of
the 1976 gas constant rather than the current CODATA value; the reason is that the goal is to
reproduce *that standard's* tables, and a "better" constant would break V-ATM-03 for the right reason
and the wrong purpose.

---

## 8. Open questions

1. Are the $T_b$ and $H_b$ values in §3.3 correct as transcribed? They are recorded from standard
   references and **must be checked against SRC-008 directly** before implementation. Flagged rather
   than assumed.
2. Does the flat-Earth validity domain (RS-001 §4, ~10 km range) make altitudes above ~30 km
   unreachable in practice, given the geometry? If so, implementing layers 4–6 is speculative work.
   Cheap enough to keep, but it should not be described as capability the project can use.
2b. **Dynamic viscosity $\mu$ is absent from the interface.** Not needed by the current aerodynamic
   model (no Reynolds dependence), but any future coefficient set with Reynolds-number dependence
   requires it. Sutherland's law is in the same defining document. Not added now — an unused quantity
   is one more thing to verify — and the return is a structure, so adding it is non-breaking.
3. Is a scale height of 8500 m the right choice for the exponential baseline, or should it be fitted
   to match the layered model over the altitude band of interest? A fitted value would make
   comparisons between the two models more informative.
