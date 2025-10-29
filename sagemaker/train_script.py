import os, joblib, pandas as pd
from sklearn.ensemble import RandomForestClassifier

def main():
    input_path = "/opt/ml/input/data/train"
    model_dir = "/opt/ml/model"
    os.makedirs(model_dir, exist_ok=True)
    df = pd.read_csv(f"{input_path}/train.csv")
    X = df[["temperature","vibration","current"]]
    y = df["abnormal"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X,y)
    joblib.dump(model, f"{model_dir}/model.joblib")
    print("Saved model to", f"{model_dir}/model.joblib")

if __name__ == "__main__":
    main()
