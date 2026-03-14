# pyre-ignore-all-errors
import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* === Global Variables & Reset === */
        :root {
            --primary-blue: #2563EB;
            --accent-teal: #14B8A6;
            --highlight-orange: #F59E0B;
            --danger-red: #EF4444;
            --bg-light: #F8FAFC;
            --text-dark: #1E293B;
            --text-muted: #64748B;
            --border-color: #E2E8F0;
            --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --border-radius: 12px;
        }
        
        /* === Main App Background === */
        .stApp {
            background-color: var(--bg-light);
            color: var(--text-dark);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        /* === Top Navbar Area === */
        .top-navbar {
            background-color: white;
            padding: 1rem 2rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: -3rem; /* Offset Streamlit default padding */
            margin-bottom: 2rem;
            margin-left: -3rem;
            margin-right: -3rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        .navbar-brand {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-blue);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .navbar-user {
            font-size: 0.95rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        /* === Typography === */
        h1, h2, h3, .main-header {
            color: var(--text-dark) !important;
            font-weight: 700 !important;
        }
        .main-header {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1rem;
            color: var(--text-muted);
            margin-bottom: 2rem;
        }

        /* === KPI Cards === */
        .kpi-wrapper {
            background: white;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            gap: 10px;
            transition: transform 0.2s ease;
        }
        .kpi-wrapper:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 0.9rem;
            font-weight: 600;
        }
        .kpi-icon {
            font-size: 1.5rem;
            color: var(--primary-blue);
            background: #EFF6FF;
            padding: 8px;
            border-radius: 8px;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-dark);
        }
        .kpi-trend {
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .trend-up { color: var(--accent-teal); }
        .trend-down { color: var(--danger-red); }
        .trend-neutral { color: var(--highlight-orange); }

        /* === Standard Chart Cards === */
        .stPlotlyChart {
            background: white;
            border-radius: var(--border-radius);
            padding: 1rem;
            box-shadow: var(--card-shadow);
            border: 1px solid var(--border-color);
        }
        
        /* === Alert Cards === */
        .alert-card {
            border-radius: var(--border-radius);
            padding: 1.25rem;
            border-left: 5px solid;
            margin-bottom: 1rem;
            background: white;
            box-shadow: var(--card-shadow);
        }
        .alert-critical { border-left-color: var(--danger-red); }
        .alert-warning { border-left-color: var(--highlight-orange); }
        .alert-normal { border-left-color: var(--accent-teal); }

        /* === Legacy metric-card support === */
        .metric-card {
            background: white;
            border-radius: var(--border-radius);
            padding: 20px;
            text-align: center;
            border: 1px solid var(--border-color);
            box-shadow: var(--card-shadow);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-blue);
        }
        .metric-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 4px;
        }
        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary-blue);
            border-bottom: 2px solid rgba(37, 99, 235, 0.2);
            padding-bottom: 6px;
            margin-bottom: 16px;
        }
        .ml-badge-high {
            background: #21c35422;
            border: 1px solid #21c354;
            border-radius: 20px;
            padding: 4px 14px;
            color: #21c354;
            font-weight: 600;
            font-size: 0.85rem;
        }
        .ml-badge-mid {
            background: #f0a50022;
            border: 1px solid #f0a500;
            border-radius: 20px;
            padding: 4px 14px;
            color: #f0a500;
            font-weight: 600;
            font-size: 0.85rem;
        }
        .ml-badge-low {
            background: #ff4b4b22;
            border: 1px solid #ff4b4b;
            border-radius: 20px;
            padding: 4px 14px;
            color: #ff4b4b;
            font-weight: 600;
            font-size: 0.85rem;
        }

        /* === Streamlit Overrides === */
        button[kind="primary"] {
            background-color: var(--primary-blue) !important;
            border-color: var(--primary-blue) !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }
        button[kind="primary"]:hover {
            background-color: #1D4ED8 !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.4);
        }
        .stTextInput>div>div>input {
            border-radius: 6px;
            border: 1px solid var(--border-color);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput>div>div>input:focus {
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
        }
        .stSelectbox>div>div {
            border-radius: 6px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_navbar(username, role):
    st.markdown(f"""
        <div class="top-navbar">
            <div class="navbar-brand">
                <span>⚡</span> Intern Analytics Platform
            </div>
            <div class="navbar-user">
                <span>{username} ({role})</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
