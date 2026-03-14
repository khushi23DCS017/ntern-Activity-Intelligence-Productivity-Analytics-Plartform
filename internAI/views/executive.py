# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.charts import plot_line_chart, plot_bar_chart, plot_pie_chart
from components.kpi_cards import kpi_card

def render():
    st.markdown("<div class='main-header'>Executive Overview</div>", unsafe_allow_html=True)
    st.write("Global organizational view of the intern program.")
    
    data = get_all_data()
    summary_df = data.get('summary', pd.DataFrame())
    prod_df = data.get('productivity', pd.DataFrame())
    
    if summary_df.empty or prod_df.empty:
        st.warning("Insufficient data to render executive dashboard.")
        return
        
    # KPI Cards using custom HTML Component
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Interns", len(summary_df), "👥", "+2 this month", "up")
    with col2:
        kpi_card("Total Tasks", summary_df['Tasks_Completed'].sum(), "✅", "On track", "neutral")
    with col3:
        kpi_card("Hours Logged", summary_df['Total_Hours'].sum(), "⏱️", "High activity", "up")
    with col4:
        avg_score = summary_df['Productivity_Score'].mean()
        kpi_card("Avg Productivity", f"{avg_score:.1f}", "📈", "+1.2% vs last week", "up")
        
    st.markdown("---")
    
    # Row 1 Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Line chart: daily activity trend
        daily_prod = prod_df.groupby('Date')['Hours_Spent'].sum().reset_index()
        fig_line = plot_line_chart(daily_prod, 'Date', 'Hours_Spent', "Daily Activity Trend (Total Hours)")
        if fig_line: st.plotly_chart(fig_line, use_container_width=True)
        
    with col_chart2:
        # Bar chart: tasks completed per intern (Top 10)
        top_tasks = summary_df.nlargest(10, 'Tasks_Completed')
        fig_bar = plot_bar_chart(top_tasks, 'Intern_ID', 'Tasks_Completed', "Tasks Completed per Intern (Top 10)")
        if fig_bar: st.plotly_chart(fig_bar, use_container_width=True)
        
    # Row 2 Charts
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        # Pie chart: task category distribution (Activity from prod_df)
        activity_dist = prod_df['Activity'].value_counts().reset_index()
        activity_dist.columns = ['Activity', 'Count']
        fig_pie = plot_pie_chart(activity_dist, 'Activity', 'Count', "Activity Category Distribution")
        if fig_pie: st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart4:
        # Top interns leaderboard
        st.subheader("🏆 Top Performing Interns")
        top_interns = summary_df[['Intern_ID', 'Role', 'Productivity_Score']].sort_values(by='Productivity_Score', ascending=False).head(5)
        st.dataframe(top_interns, use_container_width=True, hide_index=True)
        
    st.markdown("---")
    st.subheader("Organizational Structure")
    roles_dist = summary_df['Role'].value_counts().reset_index()
    roles_dist.columns = ['Role', 'Count']
    fig_roles = plot_pie_chart(roles_dist, 'Role', 'Count', "Intern Roles Distribution", hole=0.4)
    if fig_roles: st.plotly_chart(fig_roles, use_container_width=True)
