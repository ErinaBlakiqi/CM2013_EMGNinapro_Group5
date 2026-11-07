For your EMG track, the professor specifically rewards controlled experiments, comparisons in both evaluation modes, subject-level variability, at least one unsuccessful alternative, and an explanation of the cross-subject performance gap.

What we now know for certain
According to the professor's HOLDOUT_EVALUATION.md:
Requirement	Official instruction
Dataset	Ninapro DB1
Official held-out subjects	S23, S24, S25, S26, S27
Evaluation metric	Macro-F1
Split unit	Subject
Evaluation modes	Within-subject and new-subject
Final submission	predictions.csv
Before final prediction	Commit EXPECTED_SCORE.md
Hold-out usage	Predict once, never train, tune, or evaluate on it ourselves

The five official held-out subjects must remain completely untouched until our final model is frozen.

### Iteration 2 — Preprocessing experiment

**Objective:** Investigate whether additional short-term smoothing of Ninapro DB1 EMG envelopes improves gesture classification, particularly generalization to unseen subjects.

**Dataset:** Ninapro DB1, Exercise E1, subjects S1–S5; 13,875 windows, 10 EMG channels, 12 gesture classes. Windows contain 20 samples at 100 Hz (200 ms), with a 15-sample step.

**Baseline:** Identity preprocessing (`preprocess="none"`).

**Experimental configuration:** Fixed 3-sample causal moving average (`preprocess="moving_average"`), applied independently along the time axis of each EMG window. Boundary samples use nearest-value padding. No parameters are learned from other recordings, subjects, or evaluation folds.

**Verification:** Synthetic tests confirmed baseline preservation, expected numerical output, absence of future-sample dependence within each window, and preservation of the original recording. Integration tests confirmed that both configurations produce 13,875 × 50 feature matrices with identical labels and subject assignments, while changing the extracted feature values.

**Evaluation:** The same supplied evaluation harness was used for both configurations. Within-subject evaluation separates repetitions using GroupKFold; new-subject evaluation separates subjects. Feature selection occurs within the training folds.

| Metric | Baseline | Moving average | Difference |
|---|---:|---:|---:|
| Within-subject pooled macro-F1 | 0.783 | 0.781 | -0.002 |
| Within-subject pooled accuracy | 0.785 | 0.783 | -0.002 |
| New-subject pooled macro-F1 | 0.191 | 0.205 | +0.014 |
| New-subject pooled accuracy | 0.191 | 0.205 | +0.014 |
| New-subject pooled Cohen's kappa | 0.117 | 0.133 | +0.016 |

**Moving-average subject-level macro-F1:**

| Subject | Within-subject | New-subject |
|---|---:|---:|
| S1 | 0.772 | 0.219 |
| S2 | 0.776 | 0.096 |
| S3 | 0.874 | 0.196 |
| S4 | 0.742 | 0.177 |
| S5 | 0.761 | 0.173 |
| Mean ± SD | 0.785 ± 0.051 | 0.172 ± 0.046 |

**Interpretation:** Moving-average smoothing slightly increased pooled new-subject macro-F1 but slightly decreased within-subject performance. The improvement of 0.014 in pooled new-subject macro-F1 is small relative to subject-to-subject variability, and generalization remains substantially weaker than within-subject classification. The result does not establish a robust improvement across subjects.

**Decision:** Preserve both configurations. Keep identity preprocessing as the reference baseline and moving-average smoothing as an optional experimental method until the final pipeline is selected.

**Limitations:** Filtering resets at each window boundary rather than maintaining continuous filter state. The implementation uses only samples within the current window, but the exact boundary behavior should be documented when discussing real-time deployment. Repeated comparisons on the same five subjects can introduce model-selection bias; the final report must disclose the number of configurations compared and the selection procedure.



## Preprocessing comparison plan

The team uses a limited comparison budget to reduce the risk of
selecting a configuration that performs well only on the evaluation subjects.

Planned preprocessing configurations:

1. Identity preprocessing (completed).
2. Three-sample causal moving average (completed).
3. Per-channel normalization with an explicitly defined, leakage-safe
   calibration procedure (planned).
4. Per-channel normalization combined with causal moving-average
   smoothing (planned).

The comparison budget was established after evaluating configurations
1 and 2; this limitation will be disclosed in the final report.

All configurations will be evaluated using the same subject-aware and
repetition-aware cross-validation procedures.

Because the same five subjects are used for configuration comparison,
the selected configuration's performance will be treated as an
exploratory estimate rather than an independent final test result.

The team will report all compared configurations, including
unsuccessful experiments, and will not expand the comparison budget
without documenting and justifying the change.

cat >> RESULTS.md <<'EOF'

## Iteration 3 — Expanded development dataset (S1–S10): identity baseline

**Purpose.** Re-evaluate the original identity-preprocessing baseline on a larger
development cohort before testing further preprocessing methods. This establishes
a common reference for subsequent comparisons on S1–S10.

**Dataset.** Ninapro DB1, exercise E1, subjects S1–S10 (10 subjects,
27,575 EMG windows). Official hold-out subjects S23–S27 were excluded,
and `assert_no_holdout(recs)` passed.

**Configuration.** `preprocess="none"` (identity baseline).
The existing feature extraction, feature selection, and classifier defaults
were retained.

**Evaluation.**
- Within-subject: repetition-grouped cross-validation, with feature
  selection fitted inside each training fold.
- New-subject: subject-grouped cross-validation, with subjects separated
  between training and testing.
- Primary metric: macro-F1.

| Metric | Within-subject | New-subject |
|---|---:|---:|
| Pooled macro-F1 | 0.799 | 0.185 |
| Mean subject macro-F1 | 0.802 | 0.158 |
| Subject macro-F1 SD | 0.045 | 0.060 |
| Subject macro-F1 minimum | 0.742 | 0.063 |
| Subject macro-F1 maximum | 0.883 | 0.250 |
| Pooled Cohen's kappa | 0.781 | 0.116 |

**Per-subject macro-F1**

| Subject | Within-subject | New-subject |
|---|---:|---:|
| S1 | 0.7811 | 0.1843 |
| S2 | 0.7758 | 0.0874 |
| S3 | 0.8826 | 0.1788 |
| S4 | 0.7419 | 0.2229 |
| S5 | 0.7596 | 0.1917 |
| S6 | 0.7757 | 0.1522 |
| S7 | 0.8619 | 0.0632 |
| S8 | 0.8248 | 0.2499 |
| S9 | 0.8047 | 0.1047 |
| S10 | 0.8097 | 0.1457 |

**Interpretation.** The large within-subject versus new-subject performance
gap indicates limited transfer to unseen individuals. In particular,
S7 achieved within-subject macro-F1 of 0.8619 but new-subject macro-F1
of only 0.0632. Performance also varied substantially across held-out
development subjects.

Compared with the original S1–S5 identity baseline (pooled within-subject
macro-F1 0.783; new-subject macro-F1 0.191), the expanded cohort produced
0.799 and 0.185, respectively. These differences must not be interpreted
as the causal effect of adding subjects because the evaluation cohort changed.

**Decision.** Retain identity preprocessing as the reference configuration
for subsequent S1–S10 experiments. Investigate whether alternative
preprocessing can improve new-subject generalization without introducing
cross-subject data leakage.

**Hold-out status.** Official subjects S23–S27 have not been used for
development, model selection, or evaluation.

### Iteration 4 — EMG Amplitude Diagnostics (2026-11-07)

**Objective:** Investigate between-subject EMG amplitude differences before selecting a normalization method, following the Chapter 8 principle that preprocessing should address an identified signal problem.

**Dataset:** Ninapro DB1, exercise E1, subjects S1–S10, 27,575 windows, 10 channels, 100 Hz sampling frequency. Official hold-out subjects S23–S27 were excluded.

**Implementation:** Created `experiment_amplitude_diagnostics.py` to calculate mean absolute EMG amplitude independently for each subject and channel. The script validates the development cohort and saves reproducible results to `amplitude_diagnostics_S1_S10.csv`.

**Findings:** Substantial between-subject differences were observed. Channel 1 ranged from 0.0027 to 0.8043 in mean absolute amplitude, while Channel 7 ranged from 0.0247 to 1.1204. The across-subject standard deviation for Channel 1 was 0.2514, exceeding its mean of 0.1365.

**Interpretation:** The results demonstrate substantial differences in channel-amplitude distributions across the development subjects. This motivates investigating amplitude normalization as a potential approach to improving new-subject generalization. However, the analysis does not establish the causes of these differences or demonstrate that normalization will improve classification.

**Next step:** Register a limited, predefined comparison of normalization methods before evaluating classification performance. Ensure preprocessing uses only information available at prediction time or parameters fitted exclusively on training folds.

**Status:** Diagnostic analysis completed. No normalization method selected or evaluated yet.

### Iteration 4 — Preprocessing Comparison Plan (registered before evaluation)

**Motivation:** An amplitude diagnostic on Ninapro DB1 S1–S10 (27,575 windows) identified substantial between-subject variation in channel amplitudes. This motivates testing normalization to investigate whether reducing amplitude-scale differences improves new-subject generalization.

**Fixed preprocessing comparison budget:** Two new configurations will be evaluated against the existing identity baseline.

| Configuration | Description | Hypothesis |
|---|---|---|
| P1 — Per-channel window RMS normalization | Normalize each channel independently using its RMS within the current 200 ms window. | Reducing channel-specific amplitude differences may improve cross-subject generalization. |
| P2 — Global window RMS normalization | Normalize all 10 channels using one RMS value calculated across the current 200 ms window. | Reducing overall amplitude scale while preserving relative channel activation may improve cross-subject generalization. |

**Evaluation protocol:** Ninapro DB1 E1, S1–S10, unchanged windowing, baseline feature extraction and classifier. Evaluate both within-subject (repetition-grouped) and new-subject (subject-grouped) performance. Report pooled macro-F1, Cohen's kappa, and subject-level mean macro-F1 ± SD.

**Selection rule:** Prefer a method only when the improvement is meaningful relative to subject-level variability and its signal-processing trade-offs. Otherwise retain the simpler identity baseline.

**Leakage and deployment considerations:** Both proposed normalizations use only samples within the current window, with no cohort-fitted parameters or future windows. Their effect on amplitude-based features and real-time suitability must be assessed.

**Comparison accounting:** The two normalization configurations are prospective comparisons. Previous identity and moving-average experiments are recorded separately. The team-wide budget also includes feature-engineering, classification, and integration experiments.

**Status:** Planned; no normalization classification results examined yet.

### Iteration 4 — P1: Per-Channel Window RMS Normalization (2026-11-07)

**Objective:** Investigate per-channel RMS normalization as a preprocessing method to address the substantial between-subject EMG amplitude differences identified in the S1–S10 diagnostic analysis.

**Motivation:** The amplitude diagnostics revealed considerable variation in mean EMG amplitude across subjects and channels. Such differences may arise from electrode placement, muscle activation, or recording conditions and may contribute to poor new-subject generalization.

**Implementation:** Created `experiment_normalization_p1.py`, implementing per-window, per-channel RMS normalization.

For each EMG window and channel, the RMS is calculated as:

\[
\mathrm{RMS}_c=\sqrt{\frac{1}{N}\sum_{t=1}^{N}x_{t,c}^{2}}
\]

The normalized signal is then:

\[
x'_{t,c}=\frac{x_{t,c}}{\max(\mathrm{RMS}_c,\epsilon)}
\]

where \(N=20\) samples per window, \(c\) denotes the channel, and \(\epsilon=10^{-8}\) prevents division by zero.

Each channel is normalized independently within its own 200 ms window.

**Validation:** Implemented and successfully executed synthetic-data correctness tests and a direct preprocessing integration test.

The following properties were verified:

- Original and normalized signal dimensions are identical.
- Active channels have approximately unit RMS after normalization.
- Zero-amplitude channels remain zero.
- Changing one window does not affect normalization of another window.
- Original EMG recordings remain unchanged.
- The `P1NormalizedTrack` subclass correctly applies normalization through its `preprocess()` method.

**Test results:**

- P1 normalization correctness tests: PASSED
- P1 preprocessing integration test: PASSED
- Input dimensions: (48, 20, 10)
- Output dimensions: (48, 20, 10)

**Data leakage and causality:** Normalization uses only samples from the current window. No subject-wide or cohort-wide statistics are calculated, and no information from future windows is required. Therefore, the method does not introduce cross-subject fitting leakage and is compatible with window-based causal processing.

**Signal-processing trade-offs:** Independent channel normalization removes absolute channel-amplitude differences and largely eliminates relative channel-amplitude information. Although this may reduce sensitivity to subject-specific amplitude scaling, it may also remove useful gesture-discriminative information.

**Limitations:** Validation was performed using synthetic EMG recordings. The method has not yet been evaluated on real S1–S10 recordings or assessed for classification performance. Consequently, no improvement in recognition accuracy or generalization can currently be claimed.

**Status:** P1 implementation and synthetic correctness tests completed successfully. Real-data preprocessing validation and downstream performance evaluation remain pending.

### Iteration 4 — P2: Global Window RMS Normalization

**Objective:** Investigate global RMS normalization as an alternative to per-channel normalization, motivated by the substantial between-subject EMG amplitude differences identified in S1–S10.

**Implementation:** Created `experiment_normalization_p2.py`. The method calculates one RMS value across all 10 channels and 20 samples within each 200 ms window, then divides the entire window by that value.

**Validation:** All seven synthetic-data correctness and direct preprocessing integration checks passed. The implementation preserves signal dimensions, maintains relative channel amplitudes, handles zero-amplitude windows, processes windows independently, and leaves the original recordings unchanged.

**Comparison with P1:** P1 normalizes each channel independently, removing much of the relative channel-amplitude information. P2 applies a common scale to all channels, preserving relative channel activation patterns while removing overall window-amplitude scale.

**Leakage considerations:** Neither method estimates parameters from other subjects or windows. Both use only the current window's samples. No cohort-wide normalization statistics are fitted.

**Limitations:** Normalization may remove gesture-discriminative amplitude information. The tests establish implementation correctness but do not demonstrate improved classification performance.

**Status:** P1 and P2 implementations and synthetic correctness tests completed. No classification performance comparison has been conducted.


### Iteration 4 — Real-Data Validation of P1 and P2 (2026-11-07)

**Objective:** Verify that the two proposed RMS normalization methods operate correctly on real Ninapro DB1 Exercise E1 EMG recordings before downstream integration.

**Dataset:** Development subjects S1–S10, comprising 10 recordings and 27,575 EMG windows. Each window contains 20 samples across 10 channels. Official holdout subjects S23–S27 were excluded.

**Implementation:** Created `experiment_normalization_validation.py`, which loads the existing development recordings and independently applies P1 (per-window, per-channel RMS normalization) and P2 (per-window global RMS normalization).

**Validation procedure:** Both methods were evaluated for preservation of signal dimensions, finite numerical outputs, approximately unit RMS for active channels or windows, and preservation of the original recordings.

**Results:**

| Validation criterion | P1 | P2 |
|---|---|---|
| Development subjects | S1–S10 | S1–S10 |
| Windows validated | 27,575 | 27,575 |
| Signal dimensions preserved | PASS | PASS |
| Finite normalized outputs | PASS | PASS |
| Unit RMS for active channels/windows | PASS | PASS |
| Original recordings unchanged | PASS | PASS |
| Overall real-data validation | PASS | PASS |

**Interpretation:** Both normalization methods satisfy their tested mathematical and numerical requirements on the available development recordings. P1 independently normalizes each channel, whereas P2 uses a common normalization factor across all channels within each window.

**Limitations:** These results establish preprocessing correctness, not classification effectiveness. No feature extraction, classifier evaluation, or official holdout testing was performed as part of this validation.

**Status:** P1 and P2 implementation, synthetic correctness testing, and real-data validation completed. Downstream performance evaluation and final method selection remain pending.

### Iteration 4 — Signal-Level Comparison of P1 and P2

A representative high-amplitude window (S1, window index 752) was selected to examine how the two normalization strategies affect relative channel amplitudes.

The original signal exhibited substantial channel-amplitude differences, with CH7 having the highest RMS (4.6571) and CH4 the lowest (0.1998).

After P1 normalization, all ten channels had RMS equal to approximately 1, demonstrating that independent per-channel normalization removes relative channel-amplitude differences.

After P2 normalization, CH7 remained the strongest channel (RMS 2.6535), while CH4 remained the weakest (RMS 0.1138). This confirms that global RMS normalization preserves the relative channel-amplitude pattern while adjusting the overall signal scale.

**Interpretation:** P2 preserves more information about relative muscle activation across electrodes than P1. This provides a signal-processing rationale for considering P2 as a potentially less information-destructive normalization method.

**Limitation:** This comparison is descriptive and based on one illustrative window. It does not establish which normalization method improves gesture classification or cross-subject generalization.

**Status:** Signal-level comparison completed. Both methods are ready for downstream evaluation by the team.