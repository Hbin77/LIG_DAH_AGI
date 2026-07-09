| task | model | MAE | R2/F1 | Top-1/Precision |
|---|---|---:|---:|---:|
| AURA impact regression | ridge | 0.049230610953303146 | 0.8070382864860144 | 0.863013698630137 |
| AURA impact regression | random_forest | 0.018571419315396367 | 0.9610629118252112 | 0.9123287671232877 |
| AURA impact regression | hist_gradient_boosting | 0.011290458377951788 | 0.9882841559679038 | 0.9041095890410958 |
| TSRA-R anomaly detection | logistic_regression |  | 0.979757085020243 | 0.9918032786885246 |
| TSRA-R anomaly detection | random_forest |  | 0.9638802889576883 | 0.9957356076759062 |
| AURA GPU-scale MPS regression | PyTorch MPS MLP | 0.005236480850726366 | 0.9951224327087402 | 0.7486666666666667 |
