# Feature experiments — Iteration 2 (S1–S5)

The following feature experiments were carried out as part of Iteration 2 and verified
on 2026-11-07 using Ninapro DB1 Exercise E1, S1–S5. The dates below refer to the
verification runs. Planned S1–S10 reruns will be documented separately.
A summary is recorded in [RESULTS.md](RESULTS.md).

## Experiment log

| Experiment | Verification date | What changed & why | Primary metric **with spread** | Better than reference? | Decision | Commit |
|---|---|---|---|---|---|---|
| Baseline verification | 2026-11-07 | Re-ran the unchanged 50-feature baseline on S1–S5 to establish the reference for the feature comparisons below. | Within-subject: mean macro-F1 0.790 (sd 0.054, range 0.743–0.880 across 5 subjects); new-subject: mean macro-F1 0.161 (sd 0.043, range 0.097–0.210 across 5 subjects). Pooled macro-F1: within-subject 0.784; new-subject 0.192. | Reference for the feature comparisons. | Retained as the reference configuration. Earlier baseline results are preserved; the cause of the small differences between runs has not been established. | Pipeline: 0741891; verification log: 46a398b; local runner not committed |
| RMS ablation | 2026-11-07 | Removed RMS from each of the ten channels, reducing 50 features to 40, to test whether the strong MAV–RMS correlation justified removing RMS. | Within-subject: mean macro-F1 0.779 (sd 0.052, range 0.732–0.866 across 5 subjects); new-subject: mean macro-F1 0.162 (sd 0.039, range 0.103–0.211 across 5 subjects). Pooled macro-F1: within-subject 0.773; new-subject 0.194. | Mixed: pooled within-subject macro-F1 decreased 0.784 → 0.773; new-subject increased only 0.192 → 0.194. | RMS retained in the reference baseline. Removing it reduced within-subject macro-F1 for all five subjects without a clear new-subject benefit. | Original experiment: 32acf7f; setup adaptations and verification log: 46a398b |
| Adding IQR | 2026-11-07 | Added one IQR feature per channel while retaining the original 50 features, giving 60 features, to test whether robust amplitude spread adds useful information. | Within-subject: mean macro-F1 0.783 (sd 0.051, range 0.737–0.869 across 5 subjects); new-subject: mean macro-F1 0.165 (sd 0.043, range 0.095–0.208 across 5 subjects). Pooled macro-F1: within-subject 0.778; new-subject 0.199. | Mixed: pooled new-subject macro-F1 increased 0.192 → 0.199, but within-subject decreased 0.784 → 0.778. | Retained as an experimental candidate, not yet selected as the final default. The small new-subject gain was inconsistent across subjects; its interaction with preprocessing has not been tested. | Original experiment: 32acf7f; setup adaptations and verification log: 46a398b |

### Shared configuration

All comparisons used Ninapro DB1 Exercise E1, S1–S5: 13,875 windows of 20 samples
and 10 channels at 100 Hz, with a 15-sample step. The existing Random Forest baseline
and evaluation harness were used with `preprocess="none"`, `select="none"`, `seed=0`
and the default `imbalance="balanced"`. Within-subject evaluation grouped by repetition;
new-subject evaluation used leave-one-subject-out. Only the feature set changed; no additional smoothing was applied.
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
This count applies to the feature-verification runs only. Earlier team experiments
are not included, and no comparison budget was registered before these runs.

### MAV/RMS correlation

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

MAV and RMS were strongly correlated in the pooled data. Correlations were not
calculated separately within subjects. The RMS ablation was used to assess whether
removing the correlated feature affected classification performance.

### Per-subject IQR comparison

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

Pooled metrics were calculated from all out-of-fold predictions together. The
experiment log reports mean and SD across five subjects. Both aggregations are
labelled separately below and in RESULTS.md.

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
These outputs and the verification runners remain outside the repository and are not
committed. The four experiment scripts, shared helper and verification log were committed
in 46a398b (`Iteration 2: adapt and verify EMG feature experiments`).

Codex was used to set up the environment, adapt paths and import behavior, add shared
configuration/data checks, adjust configuration forwarding and result output in the
experiment scripts, execute the existing experiments, and format this log from measured
outputs and the stated feature decisions. The core adapter evaluation loop was not
changed. Individual review of the six changed files was completed before the changes
were merged into main. Team review against the course's agentic-tool rules remains
pending. RMS is retained in the reference baseline and IQR remains an experimental
candidate; final team selection remains open.

