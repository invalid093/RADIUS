# RADIUS ↔ AURA — Conceptual Interface

**Status:** Conceptual. **Not implemented, and deliberately so.**
**Governed by:** ADR-0002 (RADIUS is independent of AURA)

---

## 1. What this document is and is not

It is a sketch of how two separate projects might eventually meet, recorded so that RADIUS's output
design does not accidentally foreclose it.

It is **not** a specification, not a commitment, and not a licence to add anything to RADIUS "because
AURA will need it". No RADIUS design decision may be justified by this document. If a proposed output
format is defensible only by pointing here, it is not defensible.

---

## 2. The division

| | RADIUS | AURA |
|---|---|---|
| Question | *How does the vehicle state evolve, and how accurately can we compute it?* | *What can be inferred from observations of a system, and how confident may we be?* |
| Domain | physics, dynamics, environment, numerical integration, trajectory and state evolution | uncertainty, reliability, diagnosability, fault analysis, statistical inference, experiment validity, provenance, evidence |
| Object of study | the vehicle | the inference procedure, and the experiment itself |
| Ground truth | **is** the truth, by construction | must be inferred |

The complementarity is real. AURA's central difficulty is that inference methods are usually evaluated
on systems whose true state is unknown, so a method's performance must be argued rather than measured.
A simulator supplies a system whose truth is known exactly — which turns "is this method good?" from a
debate into a measurement.

---

## 3. What RADIUS would expose

All of it is output RADIUS produces **for its own reasons**. That is the test: if a listed item is not
independently justified by RADIUS's own needs, it does not belong in RADIUS.

| Exposed | Independently justified because |
|---|---|
| State trajectories $\mathbf{x}(t)$ | It is the primary output of a simulator |
| Derived observables — $\alpha$, $\beta$, $\bar q$, Mach, load factor | Needed for reporting and for the aerodynamic model |
| Model parameters and configuration | Reproducibility (`docs/PROVENANCE.md`) |
| Environmental conditions along the trajectory | Interpretation of aerodynamic results |
| **Perturbation abstractions** — parameter offsets, initial-condition dispersions, force disturbances | RADIUS's own uncertainty-propagation phase (Phase 13) needs exactly this |
| Deterministic seeds and the derivation rule | Reproducibility, and what makes not publishing ensembles legitimate |
| Experiment configuration and manifest | Provenance |

**Note on the perturbation interface.** RADIUS calls these *perturbations*, not *faults*. The
distinction is not cosmetic. A perturbation is a deviation from nominal parameters — a mathematical
object RADIUS can define precisely. A *fault* is a specific physical failure mode drawn from a
taxonomy, and the taxonomy is a modelling commitment RADIUS has not made and does not need. If AURA
wishes to interpret a particular perturbation as a fault, that interpretation belongs to AURA.

Keeping RADIUS's vocabulary at the level it can defend is what prevents it from quietly acquiring
AURA's modelling commitments.

---

## 4. What AURA might do with it

Uncertainty propagation · statistical analysis of ensembles · diagnosability and distinguishability
experiments · reliability analysis · perturbation studies · experiment evidence with known ground
truth.

Speculative. RADIUS takes no position on whether any of it is worth doing.

---

## 5. The coupling direction

```
RADIUS  ──emits──▶  documented output files  ──read by──▶  AURA adapter (lives in AURA)
```

Three rules, all consequences of ADR-0002:

1. **RADIUS emits, AURA consumes.** RADIUS never calls AURA and never knows it exists.
2. **The adapter lives in AURA.** If a translation between RADIUS's output and AURA's data model is
   needed, AURA owns it. RADIUS's format is a published contract, not a dependency.
3. **RADIUS's format is designed for RADIUS.** Self-describing, documented, versioned, and justified
   by RADIUS's own reproducibility needs. That it happens to be consumable is a consequence of being
   well-documented, not a design goal.

### Why the coupling must not be shared code

If AURA is to use RADIUS as a test subject, RADIUS must be an **independent** object of study. A
simulator that imports its evaluator's schemas, gates and assumptions is not independent: an error in
the shared layer corrupts the system and its evaluation *identically*, and therefore undetectably.
The duplicated code is a few hundred lines. The independence is the entire methodological premise.

---

## 6. What must be true before this is attempted

Preconditions, not a roadmap. Each is currently unmet.

1. **RADIUS is verified.** A test subject whose own correctness is unestablished cannot ground a claim
   about an inference method — a poor result would be unattributable between the method and the
   simulator.
2. **RADIUS's limitations are quantified**, not merely listed. Today several are unbounded:
   jet damping (`A-VM-03`), CM-motion momentum (`A-VM-02`), and the coefficient provenance problem
   (`A-AER-03`). An inference experiment on a model with unbounded modelling error measures the error,
   not the method.
3. **RADIUS's uncertainty propagation works on its own terms** (Phase 13), independently of anything
   AURA does with it.
4. **A specific question exists** that requires the combination. "These two projects could be
   connected" is not a research question. Building an integration in search of one is how a project
   acquires infrastructure it never uses.

`INTERPRETATION`: precondition 4 is the binding one. AURA's own record shows a research question that
was terminated and a novelty gate that returned FAIL — which is a reason to be *more* careful about
what question a combined experiment would answer, not less.

---

## 7. Current status

Nothing implemented. Nothing scheduled. No RADIUS code, configuration, schema or dependency refers to
AURA, and none may.

The correct next action regarding this interface is **none**, until RADIUS is verified and a specific
question exists.
