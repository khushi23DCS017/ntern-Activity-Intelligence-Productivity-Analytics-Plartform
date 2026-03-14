# pyre-ignore-all-errors
import pandas as pd
import psycopg2
import streamlit as st
from config import DB_CONFIG
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ================================================================
# CONNECTION
# ================================================================
def run_query(sql, params=None):
    """Open fresh connection, run query, close. Returns DataFrame."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        df = pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()
    return df

# ================================================================
# CACHED QUERIES (refresh every 60 seconds)
# ================================================================
@st.cache_data(ttl=60)
def get_all_progress():
    return run_query("""
        SELECT
            di.intern_name,
            dm.mentor_name,
            dc.course_name,
            dc.course_order,
            f.progress_percent,
            f.completion_status,
            f.knowledge_check_pct,
            f.overall_test_pct,
            f.completed_assignment_scored,
            f.completed_assignment_total,
            f.start_date,
            f.end_date
        FROM fact_learning_progress f
        JOIN dim_intern di ON f.intern_id = di.intern_id
        JOIN dim_mentor dm ON f.mentor_id = dm.mentor_id
        JOIN dim_course dc ON f.course_id = dc.course_id
        ORDER BY di.intern_name, dc.course_order
    """)

@st.cache_data(ttl=60)
def get_all_eod():
    return run_query("""
        SELECT
            di.intern_name,
            da.activity_name,
            fa.activity_date,
            fa.hours
        FROM fact_activity fa
        JOIN dim_intern   di ON fa.intern_id   = di.intern_id
        JOIN dim_activity da ON fa.activity_id = da.activity_id
        ORDER BY fa.activity_date
    """)

@st.cache_data(ttl=60)
def get_ml_features():
    """
    Pulls all features needed for ML inference directly from DB.
    Returns one row per intern with all required columns.
    """
    return run_query("""
        SELECT
            di.intern_name                             AS intern_id,
            COUNT(DISTINCT fa.activity_date)           AS active_days,
            COUNT(fa.activity_event_id)                AS number_of_activities,
            COUNT(DISTINCT dc.course_id)               AS tech_count,
            COALESCE(SUM(fa.hours), 0)                 AS hours_spent,
            COALESCE(AVG(
                NULLIF((flp.knowledge_check_pct + flp.overall_test_pct) / 2, 0)
            ), 0)                                      AS avg_score,
            COALESCE(SUM(flp.completed_assignment_scored), 0) AS assignments_completed,
            COALESCE(AVG(flp.progress_percent), 0)     AS avg_progress
        FROM dim_intern di
        LEFT JOIN fact_activity fa         ON di.intern_id = fa.intern_id
        LEFT JOIN fact_learning_progress flp ON di.intern_id = flp.intern_id
        LEFT JOIN dim_course dc            ON flp.course_id = dc.course_id
        GROUP BY di.intern_name
        ORDER BY di.intern_name
    """)

def get_course_order(df_lms):
    """Get course names sorted by course_order from DB data."""
    return (
        df_lms[['course_name', 'course_order']]
        .drop_duplicates()
        .sort_values('course_order')
        ['course_name'].tolist()
    )
