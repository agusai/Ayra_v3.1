# utils/styles.py

def get_css() -> str:
    return """
    <style>
    /* ===== AYRA 3.1 — WARM PREMIUM UI ===== */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    /* ===== GLOBAL WARM BG ===== */
    .stApp {
        background-color: #faf9f7 !important;
        color: #1c1c1c !important;
    }

    /* Hide streamlit default chrome */
    MainMenu { visibility: hidden; }
    
    /* ===== JIJI'S FIX: HEADER & COLLAPSE BUTTON ===== */
    header[data-testid="stHeader"] {
        background: transparent !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        padding: 0 15px !important;
        height: 48px !important;
        pointer-events: none !important;
    }

    header[data-testid="stHeader"] button {
        pointer-events: auto !important;
    }

    header[data-testid="stHeader"] button[data-testid="baseButton-headerNoPadding"],
    button[data-testid="baseButton-headerNoPadding"] {
        background: #ff6b6b !important;
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        border: 2px solid white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 5px !important;
        opacity: 1 !important;
        box-shadow: 0 2px 8px rgba(255,107,107,0.3) !important;
        color: white !important;
        position: relative !important;
    }

    header[data-testid="stHeader"] button svg,
    button[data-testid="baseButton-headerNoPadding"] svg {
        fill: white !important;
        width: 20px !important;
        height: 20px !important;
    }

    header[data-testid="stHeader"] button:hover,
    button[data-testid="baseButton-headerNoPadding"]:hover {
        background: #ff5252 !important;
        transform: scale(1.05) !important;
    }

    header[data-testid="stHeader"] button span,
    button[data-testid="baseButton-headerNoPadding"] span {
        display: none !important;
    }

    footer { visibility: hidden !important; }

    /* ===== MAIN CONTENT AREA ===== */
    .main .block-container {
        max-width: 780px !important;
        padding: 2rem 1.5rem 6rem 1.5rem !important;
        margin: 0 auto !important;
    }

    /* ===== HEADER ===== */
    .ayra-banner {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #1c1c1c;
        margin-top: 2rem;
        margin-bottom: 0.4rem;
        letter-spacing: -0.8px;
    }

    .proactive-greeting {
        text-align: center;
        font-size: 0.875rem;
        color: #888;
        margin-bottom: 2.5rem;
        display: block;
        font-weight: 400;
    }

    .greeting-container {
        text-align: center;
    }

    /* ===== CHAT MESSAGES ===== */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin: 1rem 0;
    }

    .user-message-bubble {
        background-color: #f0ede8;
        color: #1c1c1c;
        border-radius: 20px 20px 4px 20px;
        padding: 13px 18px;
        max-width: 72%;
        font-size: 0.95rem;
        line-height: 1.65;
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .ayra-message {
        display: flex;
        justify-content: flex-start;
        align-items: flex-start;
        margin: 1rem 0;
        gap: 12px;
    }

    .ayra-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #10a37f, #0d8c6d);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        flex-shrink: 0;
        margin-top: 2px;
        box-shadow: 0 2px 6px rgba(16,163,127,0.25);
    }

    .ayra-message-bubble {
        background-color: transparent;
        color: #1c1c1c;
        padding: 6px 4px;
        max-width: 82%;
        font-size: 0.95rem;
        line-height: 1.75;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background-color: #f2f0ec !important;
        border-right: none !important;
        box-shadow: 1px 0 12px rgba(0,0,0,0.05) !important;
    }

    [data-testid="stSidebar"] > div {
        padding: 0.75rem 0.65rem !important;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.5rem 0.5rem;
        margin-bottom: 0.4rem;
    }

    .sidebar-brand-icon {
        font-size: 1.2rem;
    }

    .sidebar-brand-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1c1c1c;
        letter-spacing: -0.5px;
    }

    .sidebar-section-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.3rem 0.5rem;
        margin-top: 0.3rem;
        margin-bottom: 0.2rem;
    }

    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        color: #2c2c2c !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.45rem 0.65rem !important;
        font-size: 0.855rem !important;
        font-weight: 500 !important;
        width: 100%;
        text-align: left !important;
        transition: background 0.15s ease;
        margin-bottom: 0.05rem !important;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(0,0,0,0.06) !important;
    }

    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.05rem !important;
    }

    .btn-new-chat button {
        background: linear-gradient(135deg, #10a37f, #0d8c6d) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(16,163,127,0.25) !important;
        text-align: left !important;
    }

    .btn-new-chat button:hover {
        background: linear-gradient(135deg, #0d8c6d, #0b7a5e) !important;
        box-shadow: 0 3px 12px rgba(16,163,127,0.35) !important;
    }

    .btn-search button {
        background-color: rgba(0,0,0,0.04) !important;
        color: #666 !important;
        border: none !important;
        border-radius: 10px !important;
        text-align: left !important;
    }

    .btn-search button:hover {
        background-color: rgba(0,0,0,0.08) !important;
        color: #1c1c1c !important;
    }

    .quick-mode-btn button {
        background-color: #ffffff !important;
        border: 1px solid #e2dfd9 !important;
        border-radius: 10px !important;
        color: #2c2c2c !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 0.3rem !important;
        text-align: left !important;
        justify-content: left !important;
        transition: all 0.15s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        margin-bottom: 0.05rem !important;
    }

    .quick-mode-btn button:hover {
        background-color: #e8f5f0 !important;
        border-color: #10a37f !important;
        color: #0d8c6d !important;
        box-shadow: 0 2px 6px rgba(16,163,127,0.15) !important;
    }

    .quick-mode-btn button p,
    .quick-mode-btn button div {
        text-align: left !important;
        width: 100% !important;
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
        border: 1px solid #e2dfd9 !important;
        border-radius: 18px !important;
        color: #1c1c1c !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07) !important;
    }

    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #1c1c1c !important;
        font-size: 0.95rem !important;
        padding: 13px 18px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #bbb !important;
    }

    /* ===== FILE UPLOADER compact ===== */
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border: 1px dashed #ddd !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploader"] label {
        color: #888 !important;
        font-size: 0.8rem !important;
    }

    .streamlit-expanderContent {
        background-color: #faf9f7 !important;
        border: 1px solid #e8e5e0 !important;
        color: #1c1c1c !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d5d0c8; border-radius: 4px; }

    /* ===== MISC ===== */
    hr {
        border: none !important;
        border-top: 1px solid #e8e5e0 !important;
        margin: 0.6rem 0 !important;
    }

    .stRadio label, .stSelectbox label { color: #1c1c1c !important; }
    .stRadio [data-testid="stWidgetLabel"] { color: #888 !important; font-size: 0.8rem !important; }

    .stAlert {
        background-color: #f5f3ef !important;
        border: 1px solid #e8e5e0 !important;
        color: #1c1c1c !important;
        border-radius: 10px !important;
    }

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e8e5e0 !important;
        border-radius: 12px !important;
        padding: 0.75rem !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stMetric"] label { color: #888 !important; font-size: 0.72rem !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #1c1c1c !important; font-size: 0.9rem !important; }

    .stApp h1, .stApp h2, .stApp h3 { color: #1c1c1c !important; }
    .stMarkdown { color: #1c1c1c; }

    /* ===== HIDE SIDEBAR COLLAPSE BUTTON TEXT ===== */
    [data-testid="collapsedControl"] span,
    button[data-testid="baseButton-headerNoPadding"] span,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapsedControl"] span {
        display: none !important;
    }
    [data-testid="stSidebar"] ~ div button span,
    .st-emotion-cache-1dp5vir span { display: none !important; }

    /* ===== MOBILE RESPONSIVE ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.75rem 5rem 0.75rem !important;
        }
        .quick-mode-btn button {
            font-size: 0.78rem !important;
            padding: 0.4rem 0.2rem !important;
        }
        [data-testid="stSidebar"] > div {
            padding: 0.5rem 0.4rem !important;
        }
        [data-testid="stSidebar"] .stButton button {
            padding: 0.4rem 0.5rem !important;
            font-size: 0.82rem !important;
        }
        .user-message-bubble {
            max-width: 88% !important;
        }
        .ayra-message-bubble {
            max-width: 92% !important;
        }
    }
    </style>
    """ 