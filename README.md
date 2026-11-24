# ClassMind: AI study companion for Google Classroom

ClassMind connects to a student's Google Classroom, sorts every post (slides, assignments, quizzes,
syllabus, announcements) and detects the teacher's sessional syllabus. Students can then chat with
their own material, with citations, and generate study guides, flashcards and quizzes for an exam.
They never have to download or upload a file.

> GenAI course project by Hamas Naveed (23i-3014) and Azfaar Salahuddin (23i-3055).
> Proposal: [docs/ClassMind_Proposal.pdf](docs/ClassMind_Proposal.pdf)

## Deliverables

| What | File | Rebuild with |
|---|---|---|
| Presentation | [docs/ClassMind_Presentation.pptx](docs/ClassMind_Presentation.pptx) | `python docs/build_slides.py` |
| Requirements, architecture & security report | [docs/ClassMind_Report.docx](docs/ClassMind_Report.docx) | `python docs/build_report.py` |
| Recorded walkthrough (about 4.5 min) | [docs/ClassMind_Walkthrough.mp4](docs/ClassMind_Walkthrough.mp4) | `python docs/build_video.py` |
| Working prototype | `app.py` | `python app.py` |

## How to run (demo mode, no keys needed)

```bash
git clone https://github.com/HamasNaveed/GenAI-Project.git
cd GenAI-Project
python -m venv .venv && .venv\Scripts\activate      # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000>. Demo mode loads a realistic semester: 3 courses, lecture decks, assignments,
quizzes and two syllabus announcements. Everything runs offline.

**Try this:**
1. **Smart stream:** every post has an AI label and a confidence score. The GenAI post "Important - read before Monday" is flagged ⚠ low confidence. Correct it with the dropdown.
2. **Syllabus map:** *Sessional 1 → Lectures 1–4* is extracted from the teacher's announcement.
3. **Ask your course:** "What is covered in Sessional 1?", "Explain Amdahl's law with an example". Answers cite their lecture and slide. "Who won the football world cup?" is refused because it is not in your material.
4. **Study tools:** choose *Sessional 1*, then Study guide, Flashcards or Practice quiz.

## Real LLM (optional)

```bash
set ANTHROPIC_API_KEY=sk-ant-...      # PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python app.py
```

With a key, Claude (`claude-opus-5-5`) does classification (structured JSON output) and grounded
generation. Retrieval stays local. Without a key, a rules and BM25 engine with the same interface is used.

## Real Google Classroom mode

1. In [Google Cloud Console](https://console.cloud.google.com/), enable the **Google Classroom API** and the **Google Drive API**.
2. Create an OAuth client of type **Web application** and add this authorised redirect URI:
   `http://localhost:5000/oauth2callback`
3. On the OAuth consent screen, add your Google account as a **test user**.
4. Download the client JSON and put it in the repo root as `client_secret_*.json`, or set
   `GOOGLE_CLIENT_SECRET_FILE=path\to\file.json`. The file is git-ignored and must never be committed.
5. Run `python app.py` and click **Sign in with Google**. ClassMind syncs your active courses read-only.
   **Disconnect & delete data** drops the tokens and all synced data.

Scopes requested (all read-only): courses, announcements, own coursework, coursework materials, Drive files.

## Project layout

```
app.py                  Flask app: routes, Google OAuth, in-memory store
classmind/
  mock_data.py          demo Classroom (courses, posts, slide decks, syllabus posts)
  classroom.py          real Classroom + Drive sync, PPTX/PDF/DOCX parsing
  pipeline.py           classify -> syllabus extraction -> BM25 index -> grounded answer -> study tools
templates/, static/     single-page UI (vanilla JS)
docs/                   proposal, report, slides, video + their build scripts
```

## How the AI works (short version)

1. **Classification:** each post gets a label, a confidence and a lecture number. Low confidence is shown to the student.
2. **Syllabus extraction:** teacher posts like "Sessional 1 covers lectures 1 to 4" become an exam-to-lectures map.
3. **Retrieval:** one chunk per slide, BM25 ranking filtered by course and exam lectures.
4. **Grounded generation:** answers use only retrieved slides, cite them, and say "not found" when the evidence score is too low.

Known limits (prototype): single-user in-memory store, full re-sync on each sign-in, no slide-image captions,
and no automated tests yet.
