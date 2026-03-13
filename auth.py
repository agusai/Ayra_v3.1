"""
AYRA Auth Module — Supabase Authentication
Supports: Email/Password + Google OAuth
"""

import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime

# -------------------------------------------------------------------
# Supabase client init
# -------------------------------------------------------------------
def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        st.error("⚠️ Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env")
        st.stop()
    return create_client(url, key)


# -------------------------------------------------------------------
# Session helpers
# -------------------------------------------------------------------
def is_logged_in() -> bool:
    return st.session_state.get("user") is not None

def get_user():
    return st.session_state.get("user")

def get_user_id() -> str:
    user = get_user()
    return user.id if user else None

def get_user_email() -> str:
    user = get_user()
    return user.email if user else None

def logout():
    supabase = get_supabase()
    try:
        supabase.auth.sign_out()
    except:
        pass
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# -------------------------------------------------------------------
# Auth UI — renders full login/register page
# -------------------------------------------------------------------
def show_auth_page():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important; }

        .stApp {
            background-color: #faf9f7 !important;
        }

        #MainMenu, footer, header { visibility: hidden; }

        .auth-logo {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 700;
            color: #1c1c1c;
            margin-bottom: 0.25rem;
            letter-spacing: -0.8px;
        }

        .auth-tagline {
            text-align: center;
            font-size: 0.875rem;
            color: #888;
            margin-bottom: 2rem;
            font-weight: 400;
        }

        /* Input fields */
        .stTextInput input {
            background: #ffffff !important;
            border: 1px solid #e2dfd9 !important;
            border-radius: 10px !important;
            padding: 12px 14px !important;
            font-size: 0.9rem !important;
            color: #1c1c1c !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        }

        .stTextInput input:focus {
            border-color: #10a37f !important;
            box-shadow: 0 0 0 3px rgba(16,163,127,0.12) !important;
            background: #ffffff !important;
        }

        .stTextInput label {
            color: #555 !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
        }

        /* Primary button */
        .stButton button {
            background: linear-gradient(135deg, #10a37f, #0d8c6d) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.65rem 1.5rem !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            width: 100%;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(16,163,127,0.25) !important;
        }

        .stButton button:hover {
            background: linear-gradient(135deg, #0d8c6d, #0b7a5e) !important;
            box-shadow: 0 3px 12px rgba(16,163,127,0.35) !important;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: #ede9e3 !important;
            border-radius: 10px !important;
            padding: 4px !important;
            gap: 4px !important;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            color: #888 !important;
        }

        .stTabs [aria-selected="true"] {
            background: #ffffff !important;
            color: #1c1c1c !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
        }

        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1.25rem !important;
        }

        /* Alert messages */
        .stAlert {
            border-radius: 10px !important;
            font-size: 0.875rem !important;
            background-color: #f5f3ef !important;
            border: 1px solid #e8e5e0 !important;
        }

        /* Center the content */
        .block-container {
            max-width: 420px !important;
            margin: 0 auto !important;
            padding-top: 4rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-logo">✨ AYRA</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-tagline">Your soulful Malaysian AI companion</div>', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        email = st.text_input("Email", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", placeholder="Your password", type="password", key="login_pass")

        if st.button("Sign In", key="btn_login", use_container_width=True):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                supabase = get_supabase()
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.session_state.user = response.user
                    st.session_state.access_token = response.session.access_token
                    st.success("Welcome back! Loading AYRA...")
                    st.rerun()
                except Exception as e:
                    err = str(e).lower()
                    if "invalid" in err or "credentials" in err:
                        st.error("❌ Wrong email or password.")
                    elif "confirm" in err:
                        st.warning("📧 Please verify your email first.")
                    else:
                        st.error(f"Login failed: {str(e)}")

        st.markdown("""
        <div style="text-align:center; margin-top: 0.75rem;">
            <span style="font-size: 0.8rem; color: #888;">Forgot your password? </span>
            <span style="font-size: 0.8rem; color: #10a37f; cursor: pointer;">Reset it</span>
        </div>
        """, unsafe_allow_html=True)

    with tab_register:
        reg_name = st.text_input("Name", placeholder="What should AYRA call you?", key="reg_name")
        reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
        reg_pass = st.text_input("Password", placeholder="Min 8 characters", type="password", key="reg_pass")
        reg_pass2 = st.text_input("Confirm Password", placeholder="Repeat password", type="password", key="reg_pass2")

        if st.button("Create Account", key="btn_register", use_container_width=True):
            if not all([reg_name, reg_email, reg_pass, reg_pass2]):
                st.error("Please fill in all fields.")
            elif len(reg_pass) < 8:
                st.error("Password must be at least 8 characters.")
            elif reg_pass != reg_pass2:
                st.error("Passwords don't match.")
            else:
                supabase = get_supabase()
                try:
                    response = supabase.auth.sign_up({
                        "email": reg_email,
                        "password": reg_pass,
                        "options": {
                            "data": {"full_name": reg_name}
                        }
                    })
                    if response.user:
                        st.success("✅ Account created! Please check your email to verify, then sign in.")
                except Exception as e:
                    err = str(e).lower()
                    if "already" in err or "registered" in err:
                        st.error("This email is already registered. Try signing in.")
                    else:
                        st.error(f"Registration failed: {str(e)}")

    st.markdown("""
    <div style="text-align:center; margin-top: 2rem; font-size: 0.75rem; color: #bbb;">
        ATMA AI · AYRA v3.1 · Your data is private & secure 🔒
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------------
# OAuth callback handler — kept as stub (Google OAuth disabled)
# -------------------------------------------------------------------
def handle_oauth_callback():
    """Google OAuth disabled. Stub kept for compatibility."""
    pass


# -------------------------------------------------------------------
# Restore session from Supabase on page refresh
# -------------------------------------------------------------------
def restore_session():
    """
    Try to restore an existing Supabase session so users
    don't get logged out on every Streamlit rerun.
    """
    if is_logged_in():
        return  # Already have user in session

    supabase = get_supabase()
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
            st.session_state.access_token = session.access_token
    except:
        pass  # No active session, will show login page