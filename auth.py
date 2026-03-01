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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif !important; }

        .stApp {
            background-color: #f9f9f9 !important;
        }

        #MainMenu, footer, header { visibility: hidden; }

        .auth-container {
            max-width: 400px;
            margin: 4rem auto 0 auto;
            padding: 2.5rem;
            background: #ffffff;
            border-radius: 16px;
            border: 1px solid #e8e8e8;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        }

        .auth-logo {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 0.25rem;
        }

        .auth-tagline {
            text-align: center;
            font-size: 0.875rem;
            color: #6b6b6b;
            margin-bottom: 2rem;
        }

        .auth-divider {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 1.25rem 0;
            color: #aaaaaa;
            font-size: 0.8rem;
        }

        .auth-divider::before, .auth-divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #e8e8e8;
        }

        /* Input fields */
        .stTextInput input {
            background: #f5f5f5 !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 10px !important;
            padding: 12px 14px !important;
            font-size: 0.9rem !important;
            color: #1a1a1a !important;
        }

        .stTextInput input:focus {
            border-color: #10a37f !important;
            box-shadow: 0 0 0 2px rgba(16,163,127,0.15) !important;
            background: #ffffff !important;
        }

        /* Primary button */
        .stButton button {
            background-color: #10a37f !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.65rem 1.5rem !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            width: 100%;
            transition: background 0.2s;
        }

        .stButton button:hover {
            background-color: #0d8c6d !important;
        }

        /* Google button override */
        .google-btn button {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
        }

        .google-btn button:hover {
            background-color: #f5f5f5 !important;
            border-color: #c0c0c0 !important;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: #f0f0f0 !important;
            border-radius: 10px !important;
            padding: 4px !important;
            gap: 4px !important;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            color: #6b6b6b !important;
        }

        .stTabs [aria-selected="true"] {
            background: #ffffff !important;
            color: #1a1a1a !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
        }

        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 1.25rem !important;
        }

        /* Alert messages */
        .stAlert {
            border-radius: 10px !important;
            font-size: 0.875rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Logo
    st.markdown('<div class="auth-logo">✨ AYRA</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-tagline">Your soulful Malaysian AI companion</div>', unsafe_allow_html=True)

    # Google OAuth button
    supabase = get_supabase()

    st.markdown('<div class="google-btn">', unsafe_allow_html=True)
    if st.button("🔵  Continue with Google", key="google_login", use_container_width=True):
        try:
            data = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": os.environ.get("SUPABASE_REDIRECT_URL", "http://localhost:8501")
                }
            })
            # Redirect user to Google OAuth URL
            st.markdown(f'<meta http-equiv="refresh" content="0; url={data.url}">', unsafe_allow_html=True)
            st.stop()
        except Exception as e:
            st.error(f"Google login failed: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Divider
    st.markdown('<div class="auth-divider">or continue with email</div>', unsafe_allow_html=True)

    # Email / Password tabs
    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        email = st.text_input("Email", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", placeholder="Your password", type="password", key="login_pass")

        if st.button("Sign In", key="btn_login", use_container_width=True):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
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
            <span style="font-size: 0.8rem; color: #6b6b6b;">Forgot your password? </span>
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

    # Footer
    st.markdown("""
    <div style="text-align:center; margin-top: 2rem; font-size: 0.75rem; color: #aaaaaa;">
        ATMA AI · AYRA v3.1 · Your data is private & secure 🔒
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------------
# OAuth callback handler — call this at TOP of app.py
# -------------------------------------------------------------------
def handle_oauth_callback():
    """
    Handles Google OAuth redirect. Streamlit gets the token
    via URL query params after Google redirects back.
    """
    params = st.query_params
    
    if "code" in params:
        supabase = get_supabase()
        try:
            # Exchange code for session
            response = supabase.auth.exchange_code_for_session({
                "auth_code": params["code"]
            })
            st.session_state.user = response.user
            st.session_state.access_token = response.session.access_token
            # Clean URL
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"OAuth error: {str(e)}")
            st.query_params.clear()


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