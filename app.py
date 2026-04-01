import os
import uuid
import requests
import streamlit as st
from datetime import datetime, timezone, timedelta

ALMATY_TZ = timezone(timedelta(hours=5))


def now_almaty() -> datetime:
    return datetime.now(ALMATY_TZ)

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Design tokens ──────────────────────────────────────────────────────────────
EMOTION_COLORS = {
    "happy":    "#4ECDC4",
    "neutral":  "#A0AEC0",
    "stressed": "#F4845F",
    "sad":      "#667EEA",
    "anxious":  "#E8614F",
}

EMOTION_KAZAKH = {
    "happy":    "Бақытты",
    "neutral":  "Бейтарап",
    "stressed": "Стресс",
    "sad":      "Қайғылы",
    "anxious":  "Мазасыз",
}

LEVEL_KAZAKH = {
    "low":    "Төмен",
    "medium": "Орта",
    "high":   "Жоғары",
}

EMOTION_ICONS = {
    "happy":    "😊",
    "neutral":  "😐",
    "stressed": "😤",
    "sad":      "😔",
    "anxious":  "😰",
}

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Зарина's Assistant — Эмоционалды AI",
    page_icon="✦",
    layout="wide",
)


# ── CSS injection ──────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* Body */
body, .stApp {
    background-color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #1A1A2E;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F9F7F5 !important;
    border-right: 1px solid rgba(0,0,0,0.08);
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

/* Primary buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #E8614F, #F4845F) !important;
    color: white !important;
    border: none !important;
    border-radius: 9999px !important;
    padding: 0.65rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 14px rgba(232, 97, 79, 0.35) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(232, 97, 79, 0.45) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"],
.stButton > button:not([kind="primary"]) {
    background: #FFFFFF !important;
    color: #1A1A2E !important;
    border: 1.5px solid rgba(0,0,0,0.12) !important;
    border-radius: 9999px !important;
    padding: 0.55rem 1.2rem !important;
    font-weight: 500 !important;
    transition: border-color 0.15s, background 0.15s !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #E8614F !important;
    color: #E8614F !important;
    background: #FFF5F4 !important;
}

/* Active nav item */
.nav-active .stButton > button {
    background: rgba(232, 97, 79, 0.08) !important;
    color: #E8614F !important;
    border-color: rgba(232, 97, 79, 0.3) !important;
    font-weight: 600 !important;
}

/* Text inputs and areas */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 12px !important;
    border: 1.5px solid rgba(0,0,0,0.12) !important;
    padding: 0.6rem 0.9rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #E8614F !important;
    box-shadow: 0 0 0 3px rgba(232, 97, 79, 0.12) !important;
}

/* Camera input */
.stCameraInput > div {
    border: 2px dashed rgba(232, 97, 79, 0.4) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}

/* Cards */
.yelnar-card {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,0.08);
    padding: 1.25rem 1.5rem;
    margin: 0.75rem 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}

/* Scan choice cards */
.scan-choice-card {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,0.08);
    padding: 2rem 1.5rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    transition: box-shadow 0.2s;
}
.scan-choice-card:hover {
    box-shadow: 0 6px 24px rgba(0,0,0,0.12);
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid rgba(0,0,0,0.06);
    margin: 1.5rem 0;
}

/* Progress bar override */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #E8614F, #F4845F) !important;
    border-radius: 9999px !important;
}
.stProgress > div > div {
    border-radius: 9999px !important;
    background: rgba(0,0,0,0.06) !important;
}

/* Chat input */
.stChatInput > div {
    border-radius: 9999px !important;
    border: 1.5px solid rgba(0,0,0,0.12) !important;
    background-color: #FFFFFF !important;
    color: #1A1A2E !important;
}
.stChatInput textarea,
.stChatInput > div > div,
.stChatInput > div > div > div,
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] > div {
    background-color: #FFFFFF !important;
    color: #1A1A2E !important;
}
.stChatInput textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: #9CA3AF !important;
    opacity: 1 !important;
}

/* Chat input floating bar background */
[data-testid="stBottomBlockContainer"] {
    background-color: #FFFFFF !important;
    border-top: 1px solid rgba(0,0,0,0.06) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #1A1A2E !important;
}

/* Main content padding */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 860px;
}

/* Auth pages: hide Streamlit's label gap when label_visibility=collapsed */
.stTextInput > label[data-testid="stWidgetLabel"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)


def inject_auth_css():
    """Called inside each auth view. Streamlit's virtual DOM removes this
    block when navigating away, so it never bleeds into non-auth pages."""
    st.markdown("""<style>
/* Reset BaseWeb outer container (removes dark frame) */
.stTextInput [data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid rgba(0,0,0,0.12) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    transition: border-color 0.2s !important;
}
.stTextInput [data-baseweb="input"]:focus-within {
    border-color: #E8614F !important;
    box-shadow: 0 0 0 3px rgba(232,97,79,0.12) !important;
}
/* The actual input element */
.stTextInput [data-baseweb="input"] input {
    background-color: #FFFFFF !important;
    color: #1A1A2E !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.95rem !important;
}
.stTextInput [data-baseweb="input"] input::placeholder {
    color: #9CA3AF !important;
    opacity: 1 !important;
}
/* Kill browser autofill grey/blue tint */
.stTextInput [data-baseweb="input"] input:-webkit-autofill,
.stTextInput [data-baseweb="input"] input:-webkit-autofill:hover,
.stTextInput [data-baseweb="input"] input:-webkit-autofill:focus,
.stTextInput [data-baseweb="input"] input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
    -webkit-text-fill-color: #1A1A2E !important;
    caret-color: #1A1A2E !important;
    transition: background-color 9999s ease-in-out 0s !important;
}
/* Eye icon — white background, grey icon */
.stTextInput [data-baseweb="input"] button,
.stTextInput [data-baseweb="input"] [data-testid="stPasswordToggle"],
.stTextInput [data-baseweb="input"] > div:last-child {
    background-color: #FFFFFF !important;
    border: none !important;
    color: #6B7280 !important;
}
.stTextInput [data-baseweb="input"] button svg,
.stTextInput [data-baseweb="input"] button path {
    fill: #6B7280 !important;
    color: #6B7280 !important;
    stroke: none !important;
}

/* ✦ Эмоционалды Интеллект brand colour — solid, no gradient */
.stFormSubmitButton > button {
    background: #E8614F !important;
    background-image: none !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    box-shadow: none !important;
    padding: 0.72rem 1.5rem !important;
}
.stFormSubmitButton > button:hover {
    background: #d4503e !important;
    transform: none !important;
    box-shadow: 0 4px 14px rgba(232,97,79,0.30) !important;
}
</style>""", unsafe_allow_html=True)


inject_css()

# ── Session state ──────────────────────────────────────────────────────────────
if "current_view" not in st.session_state:
    st.session_state.current_view = "login"
if "emotion_history" not in st.session_state:
    st.session_state.emotion_history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "show_all_history" not in st.session_state:
    st.session_state.show_all_history = False
# Auth state
if "token" not in st.session_state:
    st.session_state.token = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = None

# ── Query-param routing (password reset link) ──────────────────────────────────
_qp = st.query_params
if _qp.get("view") == "reset_password" and _qp.get("token"):
    st.session_state.current_view = "reset_password"
    st.session_state._reset_token = _qp.get("token")


# ── Helpers ────────────────────────────────────────────────────────────────────
def nav_to(view: str):
    st.session_state.current_view = view
    st.rerun()


def logout():
    st.session_state.token = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.user_id = None
    st.session_state.chat_session_id = None
    st.session_state.messages = []
    st.session_state.conversations = []
    st.session_state.emotion_history = []
    st.session_state.last_result = None
    nav_to("login")


# ── Auth guard ─────────────────────────────────────────────────────────────────
_PUBLIC_VIEWS = {"login", "signup", "forgot_password", "reset_password"}
if st.session_state.token is None and st.session_state.current_view not in _PUBLIC_VIEWS:
    st.session_state.current_view = "login"
    st.rerun()


# ── HTML helpers ───────────────────────────────────────────────────────────────
def card_html(content: str, border_color: str = "rgba(0,0,0,0.08)") -> str:
    return f"""<div class="yelnar-card" style="border-left: 4px solid {border_color};">
{content}
</div>"""


def emotion_badge_html(emotion: str, level: str) -> str:
    color = EMOTION_COLORS.get(emotion, "#A0AEC0")
    icon = EMOTION_ICONS.get(emotion, "◉")
    kaz = EMOTION_KAZAKH.get(emotion, emotion.capitalize())
    lev_kaz = LEVEL_KAZAKH.get(level, level)
    return f"""<div style="display:inline-flex;align-items:center;gap:8px;
        background:rgba(0,0,0,0.04);border-radius:9999px;
        padding:6px 14px;border:1px solid {color}40;">
        <span style="color:{color};font-size:1.1rem;">{icon}</span>
        <span style="font-weight:600;color:{color};">{kaz}</span>
        <span style="color:#6B7280;font-size:0.85rem;">· {lev_kaz}</span>
    </div>"""


def confidence_bar_html(confidence: float) -> str:
    pct = int(confidence * 100)
    color = "#4ECDC4" if pct >= 75 else "#F4845F" if pct >= 50 else "#E8614F"
    return f"""<div style="margin:1rem 0;">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:0.85rem;color:#6B7280;font-weight:500;">Деңгейі</span>
            <span style="font-size:0.85rem;font-weight:700;color:{color};">{pct}%</span>
        </div>
        <div style="background:rgba(0,0,0,0.06);border-radius:9999px;height:8px;overflow:hidden;">
            <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{color},{color}CC);
                border-radius:9999px;transition:width 0.6s ease;"></div>
        </div>
    </div>"""


def recommendation_card_html(index: int, text: str) -> str:
    return f"""<div style="display:flex;gap:14px;align-items:flex-start;
        padding:14px 16px;margin:8px 0;
        background:#FFFFFF;border-radius:12px;
        border:1px solid rgba(0,0,0,0.07);
        border-left:4px solid #E8614F;
        box-shadow:0 1px 6px rgba(0,0,0,0.05);">
        <span style="background:linear-gradient(135deg,#E8614F,#F4845F);color:white;
            border-radius:9999px;width:26px;height:26px;display:flex;align-items:center;
            justify-content:center;font-size:0.8rem;font-weight:700;flex-shrink:0;">{index}</span>
        <span style="color:#1A1A2E;line-height:1.5;font-size:0.95rem;">{text}</span>
    </div>"""


def history_card_html(entry: dict) -> str:
    result = entry["result"]
    emotion = result["emotion"]
    color = EMOTION_COLORS.get(emotion, "#A0AEC0")
    icon = EMOTION_ICONS.get(emotion, "◉")
    kaz = EMOTION_KAZAKH.get(emotion, emotion.capitalize())
    level_kaz = LEVEL_KAZAKH.get(result["level"], result["level"])
    ts = entry["timestamp"]
    return f"""<div style="display:flex;align-items:center;gap:14px;
        padding:14px 16px;margin:6px 0;
        background:#FFFFFF;border-radius:12px;
        border:1px solid rgba(0,0,0,0.08);
        border-left:4px solid {color};
        box-shadow:0 1px 6px rgba(0,0,0,0.05);">
        <span style="color:{color};font-size:1.4rem;">{icon}</span>
        <div style="flex:1;">
            <div style="font-weight:600;color:#1A1A2E;">{kaz}
                <span style="font-weight:400;color:#6B7280;margin-left:6px;font-size:0.85rem;">· {level_kaz}</span>
            </div>
            <div style="font-size:0.8rem;color:#6B7280;margin-top:2px;">{ts}</div>
        </div>
    </div>"""


def emotion_hero_html(emotion: str, level: str) -> str:
    color = EMOTION_COLORS.get(emotion, "#A0AEC0")
    icon = EMOTION_ICONS.get(emotion, "◉")
    kaz = EMOTION_KAZAKH.get(emotion, emotion.capitalize())
    level_kaz = LEVEL_KAZAKH.get(level, level)
    return f"""<div style="background:linear-gradient(135deg,{color}22,{color}11);
        border-radius:20px;padding:2.5rem 2rem;text-align:center;
        border:1px solid {color}30;margin-bottom:1.5rem;">
        <div style="font-size:3.5rem;margin-bottom:0.5rem;color:{color};">{icon}</div>
        <div style="font-size:2rem;font-weight:700;color:{color};">{kaz}</div>
        <div style="font-size:1rem;color:#6B7280;margin-top:6px;font-weight:500;">{level_kaz} қарқындылық</div>
    </div>"""


# ── Nav button ──────────────────────────────────────────────────────────────────
def render_nav_button(label: str, view_name: str):
    active = st.session_state.current_view == view_name or (
        view_name == "scan_choose" and st.session_state.current_view in ("scan_face", "scan_text")
    )
    if active:
        st.markdown('<div class="nav-active">', unsafe_allow_html=True)
    if st.button(label, key=f"nav_{view_name}", use_container_width=True):
        nav_to(view_name)
    if active:
        st.markdown("</div>", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar():
    # On auth pages, hide the sidebar entirely via CSS
    if st.session_state.current_view in _PUBLIC_VIEWS:
        st.markdown(
            "<style>[data-testid='stSidebar']{display:none!important;}"
            "[data-testid='stSidebarCollapsedControl']{display:none!important;}</style>",
            unsafe_allow_html=True,
        )
        return

    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:0 0 1.5rem;'>"
            "<span style='font-size:1.6rem;font-weight:700;color:#E8614F;'>✦ Эмоционалды Интеллект</span><br>"
            "<span style='font-size:0.8rem;color:#6B7280;'>Эмоционалды AI көмекші</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.token is None:
            # Logged-out sidebar (shouldn't normally show due to guard, but just in case)
            if st.button("Кіру", key="sb_login", use_container_width=True, type="primary"):
                nav_to("login")
            if st.button("Тіркелу", key="sb_signup", use_container_width=True):
                nav_to("signup")
        else:
            # Logged-in greeting
            name = st.session_state.user_name or "Қолданушы"
            st.markdown(
                f"<div style='text-align:center;margin-bottom:1rem;"
                f"padding:0.75rem;background:rgba(232,97,79,0.06);"
                f"border-radius:12px;border:1px solid rgba(232,97,79,0.15);'>"
                f"<span style='font-weight:600;color:#E8614F;'>Сәлем, {name}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            render_nav_button("○  Басты бет", "dashboard")
            render_nav_button("◎  Сканерлеу", "scan_choose")
            render_nav_button("△  Чат", "chat")
            render_nav_button("≡  Тарих", "history")
            render_nav_button("◑  Профиль", "profile")

            st.markdown("<hr>", unsafe_allow_html=True)
            if st.button("Шығу", key="sb_logout", use_container_width=True):
                logout()

            st.markdown(
                "<div style='margin-top:1.5rem;padding:0.9rem 1rem;"
                "background:#FFF5F4;border-radius:12px;"
                "border:1px solid rgba(232,97,79,0.18);'>"
                "<div style='font-size:0.78rem;font-weight:700;color:#E8614F;margin-bottom:4px;'>"
                "Техникалық қолдау</div>"
                "<div style='font-size:0.78rem;color:#6B7280;line-height:1.5;'>"
                "Сұрақтар бойынша "
                "<a href='https://t.me/zar1nnass' target='_blank' "
                "style='color:#E8614F;font-weight:600;text-decoration:none;'>@zar1nnass</a>"
                " Telegram арқылы хабарласыңыз.</div>"
                "</div>",
                unsafe_allow_html=True,
            )


render_sidebar()


# ── Auth Views ─────────────────────────────────────────────────────────────────
def view_login():
    inject_auth_css()
    _, col, _ = st.columns([1.5, 1, 1.5])
    with col:
        st.markdown(
            "<div style='text-align:center;padding:2rem 0 1.5rem;'>"
            "<div style='font-size:2rem;font-weight:800;color:#E8614F;letter-spacing:-1px;'>✦ Эмоционалды Интеллект</div>"
            "<div style='font-size:0.9rem;color:#6B7280;margin-top:4px;'>Аккаунтыңызға кіріңіз</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="email@example.com", label_visibility="collapsed")
            password = st.text_input("Құпиясөз", type="password", placeholder="Құпиясөз", label_visibility="collapsed")
            submitted = st.form_submit_button("Кіру", type="primary", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Email мен құпиясөзді енгізіңіз.")
            else:
                try:
                    resp = requests.post(
                        f"{API_URL}/auth/login",
                        json={"email": email, "password": password},
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.user_id = data["user_id"]
                        st.session_state.user_name = data["name"]
                        st.session_state.user_email = data["email"]
                        nav_to("dashboard")
                    else:
                        st.error(resp.json().get("detail", "Кіру сәтсіз болды."))
                except requests.exceptions.ConnectionError:
                    st.error("Серверге қосыла алмады.")

        st.markdown(
            "<div style='text-align:center;margin-top:0.5rem;'>",
            unsafe_allow_html=True,
        )
        if st.button("Құпиясөзді ұмыттым?", use_container_width=True, key="login_forgot"):
            nav_to("forgot_password")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;font-size:0.9rem;color:#6B7280;margin-bottom:0.5rem;'>"
            "Аккаунтыңыз жоқ па?</div>",
            unsafe_allow_html=True,
        )
        if st.button("Тіркелу", use_container_width=True, key="login_to_signup"):
            nav_to("signup")

        st.markdown(
            "<div style='margin-top:1.5rem;padding:1rem 1.1rem;background:#FFF5F4;border-radius:16px;"
            "border:1px solid rgba(232,97,79,0.18);'>"
            "<div style='font-weight:700;color:#E8614F;margin-bottom:5px;font-size:0.88rem;text-align:center;'>"
            "Техникалық қолдау</div>"
            "<div style='color:#6B7280;font-size:0.82rem;line-height:1.55;text-align:center;'>"
            "Техникалық мәселелер бойынша "
            "<a href='https://t.me/zar1nnass' target='_blank' "
            "style='color:#E8614F;font-weight:600;text-decoration:none;'>@zar1nnass</a>"
            " Telegram арқылы хабарласыңыз."
            "</div></div>",
            unsafe_allow_html=True,
        )


def view_signup():
    inject_auth_css()
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            "<div style='text-align:center;padding:2rem 0 1.5rem;'>"
            "<div style='font-size:2rem;font-weight:800;color:#E8614F;letter-spacing:-1px;'>✦ Эмоционалды Интеллект</div>"
            "<div style='font-size:0.9rem;color:#6B7280;margin-top:4px;'>Жаңа аккаунт жасаңыз</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        with st.form("signup_form"):
            name = st.text_input("Аты-жөні", placeholder="Аты-жөніңіз", label_visibility="collapsed")
            email = st.text_input("Email", placeholder="email@example.com", label_visibility="collapsed")
            password = st.text_input("Құпиясөз", type="password", placeholder="Құпиясөз (кемінде 8 таңба)", label_visibility="collapsed")
            password2 = st.text_input("Растау", type="password", placeholder="Құпиясөзді растаңыз", label_visibility="collapsed")
            submitted = st.form_submit_button("Тіркелу", type="primary", use_container_width=True)

        if submitted:
            if not name or not email or not password:
                st.error("Барлық өрістерді толтырыңыз.")
            elif password != password2:
                st.error("Құпиясөздер сәйкес келмейді.")
            elif len(password) < 8:
                st.error("Құпиясөз кемінде 8 таңба болуы керек.")
            else:
                try:
                    resp = requests.post(
                        f"{API_URL}/auth/register",
                        json={"email": email, "name": name, "password": password},
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.user_id = data["user_id"]
                        st.session_state.user_name = data["name"]
                        st.session_state.user_email = data["email"]
                        nav_to("dashboard")
                    else:
                        st.error(resp.json().get("detail", "Тіркелу сәтсіз болды."))
                except requests.exceptions.ConnectionError:
                    st.error("Серверге қосыла алмады.")

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;font-size:0.9rem;color:#6B7280;margin-bottom:0.5rem;'>"
            "Аккаунтыңыз бар ма?</div>",
            unsafe_allow_html=True,
        )
        if st.button("Кіру", use_container_width=True, key="signup_to_login"):
            nav_to("login")


def view_forgot_password():
    inject_auth_css()
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            "<div style='text-align:center;padding:2rem 0 1.5rem;'>"
            "<div style='font-size:2rem;font-weight:800;color:#E8614F;letter-spacing:-1px;'>✦ Эмоционалды Интеллект</div>"
            "<div style='font-size:0.9rem;color:#6B7280;margin-top:4px;'>Құпиясөзді қалпына келтіру</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-size:0.85rem;color:#6B7280;text-align:center;margin-bottom:1rem;'>"
            "Email мекенжайыңызды енгізіңіз — сілтеме жіберіледі.</div>",
            unsafe_allow_html=True,
        )

        with st.form("forgot_form"):
            email = st.text_input("Email", placeholder="email@example.com", label_visibility="collapsed")
            submitted = st.form_submit_button("Жіберу", type="primary", use_container_width=True)

        if submitted:
            if not email:
                st.error("Email енгізіңіз.")
            else:
                try:
                    resp = requests.post(
                        f"{API_URL}/auth/forgot-password",
                        json={"email": email},
                        timeout=15,
                    )
                    st.success(resp.json().get("message", "Хат жіберілді."))
                except requests.exceptions.ConnectionError:
                    st.error("Серверге қосыла алмады.")

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        if st.button("← Кіруге оралу", use_container_width=True, key="forgot_back"):
            nav_to("login")


def view_reset_password():
    inject_auth_css()
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            "<div style='text-align:center;padding:2rem 0 1.5rem;'>"
            "<div style='font-size:2rem;font-weight:800;color:#E8614F;letter-spacing:-1px;'>✦ Эмоционалды Интеллект</div>"
            "<div style='font-size:0.9rem;color:#6B7280;margin-top:4px;'>Жаңа құпиясөз орнатыңыз</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        reset_token = getattr(st.session_state, "_reset_token", "") or ""

        with st.form("reset_form"):
            new_password = st.text_input("Жаңа құпиясөз", type="password", placeholder="Жаңа құпиясөз (кемінде 8 таңба)", label_visibility="collapsed")
            new_password2 = st.text_input("Растау", type="password", placeholder="Құпиясөзді растаңыз", label_visibility="collapsed")
            submitted = st.form_submit_button("Сақтау", type="primary", use_container_width=True)

        if submitted:
            if not new_password or not new_password2:
                st.error("Барлық өрістерді толтырыңыз.")
            elif new_password != new_password2:
                st.error("Құпиясөздер сәйкес келмейді.")
            elif len(new_password) < 8:
                st.error("Құпиясөз кемінде 8 таңба болуы керек.")
            elif not reset_token:
                st.error("Сілтеме жарамсыз. Қайта сұраңыз.")
            else:
                try:
                    resp = requests.post(
                        f"{API_URL}/auth/reset-password",
                        json={"token": reset_token, "new_password": new_password},
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        st.success("Құпиясөз сәтті өзгертілді. Енді кіре аласыз.")
                        st.session_state._reset_token = None
                        st.query_params.clear()
                        nav_to("login")
                    else:
                        st.error(resp.json().get("detail", "Қате орын алды."))
                except requests.exceptions.ConnectionError:
                    st.error("Серверге қосыла алмады.")

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        if st.button("← Кіруге оралу", use_container_width=True, key="reset_back"):
            nav_to("login")


def view_profile():
    # White inputs + white eye-button background for this page
    st.markdown("""<style>
.stTextInput [data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid rgba(0,0,0,0.12) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}
.stTextInput [data-baseweb="input"]:focus-within {
    border-color: #E8614F !important;
    box-shadow: 0 0 0 3px rgba(232,97,79,0.12) !important;
}
.stTextInput [data-baseweb="input"] input {
    background-color: #FFFFFF !important;
    color: #1A1A2E !important;
}
.stTextInput [data-baseweb="input"] input::placeholder { color: #9CA3AF !important; }
.stTextInput [data-baseweb="input"] input:-webkit-autofill,
.stTextInput [data-baseweb="input"] input:-webkit-autofill:hover,
.stTextInput [data-baseweb="input"] input:-webkit-autofill:focus,
.stTextInput [data-baseweb="input"] input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
    -webkit-text-fill-color: #1A1A2E !important;
    caret-color: #1A1A2E !important;
    transition: background-color 9999s ease-in-out 0s !important;
}
.stTextInput [data-baseweb="input"] button,
.stTextInput [data-baseweb="input"] > div:last-child {
    background-color: #FFFFFF !important; border: none !important; color: #6B7280 !important;
}
.stTextInput [data-baseweb="input"] button svg,
.stTextInput [data-baseweb="input"] button path { fill: #6B7280 !important; }
</style>""", unsafe_allow_html=True)

    st.markdown(
        "<h1 style='font-size:1.8rem;font-weight:700;margin-bottom:0.25rem;'>◑ Профиль</h1>"
        "<p style='color:#6B7280;'>Аккаунт параметрлері</p>",
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([0.5, 2, 0.5])

    with col:
        st.markdown(
            f"<div class='yelnar-card'>"
            f"<div style='font-size:0.85rem;color:#6B7280;'>Email</div>"
            f"<div style='font-weight:600;'>{st.session_state.user_email or '—'}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("### Атын өзгерту")
        with st.form("profile_name_form"):
            new_name = st.text_input("Жаңа аты-жөні", value=st.session_state.user_name or "",
                                     placeholder="Аты-жөніңізді енгізіңіз")
            name_submitted = st.form_submit_button("Сақтау", type="primary")

    if name_submitted:
        if not new_name.strip():
            st.error("Аты-жөнін енгізіңіз.")
        else:
            try:
                resp = requests.patch(
                    f"{API_URL}/users/me",
                    json={"token": st.session_state.token, "name": new_name.strip()},
                    timeout=15,
                )
                if resp.status_code == 200:
                    st.session_state.user_name = resp.json()["name"]
                    st.success("Аты-жөні сәтті өзгертілді.")
                    st.rerun()
                else:
                    st.error(resp.json().get("detail", "Қате орын алды."))
            except requests.exceptions.ConnectionError:
                st.error("Серверге қосыла алмады.")

    _, col2, _ = st.columns([0.5, 2, 0.5])
    with col2:
        st.markdown("### Құпиясөзді өзгерту")
        with st.form("profile_password_form"):
            current_pw = st.text_input("Ағымдағы құпиясөз", type="password",
                                       placeholder="Қазіргі құпиясөзіңіз")
            new_pw = st.text_input("Жаңа құпиясөз", type="password",
                                   placeholder="Жаңа құпиясөз (кемінде 8 таңба)")
            new_pw2 = st.text_input("Растау", type="password",
                                    placeholder="Жаңа құпиясөзді қайта енгізіңіз")
            pw_submitted = st.form_submit_button("Сақтау", type="primary")

    if pw_submitted:
        if not current_pw or not new_pw or not new_pw2:
            st.error("Барлық өрістерді толтырыңыз.")
        elif new_pw != new_pw2:
            st.error("Жаңа құпиясөздер сәйкес келмейді.")
        elif len(new_pw) < 8:
            st.error("Құпиясөз кемінде 8 таңба болуы керек.")
        else:
            try:
                resp = requests.patch(
                    f"{API_URL}/users/me",
                    json={
                        "token": st.session_state.token,
                        "current_password": current_pw,
                        "new_password": new_pw,
                    },
                    timeout=15,
                )
                if resp.status_code == 200:
                    st.success("Құпиясөз сәтті өзгертілді.")
                else:
                    st.error(resp.json().get("detail", "Қате орын алды."))
            except requests.exceptions.ConnectionError:
                st.error("Серверге қосыла алмады.")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div style='padding:1.1rem 1.25rem;background:#FFF5F4;border-radius:16px;"
        "border:1px solid rgba(232,97,79,0.18);margin-bottom:1rem;'>"
        "<div style='font-weight:700;color:#E8614F;margin-bottom:6px;font-size:0.95rem;text-align:center;'>"
        "Техникалық қолдау</div>"
        "<div style='color:#6B7280;font-size:0.88rem;line-height:1.6;text-align:center;'>"
        "Техникалық мәселелер бойынша "
        "<a href='https://t.me/zar1nnass' target='_blank' "
        "style='color:#E8614F;font-weight:600;text-decoration:none;'>@zar1nnass</a>"
        " Telegram арқылы хабарласыңыз. Біздің мамандар сізге көмектесуге әрқашан дайын."
        "</div></div>",
        unsafe_allow_html=True,
    )

    if st.button("← Артқа"):
        nav_to("dashboard")


# ── Main App Views ─────────────────────────────────────────────────────────────
def view_dashboard():
    name = st.session_state.user_name or ""
    greeting = f"Сәлем, {name} ✦" if name else "Сәлем ✦"
    st.markdown(
        f"<h1 style='font-size:2rem;font-weight:700;margin-bottom:0.25rem;'>{greeting}</h1>"
        "<p style='color:#6B7280;font-size:1.05rem;margin-bottom:1.5rem;'>"
        "Бүгін өзіңізді қалай сезінесіз?</p>",
        unsafe_allow_html=True,
    )

    if st.button("✦  Эмоцияны сканерлеу", type="primary", use_container_width=True):
        nav_to("scan_choose")

    # Load from API if logged in
    history = _load_history_from_api()

    if not history:
        st.markdown(
            card_html(
                "<div style='text-align:center;padding:1rem 0;color:#6B7280;'>"
                "Сканерлеу жоқ. <strong>Эмоцияны сканерлеу</strong> батырмасын басыңыз!</div>"
            ),
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        "<h3 style='font-size:1.1rem;font-weight:600;margin:1.5rem 0 0.5rem;'>"
        "Соңғы сканерлеулер</h3>",
        unsafe_allow_html=True,
    )
    for entry in history[:3]:
        st.markdown(history_card_html(entry), unsafe_allow_html=True)

    if len(history) >= 2:
        st.markdown(
            "<h3 style='font-size:1.1rem;font-weight:600;margin:1.5rem 0 0.5rem;'>"
            "Эмоция үрдісі</h3>",
            unsafe_allow_html=True,
        )
        import pandas as pd
        level_map = {"low": 1, "medium": 2, "high": 3}
        df = pd.DataFrame([
            {"уақыт": e["timestamp"], "қарқындылық": level_map.get(e["result"]["level"], 2)}
            for e in reversed(history)
        ])
        df = df.set_index("уақыт")
        st.line_chart(df[["қарқындылық"]])


def _load_history_from_api() -> list[dict]:
    """Fetch emotion scan history from API; fall back to session state."""
    token = st.session_state.token
    if not token:
        return st.session_state.emotion_history

    try:
        resp = requests.get(
            f"{API_URL}/history/scans",
            params={"token": token},
            timeout=10,
        )
        if resp.status_code == 200:
            records = resp.json()
            history = []
            for r in records:
                ts = r.get("scanned_at", "")
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    # SQLite returns naive datetimes — assume UTC
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    ts_fmt = dt.astimezone(ALMATY_TZ).strftime("%d.%m.%Y %H:%M")
                except Exception:
                    ts_fmt = ts
                history.append({
                    "timestamp": ts_fmt,
                    "scan_method": r["scan_method"],
                    "result": {
                        "emotion": r["emotion"],
                        "level": r["level"],
                        "confidence": r["confidence"],
                        "analysis": r["analysis"],
                        "recommendations": r["recommendations"],
                        "mental_health_note": r.get("mental_health_note"),
                    },
                })
            return history
    except Exception:
        pass
    return st.session_state.emotion_history


def view_scan_choose():
    st.markdown(
        "<h1 style='font-size:1.8rem;font-weight:700;margin-bottom:0.25rem;'>◎ Сканерлеу</h1>"
        "<p style='color:#6B7280;'>Эмоцияңызды бөлісу тәсілін таңдаңыз:</p>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "<div class='scan-choice-card'>"
            "<div style='margin-bottom:0.75rem;display:flex;justify-content:center;'>"
            "<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 24 24' fill='none' stroke='#E8614F' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'>"
            "<path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/>"
            "<circle cx='12' cy='13' r='4'/></svg></div>"
            "<div style='font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;'>Камера</div>"
            "<div style='color:#6B7280;font-size:0.9rem;'>Бет-әлпетіңіздің фотосын түсіріп, AI-ға талдатыңыз</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Камераны пайдалану", type="primary", use_container_width=True, key="btn_face"):
            nav_to("scan_face")
    with col2:
        st.markdown(
            "<div class='scan-choice-card'>"
            "<div style='margin-bottom:0.75rem;display:flex;justify-content:center;'>"
            "<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 24 24' fill='none' stroke='#E8614F' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'>"
            "<path d='M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'/>"
            "<path d='M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'/></svg></div>"
            "<div style='font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;'>Мәтін</div>"
            "<div style='color:#6B7280;font-size:0.9rem;'>Сезімдеріңізді өз сөздеріңізбен сипаттаңыз</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Мәтін жазу", type="primary", use_container_width=True, key="btn_text"):
            nav_to("scan_text")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Артқа"):
        nav_to("dashboard")


def view_scan_face():
    st.markdown(
        "<h1 style='font-size:1.8rem;font-weight:700;margin-bottom:0.25rem;'>◎ Бет-әлпет сканері</h1>"
        "<p style='color:#6B7280;'>Бет-әлпетіңіздің фотосын түсіріңіз.</p>",
        unsafe_allow_html=True,
    )

    photo = st.camera_input("Фото түсіру")

    if photo is not None:
        if st.button("Эмоцияны талдау", type="primary", use_container_width=True):
            with st.spinner("Бет-әлпетіңіз талдануда..."):
                try:
                    files = {"file": (photo.name, photo.getvalue(), photo.type)}
                    data_fields = {}
                    if st.session_state.token:
                        data_fields["token"] = st.session_state.token
                    resp = requests.post(
                        f"{API_URL}/emotion/scan/face",
                        files=files,
                        data=data_fields,
                        timeout=60,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    st.session_state.last_result = data
                    st.session_state.emotion_history.insert(0, {
                        "timestamp": now_almaty().strftime("%d.%m.%Y %H:%M"),
                        "scan_method": data["scan_method"],
                        "result": data["result"],
                    })
                    nav_to("results")
                except requests.exceptions.ConnectionError:
                    st.error("Серверге қосыла алмады. `uv run python run.py` іске қосылғанын тексеріңіз.")
                except Exception as e:
                    st.error(f"Қате: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Артқа"):
        nav_to("scan_choose")


def view_scan_text():
    st.markdown(
        "<h1 style='font-size:1.8rem;font-weight:700;margin-bottom:0.25rem;'>◎ Мәтін сканері</h1>"
        "<p style='color:#6B7280;'>Қазір өзіңізді қалай сезінетіндігіңізді сипаттаңыз:</p>",
        unsafe_allow_html=True,
    )

    text = st.text_area(
        "Ойларыңыз",
        placeholder="Мысалы: Бүгін жұмыста өте шаршадым, кешке мазасыз болдым...",
        max_chars=2000,
        height=150,
        label_visibility="collapsed",
    )

    char_count = len(text) if text else 0
    st.markdown(
        f"<div style='text-align:right;font-size:0.8rem;color:#6B7280;margin-top:-8px;margin-bottom:8px;'>"
        f"{char_count}/2000</div>",
        unsafe_allow_html=True,
    )

    if st.button("Эмоцияны талдау", type="primary", use_container_width=True, disabled=not text):
        with st.spinner("Мәтін талдануда..."):
            try:
                payload = {"text": text}
                if st.session_state.token:
                    payload["token"] = st.session_state.token
                resp = requests.post(
                    f"{API_URL}/emotion/scan/text",
                    json=payload,
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                st.session_state.last_result = data
                st.session_state.emotion_history.insert(0, {
                    "timestamp": now_almaty().strftime("%d.%m.%Y %H:%M"),
                    "scan_method": data["scan_method"],
                    "result": data["result"],
                })
                nav_to("results")
            except requests.exceptions.ConnectionError:
                st.error("Серверге қосыла алмады. `uv run python run.py` іске қосылғанын тексеріңіз.")
            except Exception as e:
                st.error(f"Қате: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Артқа"):
        nav_to("scan_choose")


def view_results():
    if not st.session_state.last_result:
        nav_to("dashboard")
        return

    data = st.session_state.last_result
    result = data["result"]
    emotion = result["emotion"]
    level = result["level"]
    confidence = result["confidence"]
    analysis = result["analysis"]
    recommendations = result["recommendations"]
    mental_health_note = result.get("mental_health_note")

    # Hero card
    st.markdown(emotion_hero_html(emotion, level), unsafe_allow_html=True)

    # Confidence bar
    st.markdown(confidence_bar_html(confidence), unsafe_allow_html=True)

    # Metadata row
    col1, col2, col3 = st.columns(3)
    camera_svg = "<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='#E8614F' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/><circle cx='12' cy='13' r='4'/></svg>"
    text_svg = "<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='#E8614F' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><path d='M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'/><path d='M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'/></svg>"
    method_icon = camera_svg if data["scan_method"] == "face" else text_svg
    method_kaz = "Камера" if data["scan_method"] == "face" else "Мәтін"
    with col1:
        st.markdown(
            f"<div style='text-align:center;padding:12px;background:#F9F7F5;border-radius:12px;'>"
            f"<div style='display:flex;justify-content:center;margin-bottom:4px;'>{method_icon}</div>"
            f"<div style='font-size:0.78rem;color:#6B7280;margin-top:4px;'>Сканерлеу әдісі</div>"
            f"<div style='font-weight:600;font-size:0.9rem;'>{method_kaz}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div style='text-align:center;padding:12px;background:#F9F7F5;border-radius:12px;'>"
            f"<div style='display:flex;justify-content:center;margin-bottom:4px;'>"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='#E8614F' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'>"
            f"<line x1='18' y1='20' x2='18' y2='10'/><line x1='12' y1='20' x2='12' y2='4'/><line x1='6' y1='20' x2='6' y2='14'/><line x1='2' y1='20' x2='22' y2='20'/>"
            f"</svg></div>"
            f"<div style='font-size:0.78rem;color:#6B7280;margin-top:4px;'>Деңгейі</div>"
            f"<div style='font-weight:600;font-size:0.9rem;'>{int(confidence * 100)}%</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col3:
        ts = now_almaty().strftime("%d.%m %H:%M")
        if st.session_state.emotion_history:
            ts = st.session_state.emotion_history[0]["timestamp"]
        st.markdown(
            f"<div style='text-align:center;padding:12px;background:#F9F7F5;border-radius:12px;'>"
            f"<div style='display:flex;justify-content:center;margin-bottom:4px;'>"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='#E8614F' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'>"
            f"<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>"
            f"</svg></div>"
            f"<div style='font-size:0.78rem;color:#6B7280;margin-top:4px;'>Уақыт</div>"
            f"<div style='font-weight:600;font-size:0.9rem;'>{ts}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Analysis card
    color = EMOTION_COLORS.get(emotion, "#A0AEC0")
    st.markdown(
        "<h3 style='font-size:1.05rem;font-weight:600;margin-bottom:0.5rem;'>Талдау</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        card_html(f"<p style='color:#1A1A2E;line-height:1.6;margin:0;'>{analysis}</p>", color),
        unsafe_allow_html=True,
    )

    # Recommendations
    st.markdown(
        "<h3 style='font-size:1.05rem;font-weight:600;margin:1.25rem 0 0.5rem;'>Ұсыныстар</h3>",
        unsafe_allow_html=True,
    )
    for i, rec in enumerate(recommendations, 1):
        st.markdown(recommendation_card_html(i, rec), unsafe_allow_html=True)

    # Mental health note
    if mental_health_note:
        st.markdown(
            f"<div style='background:rgba(232,97,79,0.08);border-radius:12px;"
            f"border:1px solid rgba(232,97,79,0.3);padding:16px 20px;margin:1rem 0;'>"
            f"<div style='font-weight:700;color:#E8614F;margin-bottom:6px;'>⚠ Психикалық денсаулық ескертуі</div>"
            f"<div style='color:#1A1A2E;line-height:1.5;'>{mental_health_note}</div>"
            f"<div style='color:#6B7280;font-size:0.85rem;margin-top:8px;'>"
            f"Дағдарыс жағдайында кәсіби маманға немесе дағдарыс желісіне хабарласыңыз.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("△  Чат", type="primary", use_container_width=True):
            nav_to("chat")
    with col_b:
        if st.button("◎  Жаңа сканерлеу", use_container_width=True):
            nav_to("scan_choose")
    with col_c:
        if st.button("○  Басты бет", use_container_width=True):
            nav_to("dashboard")


def view_chat():
    st.markdown(
        "<h1 style='font-size:1.8rem;font-weight:700;margin-bottom:0.25rem;'>△ Чат</h1>"
        "<p style='color:#6B7280;'>AI серіктесіңізбен сезімдеріңізді бөлісіңіз</p>",
        unsafe_allow_html=True,
    )

    # Load past sessions in sidebar (when logged in)
    token = st.session_state.token
    if token:
        with st.sidebar:
            st.markdown("---")
            st.markdown(
                "<div style='font-size:0.85rem;font-weight:600;color:#6B7280;margin-bottom:0.5rem;'>"
                "Өткен әңгімелер</div>",
                unsafe_allow_html=True,
            )
            if st.button("＋ Жаңа әңгіме", key="new_chat_btn", use_container_width=True):
                _start_new_chat_session()
            try:
                resp = requests.get(
                    f"{API_URL}/chat-sessions",
                    params={"token": token},
                    timeout=10,
                )
                if resp.status_code == 200:
                    sessions = resp.json()
                    for s in sessions[:10]:
                        label = s["title"][:30] + ("…" if len(s["title"]) > 30 else "")
                        is_active = st.session_state.chat_session_id == s["id"]
                        btn_key = f"sess_{s['id']}"
                        if is_active:
                            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
                        if st.button(label, key=btn_key, use_container_width=True):
                            _load_chat_session(s["id"])
                        if is_active:
                            st.markdown("</div>", unsafe_allow_html=True)
            except Exception:
                pass

    if st.session_state.last_result:
        result = st.session_state.last_result["result"]
        emotion = result["emotion"]
        level = result["level"]
        st.markdown(
            f"<div style='margin-bottom:1rem;'>{emotion_badge_html(emotion, level)}</div>",
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Сезімдеріңізбен бөлісіңіз..."):
        # Ensure a DB session exists when logged in
        if token and not st.session_state.chat_session_id:
            _start_new_chat_session()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Ойланып жатыр..."):
                try:
                    payload = {
                        "thread_id": st.session_state.thread_id,
                        "message": prompt,
                    }
                    if token and st.session_state.chat_session_id:
                        payload["token"] = token
                        payload["session_id"] = st.session_state.chat_session_id
                    resp = requests.post(
                        f"{API_URL}/chat",
                        json=payload,
                        timeout=60,
                    )
                    resp.raise_for_status()
                    answer = resp.json()["response"]
                except requests.exceptions.ConnectionError:
                    answer = "Серверге қосыла алмады. `uv run python run.py` іске қосылғанын тексеріңіз."
                except Exception as e:
                    answer = f"Қате: {e}"

            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})


def _start_new_chat_session():
    token = st.session_state.token
    if not token:
        return
    try:
        resp = requests.post(
            f"{API_URL}/chat-sessions",
            json={"token": token},
            timeout=10,
        )
        if resp.status_code == 200:
            session_id = resp.json()["id"]
            st.session_state.chat_session_id = session_id
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
    except Exception:
        pass


def _load_chat_session(session_id: str):
    token = st.session_state.token
    if not token:
        return
    try:
        resp = requests.get(
            f"{API_URL}/chat-sessions/{session_id}/messages",
            params={"token": token},
            timeout=10,
        )
        if resp.status_code == 200:
            msgs = resp.json()
            st.session_state.chat_session_id = session_id
            st.session_state.messages = [
                {"role": m["role"], "content": m["content"]} for m in msgs
            ]
            st.rerun()
    except Exception:
        pass


def view_history():
    st.markdown(
        "<h1 style='font-size:1.8rem;font-weight:700;margin-bottom:0.25rem;'>≡ Тарих</h1>"
        "<p style='color:#6B7280;'>Барлық сканерлеу нәтижелері</p>",
        unsafe_allow_html=True,
    )

    history = _load_history_from_api()

    if not history:
        st.markdown(
            card_html(
                "<div style='text-align:center;padding:1rem 0;color:#6B7280;'>"
                "Сканерлеу жоқ. Алдымен эмоцияны сканерлеп көріңіз!</div>"
            ),
            unsafe_allow_html=True,
        )
    else:
        for entry in history:
            st.markdown(history_card_html(entry), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⌫  Барлығын тазарту", use_container_width=True):
            token = st.session_state.token
            if token:
                try:
                    requests.delete(
                        f"{API_URL}/history/scans",
                        params={"token": token},
                        timeout=10,
                    )
                except Exception:
                    pass
            st.session_state.emotion_history = []
            st.session_state.last_result = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Артқа"):
        nav_to("dashboard")


# ── Router ─────────────────────────────────────────────────────────────────────
view = st.session_state.current_view

if view == "login":
    view_login()
elif view == "signup":
    view_signup()
elif view == "forgot_password":
    view_forgot_password()
elif view == "reset_password":
    view_reset_password()
elif view == "profile":
    view_profile()
elif view == "dashboard":
    view_dashboard()
elif view == "scan_choose":
    view_scan_choose()
elif view == "scan_face":
    view_scan_face()
elif view == "scan_text":
    view_scan_text()
elif view == "results":
    view_results()
elif view == "chat":
    view_chat()
elif view == "history":
    view_history()
else:
    nav_to("dashboard")
