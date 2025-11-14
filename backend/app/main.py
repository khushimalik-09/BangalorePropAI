import os
import time
import json
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from . import model as model_module
from .schemas import PredictRequest, PredictResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = FastAPI(title="BangalorePropAI - Minimal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "changeme")
MODEL_PATH = os.getenv("MODEL_PATH", "./data/bangalore_home_prices_model.pickle")
COLUMNS_PATH = os.getenv("COLUMNS_PATH", "./data/columns.json")

# eager load
model_module.load_columns(COLUMNS_PATH)
model_module.load_model(MODEL_PATH)
model_module.load_scaler()

@app.get("/api/metadata")
def metadata():
    cols = model_module._columns.get("data_columns", [])
    locations = [c for c in cols[3:]] if len(cols) > 3 else []
    return {"locations": locations, "feature_order": ["total_sqft", "bath", "bhk"]}

@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    start = time.time()
    try:
        pred = model_module.predict(req.total_sqft, req.bhk, req.bath, req.location.lower())
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Model not loaded on server")
    latency = time.time() - start
    log = {
        "event": "predict",
        "ts": time.time(),
        "model_version": model_module._model_version,
        "input": {"total_sqft": req.total_sqft, "bhk": req.bhk, "bath": req.bath, "location": req.location},
        "prediction": pred,
        "latency_s": latency
    }
    logger.info(json.dumps(log))
    model_module.audit_log(log)
    return PredictResponse(predicted_price_lakhs=pred, model_version=model_module._model_version, input=req)

@app.get("/healthz")
def health(request: Request):
    key = request.headers.get("X-API-KEY")
    if key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    ok = model_module._model is not None
    return {"ok": ok, "model_loaded": ok, "model_version": model_module._model_version}

@app.post("/admin/upload")
async def admin_upload(request: Request, model_file: UploadFile = File(None), columns_file: UploadFile = File(None)):
    key = request.headers.get("X-API-KEY")
    if key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    saved = []
    # save model
    if model_file:
        dest = MODEL_PATH
        with open(dest, "wb") as f:
            f.write(await model_file.read())
        saved.append("model")
    if columns_file:
        dest = COLUMNS_PATH
        with open(dest, "wb") as f:
            f.write(await columns_file.read())
        saved.append("columns")
    # validate by trying a test predict (use first location if present)
    model_module.load_columns(COLUMNS_PATH)
    ok = model_module.load_model(MODEL_PATH)
    if ok:
        # attempt simple predict to validate
        cols = model_module._columns.get("data_columns", [])
        sample_loc = cols[3] if len(cols) > 3 else ""
        try:
            _ = model_module.predict(1000, 2, 2, sample_loc)
        except Exception as e:
            # failed validation -> keep previous model in memory if needed
            return {"saved": saved, "model_loaded": False, "error": str(e)}
    return {"saved": saved, "model_loaded": ok}
