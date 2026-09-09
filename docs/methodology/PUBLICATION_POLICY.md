# RADIUS — Publication and Data Governance Policy

**Status:** Authoritative. This document governs every publication decision in RADIUS.
**Established:** 2026-09-09 · ADR-0008
**Companion:** `infrastructure/publication_checklist.md` — the executable pre-push audit.

---

## 1. What this repository is

> A **curated, auditable, reproducible public research record.**

It is deliberately *not* a mirror of the local workspace. It is not a backup, a laboratory notebook,
a figure cache, an archive of every run, or a transcript of how the work was produced.

The test a reader should be able to apply: from this repository alone, a technically competent
stranger can determine **what RADIUS is, why it exists, how it is formulated, how it is implemented,
how it was verified, what experiments were run, what evidence supports each claim, what limitations
remain, and how to reproduce any published result** — without access to the author's machine.

Everything necessary for that is published. Almost nothing else is.

### The governing question

Before any artifact enters the repository:

> **Would a future researcher, reviewer or engineer learn something important from having *this exact
> artifact* in the public record?**

If no, it stays local. The objective is to maximise *scientific credibility × reproducibility ×
clarity* while minimising *clutter × ambiguity × unnecessary data exposure*. Adding files serves none
of the first three and worsens all of the last three unless the file earns its place.

---

## 2. Classification

Every artifact falls into exactly one of five classes. The class determines the handling.

### 2.1 PUBLIC BY DEFAULT

Committed as a matter of course, subject only to the pre-push audit.

| Artifact | Why |
|---|---|
| Source code implementing the model — dynamics, frames, attitude, integration, atmosphere, aerodynamics, force/moment interfaces, state representation, simulation infrastructure | The implementation *is* the methodological detail. A result that rests on an implementation choice cannot be audited without it |
| Tests — verification, regression, property | Tests are the evidence that verification happened. Publishing a claim of verification without them is an assertion |
| Specifications and reports in `docs/` | The scientific communication artifacts |
| ADRs in `docs/decisions/` | Why the design is what it is, including rejected alternatives |
| `docs/assumptions.md` | The register that makes every result's scope explicit |
| `research/SOURCES.md`, `research/RESEARCH_LOG.md` | Provenance of ideas and decisions |
| Experiment definitions — `experiments/EXP-XXXX/{README.md, config.yaml, manifest.json}` | The reproducibility artifact |
| Configuration files and seeds | Without these a result is not reproducible |
| Curated result files — convergence tables, error summaries, benchmark outputs, the values behind published figures | Small, interpretable, and the evidence for the claims |
| Figures that communicate a conclusion, plus the script that generates them | The script is the primary artifact; the image is its rendering |
| `handoffs/` state summaries | Continuation between working sessions |
| Dependency/environment specification | Required for reproduction |

### 2.2 PUBLIC ONLY AFTER REVIEW

Publishable, but never automatically. Each instance is reviewed and deliberately selected.

| Artifact | The review question |
|---|---|
| Derived datasets above a few hundred kilobytes | Is a reduced representation sufficient? Is every column documented? |
| Reference trajectories used as regression fixtures | Is it interpretable standalone? Does it carry full metadata? Is it small? |
| Notebooks | Is it maintained, reproducible, cleaned of exploratory cells, free of local paths, and *scientifically useful* — or is it just the analysis that happened to be used? |
| Figures generated in bulk | Which one communicates the conclusion? Publish that one, not the sweep |
| Negative results and terminated experiments | Is this a **meaningful negative result** (a conclusion) or an **ordinary development failure** (clutter)? See §6 |
| Experimental or incomplete implementations | Improve it until publishable, or keep it out. Do not publish code merely because it exists |
| Third-party material | Does its licence permit redistribution, and are the required notices preserved? If uncertain, do not publish — cite and link instead (§8) |

### 2.3 PRIVATE / LOCAL

Retained locally, never committed. These are not shameful; they are simply not part of the record.

Raw and intermediate simulation output · full Monte Carlo trajectory ensembles · per-run directories
(`run_000001/`…) · debugging plots · exploratory parameter sweeps · profiling output · local caches
and build artifacts · editor and IDE configuration · local environment files · shell history ·
superseded drafts · intermediate calculations that no conclusion rests on.

**Rule:** preserve locally → analyse → identify the scientifically relevant result → produce a
curated artifact → document the experiment → publish the report and the reproducibility
configuration. A simulation that produces 100 000 files does not thereby produce 100 000 publishable
artifacts.

### 2.4 NEVER PUBLISH

No review, no exception, no justification accepted.

- Credentials of any kind — API keys, tokens, passwords, SSH private keys, cloud credentials,
  certificates, `.env` files, authentication exports.
- Personal information — personal email addresses, phone numbers, home addresses, private account
  identifiers, personal documents, private correspondence. **This includes the git author and
  committer identity**, which is published alongside file contents and is not covered by
  `.gitignore`.
- Local machine information — absolute paths, usernames, home directories, machine names,
  OS-specific private configuration.
- AI interaction records — conversation transcripts, private prompts, internal reasoning, agent
  logs, tool logs, unreviewed AI-generated notes. See §7.
- Third-party copyrighted material redistributed without the right to do so — papers, PDFs,
  proprietary datasets, proprietary source, figures, proprietary parameter tables.
- Content outside the project's scope boundary (`CLAUDE.md`) — propulsion hardware detail,
  operational vehicle parameters, targeting or deployment procedure.

### 2.5 FUTURE ARCHIVAL / EXTERNAL-DATA CANDIDATES

Material with genuine scientific value that Git is the wrong mechanism for.

| Candidate | Why not Git |
|---|---|
| Large Monte Carlo ensembles that a future study might reuse | Git stores every version forever; a 2 GB ensemble is 2 GB in the clone, permanently |
| High-rate full-state trajectory archives | Same, and regenerable from config + seed |
| Any dataset intended for citation in its own right | Deserves a DOI and a persistent identifier, which GitHub does not provide |

**Mechanism when needed:** an archival research data repository (Zenodo, figshare, an institutional
repository) with a DOI, referenced from the RADIUS report. Git LFS is a possibility but is not
adopted, and would need its own ADR — it changes clone behaviour for everyone and is not a substitute
for asking whether the data needs publishing at all.

**Current status:** no such dataset exists. This class is defined in advance so the decision is made
by policy rather than under pressure when the first large ensemble appears.

---

## 3. Raw data

Raw simulation output is **not** public by default. Four questions decide it, and all four must pass.

1. **Is it necessary?** Could another researcher reproduce the result from source code +
   configuration + seed + parameters + environment specification + summarised results? If yes, do not
   publish the raw dataset. RADIUS is deterministic by design specifically so that this answer is
   usually yes.
2. **Is it interpretable standalone?** A downloader must be able to determine: what generated it,
   what each column means, its units, its coordinate frame, its sampling rate, the parameter
   configuration, the software version, and the experiment ID. If not, it is not publishable *by
   itself* — and adding the metadata is the fix, not waiving the requirement.
3. **Is it appropriately sized?** Technical capacity to store it is not a reason to.
4. **Is it reproducible?** Prefer publishing what regenerates it.

### Preferred hierarchy

```
experiment definition → configuration → seed / deterministic specification → simulation code
    → curated result → figure/table → research report
```

Instead of 10 000 Monte Carlo trajectory files, publish the experiment definition, the config, the
manifest, a summary table, the figures, and the report. Reviewed and deliberately selected — not as
an automatic by-product of running something.

---

## 4. Curated result files

Small derived datasets are welcome, with conditions.

**Naming.** A file called `results.csv` is not acceptable. Use
`EXP-0042_rk4_timestep_convergence.csv` — experiment ID, then what it contains.

**Metadata.** Every published result file carries, in a header or a sibling `README.md`:

```
experiment_id · model_version (commit) · configuration (path + hash) · units · coordinate_frame
timestamp · seed · quantity · value · uncertainty
```

An unexplained CSV is not evidence. It is a file.

**`results/` structure.** Curated and interpretable, one directory per experiment, each with a
`README.md` explaining what it contains — never a dump of per-run directories.

---

## 5. Figures

Publish figures that communicate a conclusion: convergence plots, analytical-vs-numerical
comparisons, trajectory comparisons, attitude propagation error, sensitivity analyses, uncertainty
envelopes, validation comparisons.

Do not publish automatically generated plots, debugging plots, visually redundant plots, plots with
unclear axes or unstated units, or notebook exports.

**The script is the artifact.** Where practical, publish the script and configuration that generate
the figure and treat the image as a rendering of it. A PNG whose generating code is absent cannot be
checked, corrected, or regenerated at a different scale.

---

## 6. Failed experiments and negative results

The distinction is between a **conclusion** and **clutter**.

**Meaningful negative result — publish.** A hypothesis was tested and failed; a proposed method did
not meet a pre-declared gate; an approach was abandoned for a stated reason. These belong in the
research log and, if substantial, a report. Hiding a falsified hypothesis is prohibited: it appears
in the report, the summary, and the conclusions.

**Ordinary development failure — do not publish.** Syntax errors, broken paths, debugging runs,
transient numerical instability during development, abandoned sweeps, typo-driven runs. Publishing
these is not transparency; it is noise that makes the real negative results harder to find.

The public repository demonstrates *scientific transparency*, not *development history*.

---

## 7. AI-assisted development

AI assistance does not license publishing the interaction. Never committed: conversation
transcripts, private prompts, internal reasoning, agent or tool logs, temporary AI-generated notes,
or unreviewed AI claims.

The repository contains **human-reviewed engineering artifacts**. Where AI assistance materially
affected methodology, it may be acknowledged — as a statement of method, not as an archive.

The research log records *decisions and their rationale*, not a chronological diary of interactions
or terminal commands.

---

## 8. Third-party material

Do not copy third-party papers, PDFs, datasets, source, figures, images, documentation or parameter
tables into the repository for convenience. Instead: cite, link, record bibliographic metadata, and
document what was used and for what (`research/SOURCES.md`).

Redistribute only where the licence explicitly permits it and the required attribution and licence
notices are preserved. **If uncertain, do not publish.**

---

## 9. Licensing

RADIUS currently carries **no licence** (ADR-0007): no reuse rights are granted, and the README says
so plainly rather than leaving it to inference.

Before any release presented as final:

1. decide the RADIUS licence explicitly;
2. identify every third-party dependency's licence;
3. preserve required notices;
4. document any non-redistributable dependency.

Never apply an open-source licence to material the project does not have the right to distribute.

---

## 10. Provenance

Every published number must be traceable, from the repository alone, along:

```
Result → Experiment ID → Configuration → Code commit → Model assumptions → Seed
       → Input data → Analysis method → Research report
```

The repository must answer **"where did this number come from?"** without access to the developer's
machine. Details in `docs/PROVENANCE.md`.

---

## 11. Maturity labelling

The repository may be public while incomplete. What it may not do is misrepresent its maturity.

| Label | Meaning |
|---|---|
| **Research / Architecture** | Specification only. Nothing implemented |
| **Experimental** | Implemented, unverified. No claim supportable |
| **Preliminary** | Implemented, partially verified. Claims provisional and scoped |
| **Verified** | Implementation demonstrated to solve the intended equations correctly, by stated tests |
| **Validated** | Model demonstrated adequate against **independent reference data**, for a **stated purpose**, to a **stated tolerance** |

"Validated" is never applied on the strength of passing tests. RADIUS's current label is **Research /
Architecture**, and the README states it.

---

## 12. Staging discipline

`.gitignore` prevents accidents. It does not constitute review, and a file it fails to match is not
thereby approved.

- **`git add .` is not a publication mechanism.** Stage intentionally, by path.
- Inspect `git status` and `git diff --cached` before every meaningful push.
- Run the audit in `infrastructure/publication_checklist.md` over the **working tree and the git
  history** — they are separate risks. A secret removed in a later commit is still published.

If any critical item is uncertain: **do not push. Flag it for researcher review.**

---

## 13. Relationship to AURA's policy

AURA's public repository emphasises methodology, experiment definitions, statistical results,
evidence, reports, provenance, reproducibility and curated outputs — over being an archive of
everything generated. RADIUS applies the same philosophy to simulation, numerical experiments,
verification, validation, uncertainty propagation, trajectory studies and model comparisons.

The two projects share a **research-record philosophy**. They share no implementation dependency
(ADR-0002). This document was written independently and deliberately duplicates the parts of AURA's
policy that generalise, rather than importing them.
