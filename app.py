import streamlit as st
from datetime import date, timedelta


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="College Academic Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

.stApp {
    background-color: #0b1120;
    color: #e5e7eb;
}

.block-container {
    max-width: 1250px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}


/* =========================
   SIDEBAR
   ========================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #080d1a 0%,
        #111936 55%,
        #17143b 100%
    );

    border-right: 1px solid #263354;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.8rem;
}

section[data-testid="stSidebar"] h2 {
    color: #f8fafc;
    font-weight: 800;
}

section[data-testid="stSidebar"] .stCaption {
    color: #94a3b8;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: #111827;
    border: 1px solid #263354;
    border-radius: 12px;
    padding: 10px 12px;
    color: #cbd5e1;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #1a2544;
    border-color: #6366f1;
}


/* =========================
   HEADINGS
   ========================= */

h1 {
    color: #f8fafc !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2 {
    color: #f1f5f9 !important;
    font-weight: 750 !important;
}

h3 {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}

p {
    color: #cbd5e1;
}


/* =========================
   CAPTION
   ========================= */

.stCaption {
    color: #818cf8 !important;
    font-weight: 700;
    letter-spacing: 0.5px;
}


/* =========================
   FEATURE CARDS
   ========================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111827;
    border: 1px solid #263354;
    border-radius: 18px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18);
}


/* =========================
   BUTTONS
   ========================= */

.stButton > button {
    background: linear-gradient(
        135deg,
        #4f46e5,
        #6366f1
    );

    color: white;
    border: none;
    border-radius: 11px;

    font-weight: 700;
    min-height: 45px;

    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.25);

    transition: 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        135deg,
        #4338ca,
        #4f46e5
    );

    transform: translateY(-1px);

    box-shadow: 0 9px 25px rgba(79, 70, 229, 0.35);
}


/* =========================
   TEXT INPUT
   ========================= */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #111827 !important;
    color: #f8fafc !important;

    border: 1px solid #334155 !important;
    border-radius: 11px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
}


/* =========================
   SELECT BOX
   ========================= */

div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-radius: 11px !important;
}

div[data-baseweb="select"] span {
    color: #e5e7eb !important;
}


/* =========================
   DATE INPUT
   ========================= */

[data-testid="stDateInput"] input {
    background-color: #111827 !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 11px !important;
}


/* =========================
   CHAT
   ========================= */

[data-testid="stChatMessage"] {
    background-color: #111827;
    border: 1px solid #263354;
    border-radius: 16px;
    margin-bottom: 10px;
}

[data-testid="stChatInput"] {
    background-color: #111827;
}


/* =========================
   METRICS
   ========================= */

div[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #263354;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18);
}

div[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 800;
}


/* =========================
   ALERTS
   ========================= */

div[data-testid="stAlert"] {
    border-radius: 13px;
}


/* =========================
   EXPANDERS
   ========================= */

div[data-testid="stExpander"] {
    background-color: #111827;
    border: 1px solid #263354;
    border-radius: 13px;
}


/* =========================
   DIVIDERS
   ========================= */

hr {
    border: none;
    border-top: 1px solid #263354;
    margin: 30px 0;
}


/* =========================
   FOOTER
   ========================= */

.footer-text {
    color: #64748b;
    text-align: center;
    font-size: 12px;
}


/* =========================
   MOBILE
   ========================= */

@media (max-width: 768px) {

    .block-container {
        padding-top: 1.5rem;
    }

    h1 {
        font-size: 32px !important;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "study_plan" not in st.session_state:
    st.session_state.study_plan = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🎓 College Assistant")

    st.caption("Your intelligent academic companion")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "💬 Academic Assistant",
            "📅 Study Planner",
            "ℹ️ About"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### 🔌 System Status")

    st.success("🟢 Interface: Ready")

    st.warning("🟡 RAG: Backend pending")

    st.warning("🟡 LangGraph: Backend pending")

    st.success("🟢 Study Planner: Ready")

    st.divider()

    st.caption("College Academic Assistant")
    st.caption("LLM • RAG • LangChain • LangGraph")


# =========================================================
# ACADEMIC ASSISTANT
# =========================================================

if page == "💬 Academic Assistant":

    st.caption("🎓 AI-POWERED ACADEMIC SUPPORT")

    st.title("College Academic Assistant")

    st.write(
        "Ask questions about academics, regulations, "
        "examinations, internships and college guidelines."
    )

    st.write("")

    # -----------------------------------------------------
    # FEATURE CARDS
    # -----------------------------------------------------

    st.subheader("What can I help you with?")

    col1, col2, col3 = st.columns(3)

    with col1:

        with st.container(border=True):

            st.markdown("### 📚 College Knowledge")

            st.write(
                "Get answers using official college documents "
                "and academic resources."
            )

    with col2:

        with st.container(border=True):

            st.markdown("### 💬 Conversational AI")

            st.write(
                "Ask follow-up questions while maintaining "
                "conversation context."
            )

    with col3:

        with st.container(border=True):

            st.markdown("### 📅 Study Planning")

            st.write(
                "Create personalized study plans based on "
                "your subjects and examinations."
            )

    st.divider()

    # -----------------------------------------------------
    # CHAT
    # -----------------------------------------------------

    st.subheader("💬 Academic Assistant")

    if len(st.session_state.messages) == 0:

        st.info(
            "👋 Welcome! Ask me about college regulations, "
            "examinations, internships, syllabus or other "
            "academic information."
        )

        st.markdown("### 💡 Try asking")

        example_col1, example_col2 = st.columns(2)

        with example_col1:

            st.write(
                "• What is the attendance requirement?"
            )

            st.write(
                "• What are the internship guidelines?"
            )

        with example_col2:

            st.write(
                "• Explain the examination regulations."
            )

            st.write(
                "• Summarize the academic rules."
            )

    # -----------------------------------------------------
    # SHOW PREVIOUS MESSAGES
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if (
                message["role"] == "assistant"
                and message.get("sources")
            ):

                with st.expander("📚 View Sources"):

                    for source in message["sources"]:

                        st.write("📄", source)

    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    question = st.chat_input(
        "Ask your academic question..."
    )

    if question:

        # User message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):

            st.write(question)

        # -------------------------------------------------
        # TEMPORARY BACKEND RESPONSE
        # -------------------------------------------------
        #
        # Later your team's RAG + LangGraph + LLM
        # function will be connected here.
        #
        # -------------------------------------------------

        answer = (
            "This is a temporary response from the interface. "
            "The RAG + LangGraph + LLM backend will be connected "
            "here once the team provides the backend module."
        )

        sources = [
            "Academic Regulations.pdf",
            "Examination Guidelines.pdf"
        ]

        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources
            }
        )

        with st.chat_message("assistant"):

            st.write(answer)

            with st.expander("📚 View Sources"):

                for source in sources:

                    st.write("📄", source)


# =========================================================
# STUDY PLANNER
# =========================================================

elif page == "📅 Study Planner":

    st.caption("📅 PERSONALIZED ACADEMIC PLANNING")

    st.title("Personalized Study Planner")

    st.write(
        "Create a study schedule based on your subjects, "
        "available time and examination date."
    )

    st.divider()

    # -----------------------------------------------------
    # STUDENT DETAILS
    # -----------------------------------------------------

    st.subheader("👤 Student Details")

    col1, col2 = st.columns(2)

    with col1:

        student_name = st.text_input(
            "Student Name",
            placeholder="Enter your name"
        )

    with col2:

        semester = st.selectbox(
            "Semester",
            [
                "Select semester",
                "1st Semester",
                "2nd Semester",
                "3rd Semester",
                "4th Semester",
                "5th Semester",
                "6th Semester",
                "7th Semester",
                "8th Semester"
            ]
        )

    st.divider()

    # -----------------------------------------------------
    # SUBJECTS
    # -----------------------------------------------------

    st.subheader("📚 Subjects")

    subjects_text = st.text_area(
        "Enter your subjects",
        placeholder=(
            "Example:\n"
            "Database Management Systems\n"
            "Artificial Intelligence\n"
            "Computer Networks\n"
            "Software Engineering"
        ),
        height=140
    )

    st.divider()

    # -----------------------------------------------------
    # STUDY AVAILABILITY
    # -----------------------------------------------------

    st.subheader("⏰ Study Availability")

    col1, col2 = st.columns(2)

    with col1:

        study_hours = st.number_input(
            "Available study hours per day",
            min_value=1,
            max_value=12,
            value=3
        )

    with col2:

        exam_date = st.date_input(
            "Main examination date",
            value=date.today() + timedelta(days=30)
        )

    priority = st.selectbox(
        "Which type of subject needs more attention?",
        [
            "Equal priority",
            "Difficult subjects",
            "Subjects with earlier exams",
            "Weak subjects"
        ]
    )

    st.divider()

    # -----------------------------------------------------
    # GENERATE PLAN
    # -----------------------------------------------------

    generate = st.button(
        "✨ Generate Personalized Study Plan",
        use_container_width=True
    )

    if generate:

        if not student_name.strip():

            st.warning(
                "Please enter your name."
            )

        elif not subjects_text.strip():

            st.warning(
                "Please enter at least one subject."
            )

        elif exam_date <= date.today():

            st.warning(
                "Please select a future examination date."
            )

        else:

            subjects = [
                subject.strip()
                for subject in subjects_text.split("\n")
                if subject.strip()
            ]

            hours_each = round(
                study_hours / len(subjects),
                2
            )

            plan = []

            for subject in subjects:

                plan.append(
                    {
                        "subject": subject,
                        "hours": hours_each
                    }
                )

            st.session_state.study_plan = {
                "student": student_name,
                "semester": semester,
                "subjects": subjects,
                "hours": study_hours,
                "exam_date": exam_date,
                "priority": priority,
                "plan": plan
            }

            st.success(
                "✨ Your study plan has been generated!"
            )

    # -----------------------------------------------------
    # DISPLAY PLAN
    # -----------------------------------------------------

    if st.session_state.study_plan:

        data = st.session_state.study_plan

        st.divider()

        st.subheader("📖 Your Study Plan")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📚 Subjects",
                len(data["subjects"])
            )

        with col2:

            st.metric(
                "⏰ Hours / Day",
                data["hours"]
            )

        with col3:

            days_left = (
                data["exam_date"] - date.today()
            ).days

            st.metric(
                "📅 Days Until Exam",
                max(days_left, 0)
            )

        st.write("")

        st.success(
            f"Study plan created for **{data['student']}**."
        )

        # Plan cards
        for item in data["plan"]:

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.markdown(
                        f"### 📘 {item['subject']}"
                    )

                with col2:

                    st.write("")

                    st.markdown(
                        f"**{item['hours']} hrs/day**"
                    )

        st.divider()

        # -------------------------------------------------
        # MODIFY PLAN
        # -------------------------------------------------

        st.subheader("✏️ Modify Your Plan")

        modification = st.text_input(
            "Tell the assistant what you want to change",
            placeholder=(
                "Example: I can study only 2 hours tomorrow "
                "or give more time to DBMS."
            )
        )

        if st.button(
            "🔄 Update Study Plan",
            use_container_width=True
        ):

            if modification.strip():

                st.info(
                    "Modification received. The actual "
                    "LangGraph study-planner workflow will "
                    "recalculate the schedule here."
                )

            else:

                st.warning(
                    "Please describe what you want to change."
                )


# =========================================================
# ABOUT
# =========================================================

elif page == "ℹ️ About":

    st.caption("ℹ️ PROJECT INFORMATION")

    st.title("About the Project")

    st.write(
        "AI-Based College Academic Assistant"
    )

    st.divider()

    st.subheader("🎯 Project Objective")

    st.write(
        "The College Academic Assistant provides students "
        "with a single platform for:"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            "📚 College document-based question answering"
        )

        st.info(
            "💬 Conversational academic assistance"
        )

        st.info(
            "📅 Personalized study planning"
        )

    with col2:

        st.info(
            "🔄 Study-plan modification"
        )

        st.info(
            "📄 Source-based answers"
        )

    st.divider()

    st.subheader("🧠 Technologies")

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.markdown("### 🤖 LLM")

            st.write(
                "Used to generate natural-language answers."
            )

        with st.container(border=True):

            st.markdown("### 📚 RAG")

            st.write(
                "Retrieves relevant information from "
                "college documents."
            )

        with st.container(border=True):

            st.markdown("### 🔗 LangChain")

            st.write(
                "Connects the LLM, prompts, retrieval "
                "and tools."
            )

    with col2:

        with st.container(border=True):

            st.markdown("### 🔄 LangGraph")

            st.write(
                "Manages multi-step and stateful workflows."
            )

        with st.container(border=True):

            st.markdown("### 🗄️ Vector Database")

            st.write(
                "Stores document embeddings for "
                "semantic retrieval."
            )

        with st.container(border=True):

            st.markdown("### 🎨 Streamlit")

            st.write(
                "Provides the interactive web interface."
            )

    st.divider()

    st.success(
        "🎓 The interface is ready for integration with "
        "the team's RAG, LLM and LangGraph modules."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎓 College Academic Assistant • "
    "LLM + RAG + LangChain + LangGraph"
)