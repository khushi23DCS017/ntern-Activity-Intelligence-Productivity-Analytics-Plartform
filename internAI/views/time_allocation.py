# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import get_all_data
from components.charts import plot_pie_chart
from components.kpi_cards import kpi_card

def render():
    st.markdown("<div class='main-header'>Time Allocation Dashboard</div>", unsafe_allow_html=True)
    st.write("Analyze intern work patterns and time distribution.")
    
    data = get_all_data()
    prod_df = data.get('productivity', pd.DataFrame())
    
    if prod_df.empty:
        st.warning("Productivity log data is unavailable.")
        return
        
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        total_log = prod_df['Hours_Spent'].sum()
        kpi_card("Total Hours Tracked", f"{total_log:.0f}h", "⏱️", trend_type="neutral")
    with col_kpi2:
        top_act = prod_df.groupby('Activity')['Hours_Spent'].sum().idxmax()
        kpi_card("Primary Activity", top_act, "🔥", trend_type="neutral")
    with col_kpi3:
        avg_act = prod_df.groupby('Intern_ID')["Hours_Spent"].sum().mean()
        kpi_card("Avg Hours / Intern", f"{avg_act:.1f}h", "👥", trend_type="neutral")
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Stacked bar chart: time spent per activity by intern (Top 10 most active)
        top_interns_hours = prod_df.groupby('Intern_ID')['Hours_Spent'].sum().nlargest(10).index
        filtered_prod = prod_df[prod_df['Intern_ID'].isin(top_interns_hours)]
        
        grouped = filtered_prod.groupby(['Intern_ID', 'Activity'])['Hours_Spent'].sum().reset_index()
        fig_bar = px.bar(grouped, x='Intern_ID', y='Hours_Spent', color='Activity', title="Time Spent per Activity (Top 10 Active Interns)", barmode='stack')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_chart2:
        # Pie chart: global daily time allocation
        global_alloc = prod_df.groupby('Activity')['Hours_Spent'].sum().reset_index()
        fig_pie = plot_pie_chart(global_alloc, 'Activity', 'Hours_Spent', "Overall Time Allocation", hole=0.3)
        if fig_pie: st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("Work Intensity Heatmap (Daily Hours Logged)")
    
    # Heatmap: work intensity by day
    intensity = prod_df.groupby(['Intern_ID', 'Date'])['Hours_Spent'].sum().reset_index()
    pivot_df = intensity.pivot(index='Intern_ID', columns='Date', values='Hours_Spent').fillna(0)
    
    fig_heat = px.imshow(pivot_df, 
                         labels=dict(x="Date", y="Intern", color="Hours Spent"),
                         x=pivot_df.columns,
                         y=pivot_df.index,
                         aspect="auto",
                         color_continuous_scale="Blues",
                         title="Work Intensity by Day")
    st.plotly_chart(fig_heat, use_container_width=True)
