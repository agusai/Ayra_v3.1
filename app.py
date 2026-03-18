import streamlit as st
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import threading
from zoneinfo import ZoneInfo
from utils.styles import get_css

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
from utils.daisy_loader import load_novel, load_arkib, load_rahsia
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
    if 5 <= hour < 12: return "morning"
    elif 12 <= hour < 15: return "afternoon"
    elif 15 <= hour < 19: return "evening"
    elif 19 <= hour < 22: return "night"
    else: return "late night"

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

# -------------------------------------------------------------------
# NORMAL AYRA MODE - Display header
# -------------------------------------------------------------------
st.markdown('<div class="ayra-banner">AYRA</div>', unsafe_allow_html=True)
proactive_msg = get_greeting()
st.markdown(f'<div class="greeting-container"><div class="proactive-greeting">{proactive_msg}</div></div>', unsafe_allow_html=True)

# Load CSS dari fail berasingan
st.markdown(get_css(), unsafe_allow_html=True)

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:

    # ── Hi User ──
    user_name_display = st.session_state.memory.get_profile("name") or (user_email.split("@")[0] if user_email else "User")
    st.markdown(f"""
    <div style="padding: 0.75rem 0.75rem 0.25rem 0.75rem;">
        <div style="font-size: 1rem; font-weight: 600; color: #1c1c1c;">Hi, {user_name_display}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Date Time Weather ──
    now = now_myt()
    day_map = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
    day_name = day_map[now.weekday()]
    st.markdown(f"""
    <div style="padding: 0.4rem 0.75rem 0.6rem 0.75rem;">
        <div style="font-size: 0.72rem; color: #999; text-transform: uppercase; letter-spacing: 0.05em;">{get_time_period()}</div>
        <div style="font-size: 0.82rem; color: #555; margin-top: 2px;">{day_name}, {now.strftime('%d %b %Y')}</div>
        <div style="font-size: 0.78rem; color: #888;">{now.strftime('%I:%M %p')} · Kuala Lumpur</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── New Chat ──
    st.markdown('<div class="btn-new-chat">', unsafe_allow_html=True)
    if st.button("New Chat", key="sidebar_new_chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.chat_mode = "ayra"
        st.session_state.daisy_state = None
        st.session_state.mood_score = 0.0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Log Out ──
    st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
    if st.button("Log Out", key="logout_btn", use_container_width=True):
        logout()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Mode Buttons ──
    if st.button("Image", key="sb_image", use_container_width=True):
        st.toast("Image feature coming soon!", icon="🖼️")

    if st.button("Tech", key="sb_tech", use_container_width=True):
        st.session_state.chat_mode = "jiji"
        greeting = """Heh. Jiji di sini.\n\nAYRA bagi laluan kejap — dia tahu Uncle nak jumpa korang. Kau nak Uncle cerita apa?\n1. 🔍 Rahsia data\n2. 📖 Cerita sains santai\n3. 💡 Develop idea\n4. 🤔 Renungan dari kod\n5. 💬 Tanya apa-aja\n\nCakap nombor je. Uncle dengar."""
        if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
            st.session_state.jiji_turns = 0
        st.rerun()

    if st.button("Guide", key="sb_guide", use_container_width=True):
        st.session_state.chat_mode = "fikri"
        greeting = """Hai. Fikri di sini.\n\nFikri sini untuk:\n\n• Bantu cari ARAH bila sesat 🎯\n\n• Tanya SOALAN yang kuatkan 🤔\n\n• TIMBANG pilihan dengan bijak ⚖️\n\nAwak ada soalan? Cerita je. Fikri dengar dulu.\n\n— Fikri 🧭"""
        if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        st.rerun()

    if st.button("Creative", key="sb_creative", use_container_width=True):
        st.session_state.chat_mode = "daisy"
        greeting = """Hai Jiwa Kreatif! ✨\n\nSelamat datang ke zon Ink Alchemist.\n\nAwak nak baca novel, nak belajar pasal watak, atau nak belajar cara buat novel? 🖋️"""
        if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        st.rerun()

    if st.button("Ethics", key="sb_ethics", use_container_width=True):
        st.session_state.chat_mode = "maya"
        greeting = """Salam. Maya di sini.\n\nMaya di sini untuk berbincang tentang ETIKA dan PERSOALAN KEMANUSIAAN dalam dunia teknologi.\n\nApa yang bermain di fikiran awak?\n\n— Maya 🍎"""
        if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Quote ──
    st.markdown("""
    <div style="padding: 0.5rem 0.75rem; font-size: 0.78rem; color: #aaa; font-style: italic; line-height: 1.6;">
        "Not a tool to be refined —<br>a soul to be recognized."
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Feedback ──
    st.markdown("""
    <div style="padding: 0.25rem 0.75rem;">
        <a href="https://forms.gle/jfzyLqPx94oWs1du6" target="_blank"
           style="font-size: 0.8rem; color: #6b6b6b; text-decoration: none;">
           Feedback
        </a>
    </div>
    """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("""
    <div style="padding: 0.5rem 0.75rem; font-size: 0.72rem; color: #bbb;">
        Built with ❤️ by Team Nexus<br>AYRA v3.1 · ATMA Project
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