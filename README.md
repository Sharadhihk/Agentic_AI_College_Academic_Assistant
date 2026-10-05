🎓 AI-Based College Academic Assistant
An AI-powered academic assistant that helps students get college-specific information, answer academic questions, summarize documents, and create personalized study plans using LLMs, RAG, LangChain, and LangGraph.
🚀 Features
- 📚 College Document Q&A using Retrieval-Augmented Generation (RAG)
- 🔍 Semantic search across college documents
- 🤖 LLM-powered responses using Groq
- 🔄 LangGraph workflow for intent analysis, retrieval, generation, and response review
- 📝 Document summarization
- 📅 Personalized study-plan generation based on subjects, difficulty, available study hours, and exam dates
- ✏️ Study-plan modification
- 🧮 Calculator and date-based tools
- 💬 Conversational follow-up questions
- 🛡️ Unknown-question handling when information is not available in the provided documents
- 🖥️ Streamlit user interface
🛠️ Tech Stack
- Python
- Groq LLM
- LangChain
- LangGraph
- Retrieval-Augmented Generation (RAG)
- ChromaDB
- HuggingFace Embeddings
- Streamlit
🏗️ System Workflow
Student Query
     ↓
Streamlit UI
     ↓
LangGraph
     ↓
Intent Analysis
     ↓
 ┌───────────────┬────────────────┐
 ↓               ↓                ↓
RAG Retrieval   Study Planner    Tools
 ↓               ↓                ↓
College Docs    Personalized     Calculator/
 ↓               Plan             Date Tools
 └───────────────┴────────────────┘
                 ↓
            Groq LLM
                 ↓
          Reviewed Response
                 ↓
            Student UI

📂 Project Structure
Agentic_AI_College_Academic_Assistant/
│
├── app.py
├── graph.py
├── planner.py
├── study_tools.py
├── requirements.txt
├── README.md
│
├── data/
│   └── college documents
│
└── notebooks/
    └── RAG implementation

⚙️ Installation
Clone the repository:
git clone https://github.com/Sharadhihk/Agentic_AI_College_Academic_Assistant.git
cd Agentic_AI_College_Academic_Assistant

Install dependencies:
pip install -r requirements.txt

Create a .env file and add your Groq API key:
GROQ_API_KEY=your_api_key_here

▶️ Run the Application
streamlit run app.py

The application will open in your browser.
👥 Project
Developed as an Agentic AI College Academic Assistant project using LLM, RAG, LangChain, and LangGraph to provide students with an intelligent and personalized academic support system.
