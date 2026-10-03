# 📘 IntelliPDF

**AI-Powered Personalized Learning and Exam Preparation System**
*Upload any subject PDF → Understand → Retrieve → Generate*

Upload a lecture PDF (ML, NLP, DBMS, Networks, …) and IntelliPDF turns it into an
exam-preparation platform: **mark-wise answers**, **source-grounded Q&A**,
**auto-generated quizzes**, a **study plan built around your exam date**,
**weak-topic detection**, **answer evaluation**, **timed mock exams**,
**last-minute revision**, and answers in **English / தமிழ் / Tanglish**.

> *Identifies topics for focused study; does not predict the actual question paper.*

---

## 📁 Project structure

```
intellipdf/
├── backend/
│   ├── main.py                     FastAPI app, CORS, lifespan, /health
│   ├── config.py                   .env loading, paths, retrieval constants
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py               POST /upload, document CRUD, PDF streaming
│   │   ├── chat.py                 POST /ask, capabilities, retrieval preview
│   │   ├── quiz.py                 POST /quiz, /quiz/submit, /weak-topics/{doc_id}
│   │   ├── evaluate.py             POST /evaluate
│   │   ├── study_plan.py           POST /study-plan, POST /revision
│   │   └── mock_exam.py            POST /mock-exam, timer, grading
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py        PyMuPDF extraction, header/footer stripping
│   │   ├── chunker.py              LangChain RecursiveCharacterTextSplitter
│   │   ├── embedder.py             MiniLM-L6-v2 (+ offline hashing fallback)
│   │   ├── vector_store.py         FAISS IndexFlatIP persistence (+ NumPy)
│   │   ├── rag_pipeline.py         retrieve → prompt → generate → sources
│   │   ├── llm_client.py           Groq → Gemini → Ollama fallback chain
│   │   ├── mark_wise.py            1M/2M/5M/10M/15M/16M answer rules
│   │   ├── quiz_gen.py             MCQ generation + JSON-safe parsing
│   │   ├── evaluator.py            answer grading vs. the source
│   │   ├── study_planner.py        weighted day-wise schedule
│   │   ├── revision.py             last-minute / definition / concept cards
│   │   └── weak_topics.py          per-topic accuracy from quiz history
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              every request/response model
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── language.py             english / tamil / tanglish instructions
│   │   ├── metadata.py             doc ids, filenames, JSON helpers
│   │   └── db.py                   SQLite schema + helpers
│   └── data/
│       ├── uploads/                stored PDFs
│       ├── vector_db/              {doc_id}.faiss + {doc_id}_meta.pkl
│       └── intellipdf.db           documents · quizzes · results · plans
├── frontend/
│   └── app.py                      Streamlit UI, 8 tabs
├── evaluation/
│   ├── squad_eval.py               SQuAD 2.0 → EM / F1 / answerability
│   └── threshold_sweep.py          calibrates the abstention threshold
├── tests/
│   ├── test_pipeline.py            28 pytest cases
│   ├── e2e_check.py               end-to-end smoke test of every endpoint
│   └── conftest.py
├── requirements.txt
├── .env.example
├── run.sh
└── README.md
```

---

## 🏗️ Architecture

```
                    ┌──────────────────────────────────────────┐
                    │        Streamlit UI  (port 8501)         │
                    │  Upload · Ask · Quiz · Exam · Plan ·     │
                    │  Weak Topics · Revision · Evaluate        │
                    └───────────────────┬──────────────────────┘
                                        │ HTTP (JSON)
                    ┌───────────────────▼──────────────────────┐
                    │        FastAPI  (port 8000 /docs)        │
                    │  upload · chat · quiz · evaluate ·       │
                    │  study_plan · mock_exam · health         │
                    └──┬────────────────────────────────┬───────┘
                       │                                │
       ┌───────────────▼──────────────┐   ┌─────────────▼─────────────┐
       │  INDEXING  (once per upload) │   │  GENERATION (per request) │
       │                             │   │                           │
       │  PDF ─► PyMuPDF extract      │   │  question ─► embed        │
       │      strip headers/footers   │   │  FAISS top-k + IDF lexical│
       │      de-hyphenate, collapse  │   │  hybrid re-rank           │
       │      ▼                      │   │  ▼                        │
       │  LangChain Recursive        │   │  mark rule (1M…16M)       │
       │  splitter 800 / overlap 150  │   │  language rule (en/ta/tan)│
       │      ▼                      │   │  [Page X] context         │
       │  MiniLM-L6-v2 (384-d, L2)   │   │  ▼                        │
       │      ▼                      │   │  Groq → Gemini → Ollama   │
       │  FAISS IndexFlatIP          │   │  ▼                        │
       │   {doc_id}.faiss + _meta.pkl│   │  answer + sources + score │
       └─────────────────────────────┘   └─────────────┬─────────────┘
                                                     │ fallback
                                                     ▼
                                     offline extractive answer /
                                     heuristic MCQs / lexical grading
       ┌──────────────────────────────────────────────────────────┐
       │  SQLite: documents · quizzes · quiz_results · study_plans│
       └──────────────────────────────────────────────────────────┘
```

**Pipeline (per question)**

1. **Embed** the question with `all-MiniLM-L6-v2` (normalised → cosine).
2. **Search** FAISS `IndexFlatIP` for top-5 chunks; re-rank with a hybrid score
   `0.6 · dense + 0.4 · IDF-weighted lexical overlap` (recovers exact-term
   matches that pure cosine misses on short documents).
3. **Abstain** if the combined top score < `SIMILARITY_THRESHOLD` (default
   0.12, calibrated — see *Evaluation*).
4. **Compose** the prompt: system role + `[Page X]` context + mark rule +
   language rule + question.
5. **Generate** with Groq → Gemini → Ollama, whichever answers first.
6. **Ground** the reply in the retrieved chunks → source chips with page numbers.

---

## ⚡ 5-minute quickstart

```bash
cd intellipdf

python -m venv .venv                       # Windows: py -3 -m venv .venv
source .venv/bin/activate                  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env                       # optional: add your Groq key

# Option A - one command (API + UI together)
./run.sh                                   # or: run.sh setup && run.sh

# Option B - two terminals
uvicorn backend.main:app --reload --port 8000
streamlit run frontend/app.py --server.port 8501
```

Then open:

| Service | URL |
|---|---|
| Streamlit UI | <http://localhost:8501> |
| API docs (Swagger) | <http://127.0.0.1:8000/docs> |
| Health probe | <http://127.0.0.1:8000/health> |

Upload `sample_features.pdf` (bundled) and the **Ask** tab works immediately —
**no API key required**.

> **First run downloads `all-MiniLM-L6-v2` (~90 MB) from Hugging Face.** After
> that everything runs locally. Without a model download the embedder silently
> falls back to a deterministic hashing embedder, so the app still runs offline.

---

## 🔑 Free API keys (optional but recommended)

IntelliPDF works without keys using the offline extractive fallback. Adding one
free key upgrades every feature to full LLM quality.

### Groq (primary) — <https://console.groq.com/keys>

1. Sign in → **API Keys** → **Create API Key**.
2. Copy it and put it in `.env`:

   ```ini
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
   GROQ_MODEL=llama-3.1-70b-versatile
   ```

3. Verify: `curl http://127.0.0.1:8000/health | grep active`

Free tier: generous RPM with no card required.

### Google Gemini (fallback) — <https://aistudio.google.com/app/apikey>

1. Sign in with a Google account → **Get API key**.
2. Add to `.env`:

   ```ini
   GEMINI_API_KEY=AIzaSy...
   GEMINI_MODEL=gemini-1.5-flash
   ```

### Ollama (fully local, free forever) — <https://ollama.com/download>

```bash
ollama pull llama3          # run this once
```

The app auto-detects `http://localhost:11434`; no key, no internet.

---

## 🔌 API reference

| # | Method | Endpoint | Purpose |
|---|---|---|---|
| 1 | POST | `/upload` | Save → extract → chunk → embed → index a PDF |
| 2 | POST | `/ask` | Mark-wise, source-grounded answer |
| 3 | POST | `/quiz` | Generate MCQs |
| 4 | POST | `/quiz/submit` | Score a quiz, update weak topics |
| 5 | POST | `/evaluate` | Grade an answer, list missing points |
| 6 | POST | `/study-plan` | Day-wise plan from exam date + hours |
| 7 | GET | `/weak-topics/{doc_id}` | Per-topic accuracy |
| 8 | POST | `/mock-exam` | Timed paper with a marks distribution |
| 9 | POST | `/revision` | Flashcards (last-minute / definitions / concepts) |
| 10 | GET | `/health` | Status of every service |

Extras: `GET /documents`, `GET /documents/{doc_id}`, `GET /documents/{doc_id}/file`
(open the PDF at a cited page), `DELETE /documents/{doc_id}`, `GET /quiz/{quiz_id}`,
`GET /quiz-stats/{doc_id}`, `GET /mock-exam/{exam_id}` (timer), 
`POST /mock-exam/submit`, `GET /mock-exam/{exam_id}/answer-key`,
`GET /ask/capabilities`, `GET /ask/preview/{doc_id}` (retrieval debug).

### 1. Upload

```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@notes.pdf" \
  -F "syllabus=- RAG
- Vector Search
- Evaluation metrics"
```

```json
{
  "doc_id": "notes-3f2c3528",
  "filename": "notes.pdf",
  "num_pages": 42,
  "num_chunks": 318,
  "status": "processed",
  "syllabus_chars": 41,
  "message": "Indexed 42 pages into 318 chunks."
}
```

### 2. Ask (mark-wise + language)

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"doc_id":"notes-3f2c3528",
       "question":"What is retrieval augmented generation?",
       "mark_type":"5M",
       "language":"english"}'
```

```json
{
  "answer": "• RAG retrieves relevant passages before answering ...",
  "sources": [
    {"page": 12, "chunk_id": "notes-3f2c3528::p12::c96", "heading": "2.3 RAG",
     "snippet": "Retrieval augmented generation combines a retriever ...",
     "score": 0.71}
  ],
  "confidence": 0.62, "confidence_label": "high",
  "provider": "groq", "model": "llama-3.1-70b-versatile",
  "mark_type": "5M", "language": "english", "grounded": true, "elapsed_ms": 1840
}
```

`mark_type` ∈ `1M · 2M · 5M · 10M · 15M · 16M`,
`language` ∈ `english · tamil · tanglish`.

### 3-4. Quiz and submit

```bash
curl -X POST http://127.0.0.1:8000/quiz -H "Content-Type: application/json" \
  -d '{"doc_id":"notes-3f2c3528","num_questions":5,"difficulty":"medium","topic":"RAG"}'

curl -X POST http://127.0.0.1:8000/quiz/submit -H "Content-Type: application/json" \
  -d '{"doc_id":"notes-3f2c3528","quiz_id":"quiz_ab12cd34","answers":[0,2,1,3,0]}'
```

```json
{
  "score": 4, "total": 5, "percentage": 80.0,
  "per_question_feedback": [
    {"question": "RAG stands for …", "selected": 0, "correct_index": 0,
     "is_correct": true, "explanation": "…", "source_page": 12, "topic": "RAG"}
  ],
  "weak_topics": ["Vector Search"]
}
```

### 5. Evaluate an answer

```bash
curl -X POST http://127.0.0.1:8000/evaluate -H "Content-Type: application/json" \
  -d '{"doc_id":"notes-3f2c3528","question":"What is FAISS?",
       "student_answer":"It is a library.","mark_type":"5M"}'
```

Returns `score_out_of`, `score_earned`, `missing_points`, `incorrect_points`,
`suggestions`, a `model_answer` and the `sources` used.

### 6. Study plan

```bash
curl -X POST http://127.0.0.1:8000/study-plan -H "Content-Type: application/json" \
  -d '{"doc_id":"notes-3f2c3528","exam_date":"2026-11-20","daily_hours":3}'
```

```json
{
  "days_left": 6, "daily_hours": 3.0, "total_hours": 18.5,
  "topics": ["Vector Search", "RAG", "Embeddings"],
  "plan": [
    {"day_num": 1, "date": "2026-10-04", "total_hours": 3.0,
     "topics": [{"name": "Vector Search", "hours": 1.5, "priority": "high",
                 "reason": "weak in recent quizzes", "part": 1}]},
    {"day_num": 6, "date": "2026-10-09", "total_hours": 3.5,
     "topics": [{"name": "Re-read all definitions & formulas", "hours": 1.0,
                 "priority": "high", "reason": "last-minute recall"}]}
  ],
  "disclaimer": "Identifies topics for focused study; does not predict the actual question paper."
}
```

Weights: weak **1.5×**, syllabus **1.2×**, normal **1.0×**; the final day is
always reserved for revision.

### 8. Mock exam (timer enforced server-side)

```bash
curl -X POST http://127.0.0.1:8000/mock-exam -H "Content-Type: application/json" \
  -d '{"doc_id":"notes-3f2c3528","duration_minutes":60,
       "marks_distribution":{"1M":5,"2M":3,"5M":2,"16M":1}}'

curl -X POST http://127.0.0.1:8000/mock-exam/submit -H "Content-Type: application/json" \
  -d '{"exam_id":"exam_9f2c11ab","answers":{"q1":"…","q2":"…"}}'
```

`GET /mock-exam/{exam_id}` returns `time_remaining_seconds`; submitting after
the deadline sets `auto_submitted: true`.

### 9. Revision

```bash
curl -X POST http://127.0.0.1:8000/revision -H "Content-Type: application/json" \
  -d '{"doc_id":"notes-3f2c3528","mode":"last_minute","num_cards":10,"language":"tamil"}'
```

### 10. Health

```json
{"status":"ok","services":{
  "llm":{"groq":{"configured":true},"gemini":{"configured":false},
         "ollama":{"reachable":false},"chain":["groq","gemini","ollama"],"active":"groq"},
  "embedder":{"model":"sentence-transformers","dim":384},
  "rag":{"top_k":5,"similarity_threshold":0.12,
         "abstention_message":"Insufficient information in the uploaded material."}}}
```

---

## 🎨 Feature tour (Streamlit tabs)

| Tab | What it does |
|---|---|
| 📤 Upload | PDF + optional syllabus, shows pages/chunks indexed |
| 💬 Ask | Question + mark radio (1M…16M) + language → answer card, metrics, page chips |
| 📝 Quiz | Topic + count + difficulty → MCQs, scoring, per-question feedback, weak topics |
| 🎯 Exam Mode | Duration + marks distribution → timed paper, live timer, analytics, auto-submit |
| 📅 Study Plan | Exam date + daily hours → day-wise weighted schedule |
| 🔍 Weak Topics | Plotly accuracy-per-topic bar chart (red = weak) |
| ⚡ Revision | Last-minute / definitions / key concepts flashcards |
| ✅ Evaluate | Question + your answer → marks, missing points, suggestions, sources |

Theme: deep blue `#1e3a8a` + amber `#fbbf24`, white text, rounded cards and pill
source chips (`📄 Page 12`).

---

## 📊 Evaluation

### SQuAD 2.0 — QA / RAG quality

```bash
python evaluation/squad_eval.py --num-samples 120 --seed 7
```

Each SQuAD paragraph is indexed as a mini-document and answered through the
**production** `rag_query`. Metrics follow the official SQuAD 2.0 script.

**Measured on this machine (120 questions, no LLM key, offline extractive mode):**

| Metric | Value |
|---|---|
| Questions evaluated | 120 |
| Answerable / unanswerable | 66 / 54 |
| Exact Match (answerable) | **0.000** |
| F1 (answerable) | **0.181** |
| Answerable accuracy | **0.985** |
| Unanswerable accuracy | **0.111** |
| Provider used | `extractive-fallback` (no API key configured) |

```bash
cat evaluation/squad_results.json | python -c "import json,sys;print(json.load(sys.stdin)['metrics'])"
```

**How to read these numbers**

* The extractive fallback answers with the *most relevant source sentence*, so
  **F1 stays low by construction** (SQuAD rewards a short span; a sentence
  contains extra tokens). With a Groq or Gemini key the same run uses the 2M
  mark rule and returns short answers — re-run after adding a key.
* **Unanswerable accuracy is structurally hard here**: each SQuAD context is a
  *single chunk*, so there is nothing for a similarity threshold to discriminate
  against. The pipeline therefore adds an **expected-answer-type check**
  ("…in what year?" needs a number, "who…" needs a name) before the offline
  path answers. On real multi-chunk PDFs the threshold works as intended —
  see the sweep below.

### Threshold calibration

```bash
python evaluation/threshold_sweep.py sample_rag.pdf
```

| threshold | answerable recall | unanswerable accuracy | F1 |
|---|---|---|---|
| 0.10 | 1.00 | 1.00 | **1.00** |
| 0.15 | 0.86 | 1.00 | 0.92 |
| 0.30 | 0.57 | 1.00 | 0.73 |

The textbook 0.30 cut-off was tuned for raw MiniLM cosine; the hybrid score is
on a different scale, which is why the shipped default is **0.12** — the middle
of the measured gap between answerable (min 0.12) and unanswerable (max 0.06)
scores. Re-run the sweep after swapping the embedding model.

### Tests

```bash
pytest tests -v          # 28 tests
python tests/e2e_check.py sample_features.pdf   # all 10 flows against a live server
```

---

## 🛠️ Configuration

| Variable | Default | Meaning |
|---|---|---|
| `GROQ_API_KEY` / `GROQ_MODEL` | – / `llama-3.1-70b-versatile` | Primary LLM (free) |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | – / `gemini-1.5-flash` | First fallback (free) |
| `OLLAMA_URL` / `OLLAMA_MODEL` | `http://localhost:11434` / `llama3` | Local fallback |
| `DEFAULT_LLM` | `groq` | Which provider is tried first |
| `VECTOR_DB_PATH` | `./backend/data/vector_db` | FAISS artifacts |
| `UPLOAD_PATH` | `./backend/data/uploads` | Stored PDFs |
| `DB_PATH` | `./backend/data/intellipdf.db` | SQLite database |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embeddings |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `800` / `150` | LangChain splitter |
| `TOP_K` | `5` | Chunks retrieved |
| `SIMILARITY_THRESHOLD` | `0.12` | Abstain below this score |
| `HYBRID_DENSE_WEIGHT` / `HYBRID_LEXICAL_WEIGHT` | `0.6` / `0.4` | Retrieval mix |
| `MAX_UPLOAD_MB` | `50` | Upload limit |

---

## ❓ Troubleshooting

| Symptom | Fix |
|---|---|
| `⚠️ API offline` in the UI | Start the backend: `uvicorn backend.main:app --port 8000` |
| `No selectable text found — looks like a scanned PDF` | Run the PDF through OCR first; IntelliPDF reads the text layer only |
| Answers say *"Insufficient information…"* | The question is not covered by the PDF, or retrieval scored below the threshold — rephrase the question, or lower `SIMILARITY_THRESHOLD` |
| `provider: extractive-fallback` | No API key is reachable. Add `GROQ_API_KEY` (or run `ollama serve`) |
| `sentence-transformers unavailable` | First download blocked — the app fell back to hashing embeddings; check your internet/proxy, or pre-download the model |
| Port 8000/8501 already in use | `API_PORT=8100 ./run.sh` and set `API_URL=http://127.0.0.1:8100` for Streamlit |
| `UnicodeEncodeError: … charmap` (Windows) | Use `PYTHONIOENCODING=utf-8` (already set by `run.sh`) or the Git Bash terminal |
| Port 8000 blocked by another project in this workspace | Stop the other listener first (`netstat -ano | findstr :8000`) |

---

## 📸 Screenshots

<!-- Replace the placeholders below with your own captures before presenting. -->

| Screen | Where |
|---|---|
| Upload + indexing | `docs/screenshots/1-upload.png` |
| Mark-wise answer + sources | `docs/screenshots/2-ask.png` |
| Quiz + score | `docs/screenshots/3-quiz.png` |
| Weak-topic chart | `docs/screenshots/4-weak-topics.png` |
| Study plan | `docs/screenshots/5-study-plan.png` |
| Mock exam timer | `docs/screenshots/6-exam.png` |

---

## 📚 References

* Rajpurkar, P., Jia, R., & Liang, P. (2016). *SQuAD: 100,000+ Questions for
  Machine Comprehension of Text.* EMNLP 2016.
* Rajpurkar, P., Jia, R., & Liang, P. (2018). *Know What You Don't Know:
  Unanswerable Questions for SQuAD.* ACL 2018.
* Lewis, P., et al. (2020). *Retrieval-Augmented Generation for
  Knowledge-Intensive NLP Tasks.* NeurIPS 2020.
* Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using
  Siamese BERT-Networks.* EMNLP-IJCNLP 2019.
* Johnson, J., Douze, M., & Jégou, H. (2019). *Billion-scale similarity search
  with GPUs.* IEEE Big Data 2019.
* Vaswani, A., et al. (2017). *Attention Is All You Need.* NeurIPS 2017.

---

## ⚖️ Disclaimer

IntelliPDF **identifies topics for focused study; it does not predict the actual
question paper.** It is a study companion, not a substitute for the official
syllabus or a textbook.

**All services are free tier or local:** Groq (free), Gemini (free), Ollama
(local), FAISS (local), SQLite (local), `all-MiniLM-L6-v2` (local after the
one-time download). No paid APIs, no cloud vector database, runs on an 8 GB
laptop.