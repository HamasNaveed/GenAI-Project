# ClassMind — Claude guide

AI study companion for Google Classroom (GenAI course project, Hamas Naveed & Azfaar Salahuddin).
Proposal: `docs/ClassMind_Proposal.pdf`.

## Stack
- Python 3.12, Flask (single app in `app.py`), vanilla HTML/CSS/JS in `templates/` + `static/`.
- `classmind/` = the AI pipeline: `mock_data.py` (demo Classroom), `classroom.py` (real Google API sync),
  `pipeline.py` (classify → chunk → retrieve → generate).
- LLM: Anthropic Claude (`claude-opus-5-5`) only when `ANTHROPIC_API_KEY` is set; otherwise deterministic mock answers.

## Run
```
pip install -r requirements.txt
python app.py            # mock mode, http://localhost:5000
```
Real Classroom mode: see README ("Real Google Classroom mode").

## Deliverables (generated, re-run after content changes)
- `python docs/build_report.py`  → `docs/ClassMind_Report.docx` (≤ 4 pages)
- `python docs/build_slides.py`  → `docs/ClassMind_Presentation.pptx`
- `python docs/build_video.py`   → `docs/ClassMind_Walkthrough.mp4`

## Rules
- NEVER commit `client_secret*.json`, `token*.json` or `.env` (already in .gitignore). Never print the client secret.
- Mock mode is the default and must work offline with no API keys — the demo depends on it.
- Google scopes stay read-only.
- No test suite yet (prototype stage).
