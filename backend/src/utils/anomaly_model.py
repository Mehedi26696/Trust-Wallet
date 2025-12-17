"""
Tiny helper for loading and scoring the trained anomaly model.

This utility is designed to be lightweight and safe to import in the API layer:
- It defers importing heavy PyCaret modules until you actually load/score a model.
- It keeps all paths relative to the repository layout.

Primary functions:
- get_feature_columns(features_json_path: Path | None) -> list[str]
- load_best_model(model_basename: str | None) -> Any
- predict_anomaly(df_features: pd.DataFrame, model: Any | None) -> pd.DataFrame
- merge_context(scored, context, context_cols)

Expected artifacts produced by the training notebook/script:
- ai_models/trustwallet_best_txn_v1.pkl
- ai_models/trustwallet_iforest_features.json
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence
import json

import pandas as pd
import numpy as np

# --- Default artifact locations (resolved relative to this file) ---
# .../src/utils/anomaly_model.py -> repo_root = parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[2]
_MODELS_DIR = _REPO_ROOT / "ai_models"
_DEFAULT_MODEL_BASENAME = "trustwallet_best_txn_v1"  # without .pkl extension
_DEFAULT_FEATURES_JSON = _MODELS_DIR / "trustwallet_iforest_features.json"


def get_models_dir() -> Path:
    """Return the default models directory path."""
    return _MODELS_DIR


def get_feature_columns(features_json_path: Optional[Path] = None) -> list[str]:
    """Load the exact feature column order used for training.

    Args:
        features_json_path: Optional explicit path to the features JSON file.
            Defaults to ai_models/trustwallet_iforest_features.json

    Returns:
        List of feature column names in the exact order required by the model.
    """
    path = Path(features_json_path) if features_json_path else _DEFAULT_FEATURES_JSON
    if not path.exists():
        raise FileNotFoundError(
            f"Feature list JSON not found at: {path}. Make sure the training notebook saved it."
        )
    try:
        return json.loads(path.read_text())
    except Exception as e:
        raise ValueError(f"Failed to read/parse features JSON at {path}: {e}") from e


def _ensure_feature_frame(df: pd.DataFrame, feature_cols: Sequence[str]) -> pd.DataFrame:
    """Validate and reorder feature columns, filling NaNs and removing infs.

    - Reorders columns to the expected order
    - Replaces +/-inf with NaN
    - Fills NaN with 0
    """
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise KeyError(
            "Missing required feature columns: " + ", ".join(missing)
        )
    X = df.loc[:, list(feature_cols)].copy()
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    return X


def load_best_model(model_basename: Optional[str] = None) -> Any:
    """Load the saved best anomaly model pipeline via pycaret.anomaly.load_model."""
    mb = model_basename or _DEFAULT_MODEL_BASENAME
    base_path = _MODELS_DIR / mb

    try:
        from pycaret.anomaly import load_model  # type: ignore
    except Exception as e:
        raise ImportError(
            "pycaret is required to load the anomaly model. Install it in the runtime environment."
        ) from e

    try:
        return load_model(str(base_path))
    except Exception:
        return load_model(str(base_path) + ".pkl")


def predict_anomaly(
    df_features: pd.DataFrame,
    model: Optional[Any] = None,
    features_json_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Score feature rows with the anomaly model.

    Returns a DataFrame including Anomaly and Anomaly_Score when present.
    """
    feature_cols = get_feature_columns(features_json_path)
    X = _ensure_feature_frame(df_features, feature_cols)

    try:
        from pycaret.anomaly import predict_model  # type: ignore
    except Exception as e:
        raise ImportError(
            "pycaret is required to score anomalies. Install it in the runtime environment."
        ) from e

    mdl = model or load_best_model()
    scored = predict_model(mdl, data=X)
    return scored


def merge_context(
    scored: pd.DataFrame,
    context: pd.DataFrame,
    context_cols: Sequence[str] = ("user_id", "merchant_id", "ts", "amount", "device_type", "location"),
) -> pd.DataFrame:
    """Concatenate selected context columns next to the scored results.

    Aligns by index and avoids column collisions.
    """
    safe_cols = [c for c in context_cols if c in context.columns and c not in scored.columns]
    combined = pd.concat([scored, context[safe_cols]], axis=1)
    return combined
