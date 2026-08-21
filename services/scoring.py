import numpy as np

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from xgboost import XGBClassifier
            rng = np.random.default_rng(26)
            x = rng.normal(size=(500, 3))
            y = ((x[:, 0] * 1.2 + x[:, 1] * 1.8 + x[:, 2] * 2.4) > 1.0).astype(int)
            _model = XGBClassifier(n_estimators=35, max_depth=3, learning_rate=.12, n_jobs=1, eval_metric="logloss")
            _model.fit(x, y)
        except Exception:
            _model = False
    return _model


def score(features: dict) -> int:
    """XGBoost inference, with deterministic mathematical fallback for lean deployments."""
    annual, excess, adjusted = features["annualized_return"], features["excess_over_benchmark"], features["volatility_adjusted_claim"]
    model = _get_model()
    if model:
        vector = np.array([[np.clip(annual, -3, 15), np.clip(excess, -3, 15), np.clip(adjusted, -2, 2)]])
        return int(round(float(model.predict_proba(vector)[0][1]) * 100))
    return int(np.clip(50 + excess * 35 + adjusted * 30, 0, 100))


def level(score_value: int) -> str:
    return "HIGH" if score_value >= 70 else "MEDIUM" if score_value >= 40 else "LOW"
