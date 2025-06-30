import streamlit as st
from state.state import AgentState, app
from langchain_core.messages import HumanMessage, AIMessage
import re

# Custom CSS for ChatGPT-like look, category badges, glossy spinner, Bebas Neue font, and LinkedIn background logo
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
    body, .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #2c5364 100%) !important;
        color: #f0f6fc !important;
    }
    .bebas-header {
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 2.8rem;
        letter-spacing: 2px;
        color: #aee1fb;
        text-align: center;
        margin-bottom: 0.1em;
        margin-top: 0.2em;
    }
    .bebas-subheader {
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 1.35rem;
        letter-spacing: 1px;
        color: #7ecfff;
        text-align: center;
        margin-bottom: 1.2em;
        margin-top: 0.1em;
    }
    .chat-container {
        max-width: 700px;
        margin: 0 auto;
        padding-bottom: 80px;
    }
    .chat-bubble {
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 18px;
        max-width: 80%;
        word-break: break-word;
        font-size: 1.1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        position: relative;
    }
    .user-bubble {
        background: #22304a;
        color: #aee1fb;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        border-top-right-radius: 18px;
        border-top-left-radius: 18px;
        border-bottom-left-radius: 18px;
    }
    .assistant-bubble {
        background: #16202a;
        color: #f0f6fc;
        margin-right: auto;
        border-bottom-left-radius: 4px;
        border-top-right-radius: 18px;
        border-top-left-radius: 18px;
        border-bottom-right-radius: 18px;
    }
    .speaker-label {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.1rem;
        margin-left: 0.2rem;
        color: #7ecfff;
    }
    .user-label {
        text-align: right;
        color: #aee1fb;
    }
    .assistant-label {
        text-align: left;
        color: #7ecfff;
    }
    .scrollable-history {
        max-height: 65vh;
        overflow-y: auto;
        padding-right: 8px;
    }
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100vw;
        background: rgba(15,32,39,0.98);
        padding: 1rem 0.5rem 1rem 0.5rem;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.12);
        z-index: 100;
    }
    .stTextInput>div>input {
        background: #22304a !important;
        color: #aee1fb !important;
        border-radius: 8px !important;
        border: none !important;
        font-size: 1.1rem;
        padding: 0.75rem 1rem;
    }
    .stButton>button {
        background: #22304a !important;
        color: #aee1fb !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 0.5rem 1.5rem;
    }
    .badge {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 0.2em 0.7em;
        border-radius: 12px;
        margin-bottom: 0.3em;
        margin-right: 0.5em;
        vertical-align: middle;
    }
    .badge-original {
        background: #1e90ff;
        color: #fff;
        border: 1px solid #1e90ff;
    }
    .badge-feedback {
        background: #00b894;
        color: #fff;
        border: 1px solid #00b894;
    }
    .badge-validation {
        background: #fdcb6e;
        color: #222;
        border: 1px solid #fdcb6e;
    }
    .badge-feedback-user {
        background: #a29bfe;
        color: #222;
        border: 1px solid #a29bfe;
    }
    .floating-linkedin-logo {
        position: fixed;
        top: 32px;
        right: 32px;
        z-index: 2000;
        width: 60px;
        height: 60px;
        opacity: 0.93;
        animation: floatY 2.8s ease-in-out infinite;
        box-shadow: 0 4px 24px 0 #0077b5aa;
        border-radius: 50%;
        background: rgba(255,255,255,0.07);
        transition: transform 0.2s;
    }
    .floating-linkedin-logo:hover {
        transform: scale(1.08) rotate(-6deg);
        box-shadow: 0 8px 32px 0 #0077b5cc;
        opacity: 1.0;
    }
    @keyframes floatY {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-16px); }
        100% { transform: translateY(0px); }
    }
    .linkedin-bg-logo {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 0;
        width: 420px;
        height: 420px;
        opacity: 0.08;
        filter: blur(0.5px) drop-shadow(0 0 60px #0077b5cc);
        pointer-events: none;
        user-select: none;
    }
    /* Make Streamlit tab labels larger and bolder */
    .stTabs [data-baseweb="tab"] {
        font-size: 1.18rem !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        color: #aee1fb !important;
        padding: 0.5em 1.2em !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1e90ff !important;
        background: rgba(30,144,255,0.08) !important;
        border-radius: 12px 12px 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Large LinkedIn logo as a background watermark (SVG from CDN)
st.markdown('''
    <img class="linkedin-bg-logo" src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/linkedin.svg" alt="LinkedIn Logo" />
''', unsafe_allow_html=True)

# Centered LinkedIn logo under headers
st.markdown('''
    <div style="text-align:center; margin-bottom: 1.2em; margin-top: -0.7em;">
        <a href="https://www.linkedin.com/" target="_blank" title="Visit LinkedIn">
            <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/linkedin.svg" alt="LinkedIn Logo" style="width:72px; height:72px; filter: drop-shadow(0 2px 12px #0077b5cc); transition: transform 0.18s; vertical-align: middle; border-radius: 18px; background:rgba(255,255,255,0.10); padding:8px;" onmouseover="this.style.transform='scale(1.13)';this.style.filter='drop-shadow(0 4px 24px #0077b5)';" onmouseout="this.style.transform='scale(1)';this.style.filter='drop-shadow(0 2px 12px #0077b5cc)';" />
        </a>
    </div>
''', unsafe_allow_html=True)

st.markdown("""
    <div class='bebas-header'>💬 Viral-LinkedIn Post Agent</div>
    <div class='bebas-subheader'>Generate, review, and perfect LinkedIn posts with AI-powered feedback</div>
""", unsafe_allow_html=True)

# After the CSS block, add spinner functions
spinner_placeholder = st.empty()

def show_glossy_spinner(text="Loading..."):
    spinner_placeholder.markdown(f'''
        <div class="custom-glossy-spinner">
            <div>
                <div class="glossy-loader"></div>
                <div style="text-align:center; color:#fff; font-size:1.1rem; margin-top:1.2em;">{text}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

def hide_glossy_spinner():
    spinner_placeholder.empty()

if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'state' not in st.session_state:
    st.session_state['state'] = AgentState(
        user_id="",
        topic="",
        tone=[],
        audience=[],
        drafts=[],
        best_post=None,
        feedback=None,
        history=[],
        current_step=None,
        validation=None,
        on="",
        analysis=""
    )
if 'chat_mode' not in st.session_state:
    st.session_state['chat_mode'] = False

config = {"configurable": {"thread_id": 1}}

# --- Process pending feedback if present ---
if 'pending_feedback' in st.session_state:
    user_input = st.session_state.pop('pending_feedback')
    st.session_state['history'].append(HumanMessage(content=user_input))
    st.session_state['state']['history'] = st.session_state['history']
    if st.session_state['state']['current_step'] in ['Collecting feedback from human', 'post_validation']:
        st.session_state['state']['feedback'] = user_input
    response = app.invoke(st.session_state['state'], config)
    st.session_state['state'] = response
    st.session_state['history'] = response['history']

# --- FAQ Tab for Viral LinkedIn Posts & Hacks ---
faq_qas = [
    {
        "q": "What makes a LinkedIn post go viral?",
        "a": "A viral LinkedIn post typically has a strong hook, authentic storytelling, actionable insights, and encourages engagement (e.g., questions, polls, or calls to action). Posts that tap into trending topics, personal experiences, or professional lessons often perform best."
    },
    {
        "q": "How important are hashtags for LinkedIn virality?",
        "a": "Hashtags help your post reach a broader audience beyond your immediate network. Use 3-7 relevant, trending hashtags. Avoid overloading with generic tags; instead, mix niche and popular ones for best results."
    },
    {
        "q": "What is the best time to post on LinkedIn for maximum reach?",
        "a": "Weekdays (especially Tuesday-Thursday) between 8am and 11am (your audience's local time) tend to see the highest engagement. However, experiment with your own audience for optimal timing."
    },
    {
        "q": "Should I use images or videos in my LinkedIn posts?",
        "a": "Yes! Posts with images or native videos generally get more engagement. Use high-quality, relevant visuals. For videos, keep them short (under 2 minutes) and add captions for silent viewers."
    },
    {
        "q": "What are some hacks to boost LinkedIn post engagement?",
        "a": "- Respond quickly to comments in the first hour (the 'golden hour')\n- Tag relevant people or companies (but only if truly relevant)\n- Use line breaks for readability\n- End with a question or call to action\n- Share personal stories or lessons learned\n- Engage with others' content before and after posting"
    },
]

# Place tabs before chat UI
selected_tab = st.tabs(["🤖 Viral LinkedIn Agent", "📈 FAQ: Viral LinkedIn Posts & Hacks"])

with selected_tab[1]:
    st.markdown("""
        <div style='font-family: "Bebas Neue", sans-serif; font-size: 1.6rem; color: #1e90ff; margin-bottom: 0.5em;'>
            FAQ: Viral LinkedIn Posts & Hacks
        </div>
    """, unsafe_allow_html=True)
    for qa in faq_qas:
        st.markdown(f"""
            <div style='margin-bottom:1.1em;'>
                <span style='font-weight:700; color:#7ecfff; font-size:1.08rem;'>Q: {qa['q']}</span><br/>
                <span style='color:#f0f6fc; font-size:1.01rem; margin-left:0.5em;'>{qa['a'].replace(chr(10),'<br/>')}</span>
            </div>
        """, unsafe_allow_html=True)

with selected_tab[0]:
    # Main chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Scrollable conversation history
    st.markdown('<div class="scrollable-history">', unsafe_allow_html=True)

    def get_message_category(msg):
        if isinstance(msg, AIMessage):
            if re.match(r"^Generated Post: ", msg.content):
                return 'original'
            elif re.match(r"^Generated post based on feedback:", msg.content):
                return 'feedback'
            elif re.match(r"^Post Validation Node:", msg.content):
                return 'validation'
            elif re.match(r"^Positive feedback received:", msg.content) or re.match(r"^Negative feedback received:", msg.content):
                return 'feedback-user'
        return None

    def get_badge_html(category):
        if category == 'original':
            return '<span class="badge badge-original">Original Post</span>'
        elif category == 'feedback':
            return '<span class="badge badge-feedback">Generated Post Based on Feedback</span>'
        elif category == 'validation':
            return '<span class="badge badge-validation">Validation</span>'
        elif category == 'feedback-user':
            return '<span class="badge badge-feedback-user">User Feedback</span>'
        return ''

    for msg in st.session_state['history']:
        badge_html = ''
        category = get_message_category(msg)
        if category:
            badge_html = get_badge_html(category)
        if isinstance(msg, HumanMessage):
            st.markdown(f"""
                <div class='speaker-label user-label'>User</div>
                <div class='chat-bubble user-bubble'>{msg.content}</div>
            """, unsafe_allow_html=True)
        elif isinstance(msg, AIMessage):
            st.markdown(f"""
                <div class='speaker-label assistant-label'>Assistant</div>
                <div class='chat-bubble assistant-bubble'>{badge_html}{msg.content}</div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Hybrid UI: Dropdowns at start, chat for feedback/review
    if (not st.session_state['chat_mode']) and st.session_state['state']['current_step'] in [None, 'input_node']:
        topic = st.text_input("Enter your LinkedIn post topic:", value=st.session_state['state']['topic'] if st.session_state['state']['topic'] else "")
        audience_options = ["generic", "professionals", "students", "executives", "marketers", "developers", "managers", "entrepreneurs"]
        tone_options = ["professional", "funny", "inspirational", "casual", "motivational", "educational", "friendly", "authoritative"]
        audience = st.multiselect(
            "Select your target audience(s):",
            audience_options,
            default=st.session_state['state']['audience'] if st.session_state['state']['audience'] else [],
            max_selections=3
        )
        tone = st.multiselect("Select tone(s) for your post (up to 3):", tone_options, default=st.session_state['state']['tone'] if st.session_state['state']['tone'] else [], max_selections=3)
        if st.button("Generate LinkedIn Post"):
            show_glossy_spinner("Generating your LinkedIn post...")
            st.session_state['state']['topic'] = topic
            st.session_state['state']['audience'] = audience
            st.session_state['state']['tone'] = tone
            st.session_state['history'].append(HumanMessage(content=f"Topic: {topic}, Audience: {', '.join(audience)}, Tone: {', '.join(tone)}"))
            st.session_state['state']['history'] = st.session_state['history']
            response = app.invoke(st.session_state['state'], config)
            st.session_state['state'] = response
            st.session_state['history'] = response['history']
            hide_glossy_spinner()
            st.session_state['chat_mode'] = True
            st.rerun()
    else:
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        with st.form(key="chat_input_form", clear_on_submit=True):
            user_input = st.text_input("", placeholder="Type your message and press Enter...", key="user_input_box")
            submitted = st.form_submit_button("Send")
        if submitted and user_input:
            show_glossy_spinner("Processing feedback...")
            st.session_state['pending_feedback'] = user_input
            hide_glossy_spinner()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
