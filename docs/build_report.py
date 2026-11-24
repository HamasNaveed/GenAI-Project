"""Build docs/ClassMind_Report.docx: requirements, architecture and security analysis (3-4 pages)."""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from diagram import architecture

HERE = os.path.dirname(os.path.abspath(__file__))
ACCENT = RGBColor(0x1F, 0x6F, 0x5C)

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(1.8)
    s.left_margin = s.right_margin = Cm(2.0)
st = doc.styles["Normal"]
st.font.name, st.font.size = "Calibri", Pt(10.5)
st.paragraph_format.space_after = Pt(4)
for name, size in (("Heading 1", 14), ("Heading 2", 11.5)):
    h = doc.styles[name]
    h.font.size, h.font.color.rgb, h.font.name = Pt(size), ACCENT, "Calibri"
    h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(8), Pt(3)


def p(text, bold_lead=None):
    para = doc.add_paragraph()
    if bold_lead:
        para.add_run(bold_lead).bold = True
    para.add_run(text)
    return para


def bullets(items):
    for it in items:
        lead, _, rest = it.partition(": ")
        para = doc.add_paragraph(style="List Bullet")
        para.paragraph_format.space_after = Pt(1)
        if rest:
            para.add_run(lead + ": ").bold = True
            para.add_run(rest)
        else:
            para.add_run(it)


def shade(cell, hex_fill):
    tc = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"), sh.set(qn("w:color"), "auto"), sh.set(qn("w:fill"), hex_fill)
    tc.append(sh)


def table(header, rows, widths):
    t = doc.add_table(rows=1, cols=len(header))
    t.style, t.alignment = "Table Grid", WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        c.paragraphs[0].add_run(h).bold = True
        shade(c, "DCEFE8")
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = v
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
            for para in row.cells[i].paragraphs:
                para.paragraph_format.space_after = Pt(0)
                for run in para.runs:
                    run.font.size = Pt(9)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


# ------------------------------------------------------------------ title
t = doc.add_paragraph()
r = t.add_run("ClassMind: AI Study Companion for Google Classroom")
r.bold, r.font.size, r.font.color.rgb = True, Pt(18), ACCENT
p("Requirements, Architecture and Security Analysis  ·  Hamas Naveed (23i-3014), Azfaar Salahuddin (23i-3055)").runs[0].italic = True

doc.add_heading("1. Overview", level=1)
p("ClassMind syncs a student's Google Classroom, sorts every post and detects the teacher's exam syllabus, so the "
  "student can chat with, summarise and quiz themselves on exactly the right material without downloading or "
  "uploading a single file. Course material is ingested once and shared per course; answers are grounded in that "
  "material and cite the source slide.")

# ------------------------------------------------------------------ requirements
doc.add_heading("2. Requirements", level=1)
doc.add_heading("2.1 Functional requirements", level=2)
table(["ID", "Requirement", "Prototype status"], [
    ["FR1", "Sign in with Google (OAuth 2.0) and sync active courses, announcements, coursework, materials and Drive attachments, read-only", "Implemented"],
    ["FR2", "Parse PPTX, Google Slides, PDF and DOCX attachments into per-slide / per-page chunks", "Implemented (no image captions yet)"],
    ["FR3", "Classify each post as lecture slides, assignment, quiz, syllabus, announcement or reference, with a confidence and lecture number", "Implemented"],
    ["FR4", "Extract syllabus statements (\"Sessional 1 covers lectures 1 to 4\") into an exam-to-lecture map", "Implemented"],
    ["FR5", "Chat grounded only in the course, with citations to lecture and slide", "Implemented"],
    ["FR6", "Generate study guide, flashcards and practice quiz for a chosen exam", "Implemented"],
    ["FR7", "Let the student correct a label; corrections update the syllabus map and are logged", "Implemented"],
    ["FR8", "Disconnect and delete all synced data", "Implemented"],
    ["FR9", "Past-paper library from open-licensed sources", "Stretch goal"],
], [1.2, 11.5, 4.3])

doc.add_heading("2.2 AI-specific requirements", level=2)
table(["Area", "Requirement", "Target / metric"], [
    ["Classification", "Structured JSON label + calibrated confidence per post", "≥ 90% accuracy on 200 hand-labelled posts; posts < 0.6 confidence flagged"],
    ["Syllabus extraction", "Exam → lecture ranges from teacher posts", "≥ 95% exact-match on labelled syllabus posts"],
    ["Retrieval", "Per-slide chunks, BM25 (+ vectors in production), filtered by course and exam", "Hit@5 ≥ 85% on 100 test questions"],
    ["Grounding", "Answer only from retrieved slides; refuse below evidence threshold", "Faithfulness ≥ 90% of claims supported; 100% refusals on off-topic set"],
    ["Citations", "Every answer and guide cites lecture/slide", "100% of answers carry ≥ 1 valid citation"],
    ["Latency / cost", "Chat p95 < 6 s; each file parsed and embedded once per course", "Cost per extra student falls with course adoption"],
], [3.0, 7.2, 6.8])

doc.add_heading("2.3 Non-functional requirements", level=2)
bullets([
    "Privacy: least-privilege read-only scopes; tokens kept in memory/session only; one-click data deletion.",
    "Availability: demo mode runs fully offline, so a missing API key or network never blocks the student.",
    "Scalability: ingestion (job queue + workers) scales separately from chat; shared per-course index.",
    "Usability: confidence and sources are always visible; uncertain results are marked, not hidden.",
])

doc.add_heading("2.4 Data plan", level=2)
p("Inputs are the student's own Classroom posts and attachments, accessed through the official API. Evaluation data: "
  "(1) 200 real posts from our batch's courses, hand-labelled by both team members (disagreements resolved together); "
  "(2) 100 student questions with the gold slide marked, for Hit@5; (3) 30 off-topic questions, for refusal rate. "
  "Student corrections from the app are logged as extra labelled data for prompt tuning. No data is used to train "
  "third-party models.")

# ------------------------------------------------------------------ architecture
doc.add_heading("3. Architecture", level=1)
doc.add_picture(architecture(), width=Cm(16.5))
p("Ingestion and serving are separate flows connected only by the knowledge base.", "Figure 1. ")
bullets([
    "Classroom API + sync worker: OAuth 2.0 web flow, read-only scopes, paginated reads of courses, announcements, courseWork and courseWorkMaterials; Drive files downloaded or exported (Slides → PPTX).",
    "Parser: python-pptx (slide titles, body, speaker notes), pypdf, python-docx; one chunk per slide/page with metadata (course, lecture, file, slide).",
    "AI classifier: LLM with structured JSON output (label, confidence); deterministic rules fallback. Syllabus regex/LLM extraction builds the exam map.",
    "Knowledge base + retrieval: BM25 over slide chunks (prototype); production adds embeddings in a vector store for hybrid search. Filters by course and syllabus lectures.",
    "LLM generation: Claude (claude-opus-5-5) with a grounded system prompt, numbered sources and an explicit \"not found\" path; map-reduce per lecture for large syllabi.",
    "Web app: Flask + vanilla JS — smart stream, syllabus map, chat with citations, study tools, label correction.",
])
p("Technique choice. RAG beats the alternatives for this problem: fine-tuning cannot keep up with material that changes "
  "weekly and cannot cite sources; long-context \"paste everything\" prompts cost more per question and still lose "
  "the exam boundary. Metadata-filtered retrieval lets \"Sessional 1\" select exactly lectures 1–4.")

# ------------------------------------------------------------------ failure handling
doc.add_heading("4. When the AI is wrong", level=1)
table(["Failure", "Detection", "Response"], [
    ["Post mislabelled", "Confidence < 0.6", "⚠ badge; student relabels; syllabus map rebuilt; correction logged"],
    ["Syllabus missed", "No exam entry for course", "Study tools refuse to guess and say so; student can relabel the post"],
    ["Retrieval miss / off-topic", "Low BM25 score, or evidence covers < 50% of question terms", "Answer \"I could not find this in your course material\""],
    ["Hallucinated claim", "Citations shown; faithfulness eval", "Every claim links to its slide so the student can verify"],
    ["LLM/API failure", "Exception or refusal stop reason", "Falls back to extractive mock engine; no crash"],
], [3.5, 4.8, 8.7])

# ------------------------------------------------------------------ security
doc.add_heading("5. Security and Privacy Analysis", level=1)
p("Assets: students' Google OAuth tokens, course material (teacher copyright), chat history, the OAuth client secret "
  "and the LLM API key. Trust boundaries: browser ↔ app, app ↔ Google APIs, app ↔ LLM provider.")
table(["Threat (STRIDE)", "Risk", "Mitigation"], [
    ["Spoofing: stolen session / OAuth token", "Attacker reads a student's Classroom", "Random Flask secret key, signed session cookie; tokens never written to disk; HTTPS + secure cookies in production; short-lived access tokens"],
    ["Elevation: over-broad scopes", "App could modify coursework", "Only *.readonly scopes requested (classroom + drive.readonly); no write scopes exist in code"],
    ["Information disclosure: client secret / API key leak", "Impersonation of app, cost abuse", "client_secret*.json and .env git-ignored; loaded from file/env var; never logged or shown in UI"],
    ["Tampering: prompt injection in posts/slides", "Malicious text steers the LLM", "Sources passed as numbered data; system prompt tells the model to ignore instructions inside sources; output is plain text, no tool calls"],
    ["Information disclosure: cross-student leakage", "Student sees another course's data", "Retrieval filtered by course_id; production index scoped to courses the user is enrolled in (checked via API)"],
    ["Information disclosure: data sent to LLM", "Course content leaves the app", "Only the top-k retrieved slides are sent; provider API does not train on API data; offline mode available"],
    ["Denial of service / cost", "Abuse of LLM endpoint", "Question length capped (2,000 chars); per-user rate limits and free-tier caps (planned)"],
    ["Repudiation / copyright", "Redistribution of teacher material", "Material used only for the enrolled student; no public sharing; past papers only from open-licensed sources"],
], [4.2, 4.0, 8.8])
p("Data lifecycle. Synced material lives in process memory in the prototype; \"Disconnect & delete data\" clears tokens "
  "and all synced content. Production adds encryption at rest, per-user deletion and a retention limit of one semester.")

out = os.path.join(HERE, "ClassMind_Report.docx")
doc.save(out)
print(out)
