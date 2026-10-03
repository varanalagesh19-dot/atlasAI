"""IntelliPDF - Streamlit user interface (single file, eight tabs).

Run locally with the API on a second process::

    uvicorn backend.main:app --port 8000
    streamlit run frontend/app.py --server.port 8501

Run as a single process (Streamlit Community Cloud, Render, a single VPS)::

    streamlit run frontend/app.py

In that case the UI calls the FastAPI app in-process - see
``frontend/api_client.py`` - so no second server is required.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import streamlit as st

# Allow running as `streamlit run frontend/app.py` from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Streamlit Community Cloud keeps secrets in st.secrets, not os.environ, so
# mirror them before the backend config module reads the environment.
SECRET_KEYS = (
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_MODEL",
    "GEMINI_MODEL",
    "OLLAMA_URL",
    "OLLAMA_MODEL",
    "DEFAULT_LLM",
    "EMBEDDING_BACKEND",
    "EMBEDDING_MODEL",
    "SIMILARITY_THRESHOLD",
    "TOP_K",
    "HYBRID_DENSE_WEIGHT",
    "HYBRID_LEXICAL_WEIGHT",
    "MAX_UPLOAD_MB",
)
try:
    for _key in SECRET_KEYS:
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = str(st.secrets[_key])
except Exception:  # noqa: BLE001 - no secrets configured is normal locally
    pass

from backend.services.mark_wise import MARK_TYPES, marks_distribution  # noqa: E402
from backend.utils.language import LANGUAGE_LABELS  # noqa: E402
from frontend.api_client import get_transport  # noqa: E402

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# ── Theme ─────────────────────────────────────────────────────────────────
PRIMARY = "#1e3a8a"
ACCENT = "#fbbf24"
WHITE = "#ffffff"
BG = "#f6f8fc"

st.set_page_config(
    page_title="IntelliPDF",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
      .stApp {{ background: {BG}; }}
      .intelli-header {{
        background: linear-gradient(135deg, {PRIMARY} 0%, #2743a3 100%);
        color: {WHITE}; padding: 18px 24px; border-radius: 14px;
        margin-bottom: 14px; box-shadow: 0 4px 14px rgba(30,58,138,.25);
      }}
      .intelli-header h1 {{ margin: 0; font-size: 30px; color: {WHITE}; }}
      .intelli-header p {{ margin: 4px 0 0; color: #dbeafe; font-size: 15px; }}
      .card {{
        background: {WHITE}; border-radius: 14px; padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(15,23,42,.08); margin-bottom: 14px;
        border-left: 5px solid {PRIMARY};
      }}
      .card h3 {{ margin-top: 0; color: {PRIMARY}; }}
      .answer-body {{ font-size: 16px; line-height: 1.65; color: #111827; }}
      .source-chip {{
        display: inline-block; background: {ACCENT}; color: #1f2937;
        border-radius: 999px; padding: 3px 12px; margin: 4px 6px 4px 0;
        font-size: 13px; font-weight: 600; cursor: pointer;
      }}
      .metric-card {{
        background: {WHITE}; border-radius: 12px; padding: 14px;
        text-align: center; box-shadow: 0 2px 8px rgba(15,23,42,.08);
      }}
      .metric-card .value {{ font-size: 28px; font-weight: 700; color: {PRIMARY}; }}
      .metric-card .label {{ font-size: 13px; color: #475569; }}
      .flashcard {{
        background: {WHITE}; border-radius: 14px; padding: 16px 18px;
        border-left: 6px solid {ACCENT}; margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(15,23,42,.08);
      }}
      .flashcard .front {{ font-weight: 700; color: {PRIMARY}; margin-bottom: 6px; }}
      .flashcard .back {{ color: #1f2937; line-height: 1.6; }}
      .disclaimer {{
        font-size: 12px; color: #64748b; font-style: italic; text-align: center;
        padding-top: 10px;
      }}
      div.stButton > button, .stDownloadButton > button {{
        background: {ACCENT}; color: #1f2937; font-weight: 700;
        border: none; border-radius: 10px; padding: 0.45rem 1rem;
      }}
      div.stButton > button:hover {{ background: #f59e0b; color: #111827; }}
      .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
      .stTabs [data-baseweb="tab"] {{ background: #e2e8f0; border-radius: 8px 8px 0 0; }}
      .stTabs [aria-selected="true"] {{ background: {PRIMARY}; color: {WHITE}; }}
      .timer {{ font-size: 30px; font-weight: 800; color: {PRIMARY};
                text-align: center; padding: 8px; }}
      .stProgress > div > div > div {{ background: {ACCENT}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── API helpers ──────────────────────────────────────────────────────────
def api(method: str, path: str, **kwargs: Any) -> Any:
    """Call the backend and return parsed JSON, raising ``RuntimeError``.

    Works over HTTP when a separate API server is running, and in-process on
    single-process deployments (Streamlit Community Cloud).
    """
    transport = get_transport()
    try:
        response = transport.request(method, path, **kwargs)
    except Exception as exc:  # noqa: BLE001 - surfaced in the UI
        if transport.mode == "http":
            raise RuntimeError(
                f"Cannot reach the IntelliPDF API at {API_URL}. "
                "Start it with: uvicorn backend.main:app --port 8000"
            ) from exc
        raise RuntimeError(f"IntelliPDF request failed: {exc}") from exc
    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except ValueError:
            pass
        raise RuntimeError(f"API error {response.status_code}: {detail}")
    return response.json()


@st.cache_data(ttl=30)
def fetch_health() -> dict[str, Any] | None:
    """Return ``/health`` or ``None`` when the backend is unreachable."""
    try:
        transport = get_transport()
        if not transport.reachable():
            return None
        return transport.request("GET", "/health", timeout=10).json()
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(ttl=10)
def fetch_documents() -> list[dict[str, Any]]:
    """Return the list of uploaded documents."""
    try:
        return api("GET", "/documents")
    except RuntimeError:
        return []


def clear_caches() -> None:
    """Drop cached document/answer state after a mutation."""
    fetch_documents.clear()


# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div class='intelli-header'><h1>📘 IntelliPDF</h1>"
        "<p>Upload → Understand → Retrieve → Generate</p></div>",
        unsafe_allow_html=True,
    )
    health = fetch_health()
    if health is None:
        st.error("⚠️ API offline")
        st.caption(f"Expected the backend at `{API_URL}`.")
    else:
        services = health["services"]
        st.success("API online", icon="✅")
        st.caption(
            f"Mode: `{'in-process' if get_transport().mode != 'http' else 'HTTP'}` · "
            f"Embeddings: `{services['embedder']['model']}` · "
            f"LLM: `{services['llm']['active']}`"
        )

    st.markdown("---")
    language = st.selectbox(
        "🌐 Answer language",
        list(LANGUAGE_LABELS.keys()),
        format_func=lambda key: LANGUAGE_LABELS[key],
    )

    documents = fetch_documents()
    doc_ids = [doc["doc_id"] for doc in documents]
    doc_id = st.selectbox(
        "📚 Active document",
        doc_ids or [None],
        format_func=lambda value: (
            next(
                (d["filename"] for d in documents if d["doc_id"] == value),
                "no document uploaded",
            )
            if value
            else "no document uploaded"
        ),
    )
    if doc_id:
        meta = next(d for d in documents if d["doc_id"] == doc_id)
        st.caption(
            f"{meta['num_pages']} pages · {meta['num_chunks']} chunks · "
            f"`{meta['doc_id']}`"
        )

    st.markdown("---")
    st.caption(
        "Identifies topics for focused study; does not predict the actual "
        "question paper."
    )
    if health:
        st.caption(f"v{health.get('version', '1.0.0')} · SQuAD 2.0 evaluated")


# ── Header ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class='intelli-header'>
      <h1>📘 IntelliPDF</h1>
      <p>AI-Powered Personalized Learning and Exam Preparation System</p>
    </div>
    """,
    unsafe_allow_html=True,
)

upload_tab, ask_tab, quiz_tab, exam_tab, plan_tab, weak_tab, revision_tab, eval_tab = st.tabs(
    [
        "📤 Upload",
        "💬 Ask",
        "📝 Quiz",
        "🎯 Exam Mode",
        "📅 Study Plan",
        "🔍 Weak Topics",
        "⚡ Revision",
        "✅ Evaluate",
    ]
)


def require_doc() -> bool:
    """Show a hint and return ``False`` when no document is selected."""
    if not doc_id:
        st.info("👆 Upload a PDF in the **Upload** tab first.")
        return False
    return True


def show_sources(sources: list[dict[str, Any]]) -> None:
    """Render clickable page chips that open the PDF at the cited page."""
    if not sources:
        return
    st.markdown("**📄 Sources**")
    for source in sources:
        page = source.get("page", 0)
        heading = source.get("heading") or ""
        st.markdown(
            f"<span class='source-chip'>📄 Page {page}</span>"
            + (f"<span style='color:#475569;font-size:13px'>{heading[:60]}</span>"
               if heading else ""),
            unsafe_allow_html=True,
        )
        with st.expander(f"Open snippet - page {page}", expanded=False):
            st.caption(source.get("snippet", ""))
            if doc_id:
                st.markdown(
                    f"[🔗 Open PDF at page {page}]"
                    f"({API_URL}/documents/{doc_id}/file#page={page})"
                )


# ── 1. Upload ────────────────────────────────────────────────────────────
with upload_tab:
    st.subheader("📤 Upload a subject PDF")
    left, right = st.columns([2, 1])

    with left:
        uploaded = st.file_uploader(
            "Choose a PDF (ML / NLP / DBMS / Networks / any subject)",
            type=["pdf"],
            accept_multiple_files=False,
        )
        syllabus = st.text_area(
            "Optional syllabus / important topics (one per line)",
            placeholder=(
                "- Retrieval Augmented Generation\n- Vector Search\n"
                "- Evaluation metrics"
            ),
            height=120,
        )
        if st.button("🚀 Process PDF", type="primary", use_container_width=True):
            if uploaded is None:
                st.warning("Please choose a PDF first.")
            else:
                with st.spinner("Extracting text → chunking → embedding → indexing..."):
                    try:
                        result = api(
                            "POST",
                            "/upload",
                            files={"file": (uploaded.name, uploaded.getvalue(),
                                            "application/pdf")},
                            data={"syllabus": syllabus},
                        )
                    except RuntimeError as exc:
                        st.error(str(exc))
                    else:
                        clear_caches()
                        st.success(f"✅ {result['message']}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Document ID", result["doc_id"][:18] + "...")
                        c2.metric("Pages", result["num_pages"])
                        c3.metric("Chunks", result["num_chunks"])

    with right:
        st.markdown("##### 📖 How it works")
        st.markdown(
            """
1. **PyMuPDF** extracts text page by page
2. Headers/footers are stripped, whitespace repaired
3. **LangChain** splits the text (800 chars, 150 overlap)
4. **MiniLM** embeds every chunk into a 384-d vector
5. **FAISS** stores the vectors for instant similarity search
6. **SQLite** records metadata, quizzes and results
"""
        )
        if health:
            st.markdown("##### ⚙️ Active configuration")
            services = health["services"]
            st.json(
                {
                    "embeddings": services["embedder"]["model"],
                    "llm chain": services["llm"]["chain"],
                    "llm active": services["llm"]["active"],
                    "top_k": services["rag"]["top_k"],
                    "abstain below": services["rag"]["similarity_threshold"],
                    "languages": services["features"]["languages"],
                }
            )

    if documents:
        st.markdown("---")
        st.markdown("##### 📚 Uploaded documents")
        st.dataframe(
            [
                {
                    "doc_id": doc["doc_id"],
                    "filename": doc["filename"],
                    "pages": doc["num_pages"],
                    "chunks": doc["num_chunks"],
                    "uploaded_at": doc["uploaded_at"],
                }
                for doc in documents
            ],
            use_container_width=True,
            hide_index=True,
        )


# ── 2. Ask ───────────────────────────────────────────────────────────────
with ask_tab:
    st.subheader("💬 Ask anything from your PDF")
    if require_doc():
        question = st.text_input(
            "Question", placeholder="e.g. What is Retrieval Augmented Generation?"
        )
        mark_col, lang_col, btn_col = st.columns([1, 1, 1.4])
        with mark_col:
            mark_type = st.radio(
                "Marks",
                MARK_TYPES,
                horizontal=True,
                help="The answer length and structure follow the mark rule.",
            )
            st.caption(marks_distribution(mark_type))
        with lang_col:
            st.caption("Answer language")
            st.write(f"**{LANGUAGE_LABELS[language]}**")
        with btn_col:
            st.write("")
            ask_clicked = st.button("🔍 Get answer", type="primary",
                                    use_container_width=True)

        if ask_clicked:
            if not question.strip():
                st.warning("Type a question first.")
            else:
                with st.spinner("Retrieving context and writing the answer..."):
                    try:
                        answer = api(
                            "POST",
                            "/ask",
                            json={
                                "doc_id": doc_id,
                                "question": question,
                                "mark_type": mark_type,
                                "language": language,
                            },
                        )
                    except RuntimeError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["last_answer"] = answer

        answer = st.session_state.get("last_answer")
        if answer:
            confidence = answer.get("confidence", 0.0)
            cols = st.columns(4)
            cols[0].metric("🎯 Marks", answer["mark_type"])
            cols[1].metric("🧠 Confidence", f"{confidence:.2f}")
            cols[2].metric("✅ Label", answer["confidence_label"].title())
            cols[3].metric("⚡ Time", f"{answer.get('elapsed_ms', 0)} ms")
            st.markdown(
                f"<div class='card'><h3>📘 Answer ({answer['mark_type']} · "
                f"{LANGUAGE_LABELS[answer['language']]})</h3>"
                f"<div class='answer-body'>{answer['answer']}</div>"
                f"<hr><small>Generated by <b>{answer['provider']}</b> · "
                f"model: {answer.get('model', '-')}</small></div>",
                unsafe_allow_html=True,
            )
            st.button("📋 Copy answer", on_click=lambda: st.session_state.update(
                clipboard=answer["answer"]
            ))
            show_sources(answer.get("sources", []))


# ── 3. Quiz ──────────────────────────────────────────────────────────────
with quiz_tab:
    st.subheader("📝 Auto-generated MCQ quiz")
    if require_doc():
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            topic = st.text_input("Topic (optional)", placeholder="e.g. Vector Search")
        with c2:
            num_questions = st.slider("Questions", 1, 20, 5)
        with c3:
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])

        if st.button("🎯 Generate quiz", type="primary"):
            with st.spinner("Generating questions from your PDF..."):
                try:
                    quiz = api(
                        "POST",
                        "/quiz",
                        json={
                            "doc_id": doc_id,
                            "num_questions": num_questions,
                            "difficulty": difficulty,
                            "topic": topic,
                        },
                    )
                except RuntimeError as exc:
                    st.error(str(exc))
                else:
                    st.session_state["quiz"] = quiz
                    st.session_state["answers"] = {}
            if quiz.get("warning"):
                st.warning(quiz["warning"])

        quiz = st.session_state.get("quiz")
        if quiz:
            st.markdown(
                f"<div class='card'><h3>🧩 {len(quiz['questions'])} questions "
                f"· {quiz['difficulty']} · via {quiz['provider']}</h3></div>",
                unsafe_allow_html=True,
            )
            answers: dict[int, int] = st.session_state.setdefault("answers", {})
            for index, item in enumerate(quiz["questions"]):
                with st.container(border=True):
                    st.markdown(f"**Q{index + 1}. {item['question']}**")
                    st.caption(f"📄 Page {item['source_page']} · topic: {item['topic']}")
                    answers[index] = st.radio(
                        f"Q{index + 1} options",
                        range(len(item["options"])),
                        format_func=lambda option, item=item: (
                            f"{'ABCD'[option]}. {item['options'][option]}"
                        ),
                        key=f"quiz_{quiz['quiz_id']}_{index}",
                        horizontal=False,
                    )
            if st.button("📊 Submit quiz", type="primary"):
                ordered = [answers.get(index, -1) for index in range(len(quiz["questions"]))]
                try:
                    result = api(
                        "POST",
                        "/quiz/submit",
                        json={
                            "doc_id": doc_id,
                            "quiz_id": quiz["quiz_id"],
                            "answers": ordered,
                        },
                    )
                except RuntimeError as exc:
                    st.error(str(exc))
                else:
                    st.session_state["quiz_result"] = result

            result = st.session_state.get("quiz_result")
            if result:
                st.markdown(
                    f"<div class='card'><h3>🏁 Score: {result['score']}/"
                    f"{result['total']} ({result['percentage']}%)</h3></div>",
                    unsafe_allow_html=True,
                )
                st.progress(
                    min(1.0, result["percentage"] / 100),
                    text=f"{result['percentage']}% correct",
                )
                for index, feedback in enumerate(result["per_question_feedback"]):
                    icon = "✅" if feedback["is_correct"] else "❌"
                    with st.expander(
                        f"{icon} Q{index + 1} - {feedback['topic']} "
                        f"(page {feedback['source_page']})"
                    ):
                        st.write(feedback["question"])
                        if feedback["explanation"]:
                            st.info(feedback["explanation"])
                if result["weak_topics"]:
                    st.warning(
                        "⚠️ Weak topics detected: " + ", ".join(result["weak_topics"])
                    )


# ── 4. Exam mode ─────────────────────────────────────────────────────────
with exam_tab:
    st.subheader("🎯 Timed mock exam")
    if require_doc():
        c1, c2 = st.columns([1, 2])
        duration = c1.number_input("Duration (minutes)", 5, 240, 60, step=5)
        with c2:
            st.caption("Marks distribution")
            distribution = {
                mark: st.slider(
                    f"{mark}", 0, 10, default, key=f"dist_{mark}"
                )
                for mark, default in (("1M", 5), ("2M", 3), ("5M", 2),
                                      ("10M", 0), ("15M", 0), ("16M", 1))
            }
        distribution = {k: v for k, v in distribution.items() if v > 0}

        if st.button("⏱️ Start mock exam", type="primary"):
            with st.spinner("Setting the paper and the timer..."):
                try:
                    exam = api(
                        "POST",
                        "/mock-exam",
                        json={
                            "doc_id": doc_id,
                            "duration_minutes": int(duration),
                            "marks_distribution": distribution,
                        },
                    )
                except RuntimeError as exc:
                    st.error(str(exc))
                else:
                    st.session_state["exam"] = exam
                    st.session_state["exam_started"] = time.time()
                    st.session_state["exam_answers"] = {}

        exam = st.session_state.get("exam")
        if exam:
            total = exam["total_marks"]
            st.markdown(
                f"<div class='card'><h3>📄 Question paper · {total} marks · "
                f"{exam['duration_minutes']} minutes</h3>"
                f"<p>{exam['instructions']}</p></div>",
                unsafe_allow_html=True,
            )
            timer_col, submit_col = st.columns([1, 2])
            with timer_col:
                st.session_state["deadline"] = (
                    st.session_state.get("exam_started", time.time())
                    + exam["duration_minutes"] * 60
                )
                remaining = max(0, st.session_state["deadline"] - time.time())
                minutes, seconds = divmod(int(remaining), 60)
                st.markdown(
                    f"<div class='timer'>⏳ {minutes:02d}:{seconds:02d}</div>",
                    unsafe_allow_html=True,
                )
                st.caption("The server enforces the deadline on submit.")

            exam_answers: dict[str, str] = st.session_state.setdefault(
                "exam_answers", {}
            )
            for index, item in enumerate(exam["questions"]):
                key = f"q{index + 1}"
                with st.container(border=True):
                    st.markdown(f"**{key}. {item['question']}**")
                    st.caption(
                        f"🎯 {item['mark_type']} ({item['marks']} marks) · "
                        f"page {item['source_page']}"
                    )
                    exam_answers[key] = st.text_area(
                        "Your answer",
                        height=120,
                        key=f"exam_{exam['exam_id']}_{key}",
                    )

            with submit_col:
                st.write("")
                if st.button("📝 Submit paper", type="primary"):
                    with st.spinner("Grading every answer..."):
                        try:
                            graded = api(
                                "POST",
                                "/mock-exam/submit",
                                json={"exam_id": exam["exam_id"],
                                      "answers": exam_answers},
                            )
                        except RuntimeError as exc:
                            st.error(str(exc))
                        else:
                            st.session_state["exam_result"] = graded

            graded = st.session_state.get("exam_result")
            if graded:
                if graded["auto_submitted"]:
                    st.warning("⏰ Time was up - the paper was auto-submitted.")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Score", f"{graded['score']}/{graded['total_marks']}")
                m2.metric("Percentage", f"{graded['percentage']}%")
                m3.metric("Time used", f"{graded['time_used_minutes']} min")
                m4.metric("Status", "Auto" if graded["auto_submitted"] else "Manual")
                st.progress(min(1.0, graded["percentage"] / 100))
                for item in graded["results"]:
                    with st.expander(
                        f"{item['question_id']} · {item['mark_type']} · "
                        f"{item['score_earned']}/{item['score_out_of']}"
                    ):
                        st.write(item["question"])
                        if item["missing_points"]:
                            st.warning("Missing: " + "; ".join(item["missing_points"][:4]))
                        if item["suggestions"]:
                            st.info("Tip: " + "; ".join(item["suggestions"][:2]))
                st.caption(
                    "Displays analytics only — it does not predict the real "
                    "question paper."
                )
            if st.button("🔄 New paper"):
                for key in ("exam", "exam_result", "exam_answers", "deadline"):
                    st.session_state.pop(key, None)
                st.rerun()


# ── 5. Study plan ────────────────────────────────────────────────────────
with plan_tab:
    st.subheader("📅 AI study plan")
    if require_doc():
        c1, c2 = st.columns([1, 1])
        default_exam = date.today() + timedelta(days=7)
        exam_date = c1.date_input("📆 Exam date", value=default_exam)
        daily_hours = c2.slider("⏳ Study hours per day", 0.5, 12.0, 3.0, 0.5)

        if st.button("🧠 Generate plan", type="primary"):
            with st.spinner("Weighing topics and scheduling your days..."):
                try:
                    plan = api(
                        "POST",
                        "/study-plan",
                        json={
                            "doc_id": doc_id,
                            "exam_date": exam_date.isoformat(),
                            "daily_hours": daily_hours,
                        },
                    )
                except (RuntimeError, ValueError) as exc:
                    st.error(str(exc))
                else:
                    st.session_state["plan"] = plan

        plan = st.session_state.get("plan")
        if plan:
            c1, c2, c3 = st.columns(3)
            c1.metric("Days left", plan["days_left"])
            c2.metric("Total hours", f"{plan['total_hours']} h")
            c3.metric("Topics", len(plan["topics"]))
            if plan["weak_topics"]:
                st.warning("⚠️ Weighted 1.5x: " + ", ".join(plan["weak_topics"]))
            for day in plan["plan"]:
                icon = "🔥" if "revision" in day["focus"].lower() else "📘"
                with st.container(border=True):
                    st.markdown(
                        f"**{icon} Day {day['day_num']} · {day['date']} · "
                        f"{day['total_hours']} h**"
                    )
                    st.caption(day["focus"])
                    for topic in day["topics"]:
                        badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            topic["priority"], "⚪"
                        )
                        st.markdown(
                            f"- {badge} **{topic['name']}** — "
                            f"{topic['hours']} h _({topic['reason']})_"
                        )
            st.caption(plan["disclaimer"])


# ── 6. Weak topics ───────────────────────────────────────────────────────
with weak_tab:
    st.subheader("🔍 Weak topic analysis")
    if require_doc():
        if st.button("📊 Refresh analysis", type="primary"):
            try:
                report = api("GET", f"/weak-topics/{doc_id}")
                st.session_state["weak"] = report
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                try:
                    stats = api("GET", f"/quiz-stats/{doc_id}")
                    st.session_state["stats"] = stats
                except RuntimeError:
                    pass

        report = st.session_state.get("weak")
        if report is None:
            try:
                report = api("GET", f"/weak-topics/{doc_id}")
                st.session_state["weak"] = report
            except RuntimeError:
                report = None

        if report:
            c1, c2, c3 = st.columns(3)
            c1.metric("Attempts", report["attempts"])
            c2.metric("Average score", f"{report['average_score'] * 100:.0f}%")
            c3.metric("Weak topics", len(report["weak_topics"]))

            if report["topics"]:
                import pandas as pd
                import plotly.express as px

                frame = pd.DataFrame(report["topics"])
                chart = px.bar(
                    frame.sort_values("accuracy"),
                    x="accuracy",
                    y="topic",
                    orientation="h",
                    color="accuracy",
                    color_continuous_scale=["#dc2626", "#fbbf24", "#16a34a"],
                    range_x=[0, 1],
                    title="Accuracy per topic (red = weak)",
                )
                chart.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white", height=380,
                    font=dict(color="#1e293b"),
                )
                st.plotly_chart(chart, use_container_width=True)
                st.dataframe(frame, use_container_width=True, hide_index=True)
                if report["weak_topics"]:
                    st.warning(
                        "🎯 Focus next on: " + ", ".join(report["weak_topics"])
                    )
            else:
                st.info("Take a quiz first - accuracy per topic appears here.")


# ── 7. Revision ──────────────────────────────────────────────────────────
with revision_tab:
    st.subheader("⚡ Last-minute revision")
    if require_doc():
        c1, c2 = st.columns([1, 1])
        mode = c1.selectbox(
            "Mode",
            ["last_minute", "definitions", "key_concepts"],
            format_func=lambda value: {
                "last_minute": "⚡ Last-minute mix",
                "definitions": "📖 Definitions",
                "key_concepts": "💡 Key concepts",
            }[value],
        )
        num_cards = c2.slider("Cards", 3, 20, 8)

        if st.button("🃏 Generate flashcards", type="primary"):
            with st.spinner("Picking the highest-yield points..."):
                try:
                    revision = api(
                        "POST",
                        "/revision",
                        json={
                            "doc_id": doc_id,
                            "mode": mode,
                            "num_cards": num_cards,
                            "language": language,
                        },
                    )
                except RuntimeError as exc:
                    st.error(str(exc))
                else:
                    st.session_state["cards"] = revision

        revision = st.session_state.get("cards")
        if revision:
            if mode == "definitions" and st.checkbox("🔁 Flip cards (show answers)"):
                for card in revision["cards"]:
                    st.markdown(
                        f"<div class='flashcard'><div class='front'>"
                        f"{card['front']}</div>"
                        f"<div class='back'>🙈 {card['back']}<br>"
                        f"<small>📄 Page {card['source_page']}</small></div></div>",
                        unsafe_allow_html=True,
                    )
            else:
                for card in revision["cards"]:
                    st.markdown(
                        f"<div class='flashcard'><div class='front'>"
                        f"{card['front']}</div>"
                        f"<div class='back'>{card['back']}<br>"
                        f"<small>📄 Page {card['source_page']}</small></div></div>",
                        unsafe_allow_html=True,
                    )
            if st.button("🔄 Shuffle new set"):
                st.session_state.pop("cards", None)
                st.rerun()


# ── 8. Evaluate ──────────────────────────────────────────────────────────
with eval_tab:
    st.subheader("✅ Answer evaluation")
    if require_doc():
        question = st.text_input("Question", placeholder="e.g. Explain FAISS indexing")
        student_answer = st.text_area(
            "Your answer", height=160,
            placeholder="Paste the answer you wrote in the exam...",
        )
        mark_type = st.selectbox("Marks", MARK_TYPES, index=2)
        st.caption(marks_distribution(mark_type))

        if st.button("🧐 Evaluate answer", type="primary"):
            if not question.strip() or not student_answer.strip():
                st.warning("Fill in both the question and your answer.")
            else:
                with st.spinner("Comparing with the source..."):
                    try:
                        result = api(
                            "POST",
                            "/evaluate",
                            json={
                                "doc_id": doc_id,
                                "question": question,
                                "student_answer": student_answer,
                                "mark_type": mark_type,
                            },
                        )
                    except RuntimeError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["evaluation"] = result

        result = st.session_state.get("evaluation")
        if result:
            c1, c2 = st.columns([1, 3])
            c1.metric("Score", f"{result['score_earned']}/{result['score_out_of']}")
            c2.metric("Percentage", f"{result['percentage']}%")
            st.progress(min(1.0, result["percentage"] / 100))

            st.markdown(
                f"<div class='card'><h3>📘 Model answer</h3>"
                f"<div class='answer-body'>{result['model_answer']}</div></div>",
                unsafe_allow_html=True,
            )
            if result["missing_points"]:
                st.markdown("##### ❌ Missing points")
                for point in result["missing_points"]:
                    st.markdown(f"- {point}")
            if result["incorrect_points"]:
                st.markdown("##### ⚠️ Incorrect statements")
                for point in result["incorrect_points"]:
                    st.markdown(f"- {point}")
            if result["suggestions"]:
                st.markdown("##### 💡 How to improve")
                for point in result["suggestions"]:
                    st.markdown(f"- {point}")
            show_sources(result.get("sources", []))


st.markdown(
    "<p class='disclaimer'>Foundations: NLP → Text Embeddings → Vector Search "
    "→ RAG → LLMs · Dataset: SQuAD 2.0 · IntelliPDF identifies topics for "
    "focused study; it does not predict the actual question paper.</p>",
    unsafe_allow_html=True,
)