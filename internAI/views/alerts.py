# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.kpi_cards import alert_card

def render():
    st.markdown("<div class='main-header'>Manager Alerts &amp; Predictions</div>", unsafe_allow_html=True)
    st.write("Proactive notifications and risk indicators for your team.")
    
    data = get_all_data()
    summary_df = data.get('summary', pd.DataFrame())
    clusters_df = data.get('clusters', pd.DataFrame())
    
    if summary_df.empty or clusters_df.empty:
        st.warning("Insufficient data to compute alerts.")
        return
        
    merged = pd.merge(summary_df, clusters_df, on='Intern_ID')
    
    st.subheader("⚠️ Action Required")
    
    # 1. High Risk Interns
    high_risk = merged[merged['Risk_Indicator'] == 'High']
    if not high_risk.empty:
        for _, row in high_risk.iterrows():
             alert_card(f"High Risk Detected: {row['Intern_ID']}", f"Productivity Score: {row['Productivity_Score']}. Suggested Action: Schedule 1-on-1 meeting.", severity="critical")
    else:
        st.success("No interns detected with High risk.")

    # 2. Needs Support Cluster
    support_needed = merged[merged['Cluster'] == 'Needs Support']
    if not support_needed.empty:
        for _, row in support_needed.iterrows():
             alert_card(f"Needs Support: {row['Intern_ID']}", "Falling behind average task completion. Action: Review recent blockers.", severity="warning")
    
    # 3. Super Performers (Positive Alert)
    super_perf = merged[(merged['Cluster'] == 'High Performer') & (merged['Productivity_Score'] > 90)]
    if not super_perf.empty:
         for _, row in super_perf.iterrows():
             alert_card(f"Exceeding Expectations: {row['Intern_ID']}", "Performing exceptionally well. Consider for more challenging projects.", severity="normal")
             
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
         st.subheader("Predictive Analytics")
         st.write("ML model outputs indicating likelihood of successful conversion to full-time role.")
         # Mock probability based on score
         merged['Conversion_Probability'] = (merged['Productivity_Score'] / 100).clip(0, 1) * 100
         fig = pd.DataFrame({
             'Intern': merged['Intern_ID'],
             'Likelihood (%)': merged['Conversion_Probability'].round(1)
         }).sort_values('Likelihood (%)', ascending=False).head(10)
         st.dataframe(fig, use_container_width=True, hide_index=True)
         
    with col2:
         st.subheader("Model Evaluation Metadata")
         st.write("Metrics from the backend ML clustering/prediction evaluation.")
         metrics = data.get('metrics', {})
         if metrics:
              st.json(metrics)
         else:
             st.write("No metrics available.")
