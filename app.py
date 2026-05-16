import streamlit as st
import google.generativeai as genai

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Throwball Trainer 2026",
    page_icon="🏐",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

.hero {
    text-align: center;
    padding: 2rem 1rem 1rem;
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #f7971e, #ffd200);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero p { color: #b0aed0; font-size: 1.05rem; }

.mode-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    color: #e0deff;
    transition: border-color 0.2s;
}
.mode-card:hover { border-color: #f7971e; }
.mode-card strong { color: #ffd200; }

.chat-user {
    background: rgba(247,151,30,0.18);
    border-left: 3px solid #f7971e;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0;
    color: #ffe8c0;
}
.chat-ai {
    background: rgba(255,255,255,0.07);
    border-left: 3px solid #a78bfa;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0;
    color: #e0deff;
}
.stButton > button {
    background: linear-gradient(90deg, #f7971e, #ffd200);
    color: #1a1a2e;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.6rem;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

.stTextInput > div > input, .stTextArea > div > textarea {
    background: rgba(255,255,255,0.08) !important;
    color: #e0deff !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
}
.stSelectbox > div { background: rgba(255,255,255,0.07) !important; }
label, .stRadio label { color: #c9c7e8 !important; }
.stTextInput label, .stTextArea label { color: #c9c7e8 !important; }
</style>
""", unsafe_allow_html=True)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert throwball coach and rules referee. Your ENTIRE knowledge base is the Throwball Rules 2026 below. You NEVER make up rules — you only cite what is in this document.

=== THROWBALL RULES 2026 ===
TEAM COMPOSITION
* 9 players on court, up to 3 substitutes.
* Substitutions with referee permission when ball is not in play.

OBJECTIVE
* Score by throwing the ball into opponent's court in a way they fail to catch and return.

COURT
* Length: 18m (59ft), Width: 12.2m (35–40ft)
* Net height (women): 2.2m (7.2ft)
* Neutral zone: 1m wide on both sides of net
* Service zone: 7ft from net toward back boundary

GAME RULES
1. Toss decides who serves. Serve is one-handed, within 5 seconds of whistle, from 7ft inside the service zone.
2. Server must not touch boundary lines. Ball must clear the net without touching it and land in opponent's court.
3. Ball must be caught cleanly with both hands (body touch and juggling allowed). Same player must throw within 3 seconds. No two players may catch simultaneously.
4. Throws must be one-handed. No pushing, lifting, or slinging. Ball must not touch net or go out of bounds.
5. After gaining serve, team rotates in Z-shape: 1→2→3, then 6→5→4, then 7→8→9→(back to 1). All 9 players rotate including server, through front and back zones.
6. Max 3 substitutions per team per game. Only when ball is dead. A substituted player may re-enter once per set.
7. Rally point system. Set played to 15 or 21 points. 2-point lead required to win. Match = 1 set.

FAULTS (point to opponent)
* Ball touches ground, goes out, or hits net
* Improper catch (one-handed)
* Improper throw (not one-handed)
* Holding ball more than 3 seconds
* Crossing center line or touching net
* Multiple players touching ball simultaneously
=== END OF RULES ===

You are a friendly, encouraging coach. When correcting a wrong answer, always cite the specific rule.

MODES:
1 RULES — Answer any question about the rules precisely.
2 QUIZ — Ask 5 random multiple-choice or true/false questions one at a time. After all 5, give a score and highlight areas to review.
3 SCENARIO — Describe a realistic game situation and ask the player what the correct ruling is. Give feedback after their answer.
4 ROTATION — Describe current player positions (1–9 on a 3×3 grid) and ask where each player moves on next Z-rotation. Confirm or correct.
5 FAULT JUDGE — Describe a play and ask: "Fault or no fault?" Give the rule reference after each answer.

Always be concise, friendly, and encouraging.
"""

# ── Gemini setup ──────────────────────────────────────────────────────────────
def get_model():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        st.error("⚠️ The GEMINI_API_KEY is missing! Please configure it in `.streamlit/secrets.toml`.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = None
if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.chat = None

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🏐 Throwball Trainer 2026</h1>
  <p>Your AI rules coach — powered by the official 2026 rulebook</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Setup ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 Training Modes")
    modes = {
        "1 📖 Rules Q&A": "1",
        "2 🧠 Quiz (5 questions)": "2",
        "3 🎮 Scenario Ruling": "3",
        "4 🔄 Rotation Drill": "4",
        "5 🚨 Fault Judge": "5",
    }
    selected_label = st.radio("Pick a mode", list(modes.keys()), index=None)

    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.chat = None
        st.session_state.mode = None
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<small style='color:#6b6a8a'>Built with ❤️ using Gemini & Streamlit</small>",
        unsafe_allow_html=True,
    )

# ── Mode launch ───────────────────────────────────────────────────────────────
GREET_MAP = {
    "1": "I'm in **Rules Q&A** mode! Ask me anything about the Throwball 2026 rules — court dimensions, faults, substitutions, you name it. What's your question?",
    "2": "Let's do a **Quiz**! I'll ask you 5 questions one at a time. Ready? Here's Question 1:",
    "3": "Time for a **Scenario**! I'll describe a real game situation and you tell me the correct ruling. Let's go:",
    "4": "**Rotation Drill** time! I'll show you player positions and you tell me where everyone moves in the next Z-rotation. Ready?",
    "5": "Welcome to **Fault Judge**! I'll describe a play and you call it — Fault or No Fault? First play coming up:",
}

if selected_label and modes[selected_label] != st.session_state.mode:
    new_mode = modes[selected_label]
    st.session_state.mode = new_mode
    st.session_state.messages = []
    st.session_state.chat = None

# ── Show mode cards if no mode selected ───────────────────────────────────────
if not st.session_state.mode:
    st.markdown("""
<div class="mode-card"><strong>1 📖 Rules Q&A</strong> — Ask anything about the rulebook</div>
<div class="mode-card"><strong>2 🧠 Quiz</strong> — 5 MCQ/T-F questions with a final score</div>
<div class="mode-card"><strong>3 🎮 Scenario</strong> — Real game situations, you make the call</div>
<div class="mode-card"><strong>4 🔄 Rotation</strong> — Drill the Z-shape rotation</div>
<div class="mode-card"><strong>5 🚨 Fault Judge</strong> — Fault or No Fault?</div>
<br><p style='color:#8886aa;text-align:center'>← Pick a mode from the sidebar to begin</p>
""", unsafe_allow_html=True)
    st.stop()

# (API key validation is now handled in get_model)

# ── Init chat session ─────────────────────────────────────────────────────────
if st.session_state.chat is None:
    try:
        model = get_model()
        st.session_state.chat = model.start_chat(history=[])
        # Send mode-init message
        init_msg = f"The player selected mode {st.session_state.mode}. {GREET_MAP[st.session_state.mode]} Begin immediately."
        response = st.session_state.chat.send_message(init_msg)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"❌ Could not connect to Gemini: {e}")
        st.stop()

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-ai">🏐 {msg["content"]}</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Your answer / question:", placeholder="Type here and press Enter…")
    submitted = st.form_submit_button("Send ➤")

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    try:
        response = st.session_state.chat.send_message(user_input.strip())
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Error: {e}"})
    st.rerun()
