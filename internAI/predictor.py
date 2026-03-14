# pyre-ignore-all-errors
"""
predictor.py
------------
Loads all 3 trained models and provides a single function
get_ml_predictions(df_features) that returns enriched DataFrame
with productivity prediction, cluster category, and at-risk flag.

Used by pages/ml_insights.py and injected into dashboards.
"""

import os
import sys
import pickle
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    PRODUCTIVITY_MODEL_PATH, CLUSTERING_MODEL_PATH,
    CLASSIFICATION_MODEL_PATH,
    PRODUCTIVITY_FEATURES, CLUSTERING_FEATURES
)

# ================================================================
# LOAD MODELS (cached so they load once per session)
# ================================================================
@st.cache_resource
def load_models():
    models = {}

    # Productivity regression
    if os.path.exists(PRODUCTIVITY_MODEL_PATH):
        with open(PRODUCTIVITY_MODEL_PATH, 'rb') as f:
            models['productivity'] = pickle.load(f)
    else:
        models['productivity'] = None
        st.warning(f"productivity_model.pkl not found at {PRODUCTIVITY_MODEL_PATH}")

    # Clustering KMeans
    if os.path.exists(CLUSTERING_MODEL_PATH):
        with open(CLUSTERING_MODEL_PATH, 'rb') as f:
            models['clustering'] = pickle.load(f)
    else:
        models['clustering'] = None
        st.warning(f"clustering_model.pkl not found at {CLUSTERING_MODEL_PATH}")

    # At-risk classification
    if os.path.exists(CLASSIFICATION_MODEL_PATH):
        with open(CLASSIFICATION_MODEL_PATH, 'rb') as f:
            models['classification'] = pickle.load(f)
    else:
        models['classification'] = None
        st.warning(f"classification_model.pkl not found at {CLASSIFICATION_MODEL_PATH}")

    return models

# ================================================================
# COMPUTE PRODUCTIVITY SCORE
# (same formula as feature_engineering.py)
# ================================================================
def compute_productivity_score(df):
    """
    productivity_score = 0.4*assignments_completed
                       + 0.3*avg_score
                       + 0.3*hours_spent
    """
    return (
        0.4 * df['assignments_completed'] +
        0.3 * df['avg_score'] +
        0.3 * df['hours_spent']
    )

# ================================================================
# MAIN INFERENCE FUNCTION
# ================================================================
def get_ml_predictions(df_features):
    """
    Takes the ML features DataFrame from database.get_ml_features()
    Returns same DataFrame enriched with:
        - productivity_score       (computed from formula)
        - predicted_productivity   (from regression model)
        - category                 (from clustering model)
        - cluster                  (raw cluster number)
        - at_risk                  (0/1 from classification model)
        - at_risk_label            ('At Risk' / 'Not At Risk')
        - at_risk_probability      (confidence %)
    """
    df = df_features.copy()

    # Compute productivity score using formula
    df['productivity_score'] = compute_productivity_score(df)

    models = load_models()

    # -------------------------------------------------------
    # 1. PRODUCTIVITY REGRESSION
    # -------------------------------------------------------
    prod_model = models.get('productivity')
    if prod_model is not None:
        try:
            X_prod = df[PRODUCTIVITY_FEATURES].fillna(0)
            df['predicted_productivity'] = prod_model.predict(X_prod)
        except Exception as e:
            df['predicted_productivity'] = df['productivity_score']
            st.warning(f"Productivity model error: {e}")
    else:
        df['predicted_productivity'] = df['productivity_score']

    # -------------------------------------------------------
    # 2. CLUSTERING
    # -------------------------------------------------------
    clust_bundle = models.get('clustering')
    if clust_bundle is not None:
        try:
            scaler    = clust_bundle['scaler']
            kmeans    = clust_bundle['kmeans']
            label_map = clust_bundle['label_map']

            X_clust        = df[CLUSTERING_FEATURES].fillna(0)
            X_clust_scaled = scaler.transform(X_clust)
            cluster_labels = kmeans.predict(X_clust_scaled)

            df['cluster']  = cluster_labels
            df['category'] = [label_map.get(c, 'Unknown') for c in cluster_labels]
        except Exception as e:
            df['cluster']  = 0
            df['category'] = 'Unknown'
            st.warning(f"Clustering model error: {e}")
    else:
        df['cluster']  = 0
        df['category'] = 'Unknown'

    # -------------------------------------------------------
    # 3. AT-RISK CLASSIFICATION
    # -------------------------------------------------------
    clf_bundle = models.get('classification')
    if clf_bundle is not None:
        try:
            clf      = clf_bundle['model']
            scaler_c = clf_bundle['scaler']
            features = clf_bundle['features']

            X_clf        = df[features].fillna(0)
            X_clf_scaled = scaler_c.transform(X_clf)
            preds        = clf.predict(X_clf_scaled)
            probas       = clf.predict_proba(X_clf_scaled)[:, 1]

            df['at_risk']             = preds
            df['at_risk_label']       = ['⚠️ At Risk' if p == 1 else '✅ Safe' for p in preds]
            df['at_risk_probability'] = (probas * 100).round(1)
        except Exception as e:
            df['at_risk']             = 0
            df['at_risk_label']       = '✅ Safe'
            df['at_risk_probability'] = 0.0
            st.warning(f"Classification model error: {e}")
    else:
        df['at_risk']             = 0
        df['at_risk_label']       = '✅ Safe'
        df['at_risk_probability'] = 0.0

    return df
