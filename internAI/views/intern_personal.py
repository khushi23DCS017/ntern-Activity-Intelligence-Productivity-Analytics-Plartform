# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.charts import plot_bar_chart
from components.kpi_cards import kpi_card

def render():
    st.markdown("<div class='main-header'>My Dashboard (Intern View)</div>", unsafe_allow_html=True)
    st.write("Track your personal performance, skills, and progress.")
    
    # Get current user's name from session state
    user = st.session_state.get('user', {})
    username = user.get('full_name', 'Unknown')
    
    data = get_all_data()
    summary_df = data.get('summary', pd.DataFrame())
    prod_df = data.get('productivity', pd.DataFrame())
    tech_df = data.get('tech', pd.DataFrame())
    
    if summary_df.empty:
        st.warning("Data unavailable.")
        return
        
    my_summary = summary_df[summary_df['Intern_ID'] == username]
    if my_summary.empty:
        st.error(f"Could not find data for {username}. Ensure your login display name matches an intern name in the database.")
        st.write("Showing fallback data for first available intern instead.")
        if not summary_df.empty:
            username = summary_df.iloc[0]['Intern_ID']
            my_summary = summary_df[summary_df['Intern_ID'] == username]
        else:
            return
        
    row = my_summary.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
       kpi_card("My Prod Score", f"{row['Productivity_Score']:.1f}/100", "⭐")
    with col2:
       kpi_card("Tasks Completed", row['Tasks_Completed'], "✅")
    with col3:
       kpi_card("Hours Logged", row['Total_Hours'], "⏱️")
       
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
         st.subheader("My Recent Activity")
         my_prod = prod_df[prod_df['Intern_ID'] == username]
         if not my_prod.empty:
             grouped = my_prod.groupby('Date')['Tasks_Completed'].sum().reset_index()
             st.line_chart(grouped.set_index('Date'))
         else:
             st.write("No recent activity logged.")
             
    with col_chart2:
         st.subheader("My Top Technologies")
         my_tech = tech_df[tech_df['Intern_ID'] == username]
         if not my_tech.empty:
              fig = plot_bar_chart(my_tech, 'Technology', 'Usage_Frequency', f"{username} Tech Stack", orientation='h')
              st.plotly_chart(fig, use_container_width=True)
         else:
             st.write("No technology logs found.")
             
    st.markdown("---")
    st.subheader("Feedback & Recommendations")
    # Mock generalized feedback based on score
    if row['Productivity_Score'] > 85:
         st.success("Great job! You are performing above average. Look into challenging yourself with the Advanced SQL course.")
    elif row['Productivity_Score'] > 70:
         st.info("You're doing well. Try tracking your time more carefully to boost efficiency.")
    else:
         st.warning("Focus on completing your daily assignments and reach out to your mentor if you need help debugging.")
