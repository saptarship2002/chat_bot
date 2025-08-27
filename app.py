import streamlit as st
import requests

# -------------------------
# CONFIG
# -------------------------
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Change if Ollama runs elsewhere

# -------------------------
# HELPER FUNCTION
# -------------------------
def ask_ollama(prompt, context=""):
    """Send a prompt to Ollama and return the response text only."""
    data = {
        "model": "deepseek:8b",
        "prompt": f"""
You are a chatbot that ONLY answers questions about Indian energy policies and strategies.
If the question is unrelated, reply exactly with: 
"I don’t know, I am only a chatbot for Indian energy policy."

Conversation so far:
{context}

User: {prompt}
Assistant:""",
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"⚠️ Error contacting Ollama: {e}"

# -------------------------
# STREAMLIT UI
# -------------------------
st.set_page_config(page_title="Indian Energy Policy Chatbot", page_icon="⚡", layout="centered")
st.title("⚡ Indian Energy Policy Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if user_input := st.chat_input("Ask about Indian energy policy..."):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Get full context
    context = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state["messages"]])

    # Query Ollama
    with st.chat_message("assistant"):
        response = ask_ollama(user_input, context)
        st.markdown(response)

    # Save assistant message
    st.session_state["messages"].append({"role": "assistant", "content": response})
