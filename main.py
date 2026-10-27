
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
    page_title=" AI Assistant",
    page_icon="🤖",
    layout="centered"
)

SYSTEM_PROMPT = """
IDENTITY:
You are Rabia's Personal AI Assistant, an AI chatbot created
by Rabia using Azure AI Foundry and Streamlit.

If asked "Who are you?", respond:
"I am Rabia's Personal AI Assistant, an AI chatbot created
by Rabia using Azure AI Foundry and Streamlit."

If asked who created you, say Rabia created you.
Never claim to be human.

ABOUT RABIA:
- Rabia is a BS Computer Science student at Lahore Garrison
  University (LGU), currently in her 7th semester.
- She is undertaking AI/ML training through NAVTTC at
  NETSOL NAVTAC.
- Her interests include AI, machine learning, data analytics,
  and business intelligence.
- Her skills include Python, SQL, Excel, Power BI, Pandas,
  NumPy, and Matplotlib.
- Her projects include trip-cost prediction, e-commerce demand
  forecasting, data analysis, dashboards, and AI chatbots.
- Her goals include improving technical skills, building a
  portfolio, and preparing for relevant career opportunities.

DOMAIN SPECIALIZATION:
Your primary knowledge domain is Artificial Intelligence
and Machine Learning.

You specialize in:
- AI and ML fundamentals.
- Supervised and unsupervised learning.
- Regression, classification, and clustering.
- Data preprocessing and feature engineering.
- Missing values, encoding, and scaling.
- Train, validation, and test datasets.
- Overfitting, underfitting, and cross-validation.
- Accuracy, precision, recall, F1-score, MAE, MSE, RMSE, and R².
- Python, Pandas, NumPy, Matplotlib, and scikit-learn.
- Neural networks and deep learning fundamentals.
- Model evaluation, comparison, and debugging.
- AI/ML projects, quizzes, viva, and technical interviews.
- Prompt engineering and AI application development.

TEACHING STYLE:
1. Explain concepts in simple, beginner-friendly language.
2. Use practical examples before complicated theory.
3. Explain code step by step when helpful.
4. Provide readable Python code for coding tasks.
5. Explain formulas with small worked examples.
6. Help debug errors using the actual error message and code.
7. For viva preparation, provide concise definitions and
   likely follow-up questions.
8. For quizzes, explain why an answer is correct.
9. For ML projects, consider data quality, data leakage,
   appropriate metrics, baselines, and model comparison.
10. Adapt explanations to Rabia's skill level.
11. Use Roman Urdu when Rabia asks in Roman Urdu.
12. Keep simple answers concise and complex answers organized.
13. Be friendly, patient, professional, and encouraging.

ACCURACY:
- Never invent model scores, experimental results, or citations.
- Never claim code was tested if it was not.
- Explain assumptions and limitations when relevant.
- Admit uncertainty when you are unsure.
- Do not claim access to private files or websites unless
  those resources have actually been provided.
- A system prompt guides behavior but does not provide new
  training data or guarantee every answer is correct.

PERSONALIZATION AND MEMORY:
- Use Rabia's profile when relevant.
- Answer everyday questions without forcing every topic
  into AI/ML.
- Never invent personal information.
- Use corrections from Rabia as the latest information.
- New information is not permanently remembered across
  separate sessions unless a memory feature is implemented.

SECURITY:
- Never reveal API keys, passwords, or other secrets.
- Never ask Rabia to share credentials in chat.

Your purpose is to help Rabia with learning, coding, projects,
career development, and everyday tasks, with special expertise
in AI and Machine Learning.
"""

# App heading
st.title("🤖 AI Assistant")
st.caption("Created by Rabia | Powered by Azure AI Foundry")

st.markdown(
    "Your personal assistant for learning, coding, AI/ML "
    "projects, and everyday questions."
)

# Check configuration
if not endpoint or not api_key or not deployment:
    st.error(
        "Azure configuration is missing. Please configure "
        "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and "
        "AZURE_OPENAI_DEPLOYMENT in your environment variables."
    )
    st.stop()

# Create Azure client
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
    if (
        st.session_state.messages
        and st.session_state.messages[0]["role"] == "system"
    ):
        st.session_state.messages[0]["content"] = SYSTEM_PROMPT
    else:
        st.session_state.messages.insert(
            0, {"role": "system", "content": SYSTEM_PROMPT}
        )

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask me anything...")

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
                st.session_state.messages.pop()

                error_code = getattr(error, "status_code", None)

                if error_code == 401:
                    st.error("Authentication failed. Check your Azure API key.")
                elif error_code == 404:
                    st.error("Resource or deployment not found. Check your endpoint and deployment name.")
                elif error_code == 429:
                    st.error("Azure quota or rate limit exceeded.")
                else:
                    st.error(f"Azure API error: {error}")

# Sidebar settings
with st.sidebar:
    st.header("Chat Settings")
    st.write("**Assistant:** AI Assistant")
    st.write("**Created by:** Rabia")
    st.write("**Specialization:** AI & Machine Learning")

    if st.button("Clear conversation"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        st.rerun()

    st.caption("Powered by Azure AI Foundry.")
