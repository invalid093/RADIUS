# ADR-0008 — Publication architecture and data governance

**Date:** 2026-09-09 · **Status:** Accepted
**Amends:** ADR-0001 (directory timing)

## Context

RADIUS is a public repository, and it will eventually produce simulation output at a scale where the
question "does this get committed?" has to be answered thousands of times. Answered case by case,
under time pressure, with the files already on disk, the answer drifts toward "commit it, storage is
cheap" — and the repository becomes an archive rather than a record.

Three specific pressures make the default wrong:

1. **Monte Carlo output is enormous and worthless individually.** An uncertainty study generates
   thousands of trajectories. Any one of them is uninterpretable; the ensemble statistic is the
   result. Committing the ensemble adds gigabytes and communicates nothing.
2. **Generated artifacts are self-justifying.** A file that exists feels like it should be kept. The
   fact that a simulation produced something is not evidence that anyone needs it.
3. **The costs are asymmetric and delayed.** Git keeps every version forever. A large blob or a
   leaked secret is permanent in the history of every clone, and is not fixed by deleting the file
   later.

The policy therefore has to exist *before* the first large run, not after.

## Decision

Adopt a **deny-by-default publication architecture**, specified in
`docs/methodology/PUBLICATION_POLICY.md` and enforced at three layers:

1. **Policy** — five artifact classes (public by default; public only after review; private/local;
   never publish; future archival candidate), with the classification rules and the governing
   question: *would a future researcher learn something important from having this exact artifact in
   the public record?*
2. **Mechanism** — `.gitignore` rewritten to deny each class of generated artifact wholesale and
   re-include named curated exceptions, rather than listing known-bad patterns. Notebooks are denied
   by default. AI transcripts, prompts and agent logs are denied by default.
3. **Procedure** — `infrastructure/publication_checklist.md`, a pre-push audit covering the working
   tree **and the git history** as separate risks, plus scientific, provenance, legal, repository
   and scope audits.

Supporting decisions:

- **`docs/PROVENANCE.md`** specifies the chain every published number must be traceable along:
  result → experiment ID → configuration → commit → assumptions → seed → input → analysis → report.
  Experiments are registered `PLANNED` before they run, so acceptance criteria cannot be chosen after
  seeing the output.
- **Seeds are derived, not drawn** — counter-based from a master seed, so a whole ensemble is
  regenerable from one integer in a config file. This is what makes *not* publishing the ensemble
  legitimate rather than merely convenient.
- **Reproducibility is claimed honestly**: bitwise on the same platform, tolerance-based across
  platforms. The stronger claim would require pinned compiler flags and a controlled BLAS, which
  RADIUS does not do.
- **GitHub secret scanning and push protection are enabled** as a backstop — they detect credential
  formats and know nothing about personal information, machine paths, scope violations or
  unsupported claims.

**Amendment to ADR-0001.** `infrastructure/` is created now rather than at Phase 7, because the
publication checklist is content with a documented purpose and needs a home. The principle in
ADR-0001 is unchanged — directories appear when they have content — and this is an instance of it,
not an exception to it.

## Alternatives considered

- **Decide case by case as artifacts appear.** Rejected. This is the default that produces archive
  repositories. The decision is easiest and most honest before any of the artifacts exist and none of
  them are anyone's work yet.
- **Publish everything for maximum transparency.** Rejected, and it is a misreading of what
  transparency is for. Transparency means a reader can *check* a claim. Ten thousand undocumented
  trajectory files make checking harder, not easier — the signal is buried. The transparency
  obligation is discharged by publishing the code, configuration, seed and method that regenerate the
  data, which is a stronger guarantee than publishing a snapshot of it.
- **Git LFS for large output.** Rejected for now. It changes clone behaviour for every user and
  answers "how do we store this" before answering "does this need publishing at all". Would need its
  own ADR.
- **Blocklist `.gitignore` (list known-bad patterns).** Rejected. A blocklist fails silently on the
  artifact class nobody anticipated, which is exactly the class that causes the accident. Deny-by-
  default fails toward not publishing, which is the safe direction.

## Consequences

- Publishing an artifact takes deliberate effort. That is the intent; the friction is the mechanism.
- Some genuinely useful data will be regenerable-but-not-present. Accepted, and mitigated by the
  determinism guarantee — which now has to actually hold, making V-NUM-03 (determinism) a
  load-bearing test rather than a nicety.
- A curated result file costs more to produce than a raw dump, because it must carry units, frame,
  seed, commit and configuration hash. Accepted: an unexplained CSV is not evidence.
- The `.gitignore` is longer and its ordering matters (re-inclusions before the directory denials
  that override them). Mis-editing it could silently exclude something intended for publication, so
  the checklist's `git status` / `git diff --cached` step is not optional.

## Revisit if

The first Monte Carlo experiment shows the curated-result format is insufficient to support a claim;
an external archival repository with a DOI becomes necessary; or a collaborator joins and the
staging discipline needs to be enforced mechanically rather than by procedure.
