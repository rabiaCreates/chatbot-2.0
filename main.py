
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

st.set_page_config(
    page_title="Azure AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Azure GPT-4.1 mini Chatbot")
st.caption("Chat with your deployed AI model")

# Check Azure configuration
if not endpoint or not api_key or not deployment:
    st.error(
        "Azure configuration is missing. "
        "Please check your .env file."
    )
    st.stop()

# Create Azure AI Foundry client
client = OpenAI(
    api_key=api_key,
    base_url=f"{endpoint}/openai/v1/"
)

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a helpful and friendly AI assistant."
        }
    ]

# Display previous messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=deployment,
                    messages=st.session_state.messages,
                    max_tokens=1000
                )

                reply = (
                    response.choices[0].message.content
                    or "I couldn't generate a response."
                )

                st.markdown(reply)

                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )

            except Exception as error:
                # Remove the unanswered user message
                st.session_state.messages.pop()

                error_code = getattr(error, "status_code", None)

                if error_code == 404:
                    st.error(
                        "404 Resource Not Found. Check your Azure "
                        "endpoint and deployment name."
                    )
                elif error_code == 401:
                    st.error(
                        "401 Unauthorized. Check your Azure API key."
                    )
                elif error_code == 429:
                    st.error(
                        "429 Rate Limit or Quota Exceeded. "
                        "Check your Azure quota and deployment limits."
                    )
                else:
                    st.error(f"Azure API error: {error}")

# Sidebar settings
with st.sidebar:
    st.header("Chat Settings")

    if st.button("Clear conversation"):
        st.session_state.messages = [
            {
                "role": "system",
                "content": "You are a helpful and friendly AI assistant."
            }
        ]
        st.rerun()

    st.caption("Powered by Azure AI Foundry.")
