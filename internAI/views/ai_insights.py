# pyre-ignore-all-errors
import streamlit as st
import pandas as pd
from utils.data_loader import get_all_data
from components.charts import plot_pie_chart, plot_bar_chart

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    HAS_WORDCLOUD = True
except ImportError:
    HAS_WORDCLOUD = False

def render():
    st.markdown("<div class='main-header'>AI &amp; NLP Insights</div>", unsafe_allow_html=True)
    st.write("Extracted insights from activity and technology usage data.")

    data = get_all_data()
    prod_df = data.get("productivity", pd.DataFrame())
    tech_df = data.get("tech", pd.DataFrame())
    summary_df = data.get("summary", pd.DataFrame())

    if prod_df.empty and tech_df.empty:
        st.warning("No data available for insights.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Activity Categories")
        if not prod_df.empty:
            activity_counts = prod_df.groupby("Activity")["Hours_Spent"].sum().reset_index()
            activity_counts.columns = ["Category", "Frequency"]
            fig_pie = plot_pie_chart(activity_counts, "Category", "Frequency", "Time by Activity", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No activity data available.")

    with col2:
        st.subheader("Technology Usage")
        if not tech_df.empty:
            tech_mentions = tech_df.groupby("Technology")["Usage_Frequency"].sum().reset_index()
            tech_mentions.columns = ["Technology", "Mentions"]
            tech_mentions = tech_mentions.sort_values("Mentions", ascending=True)
            fig_bar = plot_bar_chart(tech_mentions, "Mentions", "Technology", "Tech Usage Frequency", orientation="h")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No technology data available.")

    st.markdown("---")

    if HAS_WORDCLOUD:
        st.subheader("Word Cloud: Technologies & Activities")

        corpus_parts = []
        if not tech_df.empty:
            tech_words = " ".join(tech_df["Technology"].astype(str).tolist() * 3)
            corpus_parts.append(tech_words)
        if not prod_df.empty:
            activity_words = " ".join(prod_df["Activity"].astype(str).tolist() * 2)
            corpus_parts.append(activity_words)
        corpus = " ".join(corpus_parts) if corpus_parts else "No data"

        fig, ax = plt.subplots(figsize=(10, 5))
        wordcloud = WordCloud(width=800, height=400, background_color="#F8FAFC", colormap="Blues", max_words=100).generate(corpus)
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("Install `wordcloud` package for the word cloud visualization: `pip install wordcloud`")

    st.markdown("---")
    st.subheader("Intern Performance Summaries")

    if not summary_df.empty:
        for _, row in summary_df.head(5).iterrows():
            intern_id = row["Intern_ID"]
            score = row["Productivity_Score"]
            tasks = row["Tasks_Completed"]
            with st.expander(f"{intern_id} - Performance Summary"):
                sentiment = "Positive" if score >= 85 else "Neutral" if score >= 70 else "Needs Support"
                st.markdown(f"""
                * **Productivity Score:** {score:.1f}/100
                * **Tasks Completed:** {tasks}
                * **Status:** {sentiment}
                """)
