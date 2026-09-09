# RADIUS — Pre-Push Publication Checklist

**Run before every meaningful push.** Governed by `docs/methodology/PUBLICATION_POLICY.md`.

Two surfaces must be audited, and they are **separate risks**:

1. the **working tree** — what is about to be committed;
2. the **git history** — what has already been committed. A secret deleted in a later commit is
   still published, permanently, in the objects anyone can clone.

If any critical item is uncertain: **do not push. Flag it for researcher review.**

---

## 0. Stage intentionally

`git add .` is not a publication mechanism. Stage by path, then look at what you staged.

```bash
git status
git diff --cached
```

Read the diff. Not skim — read. This step catches what every automated check below misses.

---

## 1. Technical audit — secrets, paths, personal information

```bash
git diff --cached --name-only
```

Then, over the staged content:

```bash
git diff --cached -U0 | grep -nEi 'BEGIN [A-Z ]*PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|xox[baprs]-|api[_-]?key|secret[_-]?key|password|bearer [A-Za-z0-9._-]{20}'
```

```bash
git diff --cached -U0 | grep -nEi '[A-Za-z]:\\\\Users\\\\|/home/[a-z]|/Users/[a-z]|\.ssh/|localhost:[0-9]{4}'
```

```bash
git diff --cached -U0 | grep -nEi '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
```

Expected result for all three: **no matches**. Any match is examined individually; an email address
that is a `noreply` GitHub identity is acceptable, a personal address is not.

### Author identity — not covered by `.gitignore`

```bash
git log --format='%an <%ae> | %cn <%ce>' | sort -u
```

Every entry must use the GitHub `noreply` address. This is published with the file contents and
cannot be ignored away; fixing it after the fact requires rewriting history.

### History sweep (before a first push, and after any import of older material)

```bash
git log -p --all | grep -nEi 'BEGIN [A-Z ]*PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|[A-Za-z]:\\\\Users\\\\' | head
```

---

## 2. Size and binary audit

```bash
git diff --cached --numstat
```

```bash
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '$1=="blob" && $3>262144 {print $3, $4}' | sort -rn | head -20
```

For anything above ~256 KB, or any new binary, answer the §23 questions from the policy:
essential? scientifically meaningful? reproducible? legally distributable? is Git the right
mechanism? would a reduced representation do? would an archival repository be better?

A "no" to *essential* or a "yes" to *reduced representation would do* means it does not go in.

---

## 3. Generated-output audit

Confirm nothing staged came from these classes: raw simulation output, per-run directories, Monte
Carlo ensembles, logs, caches, scratch, debug plots, profiling output, build artifacts, notebook
checkpoints, editor configuration.

```bash
git diff --cached --name-only | grep -Ei '(^|/)(raw|raw_data|output|outputs|runs?|run_[0-9]+|monte_carlo|mc_output|logs?|scratch|tmp|temp|cache|generated|debug)(/|$)'
```

Expected: no matches. A match is only acceptable if that specific artifact has been deliberately
selected and documented under the policy's §2.2.

---

## 4. Scientific audit

For every claim added or changed in this push:

- [ ] Is the artifact scientifically meaningful, and necessary to understand or reproduce a result?
- [ ] Is it interpretable standalone — units, coordinate frame, experiment ID, seed, commit?
- [ ] Are claims supported by evidence that is *also* published?
- [ ] Are `FACT` / `CALCULATION` / `OBSERVATION` / `INTERPRETATION` / `HYPOTHESIS` / `ASSUMPTION` /
      `LIMITATION` distinguished, rather than blurred?
- [ ] Is any "validated" claim justified against **independent reference data**, a **stated
      purpose** and a **stated tolerance** — or is it verification wearing the wrong word?
- [ ] Are limitations stated, including the inconvenient ones?
- [ ] Does a falsified hypothesis or negative result appear in the summary and conclusions, not only
      in a footnote?
- [ ] Are new assumptions registered in `docs/assumptions.md` with an ID, and cited by ID where the
      code or document depends on them?

## 5. Provenance audit

- [ ] Does every published number trace: result → experiment ID → configuration → commit →
      assumptions → seed → analysis → report?
- [ ] Does every experiment directory carry `README.md`, `config.yaml`, `manifest.json`?
- [ ] Does every result directory carry a `README.md` explaining what it contains?
- [ ] Do result filenames identify their experiment (`EXP-0042_...`), not `results.csv`?

## 6. Legal audit

- [ ] Do we own the material, or does its licence explicitly permit redistribution?
- [ ] Are attributions and required notices preserved?
- [ ] Is any third-party text reproduced, rather than cited and linked?
- [ ] Are citations verified? Anything unverified marked `(not verified)`?

## 7. Repository-quality audit

- [ ] Does `README.md` still state the project's **actual** maturity (policy §11)?
- [ ] Does it avoid implying an incomplete prototype is a finished product?
- [ ] Is `.gitignore` still correct for what this push introduces?
- [ ] Do the tests pass? If they do not, the push says so.
- [ ] Are filenames meaningful?
- [ ] Is only what was intended staged?

## 8. Scope audit — RADIUS-specific

- [ ] Does nothing in this push cross the hard scope boundary in `CLAUDE.md`: no real or operational
      vehicle design, no propulsion hardware detail, no targeting or deployment procedure, no
      flight-readiness claim?
- [ ] Are development parameters generic and non-operational?

---

## 9. Platform protections

GitHub secret scanning and push protection are enabled for this repository. They are a **backstop**,
not a substitute for §1: they detect known credential formats, and know nothing about personal
information, machine paths, scope violations, or unsupported claims.

Verify:

```bash
gh api repos/:owner/:repo --jq '.security_and_analysis'
```

---

## 10. Push

Only after every critical item above passes.

```bash
git push
```

Then confirm what actually landed:

```bash
git log --oneline -3
git status
```
