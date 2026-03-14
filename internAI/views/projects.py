# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.charts import plot_pie_chart, plot_bar_chart
from components.kpi_cards import kpi_card

def render():
    st.markdown("<div class='main-header'>Project Contributions</div>", unsafe_allow_html=True)
    st.write("Track intern work and impact across courses/projects.")

    data = get_all_data()
    proj_df = data.get("projects", pd.DataFrame())

    if proj_df.empty:
        st.warning("No project/course contribution data available.")
        return

    projects = proj_df["Project"].unique().tolist()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Active Projects", len(projects), "📁")
    with col2:
         kpi_card("Total Contrib Tasks", proj_df['Tasks_Completed'].sum(), "✅")
    with col3:
         kpi_card("Project Hours Spent", proj_df['Hours_Spent'].sum(), "⏱️")
         
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Bar chart: project contributions by intern
        top_contrib = proj_df.groupby('Intern_ID')['Tasks_Completed'].sum().reset_index().sort_values(by='Tasks_Completed', ascending=False).head(10)
        fig_bar = plot_bar_chart(top_contrib, 'Intern_ID', 'Tasks_Completed', "Top 10 Project Contributors (by Tasks)")
        if fig_bar: st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_chart2:
        # Donut chart: project workload distribution (Hours spent per project)
        workload = proj_df.groupby('Project')['Hours_Spent'].sum().reset_index()
        fig_pie = plot_pie_chart(workload, 'Project', 'Hours_Spent', "Project Workload Distribution (Hours)", hole=0.4)
        if fig_pie: st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Course/Project Progress Summary")
    timeline_df = proj_df.groupby("Project").agg(
        Tasks_Completed=("Tasks_Completed", "sum"),
        Contribution_Score=("Contribution_Score", "mean"),
    ).reset_index()
    timeline_df["Completion %"] = timeline_df["Contribution_Score"].round(0).astype(int)
    st.dataframe(timeline_df[["Project", "Tasks_Completed", "Completion %"]], use_container_width=True, hide_index=True)
