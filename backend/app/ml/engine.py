import joblib
import os
import pandas as pd
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../../../models')

class MLEngine:
    def __init__(self):
        self.rf_model = None
        self.if_model = None
        self.features = ['packet_count', 'byte_count', 'duration', 'packets_per_second', 'bytes_per_second', 'syn_count', 'syn_ratio']
        self.load_models()

    def load_models(self):
        rf_path = os.path.join(MODEL_DIR, 'random_forest.pkl')
        if_path = os.path.join(MODEL_DIR, 'isolation_forest.pkl')
        
        if os.path.exists(rf_path):
            self.rf_model = joblib.load(rf_path)
        if os.path.exists(if_path):
            self.if_model = joblib.load(if_path)

    def analyze_flows(self, df: pd.DataFrame):
        if df.empty:
            return pd.DataFrame()
            
        # Ensure features exist
        for col in self.features:
            if col not in df.columns:
                df[col] = 0
                
        X = df[self.features].fillna(0)
        
        rf_preds = ["NORMAL"] * len(df)
        rf_probs = [0.0] * len(df)
        if self.rf_model:
            rf_preds = self.rf_model.predict(X)
            # Get probability for the predicted class
            probs = self.rf_model.predict_proba(X)
            # Ensure we get the correct probability matching the prediction
            # RandomForestClassifier classes_ usually sorted
            class_labels = self.rf_model.classes_
            rf_probs = []
            for i, p in enumerate(rf_preds):
                class_idx = list(class_labels).index(p)
                rf_probs.append(float(probs[i][class_idx]))
            
        if_preds = [1] * len(df)
        if_scores = [0.0] * len(df)
        if self.if_model:
            if_preds = self.if_model.predict(X)
            # decision_function: The anomaly score of the input samples. 
            # The lower, the more abnormal. Negative scores represent outliers.
            raw_scores = self.if_model.decision_function(X)
            # Normalize score to 0-100 range for anomaly (lower raw score -> higher anomaly)
            # Standard IF scores are usually between -1.0 and 0.5. 
            # We map: negative -> higher score, positive -> 0.
            if_scores = []
            for score in raw_scores:
                if score >= 0:
                    if_scores.append(0.0)
                else:
                    # score is usually > -1.0, map to 0-100
                    normalized = min(100.0, max(0.0, abs(score) * 100))
                    if_scores.append(round(normalized, 2))
            
        return pd.DataFrame({
            'rf_prediction': rf_preds,
            'rf_probability': rf_probs,
            'if_anomaly': [p == -1 for p in if_preds],
            'if_score': if_scores
        }, index=df.index)
