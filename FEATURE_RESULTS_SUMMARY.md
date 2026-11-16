# Ninapro DB1 E1 feature experiment results

All runs below used the development data. Metrics are macro-F1. Mean and SD are across subjects, while pooled scores use all out-of-fold predictions together. Compare configurations within the same cohort.

| Cohort | Configuration | Features | Within-subject mean (SD) | New-subject mean (SD) | Pooled within / new |
|---|---|---:|---|---|---|
| S1-S5 | Baseline | 50 | 0.790 (0.054) | 0.161 (0.043) | 0.784 / 0.192 |
| S1-S5 | Without RMS | 40 | 0.779 (0.052) | 0.162 (0.039) | 0.773 / 0.194 |
| S1-S5 | Baseline + IQR | 60 | 0.783 (0.051) | 0.165 (0.043) | 0.778 / 0.199 |
| S1-S10 | Baseline | 50 | 0.803 (0.044) | 0.158 (0.060) | 0.799 / 0.183 |
| S1-S10 | Without RMS | 40 | 0.794 (0.044) | 0.158 (0.057) | 0.791 / 0.186 |
| S1-S10 | Baseline + IQR | 60 | 0.799 (0.043) | 0.158 (0.059) | 0.795 / 0.183 |
| S1-S10 | Relative RMS | 50 | 0.816 (0.042) | 0.164 (0.054) | 0.813 / 0.19 |

The separate relative RMS run used its own baseline. The detailed log reports both scores from that run. New-subject macro-F1 increased for 9 subjects and decreased for 1 (mean paired change +0.00547).

Pooled MAV/RMS Pearson correlations ranged from 0.999392 to 0.999916 on S1-S5 and from 0.999475 to 0.999898 on S1-S10. IQR improved new-subject macro-F1 for 3 of 5 subjects on S1-S5 (+0.00445 on average) and 4 of 10 on S1-S10 (-0.00006).

See [FEATURE_EXPERIMENTS.md](FEATURE_EXPERIMENTS.md) for full details.
