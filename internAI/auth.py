# pyre-ignore-all-errors
import bcrypt
import base64
import os
import pandas as pd
import streamlit as st
from database import run_query

# ================================================================
# HELPERS
# ================================================================
def safe_int(val):
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return int(val)

def parse_roles(roles_val):
    """
    array_agg may return list or string like '{intern,employee}'.
    Handle both safely.
    """
    if isinstance(roles_val, list):
        return [str(r).strip() for r in roles_val]
    if isinstance(roles_val, str):
        cleaned = roles_val.strip('{}').strip()
        return [r.strip() for r in cleaned.split(',') if r.strip()]
    return []

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ================================================================
# LOGIN
# ================================================================
def verify_login(username, password):
    """Returns user dict or None."""
    try:
        df = run_query("""
            SELECT u.user_id, u.full_name, u.password_hash,
                   u.intern_id, u.mentor_id,
                   array_agg(ur.role::text) AS roles
            FROM users u
            JOIN user_roles ur ON u.user_id = ur.user_id
            WHERE u.username = %s AND u.is_active = TRUE
            GROUP BY u.user_id, u.full_name, u.password_hash,
                     u.intern_id, u.mentor_id
        """, params=(username,))

        if df.empty:
            return None

        row   = df.iloc[0]
        roles = parse_roles(row['roles'])

        if not bcrypt.checkpw(password.encode(), row['password_hash'].encode()):
            return None

        # Priority: manager > employee > intern
        if 'manager'   in roles: role = 'manager'
        elif 'employee' in roles: role = 'employee'
        else:                     role = 'intern'

        return {
            'user_id'  : safe_int(row['user_id']),
            'full_name': str(row['full_name']),
            'role'     : role,
            'intern_id': safe_int(row['intern_id']),
            'mentor_id': safe_int(row['mentor_id'])
        }

    except Exception as e:
        st.error(f"Login error: {e}")
        return None

# ================================================================
# LOGIN PAGE UI (Premium Split-Screen)
# ================================================================
def login_page():
    # Load background image
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, 'assets', 'login_bg.png')
        img_base64 = get_base64_of_bin_file(img_path)
        bg_image_css = f"background-image: url('data:image/png;base64,{img_base64}');"
    except Exception:
        # Fallback gradient if image is missing
        bg_image_css = "background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);"

    st.markdown(f"""
        <style>
        /* Hide navbar during login */
        .top-navbar {{ display: none; }}

        /* Typography */
        .brand-logo {{
            font-size: 1.5rem;
            font-weight: 800;
            color: #2563EB;
            margin-bottom: 60px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .welcome-text {{
            font-size: 1.8rem;
            color: #1E293B;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .subtitle-text {{
            font-size: 1.2rem;
            color: #64748B;
            font-weight: 600;
            margin-bottom: 40px;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Hide standard streamlit blocks */
        .stApp [data-testid="stHeader"] {{ display: none; }}
        .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        container = st.container()
        with container:
            scol_form, scol_image = st.columns([1, 1.2], gap="large")

            with scol_form:
                st.markdown("""
                <div class='brand-logo'>
                    <div style='background: #2563EB; color: white; border-radius: 4px; padding: 2px 6px; font-size: 1.2rem;'>⚡</div>
                    Intern Analytics
                </div>
                <div class='welcome-text'>Welcome Back</div>
                <div class='subtitle-text'>Sign into your account</div>
                """, unsafe_allow_html=True)

                with st.form("login_form", border=False):
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")

                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    submit = st.form_submit_button("Sign In", use_container_width=True)

                    if submit:
                        if not username or not password:
                            st.error("Please enter both username and password.")
                        else:
                            user = verify_login(username, password)
                            if user:
                                st.session_state['user'] = user
                                st.session_state['page'] = 'dashboard'
                                st.rerun()
                            else:
                                st.error("Invalid username or password.")

            with scol_image:
                st.markdown(f"""
                <div style="height: 100%; min-height: 500px; width: 100%; border-radius: 0 12px 12px 0; {bg_image_css} background-size: cover; background-position: center; margin-left: -2rem; padding: 0;">
                </div>
                """, unsafe_allow_html=True)

    # Style the login card
    st.markdown("""
        <style>
            /* Make the form button blue and rounded */
            div[data-testid="stForm"] button[kind="primary"] {
                background-color: #0EA5E9 !important;
                border-color: #0EA5E9 !important;
                border-radius: 8px !important;
                color: white !important;
                padding: 0.5rem 2rem !important;
                width: auto !important;
                min-width: 120px;
                display: block;
            }
            .stTextInput>div>div>input {
                border-radius: 8px;
                border: 1px solid #E2E8F0;
                background-color: #F8FAFC;
                padding: 10px 15px;
            }
        </style>
    """, unsafe_allow_html=True)
