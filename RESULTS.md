# Results log — `EMG_Ninapro`, `T5`

> **Copy this file into YOUR team's project repository** (not this scaffold repo) as
> `RESULTS.md`, and add one row per iteration as you go — not the night before the deadline.
> It exists because Chapter 16 §16.3 defines an iteration as *done* only when it (1) runs end
> to end to a result, (2) reports the primary metric **with its spread**, (3) is committed with
> a note saying what changed and why, and (4) is at least as good as the previous iteration —
> **or** says in writing why the change was kept anyway. This table is where (2), (3) and (4)
> land; `git log` is where (1) becomes checkable. It also makes writing the report an assembly
> job rather than an archaeology project.
>
> **This file is graded.** `CAPSTONE_REPORT_RUBRIC.md` **Criterion 9 — Iteration & revision
> history (3 pts)** takes `RESULTS.md` as its evidence, and it asks for one specific thing that
> a forward-only log cannot show: **at least one earlier decision you went back and changed
> because of a downstream result**, with the symptom that sent you back named. A row that
> *lowered* the headline metric and was kept for a stated reason is full-marks evidence, not a
> weakness. Rows here are also direct evidence for "Reproducibility & engineering" and "Report
> quality & defence".

**Track:** `emg_ninapro` ·
**Split unit:** `subject` for new-subject evaluation; `repetition` for within-subject evaluation ·
**Primary metric:** `macro-F1` ·
**Evaluation mode(s):** `within-subject + new-subject`

## Iteration log

Paste the metric straight from the harness — `rep["summary"]` prints the required shape, e.g.
`mean cohens_kappa 0.61 (sd 0.12, range 0.34-0.73 across 8 subjects)`. A pooled number with no
spread is half a result.

| # | Date | What changed & why (one line) | Primary metric **with spread** | Better than previous? | If not — why it was kept | Commit |
|---|---|---|---|---|---|---|
| 1 | 2026-10-05 | Supplied baseline, unchanged — establish the baseline on real Ninapro DB1 data | within-subject: mean macro-F1 0.788 (sd 0.054, range 0.741–0.881 across 5 subjects); new-subject: mean macro-F1 0.159 (sd 0.045, range 0.092–0.216 across 5 subjects) | — (baseline) | — | a0e08830cb71e1c6671cbfab15740ca0d2eaa7ca |
| 2 | 2026-11-06 | Tested fixed 3-sample causal moving-average smoothing on the preprocessed Ninapro DB1 EMG envelopes to assess whether reducing short-term fluctuations improves classification. Compared against the unchanged baseline using the same group-aware evaluation harness. | Within-subject: mean macro-F1 0.785 (sd 0.051, range 0.742–0.874 across 5 subjects); new-subject: mean macro-F1 0.172 (sd 0.046, range 0.096–0.219 across 5 subjects). Pooled macro-F1: within-subject 0.781; new-subject 0.205. | Mixed: pooled new-subject macro-F1 increased 0.191 → 0.205, but within-subject decreased 0.783 → 0.781. | Retained as an optional experimental configuration, not yet selected as the final default. The cross-subject improvement is small relative to between-subject variability; additional comparisons are needed before selecting the final preprocessing method. | 4471f14 |
| 2-FE1 | 2026-11-07 | Re-ran the unchanged 50-feature baseline on S1–S5 to establish the reference for the feature comparisons below. | Within-subject: mean macro-F1 0.790 (sd 0.054, range 0.743–0.880 across 5 subjects); new-subject: mean macro-F1 0.161 (sd 0.043, range 0.097–0.210 across 5 subjects). Pooled macro-F1: within-subject 0.784; new-subject 0.192. | Reference run, not an improvement claim. | Earlier baseline results are preserved; the small differences from the historical runs have not been attributed to a verified cause. | Pipeline: 0741891; verification run not committed |
| 2-FE2 | 2026-11-07 | Removed RMS from each of the ten channels, reducing 50 features to 40, to test whether the strong MAV–RMS correlation justified removing RMS. | Within-subject: mean macro-F1 0.779 (sd 0.052, range 0.732–0.866 across 5 subjects); new-subject: mean macro-F1 0.162 (sd 0.039, range 0.103–0.211 across 5 subjects). Pooled macro-F1: within-subject 0.773; new-subject 0.194. | Mixed: pooled within-subject macro-F1 decreased 0.784 → 0.773; new-subject increased only 0.192 → 0.194. | RMS retained in the reference baseline: removing it reduced within-subject macro-F1 for all five subjects without a clear new-subject benefit. | Original experiment: 32acf7f; setup adaptations and verification pending commit |
| 2-FE3 | 2026-11-07 | Added one IQR feature per channel while retaining the original 50 features, giving 60 features, to test whether robust amplitude spread adds useful information. | Within-subject: mean macro-F1 0.783 (sd 0.051, range 0.737–0.869 across 5 subjects); new-subject: mean macro-F1 0.165 (sd 0.043, range 0.095–0.208 across 5 subjects). Pooled macro-F1: within-subject 0.778; new-subject 0.199. | Mixed: pooled new-subject macro-F1 increased 0.192 → 0.199, but within-subject decreased 0.784 → 0.778. | IQR retained as an experimental candidate, not the default: its small new-subject gain was inconsistent across subjects. Its interaction with the team's preprocessing has not been tested. | Original experiment: 32acf7f; setup adaptations and verification pending commit |
| 3 |  |  |  | yes / no |  |  |
| 4 |  |  |  | yes / no |  |  |

*"Better" means better under the same honest harness — same split unit, same evaluation mode,
same seed. A change that lowers the metric can still be the right call (simpler, faster, more
robust across subjects, removes a leak). Say so in the column instead of quietly reverting it:
"kept — κ fell 0.02 but the worst-subject κ rose from 0.18 to 0.31" is a stronger result than a
silent higher mean.*

## Feature-engineering verification — Iteration 2

Rows 2-FE1–2-FE3 are feature-engineering experiments within the course's Iteration 2
(Real DSP & features), alongside the preprocessing work already recorded in row 2.
They do not renumber the course's later validation and delivery milestones. Dates above
refer to the verification runs, not the original experiment dates.

### Shared configuration

All comparisons used Ninapro DB1 Exercise E1, S1–S5: 13,875 windows of 20 samples
and 10 channels at 100 Hz, with a 15-sample step. The existing Random Forest baseline
and evaluation harness were used with `preprocess="none"`, `select="none"`, `seed=0`
and the default `imbalance="balanced"`. Within-subject evaluation grouped by repetition;
new-subject evaluation used leave-one-subject-out. Only the feature set changed.
No additional smoothing was used, so these comparisons isolate the feature changes.
S23–S27 were not downloaded or used.

Verification environment: Python 3.11.18, NumPy 2.2.6, SciPy 1.15.3 and
scikit-learn 1.7.2, with dependencies installed from both project requirements files.
Ordinary loading and two cache loads were checked for exact equality of EMG windows,
labels, repetition identifiers and subject groups. The second cache load reused the file.
The existing cache key includes window settings and file metadata; loader-code changes
still require a manual cache-version increment.

Three feature configurations were evaluated: the baseline, without RMS, and baseline
plus IQR. The correlation analysis was descriptive; the per-subject IQR analysis
re-evaluated the same two feature sets rather than introducing another configuration.
This is the count for this verification batch, not the total number of configurations
previously tried by the team, and not a retrospectively declared comparison budget.

### Supporting experiment — MAV/RMS correlation

Pearson correlations were computed on the pooled 50-feature matrix across S1–S5.

| Channel | MAV–RMS correlation |
|---|---:|
| 1 | 0.999884 |
| 2 | 0.999670 |
| 3 | 0.999827 |
| 4 | 0.999876 |
| 5 | 0.999476 |
| 6 | 0.999392 |
| 7 | 0.999859 |
| 8 | 0.999916 |
| 9 | 0.999786 |
| 10 | 0.999902 |

These results confirm strong linear overlap between MAV and RMS in the pooled data;
they are not within-subject correlations. Correlation alone did not establish that RMS
could be removed without affecting classification, so the ablation informed that decision.

### Supporting experiment — per-subject IQR comparison

New-subject macro-F1, with each subject excluded from training in its test fold:

| Held-out development subject | Baseline | Baseline + IQR | Change |
|---|---:|---:|---:|
| S1 | 0.2100 | 0.2081 | −0.0019 |
| S2 | 0.0973 | 0.0953 | −0.0020 |
| S3 | 0.1865 | 0.1913 | +0.0048 |
| S4 | 0.1626 | 0.1634 | +0.0008 |
| S5 | 0.1464 | 0.1669 | +0.0205 |

Three subjects improved and two worsened. The mean paired macro-F1 change was +0.00445,
with the largest gain in S5. The separate per-subject script agreed with the existing
evaluation harness for both macro-F1 and kappa. These results support keeping IQR as
an experimental candidate; they do not establish a consistent benefit or a benefit
when combined with moving-average preprocessing.

### Pooled metrics and earlier results

Pooled metrics use all out-of-fold predictions together. The iteration rows instead
lead with the mean and SD of the five subject-level scores. These are different
aggregations and should not be substituted for each other.

| Configuration | Within-subject pooled macro-F1 | Within-subject pooled kappa | New-subject pooled macro-F1 | New-subject pooled kappa |
|---|---:|---:|---:|---:|
| Reference baseline | 0.784 | 0.766 | 0.192 | 0.119 |
| Without RMS | 0.773 | 0.755 | 0.194 | 0.122 |
| Baseline + IQR | 0.778 | 0.760 | 0.199 | 0.127 |

The original feature-engineering summary reported pooled macro-F1 of 0.774 within-subject
and 0.193 new-subject without RMS (kappa 0.755 and 0.120), versus 0.773 and 0.194
(kappa 0.755 and 0.122) in this verification. The original IQR pooled values match this
verification to three decimals. Its earlier reported mean per-subject change was about
+0.0047, versus +0.00445 here. The team's earlier baseline notebook reported pooled
macro-F1 of 0.783 and 0.191. These historical values are preserved; small differences
have not been assigned a verified cause or interpreted as improvements.

### Run records and assistance disclosure

Local run records were saved as `baseline_s1_s5.json`, `without_rms_s1_s5.json`,
`with_iqr_s1_s5.json`, `feature_correlations.csv`, `iqr_per_subject_results.csv`
and `remaining_experiments_log.txt`, with correlation and per-subject figures.
The JSON records include pipeline/data hashes, environment and configuration details.
These outputs and the verification runners are currently outside the repository and
are not yet committed; the experiment adaptations also remain uncommitted.

Codex was used to set up the environment, adapt paths and import behavior, add shared
configuration/data checks, adjust configuration forwarding and result output in the
experiment scripts, execute the existing experiments, and format this log from measured
outputs and Mostafa's stated decisions. The core adapter evaluation loop was not changed.
Review of the agent-written adaptations against the course's agentic-tool rules remains
pending before integration; this disclosure does not replace that review. RMS retention
and IQR's candidate status were discussed with Mostafa; final team selection remains open.

## Leakage demonstration — Iteration 1

Using the real Ninapro DB1 data, the required one-time leakage demonstration gave:

| Split | Macro-F1 |
|---|---:|
| Naive random-window split (leaky) | 0.843 |
| Honest new-subject split | 0.191 |

The random-window split produced a much higher score because windows from the same subjects/repetitions can appear on both sides of the split. The honest new-subject evaluation is therefore the relevant deployment result for cross-subject generalisation.

## ⚠️ Before you fill in many rows — the garden of forking paths

The harness guarantees that **no single run** leaks a subject. It cannot guarantee anything
about the *sequence* of runs. Every row in the table above is scored on the **same**
group-aware folds, and those are the same folds that produce the number you will report. Try
twelve configurations against one held-out set and report the best, and the winner was chosen
partly because it happens to suit *these particular subjects*. Its margin over the runner-up is
optimistically biased, and nothing in the report will look wrong. This is a **selection effect**,
not a leak — which is exactly why the leakage guard cannot catch it, and why it has to be
handled by how you *plan* the work rather than by the code.

It bites hardest here because the cohorts are small: a dozen comparisons on five or six subjects
is a great deal of selection pressure on very little data.

Two defensible ways to handle it. **Say in the report which one you used** — Criterion 7 grades
the quality of the comparison, and this is part of that quality:

| approach | what you do | what it costs |
|---|---|---|
| **an explicit development set** | hold out a few groups *up front* as a DEV set; compare every design option on DEV only; run the chosen pipeline **once** on the untouched evaluation folds and report that | fewer groups serving each purpose — painful on these cohorts — and a noisier DEV estimate |
| **a comparison budget** | decide in advance how many configurations you will compare (a handful, not a sweep), write them into this file **before** you run them, and report the count | you may miss a better option, and you have to resist re-opening the budget once you have seen the numbers — which is the whole discipline |

Either way, two habits that cost nothing:

- **Record the count.** "We compared 6 configurations" belongs in the report. A team that
  compares six and says so is doing better science than one that compares twenty and shows a
  longer table.
- **Read a small margin as no margin.** If the difference between two options is smaller than
  the spread across your subjects/folds, it is not a result. Say "no measurable difference; we
  kept the simpler one" — that sentence earns marks, and claiming the 0.01 does not.

**Related, and equally invisible: *where* your preprocessing is fitted.** The notebook builds
features for every recording **before** `evaluate()` cuts the folds. That is safe for everything
the scaffold ships, because all of it is **stateless** — a fixed filter, or a threshold estimated
from one epoch's own samples. It stops being safe the moment you add a stage that **learns**:
CSP, PCA/ICA, a cohort-wide z-score, a learned artifact template. Fit one of those over all the
recordings and every held-out subject has already shaped the transform that built the training
features — and `assert_no_subject_leak` will still pass, because it checks group ids and cannot
see what a filter was learned from. A learned stage must be fitted **inside** the fold: as a step
in the classifier pipeline (cloned and refit per fold) or via `select_features()`. If you added
one, record here which of the two you used.

## Decision log — the choices behind the numbers

Rows above say *what happened*; this says *what you chose and why*, which is what §16.4 asks you
to make traceable and what the report's defence is built from. There is no single correct
pipeline here — the scaffold deliberately ships options, not answers. One line per decision;
add rows as the pipeline grows, and note the alternative you rejected.

| Pipeline module | Option chosen | Alternative(s) considered | Why this one (one sentence) | Iteration | Revised later? |
|---|---|---|---|---|---|
| 1. Data loading | Real Ninapro DB1, exercise E1, 5 subjects | Synthetic smoke data | Real data was used to establish the actual baseline required for the EMG track | 1 | — |
| 2. Preprocessing | Identity preprocessing (`preprocess="none"`) retained as baseline; fixed 3-sample causal moving average (`preprocess="moving_average"`) implemented as an optional configuration | No additional smoothing; subject-specific normalization (not yet implemented or evaluated) | Ninapro DB1 already contains rectified, low-pass-filtered EMG envelopes. A fixed causal moving average was tested to reduce short-term fluctuations without fitting parameters across subjects or accessing future samples. Results showed a small pooled new-subject improvement but no convincing overall benefit. | 2 | Not yet — final preprocessing selection pending |
| 3. Feature extraction | Original 50-feature reference retained, including RMS; ten appended IQR features retained as an experimental candidate | Removing RMS (40 features); adding IQR (60 features) | RMS removal reduced within-subject performance without a clear new-subject benefit; IQR gave a small, inconsistent new-subject gain and has not been tested with the team's preprocessing. | 2 (FE2–FE3) | No final default change — combined preprocessing/feature choice pending |
| 4. Feature selection | *e.g.* `select="none"` | ANOVA `SelectKBest`, tree importances | 14 features vs. ~1 800 epochs — pruning risked more than it saved | 1 | *e.g.* **yes, iter 4** — `select_k=20` was a no-op (harness said so); switched to `k=6` |
| 5. Classification, incl. `imbalance` | *e.g.* `imbalance="balanced"` | `"none"`, `"resample"`, `"threshold"` | *(if you kept the default, say you looked and why — a silent default earns nothing)* |  |  |
| 6. Inference |  |  |  |  |  |
| 7. Reporting |  |  |  |  |  |

## Revisions — the ones that went **backwards** (Criterion 9's actual evidence)

Adding iterations forward is a to-do list. What this section wants is the place a number
downstream sent you back **up** the pipeline. One row is enough; two is a good project.
The notebook's "Decision points on this track" section has a symptom → stage table to
diagnose from.

| # | The downstream result that triggered it | Which earlier decision it indicted | What you changed | What happened to the metric |
|---|---|---|---|---|
| 1 | *e.g.* worst-subject κ 0.14 vs. mean 0.61 | stage 2 — no per-recording normalisation | z-scored band powers within each recording | mean κ 0.61 → 0.59, **worst subject 0.14 → 0.38** — kept |
| 2 |  |  |  |  |

## Who did what

One line per person per iteration — the honest-disclosure requirement of §16.7, and the evidence
`INDIVIDUAL_ASSESSMENT.md` asks for. The seven modules do **not** have to map one-to-one onto
people: one person may own several modules, two people may share one, and ownership may rotate
between iterations. Record what actually happened.

| Iteration | Who | Modules / tasks owned | Reviewed by |
|---|---|---|---|
| 1 | Erina | Baseline execution on real Ninapro DB1 data; evaluation of within-subject and new-subject macro-F1; results logging | Vera |
| 2 | Erina | Implemented configurable causal moving-average preprocessing; verified baseline preservation, numerical correctness, causality within windows, non-mutation, and integration with the real Ninapro feature pipeline; evaluated both required classification modes and documented the results. | Pending team review |
| 2 | Mostafa | Original RMS ablation, MAV/RMS correlation, IQR implementation and per-subject IQR investigation; discussed decisions to retain RMS and keep IQR experimental. Verification on the updated setup and documentation were assisted by Codex as disclosed above. | Pending team review |

## Final numbers (fill in once, at the end)

| | Value | Under what split |
|---|---|---|
| Primary metric, development (mean + spread) |  |  |
| Secondary metrics (macro-F1 / balanced accuracy / per-class recall) |  |  |
| Held-out set — **scored once, never tuned against** |  |  |
| Supplied baseline, same harness |  |  |
| Yardstick from the dataset card (human ceiling / benchmark / chance) |  |  |
| **Configurations compared** before settling (a number) |  | on DEV folds / on the evaluation folds — say which |
| How option comparison was kept separate from final reporting |  | *e.g.* "separate DEV groups" / "budget of 6, fixed in advance" |

*Grading: `CAPSTONE_REPORT_RUBRIC.md` (team, 30 pts) and `INDIVIDUAL_ASSESSMENT.md`
(individual, 10 pts).*