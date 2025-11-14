import json
import os
import pickle
import numpy as np
from typing import List, Optional

MODEL_PATH = os.getenv("MODEL_PATH", "./data/bangalore_home_prices_model.pickle")
COLUMNS_PATH = os.getenv("COLUMNS_PATH", "./data/columns.json")
SCALER_PATH = os.getenv("SCALER_PATH", "./data/scaler.pkl")
AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "./data/audit_log.txt")
ENABLE_AUDIT = os.getenv("ENABLE_AUDIT_LOGS", "false").lower() == "true"

_model = None
_columns = None
_scaler = None
_model_version = "v0"

def load_columns(path: str = COLUMNS_PATH):
    global _columns
    try:
        with open(path, "r", encoding="utf-8") as f:
            _columns = json.load(f)
    except Exception:
        _columns = {"data_columns": []}
    return _columns

def load_model(path: str = MODEL_PATH):
    global _model, _model_version
    try:
        with open(path, "rb") as f:
            _model = pickle.load(f)
        _model_version = f"{os.path.basename(path)}"
        return True
    except Exception:
        _model = None
        return False

def load_scaler(path: str = SCALER_PATH):
    global _scaler
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                _scaler = pickle.load(f)
        except Exception:
            _scaler = None
    else:
        _scaler = None
    return _scaler

def ensure_loaded():
    if _columns is None:
        load_columns()
    if _model is None:
        load_model()
    if _scaler is None:
        load_scaler()

def build_feature_vector(total_sqft: float, bhk: int, bath: int, location: str) -> np.ndarray:
    ensure_loaded()
    cols: List[str] = _columns.get("data_columns", [])
    # numeric order: total_sqft, bath, bhk
    num_feats = [float(total_sqft), float(bath), int(bhk)]
    # location columns start at index 3
    loc_cols = cols[3:] if len(cols) > 3 else []
    loc_vector = [0] * len(loc_cols)
    loc = location.lower().strip()
    if loc in loc_cols:
        idx = loc_cols.index(loc)
        loc_vector[idx] = 1
    # else keep zeros (unknown => all zeros)
    arr = np.array(num_feats + loc_vector, dtype=float).reshape(1, -1)
    if _scaler is not None:
        try:
            arr = _scaler.transform(arr)
        except Exception:
            pass
    return arr

def predict(total_sqft: float, bhk: int, bath: int, location: str) -> Optional[float]:
    ensure_loaded()
    if _model is None:
        raise RuntimeError("Model not loaded")
    x = build_feature_vector(total_sqft, bhk, bath, location)
    pred = _model.predict(x)
    return float(pred[0])

def audit_log(record: dict):
    if not ENABLE_AUDIT:
        return
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass
