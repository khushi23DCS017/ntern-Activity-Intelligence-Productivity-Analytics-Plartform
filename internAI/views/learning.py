# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.charts import plot_radar_chart, plot_bar_chart
from components.kpi_cards import kpi_card

def render():
    st.markdown("<div class='main-header'>Learning Progress Dashboard</div>", unsafe_allow_html=True)
    st.write("Track intern development, skill acquisition, and training completion.")

    data = get_all_data()
    learning_df = data.get("learning", pd.DataFrame())

    if learning_df.empty:
        st.warning("No learning progress data available.")
        return

    interns = learning_df["intern_name"].unique().tolist()
    skills = learning_df["course_name"].unique().tolist()

    st.subheader("Skill Profile Comparison")

    col1, col2 = st.columns([1, 2])
    with col1:
        selected_intern = st.selectbox("Select Intern Profile", list(interns))
        st.markdown("<br>", unsafe_allow_html=True)
        my_learning = learning_df[learning_df["intern_name"] == selected_intern]
        kpi_card("Total Courses Active", str(len(my_learning)), "📚")
        total_prog = my_learning["progress_percent"].sum()
        kpi_card("Learning Progress Total", f"{total_prog:.0f}%", "⏱️")

    with col2:
        skill_df = my_learning[["course_name", "knowledge_score"]].copy()
        skill_df.columns = ["Skill", "Score"]
        skill_df["Score"] = skill_df["Score"].fillna(my_learning["test_score"]).fillna(70)
        if not skill_df.empty:
            fig_radar = plot_radar_chart(skill_df, "Skill", "Score", f"{selected_intern} Skill Profile")
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("No skill scores available.")

    st.markdown("---")

    col_prog1, col_prog2 = st.columns(2)
    with col_prog1:
        st.subheader("Course Completion Tracking")
        for _, row in my_learning.iterrows():
            prog = row.get("progress_percent") or 0
            st.write(f"**{row['course_name']}**")
            st.progress(float(prog) / 100.0)
            st.caption(f"{prog}% - {row.get('completion_status', 'In Progress')}")

    with col_prog2:
        st.subheader("Progress by Course")
        growth_df = my_learning[["course_name", "progress_percent"]].copy()
        growth_df.columns = ["Course", "Progress"]
        growth_df["Progress"] = growth_df["Progress"].fillna(0)
        if not growth_df.empty:
            fig_bar = plot_bar_chart(growth_df, "Course", "Progress", f"Progress by Course ({selected_intern})", orientation="h")
            st.plotly_chart(fig_bar, use_container_width=True)
