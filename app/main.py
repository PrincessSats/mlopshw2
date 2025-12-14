# app/main.py

import os
import pickle
from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Попробуем joblib, если модель так сохранялась
try:
    import joblib
except ImportError:
    joblib = None


MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")

app = FastAPI(title="ML Service", version=MODEL_VERSION)


def load_model(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")

    if joblib is not None:
        try:
            return joblib.load(path)
        except Exception:
            pass

    with open(path, "rb") as f:
        return pickle.load(f)


model = load_model(MODEL_PATH)


class PredictRequest(BaseModel):
    features: List[float]


class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    version: str


@app.get("/health")
def health():
    """
    Эндпоинт для проверки состояния сервиса и версии модели.
    """
    return {
        "status": "ok",
        "version": MODEL_VERSION,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Эндпоинт инференса модели.
    Принимает список чисел (features), возвращает предсказание и confidence.
    """
    if not request.features:
        raise HTTPException(status_code=400, detail="features must not be empty")

    try:
        x = np.array(request.features, dtype=float).reshape(1, -1)
    except Exception:
        raise HTTPException(status_code=400, detail="cannot convert features to float array")

    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(x)[0]
            pred_idx = int(np.argmax(proba))
            confidence = float(proba[pred_idx])

            if hasattr(model, "classes_"):
                pred = model.classes_[pred_idx]
            else:
                pred = model.predict(x)[0]
        else:
            pred = model.predict(x)[0]
            confidence = 1.0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    return PredictResponse(
        prediction=str(pred),
        confidence=confidence,
        version=MODEL_VERSION,
    )