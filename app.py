import streamlit as st
import time
import PIL.Image
import PyPDF2
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

MYT = ZoneInfo("Asia/Kuala_Lumpur")

def now_myt():
    return datetime.now(MYT)

from utils.memory_manager import MemoryManager
from utils.mood_detector import MoodDetector
from utils.model_router import ModelRouter
from utils.helpers import get_greeting
from utils.crisis_detector import detect_crisis, format_crisis_response
from utils.proactive_engine import ProactiveEngine
from utils.audit_logger import AuditLogger
from utils.consistency_layer import ayra_voice_filter
from auth import handle_oauth_callback, restore_session, is_logged_in, show_auth_page, logout, get_user_id, get_user_email

load_dotenv()

# -------------------------------------------------------------------
# Page config — must be first
# -------------------------------------------------------------------
st.set_page_config(page_title="AYRA – The Soulful Malaysian AI", page_icon="✨")

# -------------------------------------------------------------------
# Auth gate
# -------------------------------------------------------------------
handle_oauth_callback()
restore_session()

if not is_logged_in():
    show_auth_page()
    st.stop()

# -------------------------------------------------------------------
# Helper: time period (MYT)
# -------------------------------------------------------------------
def get_time_period():
    hour = now_myt().hour
    if 5 <= hour < 12:   return "pagi"
    elif 12 <= hour < 15: return "tengah hari"
    elif 15 <= hour < 19: return "petang"
    elif 19 <= hour < 22: return "malam"
    else:                  return "lewat malam"

# -------------------------------------------------------------------
# Session state init
# -------------------------------------------------------------------
def init_session():
    defaults = {
        "memory":            MemoryManager(),
        "mood":              MoodDetector(),
        "router":            ModelRouter(),
        "proactive":         ProactiveEngine(),
        "audit":             AuditLogger(),
        "chat_history":      [],
        "messages":          [],
        "mood_score":        0.0,
        "comfort_mode":      False,
        "current_story_id":  None,
        "last_user_time":    time.time(),
        "proactive_sent":    False,
        "chat_mode":         "ayra",
        "jiji_turns":        0,
        "daisy_state":       None,
        "active_world":      None,
        "novel_chapter":     0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

user_id    = get_user_id()
user_email = get_user_email()

# -------------------------------------------------------------------
# CSS
# -------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    .stApp { background-color: #faf9f7 !important; color: #1c1c1c !important; }

    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden !important; }

    .main .block-container {
        max-width: 780px !important;
        padding: 2rem 1.5rem 6rem 1.5rem !important;
        margin: 0 auto !important;
    }

    /* Header */
    .ayra-banner {
        text-align: center; font-size: 2.2rem; font-weight: 700;
        color: #1c1c1c; margin-top: 2rem; margin-bottom: 0.4rem; letter-spacing: -0.8px;
    }
    .proactive-greeting {
        text-align: center; font-size: 0.875rem; color: #888;
        margin-bottom: 2.5rem; display: block; font-weight: 400;
    }
    .greeting-container { text-align: center; }

    /* Chat bubbles */
    .user-message { display: flex; justify-content: flex-end; margin: 1rem 0; }
    .user-message-bubble {
        background-color: #f0ede8; color: #1c1c1c;
        border-radius: 20px 20px 4px 20px; padding: 13px 18px;
        max-width: 72%; font-size: 0.95rem; line-height: 1.65;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .ayra-message { display: flex; justify-content: flex-start; align-items: flex-start; margin: 1rem 0; gap: 12px; }
    .ayra-avatar {
        width: 32px; height: 32px; border-radius: 50%;
        background: linear-gradient(135deg, #10a37f, #0d8c6d);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.95rem; flex-shrink: 0; margin-top: 2px;
        box-shadow: 0 2px 6px rgba(16,163,127,0.25);
    }
    .ayra-message-bubble {
        background-color: transparent; color: #1c1c1c;
        padding: 6px 4px; max-width: 82%; font-size: 0.95rem; line-height: 1.75;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f2f0ec !important;
        border-right: none !important;
        box-shadow: 1px 0 12px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stSidebar"] > div { padding: 1rem 0.75rem !important; }

    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important; color: #2c2c2c !important;
        border: none !important; border-radius: 10px !important;
        padding: 0.45rem 0.65rem !important; font-size: 0.855rem !important;
        font-weight: 500 !important; width: 100%; text-align: left !important;
        transition: background 0.15s ease; margin-bottom: 0.05rem !important;
    }
    [data-testid="stSidebar"] .stButton button:hover { background-color: rgba(0,0,0,0.06) !important; }

    .btn-new-chat button {
        background: linear-gradient(135deg, #10a37f, #0d8c6d) !important;
        color: white !important; border-radius: 10px !important;
        font-weight: 600 !important; text-align: center !important;
        box-shadow: 0 2px 8px rgba(16,163,127,0.25) !important;
    }
    .btn-new-chat button:hover {
        background: linear-gradient(135deg, #0d8c6d, #0b7a5e) !important;
        box-shadow: 0 3px 12px rgba(16,163,127,0.35) !important;
    }

    .mode-btn button {
        background-color: #ffffff !important; border: 1px solid #e2dfd9 !important;
        border-radius: 10px !important; color: #2c2c2c !important;
        font-size: 0.82rem !important; font-weight: 500 !important;
        padding: 0.45rem 0.3rem !important; text-align: center !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    .mode-btn button:hover {
        background-color: #e8f5f0 !important; border-color: #10a37f !important;
        color: #0d8c6d !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: #ffffff !important; border: 1px solid #e2dfd9 !important;
        border-radius: 18px !important; color: #1c1c1c !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07) !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important; color: #1c1c1c !important;
        font-size: 0.95rem !important; padding: 13px 18px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: #bbb !important; }

    /* Misc */
    hr { border: none !important; border-top: 1px solid #e8e5e0 !important; margin: 0.6rem 0 !important; }
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d5d0c8; border-radius: 4px; }
    .stApp h1, .stApp h2, .stApp h3 { color: #1c1c1c !important; }
    .stMarkdown { color: #1c1c1c; }
    [data-testid="stMetric"] {
        background-color: #ffffff !important; border: 1px solid #e8e5e0 !important;
        border-radius: 12px !important; padding: 0.75rem !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    }

    @media (max-width: 768px) {
        .main .block-container { padding: 1rem 0.75rem 5rem 0.75rem !important; }
        .user-message-bubble { max-width: 88% !important; }
        .ayra-message-bubble { max-width: 92% !important; }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Daisy world (full-screen mode)
# -------------------------------------------------------------------
if st.session_state.daisy_state is not None:
    try:
        from utils.daisy_loader import load_novel, load_arkib, load_rahsia
    except ImportError:
        st.error("⚠️ Daisy modules not found. Please check utils/daisy_loader.py")
        st.session_state.daisy_state = None
        st.rerun()

    st.markdown('<div class="ayra-banner">🌸 DUNIA DAISY</div>', unsafe_allow_html=True)
    st.markdown('<div class="greeting-container"><div class="proactive-greeting">The Ink Alchemist\'s Realm</div></div>', unsafe_allow_html=True)

    if st.session_state.daisy_state == "menu":
        st.markdown("""
        <div style="text-align:center; margin:2rem 0;">
            <p style="max-width:600px; margin:0 auto; color:#a0a0a0; font-style:italic;">
                "Di antara dakwat dan takdir, aku menulis untuk mereka yang tak bersuara."
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📖 Naskhah ATMA", key="daisy_novel_menu", use_container_width=True):
                st.session_state.daisy_state = "novel"; st.rerun()
        with col2:
            if st.button("💎 Arkib Memori", key="daisy_arkib_menu", use_container_width=True):
                st.session_state.daisy_state = "arkib"; st.rerun()
        with col3:
            if st.button("⚗️ Rahsia Dakwat", key="daisy_rahsia_menu", use_container_width=True):
                st.session_state.daisy_state = "rahsia"; st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Kembali ke AYRA", key="back_to_ayra_menu", use_container_width=True):
            st.session_state.daisy_state = None; st.rerun()
        st.stop()

    elif st.session_state.daisy_state == "novel":
        novel = load_novel()
        chapters = novel['chapters']
        current = st.session_state.novel_chapter

        st.markdown(f"""
        <div style="text-align:center; margin:2rem 0 1rem 0;">
            <h2 style="color:#d4af37; margin:0;">{chapters[current]['title']}</h2>
            <p style="color:#a0a0a0; font-style:italic;">Bab {current+1} dari {len(chapters)}</p>
        </div>
        <div style="background:rgba(10,26,43,0.6); border-radius:15px; padding:2rem;
                    border:1px solid rgba(212,175,55,0.2); line-height:1.8; font-size:1.1rem;">
            {chapters[current]['content']}
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if current > 0:
                if st.button("← Sebelum", key="novel_prev", use_container_width=True):
                    st.session_state.novel_chapter -= 1; st.rerun()
        with col2:
            if st.button("← Menu Daisy", key="novel_menu", use_container_width=True):
                st.session_state.daisy_state = "menu"; st.rerun()
        with col3:
            if current < len(chapters) - 1:
                if st.button("Seterusnya →", key="novel_next", use_container_width=True):
                    st.session_state.novel_chapter += 1; st.rerun()
        st.stop()

    elif st.session_state.daisy_state == "arkib":
        arkib = load_arkib()
        st.markdown('<h2 style="color:#d4af37; text-align:center;">💎 Arkib Memori</h2>', unsafe_allow_html=True)

        character_names = [c['name'] for c in arkib['characters']]
        selected_char = st.selectbox("Pilih watak:", character_names, key="arkib_char_select")
        character = next(c for c in arkib['characters'] if c['name'] == selected_char)

        st.markdown(f"""
        <div style="background:rgba(212,175,55,0.05); border-radius:15px; padding:1.5rem;
                    margin:1rem 0; border:1px solid rgba(212,175,55,0.2);">
            <h3 style="color:#d4af37; margin:0;">{character['name']}</h3>
            <p style="color:#a0a0a0; font-style:italic; margin-top:0;">{character['role']}</p>
            <div style="margin-top:1rem;">{character['monologues'][0]['content']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("← Menu Daisy", key="arkib_menu", use_container_width=True):
            st.session_state.daisy_state = "menu"; st.rerun()
        st.stop()

    elif st.session_state.daisy_state == "rahsia":
        rahsia = load_rahsia()
        st.markdown('<h2 style="color:#d4af37; text-align:center;">⚗️ Rahsia Dakwat</h2>', unsafe_allow_html=True)

        lesson_titles = [l['title'] for l in rahsia['lessons']]
        selected_lesson = st.selectbox("Pilih pelajaran:", lesson_titles, key="rahsia_lesson_select")
        lesson = next(l for l in rahsia['lessons'] if l['title'] == selected_lesson)

        st.markdown(f"""
        <div style="background:rgba(10,26,43,0.6); border-radius:15px; padding:2rem;
                    border:1px solid rgba(212,175,55,0.2); line-height:1.8;">
            {lesson['content']}
        </div>
        """, unsafe_allow_html=True)

        if st.button("← Menu Daisy", key="rahsia_menu", use_container_width=True):
            st.session_state.daisy_state = "menu"; st.rerun()
        st.stop()

# -------------------------------------------------------------------
# Main header
# -------------------------------------------------------------------
st.markdown('<div class="ayra-banner">AYRA</div>', unsafe_allow_html=True)
proactive_msg = get_greeting()
st.markdown(f'<div class="greeting-container"><div class="proactive-greeting">{proactive_msg}</div></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px; padding:0.5rem; margin-bottom:0.75rem;">
        <span style="font-size:1.3rem;">✨</span>
        <span style="font-size:1.4rem; font-weight:700; color:#1c1c1c; letter-spacing:-0.5px;">AYRA</span>
    </div>
    """, unsafe_allow_html=True)

    # User info
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; padding:0.25rem 0.5rem 0.75rem 0.5rem;">
        <div style="width:28px; height:28px; border-radius:50%; background:#10a37f;
                    display:flex; align-items:center; justify-content:center;
                    font-size:0.75rem; color:white; font-weight:600; flex-shrink:0;">
            {user_email[0].upper() if user_email else "U"}
        </div>
        <div style="font-size:0.8rem; color:#6b6b6b; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
            {user_email or "User"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New Chat + Logout
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="btn-new-chat">', unsafe_allow_html=True)
        if st.button("✏️ New Chat", key="sidebar_new_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.chat_mode = "ayra"
            st.session_state.daisy_state = None
            st.session_state.mood_score = 0.0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        if st.button("🚪 Sign Out", key="logout_btn", use_container_width=True):
            logout()

    st.markdown('<hr>', unsafe_allow_html=True)

    # Mode selector
    st.markdown('<div style="font-size:0.68rem; font-weight:600; color:#999; text-transform:uppercase; letter-spacing:0.1em; padding:0.3rem 0.25rem 0.2rem;">Mode</div>', unsafe_allow_html=True)

    MODES = [
        ("ayra",   "🌸 AYRA",     "Chat biasa dengan Ayra"),
        ("jiji",   "🔍 Tech",     "Analisis data & sains"),
        ("fikri",  "🧭 Guide",    "Bimbingan & arah tuju"),
        ("maya",   "🍎 Soul",     "Jiwa, adab & cinta"),
        ("daisy",  "✨ Creative", "Zon kreatif Daisy"),
    ]

    MODE_GREETINGS = {
        "jiji":  "Jiji kat sini. Kau nak Uncle cerita apa? Cakap je.",
        "fikri": "Hai. Fikri di sini untuk bantu cari arah. Awak ada soalan?",
        "maya":  "Selamat datang. Saya MaYa. Ceritakan pada saya.",
        "daisy": "Hai Jiwa Kreatif! ✨ Awak nak kita buat apa hari ni?",
    }

    for mode_key, label, tooltip in MODES:
        st.markdown('<div class="mode-btn">', unsafe_allow_html=True)
        if st.button(label, key=f"mode_{mode_key}", use_container_width=True, help=tooltip):
            st.session_state.chat_mode = mode_key
            if mode_key == "maya":
                st.session_state.mood_score = 100
            greeting = MODE_GREETINGS.get(mode_key)
            if greeting:
                last = st.session_state.chat_history[-1].get("content") if st.session_state.chat_history else None
                if last != greeting:
                    st.session_state.chat_history.append({"role": "assistant", "content": greeting})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Clock + feedback
    now = now_myt()
    st.markdown(f"""
    <div style="padding:0.25rem 0.25rem 0.5rem;">
        <div style="font-size:0.72rem; color:#999;">{get_time_period().upper()} · {now.strftime('%d %b %Y')}</div>
        <div style="font-size:0.72rem; color:#999;">{now.strftime('%I:%M %p')} · Kuala Lumpur</div>
    </div>
    <div style="padding:0.25rem;">
        <a href="https://forms.gle/jfzyLqPx94oWs1du6" target="_blank"
           style="font-size:0.78rem; color:#999; text-decoration:none;">📝 Send Feedback</a>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# Quick response guard
# -------------------------------------------------------------------
if "quick_response" in st.session_state and st.session_state.quick_response:
    qr = st.session_state.pop("quick_response")
    if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != qr:
        st.session_state.chat_history.append({"role": "assistant", "content": qr})
    st.rerun()

# -------------------------------------------------------------------
# Proactive message check
# -------------------------------------------------------------------
if not st.session_state.get('analyze_file', False):
    if st.session_state.proactive.should_proactive(st.session_state.last_user_time):
        user_name = st.session_state.memory.get_profile("name") or "Awak"
        msg = st.session_state.proactive.get_proactive_message(user_name)
        if msg:
            last = st.session_state.chat_history[-1].get("content") if st.session_state.chat_history else None
            if last != msg:
                st.session_state.chat_history.append({"role": "assistant", "content": msg})
                st.session_state.proactive_sent = True
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
        avatar_map = {"jiji": "🔍", "fikri": "🧭", "maya": "🍎", "daisy": "📖"}
        avatar = avatar_map.get(st.session_state.get("chat_mode", "ayra"), "🌸")
        st.markdown(f'''
        <div class="ayra-message">
            <div class="ayra-avatar">{avatar}</div>
            <div class="ayra-message-bubble">{msg["content"]}</div>
        </div>''', unsafe_allow_html=True)

# -------------------------------------------------------------------
# File analysis
# -------------------------------------------------------------------
if st.session_state.get('analyze_file', False):
    uploaded = st.session_state.uploaded_file
    ftype    = st.session_state.file_type
    analysis = st.session_state.analysis_option
    custom   = st.session_state.custom_q
    st.session_state.analyze_file = False

    st.session_state.chat_history.append({"role": "user", "content": f"[Uploaded file: {uploaded.name}]"})

    response   = "Maaf, Ayra tak dapat analisis fail tu sekarang. Cuba lagi nanti ya! 🙏"
    model_used = "File Analysis"

    # File size guard (10 MB)
    uploaded.seek(0, 2)
    file_size = uploaded.tell()
    uploaded.seek(0)

    if file_size > 10 * 1024 * 1024:
        response   = "⚠️ Fail terlalu besar (max 10MB). Cuba muat naik fail yang lebih kecil ya."
        model_used = "Error"
    else:
        try:
            if ftype.startswith("📸"):
                import google.generativeai as genai
                img     = PIL.Image.open(uploaded)
                vision  = genai.GenerativeModel('gemini-2.5-flash-lite')
                resp    = vision.generate_content([f"Analyse this image. {analysis}. {custom}", img])
                response   = resp.text
                model_used = "Gemini Vision"
            else:
                content = ""
                if ftype.startswith("📄"):
                    pdf = PyPDF2.PdfReader(uploaded)
                    for p in pdf.pages[:10]:
                        content += p.extract_text() or ""
                elif ftype.startswith("📊"):
                    df      = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                    content = f"Shape: {df.shape}\nColumns: {list(df.columns)}\nPreview:\n{df.head().to_string()}"
                elif ftype.startswith("📝"):
                    from docx import Document
                    doc = Document(uploaded)
                    content = "\n".join(p.text for p in doc.paragraphs[:20])
                else:
                    content = uploaded.read().decode('utf-8', errors='replace')

                if len(content) > 3000:
                    content = content[:3000] + "..."

                prompt_file        = f"Analisis fail ini: {analysis}\n\nKandungan:\n{content}\n\nSoalan: {custom}"
                response, model_used = st.session_state.router.route(prompt_file, [])

        except Exception as e:
            response   = f"⚠️ Ayra tak dapat proses fail tu. Error: {str(e)}"
            model_used = "Error"

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.memory.save_interaction(f"[Upload] {uploaded.name}", response, st.session_state.mood_score, model_used)
    st.rerun()

# -------------------------------------------------------------------
# Chat input
# -------------------------------------------------------------------
if prompt := st.chat_input(
    "Message AYRA...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls", "csv", "docx", "doc", "txt", "md"]
):
    # File attachment
    if prompt.files:
        attached  = prompt.files[0]
        user_text = prompt.text or f"[File: {attached.name}]"
        name      = attached.name.lower()

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

        st.session_state.uploaded_file   = attached
        st.session_state.file_type       = ftype
        st.session_state.analysis_option = user_text
        st.session_state.custom_q        = user_text
        st.session_state.analyze_file    = True
        st.session_state.last_user_time  = time.time()
        st.session_state.chat_history.append({"role": "user", "content": f"📎 {attached.name}\n{user_text}"})
        st.rerun()

    else:
        user_text = prompt.text

    if user_text:
        st.session_state.last_user_time = time.time()
        st.session_state.chat_history.append({"role": "user", "content": user_text})

        # Crisis check
        user_name = st.session_state.memory.get_profile("name") or "Awak"
        if detect_crisis(user_text)[0]:
            crisis_response = format_crisis_response(user_name)
            st.session_state.chat_history.append({"role": "assistant", "content": crisis_response})
            st.session_state.memory.save_interaction(user_text, crisis_response, st.session_state.mood_score, "Crisis Alert")
            st.rerun()

        response   = "Maaf, Ayra tak dapat proses tu sekarang. Cuba lagi nanti ya! 🙏"
        model_used = "Unknown"

        try:
            context  = st.session_state.memory.get_recent_conversations(limit=5)
            memories = st.session_state.memory.search_memories(user_text)
            mem_text = (
                "\n[Kenangan]:\n" + "\n".join(f"- {m['metadata']['user_msg']}" for m in memories)
                if memories else ""
            )
            mood_prompt  = st.session_state.mood.get_mood_prompt()
            full_context = context + [{"role": "system", "content": mood_prompt + mem_text}]

            now = now_myt()
            profile = {
                "name":        st.session_state.memory.get_profile("name") or "Awak",
                "current_time": now.strftime("%I:%M %p"),
                "time_period":  get_time_period(),
            }

            response, model_used = st.session_state.router.route(
                user_text,
                context,
                memory_profile=profile,
                mode=st.session_state.get("chat_mode", "ayra")
            )

            show_info = st.session_state.memory.get_profile("show_model_info") == "True"
            response  = ayra_voice_filter(response, model_used, show_info)

            # Mood update
            st.session_state.mood.update_from_text(user_text)
            suggestion = st.session_state.mood.check_suggestion()
            if suggestion and st.session_state.mood.apply_suggestion(suggestion):
                st.session_state.audit.log("mood_switch", {"to": suggestion['mood']})

        except Exception as e:
            response   = f"⚠️ Eh, ada masalah sikit. Error: {str(e)}\n\nCuba tanya lagi sekali ya!"
            model_used = "Error"

        # Persist
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.memory.save_interaction(user_text, response, st.session_state.mood_score, model_used)

        important = any(w in user_text.lower() for w in ['suka', 'minat', 'nama', 'birthday', 'janji'])
        st.session_state.memory.save_to_vault(user_text, response, st.session_state.mood_score, model_used, is_important=important)
        st.session_state.memory.increment_stat("total_messages")
        st.session_state.audit.log("user_input", {
            "prompt": user_text[:50],
            "mood":   st.session_state.mood.current_mood,
            "model":  model_used,
        })

        st.rerun()