import streamlit as st
import requests
import json
import re

# Ollama config
OLLAMA_MODEL = "deepseek-r1:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"

# Initialize memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": (
            "You are an AI assistant that ONLY answers questions about Indian energy policies and strategies. "
            "If the user asks something outside this scope, respond strictly with: "
            "'I don’t know. I am a chatbot only for Indian energy policies and strategies.'"
        )}
    ]

# Function to query Ollama
def query_ollama(messages):
    headers = {"Content-Type": "application/json"}
    data = {"model": OLLAMA_MODEL, "messages": messages, "stream": True}
    response = requests.post(OLLAMA_URL, headers=headers, json=data, stream=True)

    final_answer = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            if "message" in data and "content" in data["message"]:
                final_answer += data["message"]["content"]

    # Remove <think> ... </think>
    clean_answer = re.sub(r"<think>.*?</think>", "", final_answer, flags=re.DOTALL)
    return clean_answer.strip()

# Streamlit UI
st.set_page_config(page_title="Energy Policy Assistant", layout="wide")

st.markdown("<h2 style='text-align: center;'>⚡Indian Energy Policies Chatbot</h2>", unsafe_allow_html=True)

# Display chat history
for chat in st.session_state.chat_history[1:]:  # skip system prompt
    if chat["role"] == "user":
        st.chat_message("user").markdown(chat["content"])
    elif chat["role"] == "assistant":
        st.chat_message("assistant").markdown(chat["content"])

# User input
if prompt := st.chat_input("Ask me about Indian energy policies..."):
    # Save user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Get model response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = query_ollama(st.session_state.chat_history)

            # If response is irrelevant, enforce restriction
            if not answer or "I don’t know" in answer:
                answer = "I don’t know. I am a chatbot only for Indian energy policies and strategies."

            st.markdown(answer)

    # Save assistant response
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
