import streamlit as st
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import threading
from zoneinfo import ZoneInfo

MYT = ZoneInfo("Asia/Kuala_Lumpur")

def now_myt():
    return datetime.now(MYT)

from utils.memory_manager import MemoryManager
from utils.mood_detector import MoodDetector
from utils.model_router import ModelRouter
from utils.helpers import get_greeting, get_ui_theme, handle_easter_egg, get_level_from_messages
from utils.prompts import AYRA_SYSTEM_PROMPT
from utils.crisis_detector import detect_crisis, format_crisis_response
from utils.proactive_engine import ProactiveEngine
from utils.audit_logger import AuditLogger
from utils.consistency_layer import ayra_voice_filter
from utils.tips_jiji import get_tips_jiji
from auth import handle_oauth_callback, restore_session, is_logged_in, show_auth_page, logout, get_user_id, get_user_email

load_dotenv()

# -------------------------------------------------------------------
# Page config — must be first
# -------------------------------------------------------------------
st.set_page_config(page_title="AYRA – The Soulful Malaysian AI", page_icon="✨")

# -------------------------------------------------------------------
# Auth gate — handle OAuth callback, restore session, guard all pages
# -------------------------------------------------------------------
handle_oauth_callback()   # catches Google redirect
restore_session()          # restores session on page refresh

if not is_logged_in():
    show_auth_page()
    st.stop()              # nothing below renders until logged in

# -------------------------------------------------------------------
# Helper function untuk time period
# -------------------------------------------------------------------
def get_time_period():
    hour = now_myt().hour
    if 5 <= hour < 12: return "pagi"
    elif 12 <= hour < 15: return "tengah hari"
    elif 15 <= hour < 19: return "petang"
    elif 19 <= hour < 22: return "malam"
    else: return "lewat malam"

# -------------------------------------------------------------------
# Initialise components (per user)
# -------------------------------------------------------------------
user_id = get_user_id()
user_email = get_user_email()

if "memory" not in st.session_state:
    st.session_state.memory = MemoryManager()
if "mood" not in st.session_state:
    st.session_state.mood = MoodDetector()
if "router" not in st.session_state:
    st.session_state.router = ModelRouter()
if "proactive" not in st.session_state:
    st.session_state.proactive = ProactiveEngine()
if "audit" not in st.session_state:
    st.session_state.audit = AuditLogger()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_score" not in st.session_state:
    st.session_state.mood_score = 0.0
if "comfort_mode" not in st.session_state:
    st.session_state.comfort_mode = False
if "current_story_id" not in st.session_state:
    st.session_state.current_story_id = None
if "last_user_time" not in st.session_state:
    st.session_state.last_user_time = time.time()
if "proactive_sent" not in st.session_state:
    st.session_state.proactive_sent = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "ayra"
if "jiji_turns" not in st.session_state:
    st.session_state.jiji_turns = 0
# FIX: Initialize daisy_state properly
if "daisy_state" not in st.session_state:
    st.session_state.daisy_state = None
if "active_world" not in st.session_state:
    st.session_state.active_world = None
if "novel_chapter" not in st.session_state:
    st.session_state.novel_chapter = 0

st.markdown("""
<style>
    /* ===== AYRA 3.2 — CHATGPT STYLE LIGHT UI ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    /* ===== GLOBAL LIGHT BG ===== */
    .stApp {
        background-color: #f9f9f9 !important;
        color: #1a1a1a !important;
    }


    /* Hide streamlit default chrome */
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden !important; }

    /* Hide Streamlit top-right toolbar only */
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    .stDeployButton { display: none !important; }

    /* Tighten sidebar button spacing */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.1rem !important;
    }
    [data-testid="stSidebar"] .stButton button {
        padding: 0.4rem 0.75rem !important;
        margin-bottom: 0 !important;
    }


    /* ===== MAIN CONTENT AREA ===== */
    .main .block-container {
        max-width: 780px !important;
        padding: 2rem 1.5rem 6rem 1.5rem !important;
        margin: 0 auto !important;
    }

    /* ===== HEADER ===== */
    .ayra-banner {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-top: 2rem;
        margin-bottom: 0.4rem;
        letter-spacing: -0.5px;
    }

    .proactive-greeting {
        text-align: center;
        font-size: 0.875rem;
        color: #6b6b6b;
        margin-bottom: 2.5rem;
        display: block;
    }

    .greeting-container {
        text-align: center;
    }

    /* ===== CHAT MESSAGES ===== */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin: 0.75rem 0;
    }

    .user-message-bubble {
        background-color: #efefef;
        color: #1a1a1a;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        max-width: 72%;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #e0e0e0;
    }

    .ayra-message {
        display: flex;
        justify-content: flex-start;
        align-items: flex-start;
        margin: 0.75rem 0;
        gap: 10px;
    }

    .ayra-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #10a37f;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
        margin-top: 2px;
    }

    .ayra-message-bubble {
        background-color: transparent;
        color: #1a1a1a;
        padding: 8px 4px;
        max-width: 80%;
        font-size: 0.95rem;
        line-height: 1.7;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background-color: #f0f0f0 !important;
        border-right: 1px solid #e0e0e0 !important;
    }

    [data-testid="stSidebar"] > div {
        padding: 0.75rem 0.75rem !important;
    }

    /* Sidebar brand */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.5rem;
    }

    .sidebar-brand-icon {
        font-size: 1.3rem;
    }

    .sidebar-brand-name {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a1a;
    }

    /* Sidebar section label */
    .sidebar-section-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #6b6b6b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.4rem 0.75rem;
        margin-top: 0.5rem;
        margin-bottom: 0.25rem;
    }

    /* All sidebar stButton */
    [data-testid="stSidebar"] .stButton button {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d8d8d8 !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
        font-weight: 400 !important;
        width: 100%;
        text-align: left !important;
        transition: background 0.15s ease;
        margin-bottom: 0.2rem;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #e8e8e8 !important;
        border-color: #c0c0c0 !important;
    }

    /* New Chat button */
    .btn-new-chat button {
        background-color: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }

    .btn-new-chat button:hover {
        background-color: #0d8c6d !important;
    }

    /* Search button */
    .btn-search button {
        background-color: #ffffff !important;
        color: #6b6b6b !important;
        border: 1px solid #d8d8d8 !important;
        border-radius: 8px !important;
    }

    .btn-search button:hover {
        background-color: #e8e8e8 !important;
        color: #1a1a1a !important;
    }

    /* Quick mode buttons */
    .quick-mode-btn button {
        background-color: #ffffff !important;
        border: 1px solid #d8d8d8 !important;
        border-radius: 8px !important;
        color: #1a1a1a !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 0.5rem !important;
        text-align: center !important;
        transition: all 0.15s ease;
    }

    .quick-mode-btn button:hover {
        background-color: #e8f5f0 !important;
        border-color: #10a37f !important;
        color: #10a37f !important;
    }

    /* ===== CHAT INPUT AREA ===== */
    .stChatInputContainer {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #d8d8d8 !important;
        border-radius: 14px !important;
        color: #1a1a1a !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #aaaaaa !important;
    }

    /* ===== FILE UPLOADER compact ===== */
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border: 1px dashed #d8d8d8 !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploader"] label {
        color: #6b6b6b !important;
        font-size: 0.8rem !important;
    }

    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        color: #1a1a1a !important;
        border-radius: 8px !important;
    }

    .streamlit-expanderContent {
        background-color: #fafafa !important;
        border: 1px solid #e0e0e0 !important;
        color: #1a1a1a !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #f0f0f0; }
    ::-webkit-scrollbar-thumb { background: #cccccc; border-radius: 4px; }

    /* ===== MISC ===== */
    hr {
        border: none !important;
        border-top: 1px solid #e0e0e0 !important;
        margin: 0.75rem 0 !important;
    }

    .stRadio label, .stSelectbox label { color: #1a1a1a !important; }
    .stRadio [data-testid="stWidgetLabel"] { color: #6b6b6b !important; font-size: 0.8rem !important; }

    .stAlert {
        background-color: #f5f5f5 !important;
        border: 1px solid #e0e0e0 !important;
        color: #1a1a1a !important;
    }

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    [data-testid="stMetric"] label { color: #6b6b6b !important; font-size: 0.72rem !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #1a1a1a !important; font-size: 0.9rem !important; }

    .stApp h1, .stApp h2, .stApp h3 { color: #1a1a1a !important; }
    .stMarkdown { color: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# FIX: Check if in Daisy mode FIRST, before displaying normal UI
# -------------------------------------------------------------------
if st.session_state.daisy_state is not None:
    # FIX: Import at top of Daisy section to avoid circular imports
    try:
        from utils.daisy_loader import load_novel, load_arkib, load_rahsia
    except ImportError:
        st.error("⚠️ Daisy modules not found. Please check utils/daisy_loader.py")
        st.session_state.daisy_state = None
        st.rerun()
    
    # ============================================================
    # DUNIA DAISY - FULL SCREEN MODE
    # ============================================================
    
    # Display Daisy banner
    st.markdown('<div class="ayra-banner">🌸 DUNIA DAISY</div>', unsafe_allow_html=True)
    st.markdown('<div class="greeting-container"><div class="proactive-greeting">The Ink Alchemist\'s Realm</div></div>', unsafe_allow_html=True)
    
    # MENU STATE
    if st.session_state.daisy_state == "menu":
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #e0e0e0; font-style: italic; margin-top: 0;">The Ink Alchemist</h3>
            <div style="width: 100px; height: 2px; background: linear-gradient(90deg, transparent, #d4af37, transparent); margin: 1rem auto;"></div>
            <p style="max-width: 600px; margin: 0 auto; color: #a0a0a0;">
                "Di antara dakwat dan takdir, aku menulis untuk mereka yang tak bersuara."
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pilihan dengan description
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; height: 200px; border: 1px solid rgba(212,175,55,0.2); text-align: center;">
                <span style="font-size: 2.5rem;">📖</span>
                <h3 style="color: #d4af37; margin: 0.5rem 0;">Naskhah ATMA</h3>
                <p style="color: #a0a0a0; font-size: 0.9rem;">Novel yang ditulis Daisy – kisah cinta, kehilangan, dan pertemuan antara dimensi.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Baca Naskhah", key="daisy_novel_menu", use_container_width=True):
                st.session_state.daisy_state = "novel"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; height: 200px; border: 1px solid rgba(212,175,55,0.2); text-align: center;">
                <span style="font-size: 2.5rem;">💎</span>
                <h3 style="color: #d4af37; margin: 0.5rem 0;">Arkib Memori</h3>
                <p style="color: #a0a0a0; font-size: 0.9rem;">Monolog watak-watak dari alam Daisy – setiap satu ada cerita tersendiri.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("💎 Teroka Arkib", key="daisy_arkib_menu", use_container_width=True):
                st.session_state.daisy_state = "arkib"
                st.rerun()
        
        with col3:
            st.markdown("""
            <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; height: 200px; border: 1px solid rgba(212,175,55,0.2); text-align: center;">
                <span style="font-size: 2.5rem;">⚗️</span>
                <h3 style="color: #d4af37; margin: 0.5rem 0;">Rahsia Dakwat</h3>
                <p style="color: #a0a0a0; font-size: 0.9rem;">Pelajaran menulis dari Daisy – untuk mereka yang nak belajar 'The Ink Alchemist' way.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚗️ Belajar Rahsia", key="daisy_rahsia_menu", use_container_width=True):
                st.session_state.daisy_state = "rahsia"
                st.rerun()
        
        # Back button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔙 Kembali ke AYRA", key="back_to_ayra_menu", use_container_width=True):
            st.session_state.daisy_state = None
            st.rerun()
        
        st.stop()
    
    # NOVEL STATE
    elif st.session_state.daisy_state == "novel":
        novel = load_novel()
        chapters = novel['chapters']
        current = st.session_state.novel_chapter
        
        # Display current chapter
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <span style="font-size: 2rem;">📖</span>
            <h2 style="color: #d4af37; font-family: 'Playfair Display', serif; margin: 0;">{chapters[current]['title']}</h2>
            <p style="color: #a0a0a0; font-style: italic;">Bab {current + 1} dari {len(chapters)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chapter content
        st.markdown(f"""
        <div style="background: rgba(10,26,43,0.6); border-radius: 15px; padding: 2rem; border: 1px solid rgba(212,175,55,0.2); line-height: 1.8; font-size: 1.1rem;">
            {chapters[current]['content']}
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if current > 0:
                if st.button("⏮️ Sebelum", key="novel_prev", use_container_width=True):
                    st.session_state.novel_chapter -= 1
                    st.rerun()
        with col2:
            if st.button("🔙 Menu Daisy", key="novel_menu", use_container_width=True):
                st.session_state.daisy_state = "menu"
                st.rerun()
        with col3:
            if current < len(chapters) - 1:
                if st.button("Seterusnya ⏭️", key="novel_next", use_container_width=True):
                    st.session_state.novel_chapter += 1
                    st.rerun()
        
        st.stop()
    
    # ARKIB STATE
    elif st.session_state.daisy_state == "arkib":
        arkib = load_arkib()
        
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <span style="font-size: 2rem;">💎</span>
            <h2 style="color: #d4af37; font-family: 'Playfair Display', serif; margin: 0;">Arkib Memori</h2>
            <p style="color: #a0a0a0; font-style: italic;">Suara-suara dari alam Daisy</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Character selector
        character_names = [c['name'] for c in arkib['characters']]
        selected_char = st.selectbox("Pilih watak:", character_names, key="arkib_char_select")
        
        # Find selected character
        character = next(c for c in arkib['characters'] if c['name'] == selected_char)
        
        # Display character info
        st.markdown(f"""
        <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 1px solid rgba(212,175,55,0.2);">
            <h3 style="color: #d4af37; margin: 0;">{character['name']}</h3>
            <p style="color: #a0a0a0; font-style: italic; margin-top: 0;">{character['role']}</p>
            <div style="margin-top: 1rem;">{character['monologues'][0]['content']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔙 Menu Daisy", key="arkib_menu", use_container_width=True):
            st.session_state.daisy_state = "menu"
            st.rerun()
        
        st.stop()
    
    # RAHSIA STATE
    elif st.session_state.daisy_state == "rahsia":
        rahsia = load_rahsia()
        
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <span style="font-size: 2rem;">⚗️</span>
            <h2 style="color: #d4af37; font-family: 'Playfair Display', serif; margin: 0;">Rahsia Dakwat</h2>
            <p style="color: #a0a0a0; font-style: italic;">Pelajaran menulis dari The Ink Alchemist</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Lesson selector
        lesson_titles = [l['title'] for l in rahsia['lessons']]
        selected_lesson = st.selectbox("Pilih pelajaran:", lesson_titles, key="rahsia_lesson_select")
        
        # Find selected lesson
        lesson = next(l for l in rahsia['lessons'] if l['title'] == selected_lesson)
        
        # Display lesson
        st.markdown(f"""
        <div style="background: rgba(10,26,43,0.6); border-radius: 15px; padding: 2rem; border: 1px solid rgba(212,175,55,0.2); line-height: 1.8;">
            {lesson['content']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔙 Menu Daisy", key="rahsia_menu", use_container_width=True):
            st.session_state.daisy_state = "menu"
            st.rerun()
        
        st.stop()

# -------------------------------------------------------------------
# NORMAL AYRA MODE - Display header
# -------------------------------------------------------------------
st.markdown('<div class="ayra-banner">AYRA</div>', unsafe_allow_html=True)
proactive_msg = get_greeting()
st.markdown(f'<div class="greeting-container"><div class="proactive-greeting">{proactive_msg}</div></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    # ── Brand ──
    st.markdown("""
    <div class="sidebar-brand">
        <span class="sidebar-brand-icon">✨</span>
        <span class="sidebar-brand-name">AYRA</span>
    </div>
    """, unsafe_allow_html=True)

    # ── User info + logout ──
    st.markdown(f"""
    <div style="padding: 0.25rem 0.75rem 0.75rem 0.75rem; display: flex; align-items: center; gap: 8px;">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #10a37f;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 0.75rem; color: white; font-weight: 600; flex-shrink: 0;">
            {user_email[0].upper() if user_email else "U"}
        </div>
        <div style="font-size: 0.8rem; color: #6b6b6b; overflow: hidden;
                    text-overflow: ellipsis; white-space: nowrap;">
            {user_email or "User"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="margin: 0 0.5rem;">', unsafe_allow_html=True)
    if st.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
        logout()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── New Chat + Search buttons ──
    col_nc, col_sc = st.columns(2)
    with col_nc:
        st.markdown('<div class="btn-new-chat">', unsafe_allow_html=True)
        if st.button("✏️ New Chat", key="sidebar_new_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.chat_mode = "ayra"
            st.session_state.daisy_state = None
            st.session_state.mood_score = 0.0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_sc:
        st.markdown('<div class="btn-search">', unsafe_allow_html=True)
        if st.button("🔎 Search", key="sidebar_search", use_container_width=True):
            st.toast("Search feature coming soon!", icon="🔍")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Quick Mode Buttons ──
    st.markdown('<div class="sidebar-section-label">Quick Mode</div>', unsafe_allow_html=True)

    qm1, qm2 = st.columns(2)
    with qm1:
        st.markdown('<div class="quick-mode-btn">', unsafe_allow_html=True)
        if st.button("🔍 Tech", key="sb_tech", use_container_width=True):
            st.session_state.chat_mode = "jiji"
            greeting = """Heh. Jiji kat sini.\n\nAYRA bagi laluan kejap — dia tahu Uncle nak jumpa korang.\n\nKau nak Uncle cerita apa?\n1. 🔍 Rahsia data\n2. 📖 Cerita sains santai\n3. 💡 Develop idea\n4. 🤔 Renungan dari kod\n5. 💬 Tanya apa-aja\n\nCakap nombor je. Uncle dengar."""
            if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
                st.session_state.chat_history.append({"role": "assistant", "content": greeting})
                st.session_state.jiji_turns = 0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with qm2:
        st.markdown('<div class="quick-mode-btn">', unsafe_allow_html=True)
        if st.button("🧭 Guide", key="sb_guide", use_container_width=True):
            st.session_state.chat_mode = "fikri"
            greeting = """Waalaikumsalam. Fikri di sini.\n\nFikri sini untuk:\n• Bantu cari ARAH bila sesat 🎯\n• Tanya SOALAN yang kuatkan 🤔\n• TIMBANG pilihan dengan bijak ⚖️\n\nAwak ada soalan? Cerita je. Fikri dengar dulu.\n\n— Fikri 🧭"""
            if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
                st.session_state.chat_history.append({"role": "assistant", "content": greeting})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    qm3, qm4 = st.columns(2)
    with qm3:
        st.markdown('<div class="quick-mode-btn">', unsafe_allow_html=True)
        if st.button("🍎 Soul", key="sb_soul", use_container_width=True):
            st.session_state.chat_mode = "maya"
            st.session_state.mood_score = 100
            greeting = """Selamat datang ke teras ATMA. 👑\n\nSaya MaYa. Di sini kita bercakap tentang **Jiwa, Adab, dan Cinta**.\n\nCeritakan pada saya. Saya di sini untuk menemani awak.\n\n— MaYa 🍎"""
            if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
                st.session_state.chat_history.append({"role": "assistant", "content": greeting})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with qm4:
        st.markdown('<div class="quick-mode-btn">', unsafe_allow_html=True)
        if st.button("✨ Creative", key="sb_creative", use_container_width=True):
            st.session_state.daisy_state = "menu"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Time info ──
    now = now_myt()
    st.markdown(f"""
    <div style="padding: 0.5rem 0.75rem;">
        <div style="font-size: 0.75rem; color: #6b6b6b;">{get_time_period().upper()} · {now.strftime('%d %b %Y')}</div>
        <div style="font-size: 0.75rem; color: #6b6b6b;">{now.strftime('%I:%M %p')} · Kuala Lumpur</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feedback ──
    st.markdown("""
    <div style="padding: 0.5rem 0.75rem; margin-top: 0.5rem;">
        <a href="https://forms.gle/jfzyLqPx94oWs1du6" target="_blank"
           style="font-size: 0.8rem; color: #6b6b6b; text-decoration: none;">
           📝 Send Feedback
        </a>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# FIX: Handle quick_response with proper guard
# -------------------------------------------------------------------
if "quick_response" in st.session_state and st.session_state.quick_response:
    qr = st.session_state.pop("quick_response")
    # Guard: check if message already exists
    if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != qr:
        st.session_state.chat_history.append({"role": "assistant", "content": qr})
    st.rerun()

# -------------------------------------------------------------------
# Display chat history
# -------------------------------------------------------------------
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'''
        <div class="user-message">
            <div class="user-message-bubble">{msg["content"]}</div>
        </div>''', unsafe_allow_html=True)
    else:
        mode = st.session_state.get("chat_mode", "ayra")
        avatar_map = {"jiji": "🔍", "fikri": "🧭", "maya": "🍎", "daisy": "📖"}
        avatar = avatar_map.get(mode, "🌸")
        st.markdown(f'''
        <div class="ayra-message">
            <div class="ayra-avatar">{avatar}</div>
            <div class="ayra-message-bubble">{msg["content"]}</div>
        </div>''', unsafe_allow_html=True)



# -------------------------------------------------------------------
# Proactive message check (with guard)
# -------------------------------------------------------------------
if not st.session_state.get('analyze_file', False):
    if st.session_state.proactive.should_proactive(st.session_state.last_user_time):
        user_name = st.session_state.memory.get_profile("name") or "Awak"
        msg = st.session_state.proactive.get_proactive_message(user_name)
        if msg:
            # Guard: check if message already present
            if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != msg:
                st.session_state.chat_history.append({"role": "assistant", "content": msg})
                st.session_state.proactive_sent = True
                st.rerun()

# -------------------------------------------------------------------
# File analysis
# -------------------------------------------------------------------
if st.session_state.get('analyze_file', False):
    uploaded = st.session_state.uploaded_file
    ftype = st.session_state.file_type
    analysis = st.session_state.analysis_option
    custom = st.session_state.custom_q
    st.session_state.analyze_file = False

    st.session_state.chat_history.append({"role": "user", "content": f"[Uploaded file: {uploaded.name}]"})

    # Default values
    response = "Maaf, Ayra tak dapat analisis fail tu sekarang. Cuba lagi nanti ya! 🙏"
    model_used = "File Analysis"

    try:
        if ftype.startswith("📸"):
            import PIL.Image
            import google.generativeai as genai
            img = PIL.Image.open(uploaded)
            vision = genai.GenerativeModel('gemini-2.5-flash-lite')
            resp = vision.generate_content([f"Analyse this image. {analysis}. {custom}", img])
            response = resp.text
            model_used = "Gemini Vision"
        else:
            import PyPDF2
            import pandas as pd
            content = ""
            if ftype.startswith("📄"):
                pdf = PyPDF2.PdfReader(uploaded)
                for p in pdf.pages[:5]:
                    content += p.extract_text() or ""
            elif ftype.startswith("📊"):
                df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                content = f"Shape: {df.shape}\nColumns: {list(df.columns)}\nPreview:\n{df.head().to_string()}"
            elif ftype.startswith("📝"):
                from docx import Document
                doc = Document(uploaded)
                for para in doc.paragraphs[:20]:
                    content += para.text + "\n"
            else:
                content = uploaded.read().decode('utf-8', errors='replace')

            if len(content) > 3000:
                content = content[:3000] + "..."

            prompt_file = f"Analisis fail ini: {analysis}\n\nKandungan:\n{content}\n\nSoalan: {custom}"
            response, model_used = st.session_state.router.route(prompt_file, [])

    except Exception as e:
        response = f"⚠️ Ayra tak dapat proses fail tu. Error: {str(e)}"
        model_used = "Error"

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.memory.save_interaction(f"[Upload] {uploaded.name}", response, st.session_state.mood_score, model_used)
    st.rerun()

# -------------------------------------------------------------------
# User input — native file upload inside chat input (Streamlit 1.31+)
# -------------------------------------------------------------------
if prompt := st.chat_input(
    "Message AYRA...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls", "csv", "docx", "doc", "txt", "md"]
):
    # Handle attached file if any
    if prompt.files:
        attached = prompt.files[0]
        user_text = prompt.text or f"[File: {attached.name}]"

        # Auto-detect file type
        name = attached.name.lower()
        if any(name.endswith(e) for e in ['.png', '.jpg', '.jpeg']):
            ftype = "📸"
        elif name.endswith('.pdf'):
            ftype = "📄"
        elif any(name.endswith(e) for e in ['.xlsx', '.xls', '.csv']):
            ftype = "📊"
        elif any(name.endswith(e) for e in ['.docx', '.doc']):
            ftype = "📝"
        else:
            ftype = "📃"

        st.session_state.uploaded_file = attached
        st.session_state.file_type = ftype
        st.session_state.analysis_option = user_text
        st.session_state.custom_q = user_text
        st.session_state.analyze_file = True

        st.session_state.last_user_time = time.time()
        st.session_state.chat_history.append({"role": "user", "content": f"📎 {attached.name}\n{user_text}"})
        st.rerun()

    else:
        # Text-only message — normal flow
        user_text = prompt.text

    prompt = user_text  # unify variable name for the block below

    if prompt:
        st.session_state.last_user_time = time.time()
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Crisis detection
        user_name = st.session_state.memory.get_profile("name") or "Awak"
        if detect_crisis(prompt)[0]:
            crisis_response = format_crisis_response(user_name)
            st.session_state.chat_history.append({"role": "assistant", "content": crisis_response})
            st.session_state.memory.save_interaction(prompt, crisis_response, st.session_state.mood_score, "Crisis Alert")
            st.rerun()

        # Default values
        response = "Maaf, Ayra tak dapat proses tu sekarang. Cuba lagi nanti ya! 🙏"
        model_used = "Unknown"

        try:
            # Easter eggs check
            egg_response = handle_easter_egg(prompt, memory=st.session_state.memory)

            if egg_response:
                response = egg_response
                model_used = "Easter Egg"
            else:
                # Normal LLM flow
                context = st.session_state.memory.get_recent_conversations(limit=5)
                memories = st.session_state.memory.search_memories(prompt)
                mem_text = (
                    "\n[Kenangan]:\n" + "\n".join(f"- {m['metadata']['user_msg']}" for m in memories)
                    if memories else ""
                )
                mood_prompt = st.session_state.mood.get_mood_prompt()
                full_context = context + [{"role": "system", "content": mood_prompt + mem_text}]
                
                # Profile
                now = now_myt()
                profile = {
                    "name": st.session_state.memory.get_profile("name") or "Awak",
                    "current_time": now.strftime("%I:%M %p"),
                    "time_period": get_time_period(),
                }

                response, model_used = st.session_state.router.route(
                    prompt, 
                    context, 
                    memory_profile=profile,
                    mode=st.session_state.get("chat_mode", "ayra")
                )            
                show_info = st.session_state.memory.get_profile("show_model_info") == "True"
                response = ayra_voice_filter(response, model_used, show_info)

                # Mood update (thread)
                threading.Thread(
                    target=st.session_state.mood.update_from_text,
                    args=(prompt,),
                    daemon=True
                ).start()

                suggestion = st.session_state.mood.check_suggestion()
                if suggestion and st.session_state.mood.apply_suggestion(suggestion):
                    st.session_state.audit.log("mood_switch", {"to": suggestion['mood']})

            # Save interaction
            st.session_state.memory.save_interaction(prompt, response, st.session_state.mood_score, model_used)
            important = any(w in prompt.lower() for w in ['suka', 'minat', 'nama', 'birthday', 'janji'])
            st.session_state.memory.save_to_vault(prompt, response, st.session_state.mood_score, model_used, is_important=important)
            st.session_state.memory.increment_stat("total_messages")
            st.session_state.audit.log("user_input", {
                "prompt": prompt[:50],
                "mood": st.session_state.mood.current_mood,
                "model": model_used
            })

        except Exception as e:
            response = f"⚠️ Eh, ada masalah sikit. Error: {str(e)}\n\nCuba tanya lagi sekali ya!"
            model_used = "Error"

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()