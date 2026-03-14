# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.charts import plot_bar_chart, plot_pie_chart
from components.kpi_cards import kpi_card

def render():
    st.markdown("<div class='main-header'>Technology Insights</div>", unsafe_allow_html=True)
    st.write("Understand skill distribution, technology usage, and emerging trends among interns.")
    
    data = get_all_data()
    tech_df = data.get('tech', pd.DataFrame())
    
    if tech_df.empty:
        st.warning("Technology data is currently unavailable.")
        return
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        top_tech = tech_df.groupby('Technology')['Usage_Frequency'].sum().idxmax()
        kpi_card("Most Used Technology", top_tech, "💻", trend_type="neutral")
    with col2:
        top_prof = tech_df.groupby('Technology')['Proficiency_Score'].mean().idxmax()
        kpi_card("Highest Avg Proficiency", top_prof, "🎯", trend_type="up")
    with col3:
        unique_techs = tech_df['Technology'].nunique()
        kpi_card("Total Unique Tech", unique_techs, "🔧", trend_type="neutral")
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Bar chart: technology usage frequency
        usage = tech_df.groupby('Technology')['Usage_Frequency'].sum().reset_index().sort_values(by='Usage_Frequency', ascending=False)
        fig_bar = plot_bar_chart(usage, 'Technology', 'Usage_Frequency', "Technology Usage Frequency")
        if fig_bar: st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_chart2:
        # Pie chart: technology distribution (based on number of interns using it)
        users_count = tech_df.groupby('Technology')['Intern_ID'].nunique().reset_index()
        users_count.columns = ['Technology', 'Intern_Count']
        fig_pie = plot_pie_chart(users_count, 'Technology', 'Intern_Count', "Intern Distribution by Technology")
        if fig_pie: st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    
    # Skill Gaps (Simulated by lowest proficiency scores)
    st.subheader("Potential Skill Gaps")
    st.write("Technologies with lowest average proficiency score across the team.")
    gaps = tech_df.groupby('Technology')['Proficiency_Score'].mean().reset_index().sort_values(by='Proficiency_Score').head(5)
    st.dataframe(gaps.round(2), use_container_width=True, hide_index=True)
