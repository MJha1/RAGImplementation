"""Sage — AI knowledge assistant. Web UI for the RAG app.

Run with:  streamlit run app.py
"""

import streamlit as st
import rag

st.set_page_config(page_title="Sage · AI Knowledge Assistant", page_icon="✨", layout="centered")

# Hide Streamlit's built-in "Deploy" button and the ⋮ menu, and tighten the top
# padding so the header sits near the top of the screen (looks cleaner in shots).
st.markdown(
    """
    <style>
      [data-testid='stAppDeployButton'] {display: none;}
      [data-testid='stMainMenu'] {display: none;}
      [data-testid='stHeader'] {height: 0;}
      .block-container {padding-top: 2.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Neutral, professional chat avatars.
USER_AVATAR = "🧑"
BOT_AVATAR = "✨"

# Clickable starter questions — each maps to one of the sample docs.
STARTER_QUESTIONS = [
    "What is retrieval-augmented generation?",
    "Why do LLMs hallucinate?",
    "What is harness engineering?",
]

ACCENT = "#4F46E5"


# Build the index once per session (embeddings run locally, so this is cheap
# after the first time). Cached so it doesn't re-run on every interaction.
@st.cache_resource
def setup_index():
    rag.build_index()
    return True


# --- Header: minimal logo mark + product name + tagline ---
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
      <div style="width:46px; height:46px; border-radius:13px; flex-shrink:0;
                  background:linear-gradient(135deg,#4F46E5,#7C3AED);
                  display:flex; align-items:center; justify-content:center;">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="white">
          <path d="M12 2l2.1 5.3L19.5 9l-4.2 3.5L16.4 18 12 15l-4.4 3 1.1-5.5L4.5 9l5.4-1.7L12 2z"/>
        </svg>
      </div>
      <div>
        <div style="font-size:1.7rem; font-weight:750; letter-spacing:-.02em; line-height:1.05; color:#1A1A2E;">
          Sage <span style="color:{ACCENT};">AI</span>
        </div>
        <div style="color:#6B7280; font-size:.98rem; margin-top:2px;">
          Answers grounded in your documents — no hallucinations, with sources.
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- "How it works" strip: signals the architecture at a glance ---
st.markdown(
    f"""
    <div style="display:flex; gap:10px; margin:14px 0 22px;">
      {''.join(
        f'''<div style="flex:1; background:#F5F6F8; border:1px solid #ECEDF1;
                       border-radius:12px; padding:12px 14px;">
              <div style="font-size:.72rem; font-weight:700; letter-spacing:.04em;
                          color:{ACCENT}; text-transform:uppercase;">{step}</div>
              <div style="font-size:.82rem; color:#4B5563; margin-top:4px; line-height:1.35;">{desc}</div>
            </div>'''
        for step, desc in [
            ("1 · Retrieve", "Semantic search finds the most relevant passages in your documents, locally."),
            ("2 · Augment", "Those passages are passed to the model as grounded context."),
            ("3 · Generate", "Groq's LLM answers using only that context, and cites its sources."),
        ]
      )}
    </div>
    """,
    unsafe_allow_html=True,
)

# Make sure the documents are indexed before we take questions.
try:
    setup_index()
except Exception as e:
    st.error(f"Could not build the index: {e}")
    st.stop()

# Keep the conversation in session state so it survives reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the conversation so far.
for msg in st.session_state.messages:
    avatar = USER_AVATAR if msg["role"] == "user" else BOT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption(f"📄 Sources: {msg['sources']}")

# A question can come from either a starter button or the chat box.
clicked = None
if not st.session_state.messages:
    st.markdown("###### Try one of these")
    cols = st.columns(len(STARTER_QUESTIONS))
    for col, starter in zip(cols, STARTER_QUESTIONS):
        if col.button(starter, use_container_width=True):
            clicked = starter

typed = st.chat_input("Ask a question about the documents…")
question = clicked or typed

# Handle a new question.
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(question)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.spinner("Searching the documents…"):
            try:
                answer, sources = rag.answer_question(question)
            except Exception as e:
                answer, sources = f"Something went wrong: {e}", ""
        st.markdown(answer)
        if sources:
            st.caption(f"📄 Sources: {sources}")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )

    # If a starter button was used, rerun so the buttons disappear cleanly.
    if clicked:
        st.rerun()

# Subtle brand footer.
st.markdown(
    f"""
    <div style="margin-top:28px; padding-top:12px; border-top:1px solid #ECEDF1;
                color:#9AA0AA; font-size:.8rem; text-align:center;">
      <span style="font-weight:650; color:#6B7280;">Sage <span style="color:{ACCENT};">AI</span></span>
      &nbsp;·&nbsp; Grounded answers you can trust.
    </div>
    """,
    unsafe_allow_html=True,
)
