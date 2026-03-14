# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.charts import plot_bar_chart, plot_line_chart, plot_scatter_clusters
from components.kpi_cards import kpi_card

def render():
    st.markdown("<div class='main-header'>Intern Productivity</div>", unsafe_allow_html=True)
    st.write("Track team productivity, task completion, and performance clusters.")
    
    data = get_all_data()
    summary_df = data.get('summary', pd.DataFrame())
    prod_df = data.get('productivity', pd.DataFrame())
    clusters_df = data.get('clusters', pd.DataFrame())
    
    if summary_df.empty or prod_df.empty:
        st.warning("Insufficient data.")
        return
        
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_tasks = summary_df['Tasks_Completed'].mean()
        kpi_card("Avg Tasks/Intern", f"{avg_tasks:.1f}", "📝", trend_type="up")
    with col2:
        total_hours = summary_df['Total_Hours'].sum()
        total_tasks = summary_df['Tasks_Completed'].sum()
        avg_time = total_hours / total_tasks if total_tasks > 0 else 0
        kpi_card("Avg Time/Task", f"{avg_time:.1f}h", "⏱️", trend_type="down")
    with col3:
        avg_prod = summary_df['Productivity_Score'].mean()
        kpi_card("Avg Prod Score", f"{avg_prod:.1f}", "⭐", trend_type="up")
    with col4:
        active = len(prod_df['Intern_ID'].unique())
        total = len(summary_df)
        kpi_card("Active Interns", f"{active}/{total}", "🟢", "30d Window", "neutral")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        # bar chart productivity score by intern
        fig_bar = plot_bar_chart(summary_df.sort_values(by='Productivity_Score'), 'Productivity_Score', 'Intern_ID', "Productivity Score by Intern", orientation='h')
        if fig_bar: st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_chart2:
         # Leaderboard of top interns
         st.subheader("Top Performers")
         top = summary_df.sort_values(by='Productivity_Score', ascending=False).head(10)[['Intern_ID', 'Productivity_Score', 'Tasks_Completed']]
         st.dataframe(top, use_container_width=True, hide_index=True)

    st.markdown("---")

    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        # Productivity trend line (using tasks completed per day)
        trend = prod_df.groupby('Date')['Tasks_Completed'].sum().reset_index()
        fig_line = plot_line_chart(trend, 'Date', 'Tasks_Completed', "Team Daily Task Completion Trend")
        if fig_line: st.plotly_chart(fig_line, use_container_width=True)
        
    with col_chart4:
        # Cluster visualization
        if not clusters_df.empty:
            merged = pd.merge(summary_df, clusters_df, on='Intern_ID')
            fig_cluster = plot_scatter_clusters(merged, 'Total_Hours', 'Productivity_Score', 'Cluster', "Intern Performance Clusters")
            if fig_cluster: st.plotly_chart(fig_cluster, use_container_width=True)
        else:
             st.info("Cluster data unavailable.")
