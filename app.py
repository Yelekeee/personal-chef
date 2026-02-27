import os
import uuid
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Yelnar's Assistant", page_icon="🔍", layout="wide")
st.title("Yelnar's Assistant")

# ── Session state ──────────────────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversations" not in st.session_state:
    st.session_state.conversations = []  # [{thread_id, title, messages}]
if "show_all_history" not in st.session_state:
    st.session_state.show_all_history = False


def save_current():
    """Save current conversation to history (skip if empty)."""
    if not st.session_state.messages:
        return
    title = next(
        (m["content"][:45] + ("…" if len(m["content"]) > 45 else "")
         for m in st.session_state.messages if m["role"] == "user"),
        "Conversation",
    )
    for conv in st.session_state.conversations:
        if conv["thread_id"] == st.session_state.thread_id:
            conv["messages"] = st.session_state.messages.copy()
            conv["title"] = title
            return
    st.session_state.conversations.insert(0, {
        "thread_id": st.session_state.thread_id,
        "title": title,
        "messages": st.session_state.messages.copy(),
    })


def new_conversation():
    save_current()
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.show_all_history = False


def load_conversation(conv: dict):
    save_current()
    st.session_state.thread_id = conv["thread_id"]
    st.session_state.messages = conv["messages"].copy()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    if st.button("+ New Conversation", use_container_width=True, type="primary"):
        new_conversation()
        st.rerun()

    if st.session_state.conversations:
        st.divider()
        st.caption("History")

        history = st.session_state.conversations
        visible = history if st.session_state.show_all_history else history[:5]

        for conv in visible:
            active = conv["thread_id"] == st.session_state.thread_id
            label = f"● {conv['title']}" if active else conv["title"]
            if st.button(label, key=f"conv_{conv['thread_id']}", use_container_width=True):
                load_conversation(conv)
                st.rerun()

        remaining = len(history) - 5
        if not st.session_state.show_all_history and remaining > 0:
            if st.button(f"Show {remaining} more…", use_container_width=True):
                st.session_state.show_all_history = True
                st.rerun()
        elif st.session_state.show_all_history and len(history) > 5:
            if st.button("Show less", use_container_width=True):
                st.session_state.show_all_history = False
                st.rerun()

    st.divider()
    st.caption("Attach Image (optional)")
    image_mode = st.radio("Source", ["None", "URL", "Upload file"], label_visibility="collapsed")

    image_url = None
    uploaded_file = None

    if image_mode == "URL":
        image_url = st.text_input("Image URL", placeholder="https://...")
    elif image_mode == "Upload file":
        uploaded_file = st.file_uploader("Image file", type=["jpg", "jpeg", "png", "gif", "webp"])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask Yelnar's Assistant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                if image_mode == "URL" and image_url:
                    resp = requests.post(
                        f"{API_URL}/chat/image-url",
                        json={
                            "thread_id": st.session_state.thread_id,
                            "image_url": image_url,
                            "question": prompt,
                        },
                        timeout=60,
                    )
                elif image_mode == "Upload file" and uploaded_file:
                    resp = requests.post(
                        f"{API_URL}/chat/image-file",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        data={"thread_id": st.session_state.thread_id, "question": prompt},
                        timeout=60,
                    )
                else:
                    resp = requests.post(
                        f"{API_URL}/chat",
                        json={"thread_id": st.session_state.thread_id, "message": prompt},
                        timeout=60,
                    )

                resp.raise_for_status()
                answer = resp.json()["response"]

            except requests.exceptions.ConnectionError:
                answer = "Cannot reach the server. Make sure `uv run python run.py` is running."
            except Exception as e:
                answer = f"Error: {e}"

        st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
