"""
Utilities to load and run the Keras autoencoder anomaly model on raw transaction input.

Artifacts expected by default under `models/`:
- autoencoder_anomaly_model.keras
- scaler.pkl
- label_encoders.pkl (dict of column->LabelEncoder)

Falls back to `ai_models/` if not found in `models/`.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Dict, Any

import numpy as np

try:
    import tensorflow as tf
except Exception:  # pragma: no cover - optional at runtime
    tf = None  # type: ignore

try:
    import joblib  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    joblib = None  # type: ignore

from ..config import settings


DEFAULT_MODEL_DIRS = [
    os.path.join(os.getcwd(), "models"),
    os.path.join(os.getcwd(), "ai_models"),
]


def _resolve_path(filename: str) -> str:
    for base in DEFAULT_MODEL_DIRS:
        path = os.path.join(base, filename)
        if os.path.exists(path):
            return path
    # default to first dir even if missing (will error later with clear message)
    return os.path.join(DEFAULT_MODEL_DIRS[0], filename)


@lru_cache(maxsize=1)
def get_threshold() -> float:
    # Allow env override; default to 1.96
    try:
        return float(os.getenv("AUTOENCODER_THRESHOLD", "1.96"))
    except Exception:
        return 1.96


@lru_cache(maxsize=1)
def load_autoencoder() -> Any:
    if tf is None:
        raise RuntimeError("TensorFlow is not installed. Install tensorflow to enable autoencoder predictions.")
    model_path = _resolve_path("autoencoder_anomaly_model.keras")
    return tf.keras.models.load_model(model_path)


@lru_cache(maxsize=1)
def load_scaler() -> Any:
    if joblib is None:
        raise RuntimeError("joblib is not installed. Install joblib to load scaler.")
    scaler_path = _resolve_path("scaler.pkl")
    return joblib.load(scaler_path)


@lru_cache(maxsize=1)
def load_label_encoders() -> Dict[str, Any]:
    if joblib is None:
        raise RuntimeError("joblib is not installed. Install joblib to load label encoders.")
    le_path = _resolve_path("label_encoders.pkl")
    enc = joblib.load(le_path)
    if not isinstance(enc, dict):
        raise RuntimeError("label_encoders.pkl must be a dict of column->LabelEncoder")
    return enc


def predict_raw_autoencoder(data: Dict[str, Any]) -> Dict[str, Any]:
    """Score a raw transaction dict using the autoencoder pipeline.

    Returns a dict with is_anomaly, reconstruction_error, threshold, and optional details.
    """
    categorical_cols = [
        "product_category",
        "product_name",
        "merchant_name",
        "payment_method",
        "transaction_status",
        "device_type",
        "location",
    ]

    # Load artifacts
    model = load_autoencoder()
    scaler = load_scaler()
    label_encoders = load_label_encoders()
    threshold = get_threshold()

    # Encode categoricals
    encoded_features = []
    for col in categorical_cols:
        le = label_encoders.get(col)
        if le is None:
            # Missing encoder for this column -> unseen handling: -1
            encoded = -1
        else:
            val = data.get(col)
            if val in getattr(le, "classes_", []):
                encoded = int(le.transform([val])[0])
            else:
                encoded = -1
        encoded_features.append(encoded)

    # Numerical part (keep order consistent with training)
    import math

    numerical_features = [
        math.log1p(float(data.get("product_amount", 0.0))),
        math.log1p(float(data.get("transaction_fee", 0.0))),
        math.log1p(float(data.get("cashback", 0.0))),
        math.log1p(float(data.get("loyalty_points", 0.0))),
        float(data.get("user_tx_count", 0.0)),
        math.log1p(float(data.get("user_avg_amount", 0.0))),
        float(data.get("user_freq", 0.0)),
        float(data.get("merch_tx_count", 0.0)),
        math.log1p(float(data.get("merch_avg_amount", 0.0))),
        float(data.get("merchant_freq", 0.0)),
        float(data.get("hour", 0)),
        float(data.get("day", 0)),
        float(data.get("month", 0)),
    ]

    full_input = np.array(encoded_features + numerical_features, dtype=float).reshape(1, -1)

    # Scale -> reconstruct -> error
    scaled = scaler.transform(full_input)
    reconstructed = model.predict(scaled)
    recon_error = float(np.mean(np.square(scaled - reconstructed)))
    is_anomaly = int(recon_error > threshold)

    return {
        "is_anomaly": is_anomaly,
        "reconstruction_error": recon_error,
        "threshold": threshold,
    }
