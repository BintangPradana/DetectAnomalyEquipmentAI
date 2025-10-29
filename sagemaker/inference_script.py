import os, io, joblib, pandas as pd

def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "model.joblib"))

def input_fn(input_data, content_type):
    if "csv" in content_type:
        return pd.read_csv(io.StringIO(input_data))
    raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    X = input_data[["temperature","vibration","current"]]
    probs = model.predict_proba(X)[:,1]
    preds = (probs >= 0.5).astype(int)
    out = input_data.copy()
    out["predicted_abnormal"] = preds
    out["abnormal_probability"] = probs
    return out

def output_fn(prediction, accept):
    return prediction.to_csv(index=False), "text/csv"
