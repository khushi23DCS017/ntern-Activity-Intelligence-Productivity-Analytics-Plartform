# pyre-ignore-all-errors
"""
Loads data from PostgreSQL. Expects a star schema with dim_* and fact_* tables.
Adjust SQL below if your schema differs (table/column names).
"""
import pandas as pd
import streamlit as st

from utils.db_config import get_db_uri


@st.cache_data(ttl=300)  # Cache 5 min
def _run_query(query: str) -> pd.DataFrame:
    """Execute SQL and return DataFrame."""
    try:
        return pd.read_sql_query(query, get_db_uri())
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


def get_all_data():
    """
    Load summary, productivity, clusters, tech, metrics, learning, projects from PostgreSQL.
    Schema assumed: dim_intern, dim_mentor, dim_course, dim_activity, dim_date,
                    fact_activity, fact_learning_progress.
    """
    summary_df = _load_summary()
    prod_df = _load_productivity()
    clusters_df = _load_clusters()
    tech_df = _load_tech()
    metrics = _load_metrics()
    learning_df = _load_learning()
    projects_df = _load_projects()

    return {
        "summary": summary_df,
        "productivity": prod_df,
        "clusters": clusters_df,
        "tech": tech_df,
        "metrics": metrics,
        "learning": learning_df,
        "projects": projects_df,
    }


def _load_summary():
    """Intern summary: Intern_ID, Role, Total_Hours, Productivity_Score, Tasks_Completed, Manager_ID, Mentor_ID."""
    query = """
    WITH intern_hours AS (
        SELECT fa.intern_id, SUM(fa.hours) AS total_hours, COUNT(*) AS task_count
        FROM fact_activity fa
        GROUP BY fa.intern_id
    ),
    intern_scores AS (
        SELECT flp.intern_id,
               AVG(COALESCE(flp.knowledge_score, flp.test_score, 70)) AS avg_score
        FROM fact_learning_progress flp
        GROUP BY flp.intern_id
    )
    SELECT
        i.intern_name AS "Intern_ID",
        'Intern' AS "Role",
        COALESCE(ih.total_hours, 0)::numeric(10,2) AS "Total_Hours",
        COALESCE(ROUND((iscores.avg_score)::numeric, 2), 75) AS "Productivity_Score",
        COALESCE(ih.task_count, 0)::int AS "Tasks_Completed",
        i.mentor_name AS "Manager_ID",
        i.mentor_name AS "Mentor_ID"
    FROM dim_intern i
    LEFT JOIN intern_hours ih ON i.intern_id = ih.intern_id
    LEFT JOIN intern_scores iscores ON i.intern_id = iscores.intern_id
    """
    return _run_query(query)


def _load_productivity():
    """Daily activity: Intern_ID, Date, Activity, Hours_Spent, Tasks_Completed."""
    query = """
    SELECT
        i.intern_name AS "Intern_ID",
        d.date::text AS "Date",
        a.activity_name AS "Activity",
        fa.hours AS "Hours_Spent",
        1 AS "Tasks_Completed"
    FROM fact_activity fa
    JOIN dim_intern i ON fa.intern_id = i.intern_id
    JOIN dim_activity a ON fa.activity_id = a.activity_id
    JOIN dim_date d ON fa.date_id = d.date_id
    ORDER BY d.date DESC, i.intern_name
    """
    return _run_query(query)


def _load_clusters():
    """Intern clusters: Intern_ID, Cluster, Risk_Indicator (derived from performance)."""
    query = """
    WITH perf AS (
        SELECT
            i.intern_id,
            i.intern_name,
            SUM(fa.hours) AS total_hours,
            (SELECT AVG(COALESCE(flp.knowledge_score, flp.test_score, 70))
             FROM fact_learning_progress flp WHERE flp.intern_id = i.intern_id) AS avg_score
        FROM dim_intern i
        LEFT JOIN fact_activity fa ON i.intern_id = fa.intern_id
        GROUP BY i.intern_id, i.intern_name
    )
    SELECT
        intern_name AS "Intern_ID",
        CASE
            WHEN COALESCE(avg_score, 0) >= 85 THEN 'High Performer'
            WHEN COALESCE(avg_score, 0) >= 70 THEN 'Consistent'
            WHEN COALESCE(avg_score, 0) >= 55 THEN 'Needs Support'
            ELSE 'Learning Phase'
        END AS "Cluster",
        CASE
            WHEN COALESCE(avg_score, 0) < 55 THEN 'High'
            WHEN COALESCE(avg_score, 0) < 70 THEN 'Medium'
            ELSE 'Low'
        END AS "Risk_Indicator"
    FROM perf
    """
    return _run_query(query)


def _load_tech():
    """Technology usage: Intern_ID, Technology, Usage_Frequency, Proficiency_Score (from courses)."""
    query = """
    SELECT
        i.intern_name AS "Intern_ID",
        c.course_name AS "Technology",
        COUNT(*)::int AS "Usage_Frequency",
        ROUND(AVG(COALESCE(flp.knowledge_score, flp.test_score, 70))::numeric, 2) AS "Proficiency_Score"
    FROM fact_learning_progress flp
    JOIN dim_intern i ON flp.intern_id = i.intern_id
    JOIN dim_course c ON flp.course_id = c.course_id
    GROUP BY i.intern_name, c.course_name
    """
    return _run_query(query)


def _load_metrics():
    """ML model evaluation metadata (placeholder - no dedicated table in schema)."""
    return {}


def _load_learning():
    """Course progress: intern_name, course_name, progress_percent, knowledge_score, test_score, completion_status."""
    query = """
    SELECT
        i.intern_name,
        c.course_name,
        flp.progress_percent,
        flp.knowledge_score,
        flp.test_score,
        flp.completion_status
    FROM fact_learning_progress flp
    JOIN dim_intern i ON flp.intern_id = i.intern_id
    JOIN dim_course c ON flp.course_id = c.course_id
    ORDER BY i.intern_name, c.course_name
    """
    return _run_query(query)


def _load_projects():
    """Project-like data from courses (course = project): Intern_ID, Project, Tasks_Completed, Hours_Spent, Contribution_Score."""
    query = """
    SELECT
        i.intern_name AS "Intern_ID",
        c.course_name AS "Project",
        COUNT(*)::int AS "Tasks_Completed",
        SUM(COALESCE(flp.progress_percent, 0))::numeric(10,2) AS "Hours_Spent",
        ROUND(AVG(COALESCE(flp.knowledge_score, flp.test_score, 70))::numeric, 2) AS "Contribution_Score"
    FROM fact_learning_progress flp
    JOIN dim_intern i ON flp.intern_id = i.intern_id
    JOIN dim_course c ON flp.course_id = c.course_id
    GROUP BY i.intern_name, c.course_name
    """
    return _run_query(query)
