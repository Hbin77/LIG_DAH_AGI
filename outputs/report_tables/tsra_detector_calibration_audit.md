# TSRA-R Detector Calibration Audit

This audit checks whether the TSRA-R-ML detector probabilities are usable for closed-simulation thresholded defense.
Safety boundary: closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action

| check_id | area | status | observed | interpretation |
|---|---|---|---|---|
| CAL01 | Holdout coverage | pass | holdout_rows=4000; seed=9100; prevalence=0.49525; probability_min=0.010463; probability_max=1; probability_mean=0.501124 | The calibration audit uses a balanced deterministic synthetic holdout separate from the saved metric JSON. |
| CAL02 | Probability calibration | pass | brier_score=0.0351619; expected_calibration_error=0.093589; bins=10 | Brier score is strong and ECE is acceptable for closed-simulation thresholding; the audit still records that probabilities are not perfect calibrated truths. |
| CAL03 | Baseline threshold quality | pass | threshold=0.75; precision=1; recall=0.833417; f1=0.909141; false_positive_rate=0; false_negative_rate=0.166583; tp=1651; fp=0; fn=330; tn=2019 | The 0.75 detector threshold is conservative: it sharply limits false positives while retaining enough attack recall for reactive defense. |
| CAL04 | Threshold sensitivity | pass | threshold_0.55_precision=0.991767; threshold_0.55_recall=0.912166; threshold_0.75_precision=1; threshold_0.75_recall=0.833417; threshold_0.95_precision=1; threshold_0.95_recall=0.532055 | The detector behaves monotonically enough for threshold tuning: higher threshold reduces recall while preserving high precision. |
| CAL05 | Class probability separation | pass | positive_median=0.956382; positive_q75=0.986759; negative_median=0.106435; negative_q95=0.31731; median_gap=0.849948 | Attack-present states cluster near high probabilities and non-attack states stay low, which supports threshold-triggered defense windows. |
| CAL06 | Closed-loop threshold consistency | pass | sweep_0.75_status=usable; sweep_0.75_impact=0.161111; sweep_0.95_status=watch; sweep_0.95_impact=0.232634; offline_0.75_recall=0.833417; offline_0.95_recall=0.532055 | Offline calibration and closed-loop sweep agree: an overly high threshold loses recall and increases mission impact. |

## Detail

### CAL01 Holdout coverage

- Requirement: Calibration audit must use an independent deterministic holdout set.
- Evidence: src/ml/train_tsra_detector.py | outputs/models/tsra_detector.pkl
- Observed: holdout_rows=4000; seed=9100; prevalence=0.49525; probability_min=0.010463; probability_max=1; probability_mean=0.501124
- Status: pass
- Interpretation: The calibration audit uses a balanced deterministic synthetic holdout separate from the saved metric JSON.
- Safety boundary: closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action

### CAL02 Probability calibration

- Requirement: Detector probabilities must be usable for thresholding while exposing calibration error.
- Evidence: outputs/report_tables/tsra_detector_calibration_bins.csv
- Observed: brier_score=0.0351619; expected_calibration_error=0.093589; bins=10
- Status: pass
- Interpretation: Brier score is strong and ECE is acceptable for closed-simulation thresholding; the audit still records that probabilities are not perfect calibrated truths.
- Safety boundary: closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action

### CAL03 Baseline threshold quality

- Requirement: The deployed 0.75 threshold must provide high precision and bounded false positives.
- Evidence: outputs/report_tables/tsra_detector_calibration_audit.csv
- Observed: threshold=0.75; precision=1; recall=0.833417; f1=0.909141; false_positive_rate=0; false_negative_rate=0.166583; tp=1651; fp=0; fn=330; tn=2019
- Status: pass
- Interpretation: The 0.75 detector threshold is conservative: it sharply limits false positives while retaining enough attack recall for reactive defense.
- Safety boundary: closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action

### CAL04 Threshold sensitivity

- Requirement: Higher thresholds must show the expected precision/recall tradeoff.
- Evidence: outputs/report_tables/tsra_detector_calibration_audit.csv
- Observed: threshold_0.55_precision=0.991767; threshold_0.55_recall=0.912166; threshold_0.75_precision=1; threshold_0.75_recall=0.833417; threshold_0.95_precision=1; threshold_0.95_recall=0.532055
- Status: pass
- Interpretation: The detector behaves monotonically enough for threshold tuning: higher threshold reduces recall while preserving high precision.
- Safety boundary: closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action

### CAL05 Class probability separation

- Requirement: Attack and non-attack holdout states must separate in probability space.
- Evidence: outputs/report_tables/tsra_detector_calibration_audit.csv
- Observed: positive_median=0.956382; positive_q75=0.986759; negative_median=0.106435; negative_q95=0.31731; median_gap=0.849948
- Status: pass
- Interpretation: Attack-present states cluster near high probabilities and non-attack states stay low, which supports threshold-triggered defense windows.
- Safety boundary: closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action

### CAL06 Closed-loop threshold consistency

- Requirement: Offline detector calibration must agree with the closed-loop threshold sweep direction.
- Evidence: outputs/batch/ml_threshold_sweep_summary.csv | outputs/report_tables/ml_threshold_sweep.csv
- Observed: sweep_0.75_status=usable; sweep_0.75_impact=0.161111; sweep_0.95_status=watch; sweep_0.95_impact=0.232634; offline_0.75_recall=0.833417; offline_0.95_recall=0.532055
- Status: pass
- Interpretation: Offline calibration and closed-loop sweep agree: an overly high threshold loses recall and increases mission impact.
- Safety boundary: closed simulation TSRA-R detector calibration audit only; no RF, exploit, or live network action
