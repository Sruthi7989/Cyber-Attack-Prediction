import os
import numpy as np
import torch
import joblib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from pytorch_tabnet.tab_model import TabNetClassifier
from .models import PredictionRecord
from collections import Counter
import json
from django.db.models import Count

MODEL_DIR = "model/models"
MODEL_PATH = os.path.join(MODEL_DIR, "tabnet_model.zip.zip") 
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")

label_map = {
    0: "Exploits",
    1: "Generic",
    2: "Normal",
    3: "Other"
}

feature_columns = [
    "dur","spkts","dpkts","sbytes","dbytes","rate","sttl","dttl","sload","dload",
    "sloss","dloss","sinpkt","dinpkt","sjit","djit","swin","stcpb","dtcpb","dwin",
    "tcprtt","synack","ackdat","smean","dmean","trans_depth","response_body_len",
    "ct_srv_src","ct_state_ttl","ct_dst_ltm","ct_src_dport_ltm","ct_dst_sport_ltm",
    "ct_dst_src_ltm","is_ftp_login","ct_ftp_cmd","ct_flw_http_mthd","ct_src_ltm",
    "ct_srv_dst","is_sm_ips_ports"
]

# Load model and scaler
scaler = joblib.load(SCALER_PATH)
tabnet = TabNetClassifier()
tabnet.load_model(MODEL_PATH)
tabnet.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create your views here.
def userhome(request):
    user = request.user
    return render(request, 'User/userhome.html', {'user':user})

@login_required
def prediction(request):
    context = {}
    if request.method == "POST":
        user_input = request.POST.get("features", "")
        try:
            values = [float(v.strip()) for v in user_input.split(",") if v.strip() != ""]
            if len(values) != len(feature_columns):
                raise ValueError(f"Expected {len(feature_columns)} values, got {len(values)}")

            X_input = np.array([values])
            X_scaled = scaler.transform(X_input)

            preds = tabnet.predict(X_scaled)
            probs = tabnet.predict_proba(X_scaled)
            pred_label = label_map.get(int(preds[0]), "Unknown")

            # Save prediction
            PredictionRecord.objects.create(
                user=request.user,
                input_data=user_input,
                predicted_class=pred_label
            )

            context.update({
                "predicted_label": pred_label,
                "probabilities": np.round(probs[0], 4)
            })

        except Exception as e:
            context["error"] = f"Error: {e}"

    return render(request, "User/prediction.html", context)

def datavisulization(request):
    return render(request, 'User/datavisulization.html')

def exsisting(request):
    return render(request, 'User/exsisting.html')

def proposed(request):
    return render(request, 'User/proposed.html')

@login_required
def history(request):
    user = request.user
    # Fetch this user’s prediction records (latest first)
    records = PredictionRecord.objects.filter(user=user).order_by("-created_at")
    return render(request, "User/history.html", {"records": records})

@login_required
def analytics(request):
    user = request.user
    records = PredictionRecord.objects.filter(user=user).order_by("created_at")

    # --- Prepare data ---
    labels = [r.created_at.strftime("%Y-%m-%d %H:%M") for r in records]
    classes = [r.predicted_class for r in records]

    # Count per class for bar/pie charts
    class_counts = Counter(classes)
    class_labels = list(class_counts.keys())
    class_values = list(class_counts.values())

    # Pass all as JSON-safe strings
    context = {
        "labels": json.dumps(labels),
        "classes": json.dumps(classes),
        "class_labels": json.dumps(class_labels),
        "class_values": json.dumps(class_values),
    }

    return render(request, "User/analytics.html", context)