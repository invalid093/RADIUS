# RADIUS — Provenance and Reproducibility

**Status:** Specification. No experiment has yet been run, so nothing described here is exercised.
**Governed by:** `docs/methodology/PUBLICATION_POLICY.md` §10

---

## 1. The requirement

The repository must answer, from itself alone:

> **Where did this number come from?**

Not "roughly how was it produced" — the specific chain, for a specific value in a specific figure,
without access to the author's machine.

```
Result value
  → Experiment ID          which deliberate experiment produced it
  → Configuration          exact parameters, with a content hash
  → Code commit            the exact source that ran
  → Model assumptions      which registered assumptions it depends on
  → Seed                   the deterministic specification, if stochastic
  → Input data             what went in, identified and hashed
  → Analysis method        how raw output became this number
  → Research report        what it was taken to mean, and with what limitations
```

A result that cannot be walked back along this chain is not a published result. It is a number.

---

## 2. Experiment identity

Experiments are `EXP-NNNN`, allocated in order, never reused, never renumbered — including for
experiments that were abandoned. A gap in the numbering is information.

```
experiments/EXP-0001/
    README.md        research question, hypothesis, model, parameters, expected behaviour,
                     acceptance criteria, output artifacts, result location, status
    config.yaml      every parameter. No parameter lives in code
    manifest.json    machine-readable provenance record (§3)
```

**Registered before the run, not after.** The entry is created with status `PLANNED`, containing the
acceptance criteria, *before* anything executes. Writing acceptance criteria after seeing the output
is how a threshold gets chosen to fit the result, and the ordering is the only defence against it.

Status transitions: `PLANNED` → `RUNNING` → `COMPLETE` | `FAILED` | `ABANDONED`. A `FAILED` or
`ABANDONED` experiment keeps its entry and records why.

Raw output does not go in the experiment directory. The directory defines the experiment; results
live in `results/EXP-NNNN/`.

---

## 3. Manifest

`manifest.json` is written by the run, not by hand.

```json
{
  "experiment_id": "EXP-0001",
  "title": "...",
  "status": "COMPLETE",
  "created_utc": "...",
  "completed_utc": "...",
  "code": {
    "commit": "<40-hex>",
    "dirty": false,
    "radius_version": "0.1.0"
  },
  "configuration": {
    "path": "experiments/EXP-0001/config.yaml",
    "sha256": "<hex>"
  },
  "environment": {
    "python": "3.13.15",
    "numpy": "2.5.2",
    "platform": "<os>-<arch>",
    "note": "Recorded for interpretation; cross-platform bitwise identity is NOT claimed (§5)"
  },
  "seeds": {
    "master_seed": 20260909,
    "derivation": "counter-based; see docs/PROVENANCE.md section 4"
  },
  "inputs": [{"path": "...", "sha256": "..."}],
  "outputs": [{"path": "...", "sha256": "...", "published": true}],
  "assumptions": ["A-FRM-01", "A-ATM-02"],
  "acceptance_criteria": ["..."],
  "outcome": "..."
}
```

**`dirty: true` invalidates the result.** A run against uncommitted changes cannot be reproduced,
because the code that produced it does not exist anywhere retrievable. Such a run is development,
not an experiment, and is not published.

**`assumptions`** is the field most often omitted and most often needed: it is what lets a reader
determine, years later, whether a result survives a refuted assumption.

---

## 4. Determinism and seeds

Every stochastic component takes an **explicit seed**. No component reads global RNG state, and no
component seeds itself from the clock, the process ID, or a hash of anything environmental.

### Seed derivation

Seeds are derived, not drawn. Given a `master_seed` recorded in the configuration:

```
seed(experiment_id, stream_name, replicate_index)
    = SHA-256(master_seed ‖ experiment_id ‖ stream_name ‖ replicate_index)  → 64-bit integer
```

Counter-based, so that:

- replicate *k* is reproducible **without running replicates 0…k−1**, which matters for
  investigating one bad Monte Carlo sample out of ten thousand;
- independent streams (initial-condition perturbation, atmospheric disturbance, sensor noise) cannot
  accidentally share a sequence;
- the full ensemble is regenerable from one integer in a config file, which is why the ensemble
  itself need not be published (policy §3).

Publishing the master seed and the derivation rule is what makes not publishing the ensemble
legitimate.

---

## 5. What "reproducible" claims, exactly

An honest statement, because the usual one is overstated:

| Claim | Status |
|---|---|
| Same commit, same config, same seed, **same machine and library versions** → bitwise-identical output | **Claimed.** Enforced by fixed-step integration, no adaptive control, fixed operation order, no threading, no global RNG. Tested by V-NUM-03 |
| Same commit, same config, same seed, **different platform** → bitwise-identical output | **Not claimed.** Floating-point summation order, FMA contraction, and library differences all break it |
| Same commit, same config, same seed, different platform → agreement within a stated tolerance | **Claimed**, with the tolerance stated per result |

Cross-platform bitwise reproducibility would require pinned compiler flags, disabled FMA, and a
controlled BLAS. That cost is not justified for RADIUS, and claiming it without paying it would be
false. The environment is recorded in the manifest precisely so that a cross-platform discrepancy can
be recognised as such rather than mistaken for a bug.

---

## 6. Result artifacts

`results/EXP-NNNN/` contains curated, interpretable output only.

```
results/EXP-0001/
    README.md                              what this is, how it was produced, what it shows
    EXP-0001_rk4_timestep_convergence.csv  named for its experiment and content
    figures/
        EXP-0001_fig01_order_of_accuracy.png
        make_figures.py                    the figure's primary artifact
```

Every published data file carries: `experiment_id`, `model_version` (commit), `configuration` path
and hash, `units`, `coordinate_frame`, `timestamp`, `seed`, and per row `quantity`, `value`,
`uncertainty`.

Never `results.csv`. Never a per-run dump.

---

## 7. Assumptions in the chain

`docs/assumptions.md` is part of provenance, not documentation garnish. Each assumption has an ID,
a status (`OPEN` / `TO-VERIFY` / `VALIDATED` / `REFUTED`), a stated consequence if wrong, and an
action. Code cites the ID where it depends on one.

An assumption that is later refuted is **never silently deleted**. It moves to `REFUTED`, and every
result whose manifest lists that ID is traceable — which is the entire reason the manifest carries
the list.

---

## 8. Current state

`FACT`: nothing in this document is implemented. There are no experiments, no manifests, no seeds and
no results. It is specified now so that the first experiment is registered correctly rather than
retrofitted — provenance added after the fact is a reconstruction, and a reconstruction is exactly
what provenance is supposed to make unnecessary.
