import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from PIL import Image
import os
import base64
import io
import PyPDF2
import re

# --- Page Config ---
st.set_page_config(page_title="PathPilot", layout="centered", page_icon="🌽")

# --- Theme Toggle ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

icon = "🌙" if st.session_state.dark_mode else "☀️"

# Inject theme toggle button
st.markdown(f"""
    <style>
    .theme-toggle {{
        position: fixed;
        top: 10px;
        right: 10px;
        font-size: 26px;
        background: none;
        border: none;
        z-index: 1000;
        color: {'white' if st.session_state.dark_mode else 'black'};
    }}
    </style>
    <script>
    const toggleBtn = window.parent.document.querySelector('button[kind="theme_toggle_button"]');
    if (toggleBtn) toggleBtn.classList.add("theme-toggle");
    </script>
""", unsafe_allow_html=True)

if st.button(icon, key="theme_toggle_button"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# --- Sidebar Section ---
with st.sidebar:
    st.markdown("## 📚 Career Resources")
    resource_option = st.radio(
        "Choose a topic:",
        ["None", "📄 Resume Tips", "🎤 Interview Preparation", "🧠 Soft Skills", "💼 Job Search Strategies"]
    )

    resource_content = {
        "📄 Resume Tips": """
        ### 📄 Resume Tips
        - ✂️ Keep it concise and relevant (1-2 pages).
        - ✅ Use bullet points to list achievements.
        - 🎯 Tailor your resume for the job role.
        - 🛠️ Highlight technical skills and certifications.
        - 🔗 Include links to GitHub, LinkedIn, or a portfolio.
        """,
        "🎤 Interview Preparation": """
        ### 🎤 Interview Preparation
        - 🏢 Research the company and role.
        - 📚 Practice common interview questions.
        - 🧪 Be ready to explain your projects.
        - ❓ Ask questions to show genuine interest.
        - 👔 Dress professionally and be punctual.
        """,
        "🧠 Soft Skills": """
        ### 🧠 Soft Skills to Develop
        - 🗣️ Communication & teamwork
        - 🧩 Critical thinking & problem-solving
        - ⏳ Time management
        - 🔄 Adaptability & continuous learning
        - 🤝 Empathy & emotional intelligence
        """,
        "💼 Job Search Strategies": """
        ### 💼 Job Search Strategies
        - 🧭 Define your career goals clearly.
        - 📍 Use platforms like LinkedIn, Naukri, and Internshala.
        - 📝 Customize your resume for each application.
        - 🧑‍💼 Network with industry professionals.
        - 💌 Follow up after applications and interviews.
        """
    }

    if resource_option != "None":
        st.markdown(resource_content.get(resource_option, ""))

# --- Configure Gemini API (only once) ---
if not hasattr(genai, "_configured") or not genai._configured:
    genai.configure(api_key="AIzaSyDUYOlvTUy6LAbz9tTtQg2qkvxCKL6ZPCA")
    genai._configured = True

# --- Load and Display Logo ---
try:
    logo = Image.open("logo.jpeg")
    buffered = io.BytesIO()
    logo.save(buffered, format="JPEG")
    logo_b64 = base64.b64encode(buffered.getvalue()).decode()
    st.markdown(f"""
        <div style='display: flex; justify-content: center; margin-top: 10px; margin-bottom: -20px;'>
            <img src='data:image/jpeg;base64,{logo_b64}' width='150'/>
        </div>
    """, unsafe_allow_html=True)
except:
    st.warning("Logo image not found.")

# --- CSS Styling ---
dark_css = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-color: #0e1117;
    color: white;
    font-family: 'Segoe UI', sans-serif;
    padding-top: 0px;
}
.chat-card {
    background-color: #1e222a;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}
.header {
    font-size: 3rem;
    background: linear-gradient(to right, #00c6ff, #0077ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold;
    margin-top: 0.5rem;
    text-align:center;
}
.subheader {
    font-size: 2rem;
    color: #bbbbbb;
    margin-bottom: 1.5rem;
    text-align:center;
}
.feedback-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    font-size: 1.5rem;
    margin-top: 10px;
    margin-bottom: 10px;
}
</style>
"""

light_css = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-color: #ffffff;
    color: #000000;
    font-family: 'Segoe UI', sans-serif;
    padding-top: 0px;
}
.chat-card {
    background-color: #f0f2f6;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.header {
    font-size: 3rem;
    color: #0077ff;
    font-weight: bold;
    margin-top: 0.5rem;
    text-align:center;
}
.subheader {
    font-size: 2rem;
    color: #444;
    margin-bottom: 1.5rem;
    text-align:center;
}
.feedback-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    font-size: 1.5rem;
    margin-top: 10px;
    margin-bottom: 10px;
}
</style>
"""

st.markdown(dark_css if st.session_state.dark_mode else light_css, unsafe_allow_html=True)

# --- Branding Title ---
st.markdown('<div class="header">Future Navigators</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Your Career. Your Map. Your Journey.</div>', unsafe_allow_html=True)


# --- Upload Resume Section ---

uploaded_resume = st.file_uploader("Upload PDF Resume", type=["pdf"])
if uploaded_resume:
    st.success(f"Resume '{uploaded_resume.name}' uploaded successfully! ✅")

    # Extract text
    pdf_reader = PyPDF2.PdfReader(uploaded_resume)
    resume_text = " ".join([page.extract_text() or "" for page in pdf_reader.pages])

    # Generate analysis from Gemini
    prompt = f"""
    You are a career advisor. Analyze the following resume content and provide:
    1. Key skills
    2. Suggested job roles
    3. Suggested learning paths
    4. Suggestions for improvement
    5. Suggested LinkedIn profile headline and summary based on the resume

    Resume Content:
    {resume_text}
    """

    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    st.subheader("🧾 Resume Analysis Report")
    full_response = response.text.strip()
    st.markdown(full_response)

    # --- Job Role Suggestions + Job Search Links with Filters ---
    st.markdown("## 🌐 Suggested Job Roles & Opportunities")

    # Customize filters
    location = "India"
    experience = "Entry Level"
    job_type = "Full-time"

    job_role_matches = re.findall(r"(?i)suggested job roles\s*:\s*(.+?)(?:\n|$)", full_response)
    if job_role_matches:
        raw_roles = job_role_matches[0]
        job_roles = [role.strip(" •-") for role in re.split(r",|•|-|\n", raw_roles) if role.strip()]
        job_roles = list(set(job_roles))

        st.write("🔎 Filter: ", f"`{experience}` | `{location}` | `{job_type}`")

        for role in job_roles:
            st.markdown(f"### 💼 {role}")

            search_role = role.replace(" ", "+")
            internshala_term = role.lower().replace(" ", "-")

            links = {
                "🔗 LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={search_role}&location={location}&f_E=2&f_JT=F",
                "🔗 Naukri": f"https://www.naukri.com/{search_role}-jobs-in-{location.lower().replace(' ', '-')}",
                "🔗 Indeed": f"https://www.indeed.com/jobs?q={search_role}&l={location}&explvl=entry_level",
                "🔗 Internshala": f"https://internshala.com/internships/{internshala_term}-internship/",
                "🔗 Google Jobs": f"https://www.google.com/search?q={search_role}+jobs+in+{location.replace(' ', '+')}"
            }

            for name, url in links.items():
                st.markdown(f"- {name} → [View Jobs]({url})", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No job roles detected in the resume analysis.")

    


# --- Load Excel Questions ---
try:
    df = pd.read_excel("career_guidance_qna (1).xlsx")
except Exception as e:
    st.error("❌ Error loading Excel file. Please check the file path and name.")
    st.stop()

@st.cache_resource
def get_vectorizer_and_matrix(questions):
    vectorizer = TfidfVectorizer()
    question_vectors = vectorizer.fit_transform(questions)
    return vectorizer, question_vectors

vectorizer, question_vectors = get_vectorizer_and_matrix(df['Question'])

def find_best_match(user_question):
    user_vec = vectorizer.transform([user_question])
    similarity = cosine_similarity(user_vec, question_vectors)
    best_idx = similarity.argmax()
    return df.iloc[best_idx]['Question'], df.iloc[best_idx]['Answer']

def generate_response(chat_history, relevant_answer):
    prompt = f"""
This is a career guidance chatbot.

User asked: "{chat_history[-1]['user']}"
Relevant info: "{relevant_answer}"
Give a helpful, friendly, and informative answer to guide the user.
"""
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text.strip()

def save_chat_to_excel(chat_history, filename="pathpilot_chat_history.xlsx"):
    chat_df = pd.DataFrame(chat_history)
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        final_df = pd.concat([existing_df, chat_df], ignore_index=True)
    else:
        final_df = chat_df
    final_df.to_excel(filename, index=False)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'feedback_given' not in st.session_state:
    st.session_state.feedback_given = {}

user_input = st.text_input("💬 Ask your career question here:", key="user_input")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔍 Get Answer"):
        if user_input.strip():
            matched_q, matched_a = find_best_match(user_input)
            st.session_state.chat_history.append({"user": user_input, "bot": matched_a, "feedback": None})
            final_response = generate_response(st.session_state.chat_history, matched_a)
            st.session_state.chat_history[-1]['bot'] = final_response
            save_chat_to_excel(st.session_state.chat_history)

with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.feedback_given = {}
        st.success("Chat cleared!")

for i, entry in enumerate(st.session_state.chat_history):
    with st.container():
        st.markdown(f"""
        <div class="chat-card">
        <b>🧑‍🏬 You:</b> {entry['user']}<br><br>
        <b>🤖 PathPilot:</b> {entry['bot']}
        </div>
        """, unsafe_allow_html=True)

        if entry['feedback'] is None:
            st.markdown("<div class='feedback-buttons'>", unsafe_allow_html=True)
            st.markdown("We’d love your feedback! Let us know what you think ✨📝")
            col_fb = st.columns(5)
            feedback_emojis = ["😀", "😊", "😐", "😕", "😡"]
            for j, emoji in enumerate(feedback_emojis):
                if col_fb[j].button(emoji, key=f"fb_{i}_{j}"):
                    st.session_state.chat_history[i]['feedback'] = f"{emoji}"
                    save_chat_to_excel(st.session_state.chat_history)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<hr style="border: 1px solid #444;">
<div style='text-align: center; color: #888;'>
    Made with ❤️ by <b>Team Future Navigators</b> | Powered by Google Gemini & Streamlit
</div>
""", unsafe_allow_html=True)
