# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data

def render():
    st.markdown("<div class='main-header'>Mentorship Overview</div>", unsafe_allow_html=True)
    st.write("Track the progress and well-being of your assigned interns.")
    
    data = get_all_data()
    summary_df = data.get('summary', pd.DataFrame())
    
    # Filter by logged-in mentor
    user = st.session_state.get('user', {})
    mentor_name = user.get('full_name', '')
    st.write(f"Showing assigned cohort for **{mentor_name}**")

    cohort = summary_df[summary_df["Mentor_ID"] == mentor_name]
    
    if cohort.empty:
         st.warning("No interns assigned currently.")
         return
         
    st.subheader("Cohort Snapshot")
    st.dataframe(cohort[['Intern_ID', 'Role', 'Tasks_Completed', 'Productivity_Score']], use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
         st.subheader("1-on-1 Meeting Schedule Focus")
         st.write("Suggested topics based on intern performance metrics.")
         
         for _, row in cohort.iterrows():
             score = row['Productivity_Score']
             if score < 75:
                  st.error(f"**{row['Intern_ID']}**: Needs support. Discuss blockers and time management.")
             elif score > 90:
                  st.success(f"**{row['Intern_ID']}**: High performer. Discuss stretch goals and career path.")
             else:
                  st.info(f"**{row['Intern_ID']}**: Performing well. Routine check-in on current projects.")
                  
    with col2:
         st.subheader("Recent Messages/Feedback Log")
         st.chat_message("user").write("Hey mentor, I am stuck on the PySpark aggregation task.")
         st.chat_message("user").write("I finally fixed that Docker networking issue from yesterday!")
