# pyre-ignore-all-errors
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ================================================================
# DATABASE CONFIG
# Change DB_HOST if running on a different machine
# ================================================================
DB_CONFIG = {
    "host"    : os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "intern_analytics"),
    "user"    : os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "1234")
}

# ================================================================
# ML MODEL PATHS
# Place your .pkl files in the models/ folder
# ================================================================
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

PRODUCTIVITY_MODEL_PATH  = os.path.join(MODELS_DIR, "productivity_model.pkl")
CLUSTERING_MODEL_PATH    = os.path.join(MODELS_DIR, "clustering_model.pkl")
CLASSIFICATION_MODEL_PATH= os.path.join(MODELS_DIR, "classification_model.pkl")

# ================================================================
# ML FEATURE COLUMNS
# Must match exactly what models were trained on
# ================================================================
PRODUCTIVITY_FEATURES  = ['active_days', 'number_of_activities', 'tech_count']
CLUSTERING_FEATURES    = ['productivity_score', 'hours_spent', 'avg_score']
CLASSIFICATION_FEATURES= ['active_days', 'number_of_activities',
                           'tech_count', 'hours_spent', 'avg_score']

# ================================================================
# BUSINESS THRESHOLDS
# ================================================================
AT_RISK_PROGRESS_THRESHOLD  = 50.0   # progress % below this = at risk
AT_RISK_KNOWLEDGE_THRESHOLD = 70.0   # knowledge % below this = at risk

# ================================================================
# COURSE SHORT NAMES (display only)
# ================================================================
COURSE_SHORT_NAMES = {
    'Basic Python Programming'            : 'Python',
    'Basic SQL'                           : 'SQL',
    'Data Processing using NumPy & Pandas': 'NumPy',
    'Data Processing using Pyspark'       : 'PySpark',
}
