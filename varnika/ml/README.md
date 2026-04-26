# 🚀 Anomaly Detection for Cloud Resource Usage

## 📌 Overview
This module detects anomalies in cloud resource usage using an **Isolation Forest** model.  
It analyzes CPU, Memory, Cost, Instance Type (Tag), and Cloud Provider.

---

## 🚀 Usage

### Step 1: Import the module

```python
import sys
sys.path.append('cloud/ml')

from anomaly_detection import detect_anomaly
```

---

### Step 2: Call the function

```python
is_anomaly, score, reason = detect_anomaly(
    cpu=85,
    memory=80,
    cost=80,
    tag='m5.large',
    cloud='AWS'
)

print(is_anomaly, score, reason)
```

---

## 📊 Output

- **is_anomaly (bool)** → `True` if anomaly detected  
- **score (float)** → Higher = more anomalous  
- **reason (str)** → Human-readable explanation  

---

## 🧠 Model Details

- Algorithm: **Isolation Forest**
- Type: **Unsupervised Learning**
- Features used:
  - CPU
  - Memory
  - Cost
  - Tag (Instance Type)
  - Cloud Provider

---

## 📂 Project Structure

```
cloud/
│
├── ml/
│   └── anomaly_detection.py
│
├── models/
│   ├── anomaly_model.pkl
│   ├── anomaly_tag_encoder.pkl
│   └── anomaly_cloud_encoder.pkl
│
├── datasets/
│   └── cleaned_dataset.csv
```

---

## ⚠️ Important Notes

- Ensure model files exist in:
  ```
  cloud/models/
  ```
- These files are generated during training (Day 4 notebook)
- If missing, re-run the training notebook

---

## 🔌 Integration

### Backend (Django)
- Import `detect_anomaly()` in your view
- Pass user input values
- Return result via API

### UI
Display:
- Anomaly status  
- Score  
- Explanation  

---

## 💡 Example Use Case

```python
detect_anomaly(95, 90, 200, 't2.micro', 'AWS')
```

### Output
```
(True, 0.05, "CPU 95% is unusually high")
```

---

## 🎯 Why This Matters

- Helps detect cost spikes  
- Identifies inefficient resource usage  
- Enables proactive cloud monitoring  

---

## 👩‍💻 Author

Developed as part of **ML Cloud Optimization Project**  
**Day 4 – Intelligence Phase**

---

