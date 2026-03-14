# pyre-ignore-all-errors
import streamlit as st
from auth import login_page
from components import inject_css
from components.chatbot import ai_chatbot_sidebar
from utils.style import render_navbar

# New views from Frontend_&_AI
import views.executive as executive
import views.productivity as productivity
import views.tech_insights as tech_insights
import views.time_allocation as time_allocation
import views.projects as projects
import views.ai_insights as ai_insights
import views.learning as learning
import views.alerts as alerts
import views.intern_personal as intern_personal
import views.mentor as mentor

# Existing ML insights page (preserved)
from pages.ml_insights import ml_insights_page

from streamlit_option_menu import option_menu

# ================================================================
# PAGE CONFIG
# ================================================================
st.set_page_config(
    page_title="Intern Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# MAIN ROUTER
# ================================================================
def main():
    inject_css()

    # Not logged in → show login page
    if 'user' not in st.session_state:
        login_page()
        return

    user = st.session_state['user']
    role = user['role']
    name = user['full_name']

    # Top Navbar Injection
    render_navbar(name, role.capitalize())

    # Role-based pages mapping
    pages = {}
    options = []
    icons = []

    if role == 'manager':
        options = ["Executive Overview", "Intern Productivity", "Technology Insights",
                   "AI Insights", "Manager Alerts", "🤖 ML Insights"]
        icons = ["house", "people", "laptop", "robot", "exclamation-triangle", "gear"]
        pages = {
            "Executive Overview": executive.render,
            "Intern Productivity": productivity.render,
            "Technology Insights": tech_insights.render,
            "AI Insights": ai_insights.render,
            "Manager Alerts": alerts.render,
            "🤖 ML Insights": lambda: ml_insights_page(user),
        }
    elif role == 'employee':
        options = ["Mentorship Overview", "Team Productivity", "Time Allocation", "Project Contributions",
                   "Learning Progress", "Manager Alerts", "🤖 ML Insights"]
        icons = ["person-heart", "people", "clock", "folder", "book", "exclamation-triangle", "gear"]
        pages = {
            "Mentorship Overview": mentor.render,
            "Team Productivity": productivity.render,
            "Time Allocation": time_allocation.render,
            "Project Contributions": projects.render,
            "Learning Progress": learning.render,
            "Manager Alerts": alerts.render,
            "🤖 ML Insights": lambda: ml_insights_page(user),
        }
    elif role == 'intern':
        options = ["My Dashboard", "My Learning"]
        icons = ["person-badge", "book"]
        pages = {
            "My Dashboard": intern_personal.render,
            "My Learning": learning.render,
        }

    with st.sidebar:
        st.markdown("<div style='padding-top: 1rem; padding-bottom: 1rem; font-weight: 700; color: #64748B;'>PLATFORM MENU</div>", unsafe_allow_html=True)
        selection = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#64748B", "font-size": "1.1rem"},
                "nav-link": {"font-size": "0.95rem", "text-align": "left", "margin": "0px", "--hover-color": "#F1F5F9", "color": "#1E293B"},
                "nav-link-selected": {"background-color": "#EFF6FF", "color": "#2563EB", "font-weight": "600", "border-left": "4px solid #2563EB"},
            }
        )
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            del st.session_state['user']
            st.rerun()

    # Add chatbot to sidebar for all users
    ai_chatbot_sidebar()

    # Render selected page
    pages[selection]()


if __name__ == "__main__":
    main()
