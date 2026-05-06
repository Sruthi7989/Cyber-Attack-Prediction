import numpy as np
import pandas as pd
import torch
import joblib
import sys
from pytorch_tabnet.tab_model import TabNetClassifier

MODEL_DIR = "models"
MODEL_PATH = f"{MODEL_DIR}/tabnet_model.zip.zip"
SCALER_PATH = f"{MODEL_DIR}/scaler.joblib"

# Label mapping
label_map = {
    0: "Exploits",
    1: "Generic",
    2: "Normal",
    3: "Other"
}

# Feature columns (40)
feature_columns = [
    "dur","spkts","dpkts","sbytes","dbytes","rate","sttl","dttl","sload","dload",
    "sloss","dloss","sinpkt","dinpkt","sjit","djit","swin","stcpb","dtcpb","dwin",
    "tcprtt","synack","ackdat","smean","dmean","trans_depth","response_body_len",
    "ct_srv_src","ct_state_ttl","ct_dst_ltm","ct_src_dport_ltm","ct_dst_sport_ltm",
    "ct_dst_src_ltm","is_ftp_login","ct_ftp_cmd","ct_flw_http_mthd","ct_src_ltm",
    "ct_srv_dst","is_sm_ips_ports"
]


print("Loading TabNet model and scaler...")
scaler = joblib.load(SCALER_PATH)

tabnet = TabNetClassifier()
tabnet.load_model(MODEL_PATH)

# Force GPU if available
if torch.cuda.is_available():
    tabnet.device = torch.device("cuda")
else:
    tabnet.device = torch.device("cpu")

print(f" Model and scaler loaded successfully! Device: {tabnet.device}\n")

def get_input_data():
    """
    Decide how to load input:
      1. CSV file path as argument
      2. Inline comma-separated string as argument
      3. Ask user interactively
    """
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.endswith(".csv"):
            print(f"📂 Loading input from file: {arg}")
            df = pd.read_csv(arg)
            return df[feature_columns].values
        else:
            print(f"🧮 Using comma-separated inline input")
            values = np.array([list(map(float, arg.split(',')))])
            return values
    else:
        print("\nEnter your comma-separated feature values:")
        input_str = input("👉 ")
        values = np.array([list(map(float, input_str.split(',')))])
        return values

# Get input
X_input = get_input_data()

# Validate shape
if X_input.shape[1] != len(feature_columns):
    raise ValueError(f"Expected {len(feature_columns)} features, got {X_input.shape[1]}")


X_scaled = scaler.transform(X_input)
preds = tabnet.predict(X_scaled)
probs = tabnet.predict_proba(X_scaled)

print("\n========== PREDICTION RESULTS ==========")
for i, (p, prob) in enumerate(zip(preds, probs)):
    label = label_map.get(int(p), f"Unknown({int(p)})")
    print(f"Sample {i+1}:")
    print(f"  Predicted Class ID  : {int(p)}")
    print(f"  Predicted Label     : {label}")
    print(f"  Class Probabilities : {np.round(prob, 4)}\n")
print("========================================")
