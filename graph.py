"""LangGraph workflow: analysis -> retrieval -> generation -> review, plus planner and tool branches."""
import json
import re
from datetime import date
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from planner import apply_changes, build_plan, format_plan
from study_tools import add_days, calculator, days_until

# ---------------------------------------------------------------- state
class AssistantState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]   # conversation memory
    question: str
    standalone_question: str      # follow-up rewritten as a full question
    intent: str
    docs: list[dict]
    answer: str
    review_ok: bool
    review_feedback: str
    retries: int
    # planner (persisted across turns by the checkpointer)
    profile: dict
    plan: list[dict]
    # optional structured inputs from the UI (forms) - skip the LLM parsing
    study_input: dict             # {"subjects":[...], "daily_hours": 4}
    plan_changes: list[dict]      # [{"action":"set_exam_date","subject":"Maths","date":"2026-11-25"}]


# ---------------------------------------------------------------- prompts (replace with yours if you have them)
QA_PROMPT = ChatPromptTemplate.from_template(
    """You are a college academic assistant. Answer ONLY from the context below.
If the context does not contain the answer, say you could not find it.

Conversation so far:
{history}

Context:
{context}

Question: {question}
{feedback}
Answer clearly and mention the source document names."""
)

SUMMARY_PROMPT = ChatPromptTemplate.from_template(
    """Summarize the following college document content for a student in short, clear points.
Use ONLY the context.

Context:
{context}

Request: {question}
{feedback}"""
)

INTENTS = ["qa", "summarize", "create_plan", "modify_plan", "show_plan",
           "calculate", "date_calc", "chitchat"]
MAX_HISTORY = 6


# ---------------------------------------------------------------- helpers
def _last_user_text(state):
    for m in reversed(state["messages"]):
        if m.type == "human":
            return m.content
    return ""


def _history(messages, n=MAX_HISTORY):
    lines = []
    for m in messages[:-1][-n:]:
        who = "Student" if m.type == "human" else "Assistant"
        lines.append(f"{who}: {m.content}")
    return "\n".join(lines) or "(none)"


def _json(llm, prompt):
    raw = llm.invoke(prompt).content
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _rule_intent(q: str, has_plan: bool) -> str:
    """Keyword fallback when the LLM output cannot be parsed."""
    ql = q.lower()
    if any(k in ql for k in ["calculate", "cgpa", "sgpa", "percentage", "average of"]) or re.search(r"\d+\s*[\+\-\*/x]\s*\d+", ql):
        return "calculate"
    if any(k in ql for k in ["days left", "days until", "how many days", "weeks left"]):
        return "date_calc"
    if has_plan and any(k in ql for k in ["change", "postpone", "prepone", "reschedule", "update", "modify", "add subject", "remove", "instead", "only have"]):
        return "modify_plan"
    if any(k in ql for k in ["show my plan", "my plan", "my schedule"]):
        return "show_plan"
    if any(k in ql for k in ["study plan", "make a plan", "create a plan", "timetable", "schedule"]):
        return "create_plan"
    if any(k in ql for k in ["summarize", "summary", "summarise"]):
        return "summarize"
    if ql.strip() in {"hi", "hello", "hey", "thanks", "thank you"}:
        return "chitchat"
    return "qa"


def _ai(text, **extra):
    return {"messages": [AIMessage(content=text)], "answer": text, **extra}


# ---------------------------------------------------------------- graph builder
def build_graph(llm, retriever, max_retries: int = 1, checkpointer=None):
    """
    llm       : any LangChain chat model (your existing one)
    retriever : any LangChain retriever (your existing RAG retriever).
                For 'unknown question' handling use a score-threshold retriever, e.g.
                vectorstore.as_retriever(search_type="similarity_score_threshold",
                                         search_kwargs={"score_threshold": 0.3, "k": 4})
    """

    # ---- Node 1: question analysis ------------------------------------
    def analyze(state: AssistantState):
        q = _last_user_text(state)
        has_plan = bool(state.get("profile"))
        base_reset = {"question": q, "docs": [], "answer": "", "review_ok": False,
                      "review_feedback": "", "retries": 0}

        # structured UI input has priority (form submit / edit buttons)
        if state.get("study_input"):
            return {**base_reset, "intent": "create_plan", "standalone_question": q}
        if state.get("plan_changes"):
            return {**base_reset, "intent": "modify_plan", "standalone_question": q}

        prompt = f"""Classify the student's latest message and rewrite it as a standalone question
using the conversation (resolve words like "it", "that", "those").
Intents: {INTENTS}
- qa: question about syllabus, rules, exams, internships, FAQs
- summarize: summarize a document/topic
- create_plan: wants a new study plan
- modify_plan: wants to change an existing plan (deadline, hours, subjects)
- show_plan: wants to see current plan
- calculate: math / CGPA / percentage
- date_calc: days until a date / date arithmetic
- chitchat: greeting/thanks
A study plan currently exists: {has_plan}

Conversation:
{_history(state['messages'])}

Latest message: {q}

Reply ONLY with JSON: {{"intent": "...", "standalone_question": "..."}}"""
        data = _json(llm, prompt) or {}
        intent = data.get("intent")
        if intent not in INTENTS:
            intent = _rule_intent(q, has_plan)
        if intent == "modify_plan" and not has_plan:
            intent = "create_plan"
        return {**base_reset, "intent": intent,
                "standalone_question": data.get("standalone_question") or q}

    def route_after_analyze(state):
        return {
            "qa": "retrieve", "summarize": "retrieve",
            "create_plan": "plan_create", "modify_plan": "plan_modify",
            "show_plan": "plan_show",
            "calculate": "tool_node", "date_calc": "tool_node",
            "chitchat": "chitchat",
        }[state["intent"]]

    # ---- Node 2: retrieval ---------------------------------------------
    def retrieve(state: AssistantState):
        docs = retriever.invoke(state["standalone_question"])
        out = [{"text": d.page_content,
                "source": d.metadata.get("source", d.metadata.get("file_name", "college document"))}
               for d in docs if d.page_content.strip()]
        return {"docs": out}

    def route_after_retrieve(state):
        return "generate" if state.get("docs") else "no_answer"

    # ---- unknown-question handler --------------------------------------
    def no_answer(state: AssistantState):
        return _ai("I could not find this information in the college documents I have access to. "
                   "Please check with your department office or the examination cell for an "
                   "accurate answer. You can also rephrase the question or ask about syllabus, "
                   "regulations, exams or internships.")

    # ---- Node 3: answer generation -------------------------------------
    def generate(state: AssistantState):
        context = "\n\n".join(f"[{d['source']}]\n{d['text']}" for d in state["docs"])
        fb = state.get("review_feedback", "")
        feedback = f"\nA reviewer rejected the previous answer: {fb}\nFix this." if fb else ""
        template = SUMMARY_PROMPT if state["intent"] == "summarize" else QA_PROMPT
        msg = (template | llm).invoke({
            "history": _history(state["messages"]),
            "context": context,
            "question": state["standalone_question"],
            "feedback": feedback,
        })
        return {"answer": msg.content}

    # ---- Node 4: response review ---------------------------------------
    def review(state: AssistantState):
        context = "\n\n".join(d["text"] for d in state["docs"])
        verdict = llm.invoke(
            f"""You are a strict reviewer. Check whether the ANSWER is fully supported by the CONTEXT
and actually answers the QUESTION. Do not accept invented facts.

QUESTION: {state['standalone_question']}
CONTEXT: {context}
ANSWER: {state['answer']}

Reply with 'PASS' or 'FAIL: <short reason>'."""
        ).content.strip()
        ok = verdict.upper().startswith("PASS")
        retries = state.get("retries", 0)
        if ok or retries >= max_retries:
            sources = sorted({d["source"] for d in state["docs"]})
            final = state["answer"]
            if not ok:
                final += "\n\n(Note: this answer could not be fully verified. Please confirm with the college office.)"
            final += "\n\nSources: " + ", ".join(sources)
            return {"review_ok": True, "messages": [AIMessage(content=final)], "answer": final}
        return {"review_ok": False, "review_feedback": verdict, "retries": retries + 1}

    def route_after_review(state):
        return END if state.get("review_ok") else "generate"

    # ---- Tool node (calculator + date tools) ---------------------------
    def tool_node(state: AssistantState):
        q = state["standalone_question"]
        today = date.today().isoformat()
        if state["intent"] == "calculate":
            data = _json(llm, f'Extract ONE arithmetic expression (digits and + - * / ** % parentheses only) '
                              f'from: "{q}". Reply ONLY JSON: {{"expression": "..."}}') or {}
            expr = data.get("expression") or "".join(re.findall(r"[\d\.\+\-\*/\(\)%\s]", q)).strip()
            if not expr:
                return _ai("Please give me the numbers/expression to calculate.")
            res = calculator.invoke({"expression": expr})
            return _ai(f"{expr} = **{res}**")
        data = _json(llm, f"""Today is {today}. From: "{q}"
Choose op "days_until" (needs date) or "add_days" (needs date and days).
Reply ONLY JSON: {{"op": "...", "date": "YYYY-MM-DD", "days": 0}}""") or {}
        if not data.get("date"):
            m = re.search(r"\d{4}-\d{2}-\d{2}", q)
            data = {"op": "days_until", "date": m.group(0) if m else None}
        if not data.get("date"):
            return _ai("Please give the date in YYYY-MM-DD format, e.g. 2026-11-20.")
        if data.get("op") == "add_days":
            return _ai(add_days.invoke({"start_date": data["date"], "days": int(data.get("days", 0))}))
        return _ai(days_until.invoke({"target_date": data["date"]}))

    # ---- Planner nodes -------------------------------------------------
    def plan_create(state: AssistantState):
        info = state.get("study_input")
        if not info:
            info = _json(llm, f"""Today is {date.today().isoformat()}.
Extract a study-plan request from: "{state['standalone_question']}"
Reply ONLY JSON:
{{"subjects": [{{"name": "...", "exam_date": "YYYY-MM-DD", "difficulty": 1-5}}], "daily_hours": number}}
Use null for anything not stated. Difficulty defaults to 3.""") or {}
        subjects = [s for s in info.get("subjects") or [] if s.get("name") and s.get("exam_date")]
        hours = info.get("daily_hours")
        if not subjects or not hours:
            return {**_ai("To build your plan I need: (1) your subjects with exam dates "
                          "(e.g. Maths 2026-11-20), and (2) how many hours you can study per day. "
                          "Optionally tell me which subjects are hardest (1-5)."),
                    "study_input": None}
        profile = {"subjects": [{"name": s["name"], "exam_date": s["exam_date"],
                                 "difficulty": int(s.get("difficulty") or 3)} for s in subjects],
                   "daily_hours": float(hours), "day_overrides": {}}
        plan, warns = build_plan(profile)
        text = format_plan(plan, warns) + "\n\nYou can edit this: change an exam date, daily hours, add or remove a subject."
        return {**_ai(text), "profile": profile, "plan": plan, "study_input": None}

    def plan_modify(state: AssistantState):
        profile = state.get("profile")
        if not profile:
            return {**_ai("You do not have a study plan yet. Tell me your subjects, exam dates and daily hours first."),
                    "plan_changes": None}
        changes = state.get("plan_changes")
        if not changes:
            data = _json(llm, f"""Today is {date.today().isoformat()}.
Current plan profile: {json.dumps(profile)}
Student request: "{state['standalone_question']}"
Convert it into changes. Allowed actions:
set_exam_date {{subject, date}}, set_daily_hours {{hours}}, set_day_hours {{date, hours}},
add_subject {{subject, date, difficulty}}, remove_subject {{subject}}, set_difficulty {{subject, difficulty}}
Dates must be YYYY-MM-DD. Reply ONLY JSON: {{"changes": [{{"action": "...", ...}}]}}""") or {}
            changes = data.get("changes") or []
        if not changes:
            return {**_ai("I could not understand what to change. Try: 'move Maths exam to 2026-11-25' "
                          "or 'I can only study 3 hours a day'."), "plan_changes": None}
        new_profile, notes = apply_changes(profile, changes)
        plan, warns = build_plan(new_profile)            # <- recalculation
        text = ("**Changes applied**\n" + "\n".join(f"- {n}" for n in notes) +
                "\n\n" + format_plan(plan, warns))
        return {**_ai(text), "profile": new_profile, "plan": plan, "plan_changes": None}

    def plan_show(state: AssistantState):
        if not state.get("profile"):
            return _ai("You do not have a study plan yet. Tell me your subjects, exam dates and daily hours.")
        plan, warns = build_plan(state["profile"])       # always up to date with today's date
        return {**_ai(format_plan(plan, warns)), "plan": plan}

    def chitchat(state: AssistantState):
        return _ai("Hi! I can answer questions from college documents, summarize them, "
                   "build and edit your study plan, and do quick calculations or date counts. What do you need?")

    # ---- wiring --------------------------------------------------------
    g = StateGraph(AssistantState)
    for name, fn in [("analyze", analyze), ("retrieve", retrieve), ("no_answer", no_answer),
                     ("generate", generate), ("review", review), ("tool_node", tool_node),
                     ("plan_create", plan_create), ("plan_modify", plan_modify),
                     ("plan_show", plan_show), ("chitchat", chitchat)]:
        g.add_node(name, fn)

    g.add_edge(START, "analyze")
    g.add_conditional_edges("analyze", route_after_analyze,
                            ["retrieve", "plan_create", "plan_modify", "plan_show", "tool_node", "chitchat"])
    g.add_conditional_edges("retrieve", route_after_retrieve, ["generate", "no_answer"])
    g.add_edge("generate", "review")
    g.add_conditional_edges("review", route_after_review, ["generate", END])
    for terminal in ["no_answer", "tool_node", "plan_create", "plan_modify", "plan_show", "chitchat"]:
        g.add_edge(terminal, END)

    return g.compile(checkpointer=checkpointer or MemorySaver())


# ---------------------------------------------------------------- convenience API for the UI
def ask(app, text: str, thread_id: str = "student-1", **structured):
    """Send one message. `structured` may carry study_input=... or plan_changes=..."""
    cfg = {"configurable": {"thread_id": thread_id}}
    out = app.invoke({"messages": [("user", text)], **structured}, cfg)
    return out["messages"][-1].content
