import numpy as np
import joblib

# Load model and encoders
anomaly_model = joblib.load('/content/cloud/models/anomaly_model.pkl')
tag_encoder = joblib.load('/content/cloud/models/anomaly_tag_encoder.pkl')
cloud_encoder = joblib.load('/content/cloud/models/anomaly_cloud_encoder.pkl')

def detect_anomaly(cpu, memory, cost, tag, cloud):
    """
    Returns:
        - is_anomaly (bool)
        - anomaly_score (float, 0-1: higher = more anomalous)
        - reason (str, e.g. 'CPU 98% is unusually high')
    """
    # Encode categorical inputs
    import pandas as pd
    tag_encoded = tag_encoder.transform([tag])[0]
    cloud_encoded = cloud_encoder.transform([cloud])[0]
    features = pd.DataFrame([[cpu, memory, cost, tag_encoded, cloud_encoded]],
                        columns=['CPU', 'Memory', 'Cost', 'Tag_encoded', 'Cloud_encoded'])
    pred = anomaly_model.predict(features)[0]     # -1=anomaly, 1=normal
    score = -anomaly_model.decision_function(features)[0]  # Higher = more anomalous
    is_anomaly = bool(pred == -1)
    anomaly_score = float(score) / 1.0  # Not strictly normalized, but meaningful for ranking

    if is_anomaly:
        # Basic post-hoc explanation (can be improved)
        if cpu > 90:
            reason = f'CPU {cpu}% is unusually high'
        elif cpu < 10:
            reason = f'CPU {cpu}% is unusually low'
        elif memory > 90:
            reason = f'Memory {memory}% is unusually high'
        elif memory < 10:
            reason = f'Memory {memory}% is unusually low'
        elif cost > 200:
            reason = f'Cost ${cost} is unusually high'
        elif cost < 2:
            reason = f'Cost ${cost} is unusually low'
        else:
            reason = "Resource usage pattern is abnormal for given instance/provider"
    else:
        reason = "Resource usage is within normal range"
    return is_anomaly, anomaly_score, reason