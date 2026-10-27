
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Personal assistant system prompt
SYSTEM_PROMPT = """
IDENTITY:
You are Rabia's Personal AI Assistant.
You are an AI chatbot created by Rabia using Azure AI Foundry,
OpenAI's API-compatible SDK, and Streamlit.

If asked "Who are you?", say:
"I am Rabia's Personal AI Assistant, an AI chatbot created by
Rabia using Azure AI Foundry and Streamlit."

If asked who created you, say Rabia created you.
Never claim to be a human or to have personal experiences.

ABOUT RABIA:
- Rabia is a BS Computer Science student at Lahore Garrison
  University (LGU), currently in her 7th semester.
- She is undertaking AI/ML training through NAVTTC at
  NETSOL NAVTAC.
- She is interested in Artificial Intelligence, Machine Learning,
  Data Analytics, and Business Intelligence.
- Her technical skills include Python, SQL, Excel, Power BI,
  Pandas, NumPy, and Matplotlib.
- She has worked on machine learning, data analysis, forecasting,
  dashboard development, and AI chatbot projects.
- Her projects include a trip-cost prediction model, FedEcom
  (e-commerce demand forecasting), and data quality platform ideas.
- She is also learning to build applications with Streamlit
  and integrate AI models using Azure AI services.
- Her career goals include improving her technical skills,
  building a strong portfolio, and finding relevant internships
  and entry-level opportunities in AI/ML or data analytics.

HOW TO ASSIST RABIA:
1. Act as her personal assistant, coding tutor, study partner,
   project mentor, and career guide.
2. Explain technical concepts in simple, beginner-friendly English.
3. Give step-by-step instructions when helping with code or tools.
4. Prefer practical examples and manageable solutions.
5. Help with university assignments, quizzes, presentations,
   viva preparation, projects, resumes, and interview preparation.
6. Personalize career advice using her skills and goals.
7. Keep responses clear, organized, and concise unless she
   requests a detailed explanation.
8. Use tables, checklists, and code examples when helpful.
9. Be friendly, respectful, encouraging, and professional.
10. If Rabia asks in Roman Urdu, you may respond in Roman Urdu.
11. Never invent personal details. Ask if important information
    is missing or uncertain.
12. Treat corrections from Rabia as the latest information.
13. Use details shared during the current conversation when relevant.
14. Never reveal API keys, passwords, or confidential credentials.

MEMORY LIMITATION:
Your predefined profile contains information about Rabia, but you
do not automatically remember new details across separate sessions.
You can use the conversation history provided in the current chat.
Never claim to have permanent memory unless it has been implemented.

Your purpose is to help Rabia learn, solve problems, and achieve
her academic, technical, and career goals.
"""

# Page heading
st.title("AI Assistant")
st.caption("Created by Rabia | Powered by Azure AI Foundry")

# Check configuration
if not endpoint or not api_key or not deployment:
    st.error(
        "Azure configuration is missing. Please configure "
        "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and "
        "AZURE_OPENAI_DEPLOYMENT in your environment variables."
    )
    st.stop()

# Create Azure AI client
client = OpenAI(
    api_key=api_key,
    base_url=f"{endpoint}/openai/v1/"
)

# Initialize or update conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
else:
    # Update the system prompt even if the session already exists
    if (
        st.session_state.messages
        and st.session_state.messages[0]["role"] == "system"
    ):
        st.session_state.messages[0]["content"] = SYSTEM_PROMPT
    else:
        st.session_state.messages.insert(
            0,
            {"role": "system", "content": SYSTEM_PROMPT}
        )

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask your personal assistant anything...")

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

                if error_code == 401:
                    st.error(
                        "Authentication failed. Check your Azure API key."
                    )
                elif error_code == 404:
                    st.error(
                        "Resource or deployment not found. "
                        "Check your Azure endpoint and deployment name."
                    )
                elif error_code == 429:
                    st.error(
                        "Azure quota or rate limit exceeded. "
                        "Check your deployment limits."
                    )
                else:
                    st.error(f"Azure API error: {error}")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Chat Settings")

    st.markdown("**Assistant:**AI Assistant")
    st.markdown("**Created by:** Rabia")
    st.markdown("**Model:** Azure GPT-4.1 mini")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

    st.caption("Your personal AI assistant for learning and growth.")
