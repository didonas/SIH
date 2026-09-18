import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib
import os
import json

os.makedirs('training/datasets', exist_ok=True)
os.makedirs('models', exist_ok=True)

n_samples = 2000
features = ['packet_count', 'byte_count', 'duration', 'packets_per_second', 'bytes_per_second', 'syn_count', 'syn_ratio']

normal_data = pd.DataFrame({
    'packet_count': np.random.randint(1, 50, n_samples),
    'byte_count': np.random.randint(100, 10000, n_samples),
    'duration': np.random.uniform(0.1, 10.0, n_samples),
    'syn_count': np.random.randint(0, 3, n_samples),
    'label': 'NORMAL'
})
normal_data['packets_per_second'] = normal_data['packet_count'] / normal_data['duration']
normal_data['bytes_per_second'] = normal_data['byte_count'] / normal_data['duration']
normal_data['syn_ratio'] = normal_data['syn_count'] / normal_data['packet_count']

attack_data = pd.DataFrame({
    'packet_count': np.random.randint(100, 1000, n_samples),
    'byte_count': np.random.randint(5000, 100000, n_samples),
    'duration': np.random.uniform(0.01, 2.0, n_samples),
    'syn_count': np.random.randint(90, 1000, n_samples),
    'label': 'ATTACK'
})
attack_data['packets_per_second'] = attack_data['packet_count'] / attack_data['duration']
attack_data['bytes_per_second'] = attack_data['byte_count'] / attack_data['duration']
attack_data['syn_ratio'] = attack_data['syn_count'] / attack_data['packet_count']

df = pd.concat([normal_data, attack_data]).reset_index(drop=True)
df.to_csv('training/datasets/synthetic_dataset.csv', index=False)

X = df[features]
y = df['label']

# True Train/Test split for evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

print("--- Random Forest Evaluation (Test Set) ---")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

metrics_rf = {
    "accuracy": round(accuracy_score(y_test, y_pred), 4),
    "precision": round(precision_score(y_test, y_pred, pos_label='ATTACK'), 4),
    "recall": round(recall_score(y_test, y_pred, pos_label='ATTACK'), 4),
    "f1_score": round(f1_score(y_test, y_pred, pos_label='ATTACK'), 4)
}
print(metrics_rf)
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred, labels=['NORMAL', 'ATTACK']))

joblib.dump(rf, 'models/random_forest.pkl')
with open('models/rf_metrics.json', 'w') as f:
    json.dump(metrics_rf, f)

print("\n--- Isolation Forest Evaluation (Test Set) ---")
# Train Isolation Forest mostly on NORMAL data to establish baseline
X_train_if = X_train[y_train == 'NORMAL']
isf = IsolationForest(contamination=0.05, random_state=42)
isf.fit(X_train_if)

# Evaluate on full test set
isf_pred = isf.predict(X_test)
# -1 is anomaly (ATTACK), 1 is normal (NORMAL)
anomaly_labels = np.where(isf_pred == -1, 'ATTACK', 'NORMAL')

metrics_if = {
    "accuracy": round(accuracy_score(y_test, anomaly_labels), 4)
}
print(metrics_if)
print("Confusion Matrix:")
print(confusion_matrix(y_test, anomaly_labels, labels=['NORMAL', 'ATTACK']))

joblib.dump(isf, 'models/isolation_forest.pkl')
with open('models/if_metrics.json', 'w') as f:
    json.dump(metrics_if, f)
