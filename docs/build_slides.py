"""Build docs/ClassMind_Presentation.pptx (python-pptx). Slide order follows the course guidelines."""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from diagram import architecture

HERE = os.path.dirname(os.path.abspath(__file__))
DARK, ACCENT, SOFT, INK, MUTED = "12312A", "1F6F5C", "DCEFE8", "1D2320", "5F6762"
WARN, WARN_SOFT, WHITE, LINE, MINT = "B4651B", "FBEAD8", "FFFFFF", "D9D6CE", "7FD1B9"
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def rgb(h):
    return RGBColor.from_string(h)


def text(slide, x, y, w, h, runs, size=16, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=4):
    """runs: str, or list of paragraphs; a paragraph is a str or list of (text, {opts})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap, tf.vertical_anchor = True, anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = [runs] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.space_after = align, Pt(spacing)
        for t, o in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name, f.size = o.get("font", font), Pt(o.get("size", size))
            f.bold, f.italic = o.get("bold", bold), o.get("italic", False)
            f.color.rgb = rgb(o.get("color", color))
    return tb


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = rgb(fill)
    if line:
        s.line.color.rgb, s.line.width = rgb(line), Pt(1.25)
    else:
        s.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    return s


def dot(slide, x, y, label, fill=ACCENT, color=WHITE, d=0.62, size=18):
    rect(slide, x, y, d, d, fill, shape=MSO_SHAPE.OVAL)
    text(slide, x, y, d, d, [[(label, {"bold": True})]], size=size, color=color, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)


def new(title=None, kicker=None, dark=False, notes=""):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(DARK if dark else WHITE)
    if kicker:
        text(s, 0.7, 0.45, 11, 0.35, kicker.upper(), size=13, bold=True, color=MINT if dark else ACCENT)
    if title:
        text(s, 0.7, 0.8, 12, 0.9, title, size=34, font=HEAD, bold=True, color=WHITE if dark else INK)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    if not dark:
        text(s, 0.7, 7.0, 6, 0.3, "ClassMind · AI Study Companion for Google Classroom", size=10, color=MUTED)
        text(s, 11.6, 7.0, 1.0, 0.3, str(len(prs.slides)), size=10, color=MUTED, align=PP_ALIGN.RIGHT)
    return s


# 1 ─ title
s = new(dark=True, notes="Introduce the team and the one-line idea: ClassMind turns a student's Google Classroom into an AI-ready, syllabus-aware study workspace.")
text(s, 0.9, 1.6, 2, 0.8, "◆", size=54, color=MINT)
text(s, 0.9, 2.5, 11.5, 1.4, "ClassMind", size=66, font=HEAD, bold=True, color=WHITE)
text(s, 0.9, 3.7, 11, 0.8, "An AI study companion for Google Classroom", size=28, color=MINT)
text(s, 0.9, 5.3, 11, 1.0, [[("Hamas Naveed (23i-3014)  ·  Azfaar Salahuddin (23i-3055)", {"bold": True})],
                           "Generative AI · Project presentation"], size=18, color="C9D6D1")

# 2 ─ problem
s = new("Students lose time before they start studying", "The problem",
        notes="Material is spread over a dozen courses in one flat chronological stream. Every AI study session starts with the same four manual steps, repeated per course, per exam. Generic chatbots don't know your courses, deadlines or syllabus.")
steps = [("Scroll", "the Classroom stream to find which posts fall under the sessional syllabus"),
         ("Download", "every PPTX and PDF one by one, across a dozen courses"),
         ("Upload", "them to a general chatbot — which forgets them in the next chat"),
         ("Repeat", "for every course and every exam, all semester")]
for i, (h, b) in enumerate(steps):
    y = 2.0 + i * 1.12
    dot(s, 0.8, y, str(i + 1))
    text(s, 1.65, y - 0.02, 6.4, 1.0, [[(h + " ", {"bold": True, "color": ACCENT}), (b, {})]], size=18)
rect(s, 8.5, 2.0, 4.1, 4.3, SOFT)
text(s, 8.85, 2.3, 3.5, 1.2, "150M+", size=60, font=HEAD, bold=True, color=ACCENT)
text(s, 8.85, 3.45, 3.5, 0.9, "Google Classroom users worldwide (Google, 2021)", size=15, color=INK)
text(s, 8.85, 4.55, 3.5, 1.6, [[("Result: ", {"bold": True}), ("wasted time, missed material and generic answers that ignore what is actually in the exam.", {})]],
     size=15, color=INK)

# 3 ─ gap table
s = new("No existing tool closes the whole gap", "The gap",
        notes="Each tool solves part of the problem. None syncs Classroom automatically AND knows which lectures belong to which exam AND grounds answers in citations.")
cols = ["", "Auto-sync from Classroom", "Knows exam syllabus", "Cited, grounded answers", "Study tools generated", "No manual uploads"]
rows = [("Google Classroom", "✓", "✗", "✗", "✗", "✓"),
        ("ChatGPT / Gemini / Claude chat", "✗", "✗", "~", "✓", "✗"),
        ("NotebookLM-style tools", "✗", "✗", "✓", "✓", "✗"),
        ("Flashcard apps", "✗", "✗", "✗", "~", "✗"),
        ("ClassMind", "✓", "✓", "✓", "✓", "✓")]
tbl = s.shapes.add_table(len(rows) + 1, len(cols), Inches(0.7), Inches(1.95), Inches(11.9), Inches(4.4)).table
tbl.columns[0].width = Inches(3.4)
for j in range(1, len(cols)):
    tbl.columns[j].width = Inches(1.7)
for i, r in enumerate([cols] + rows):
    for j, v in enumerate(r):
        c = tbl.cell(i, j)
        c.fill.solid()
        last = i == len(rows)
        c.fill.fore_color.rgb = rgb(ACCENT if i == 0 else SOFT if last else (WHITE if i % 2 else "F4F6F5"))
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
        run = p.add_run()
        run.text = v
        col = WHITE if i == 0 else {"✓": ACCENT, "✗": "A33A3A", "~": WARN}.get(v, INK)
        run.font.size, run.font.name, run.font.color.rgb = Pt(14 if i == 0 else 20 if j else 16), BODY, rgb(col)
        run.font.bold = i == 0 or last or v in "✓✗~"
text(s, 0.7, 6.5, 12, 0.4, "✓ yes   ~ partly   ✗ no   — based on our current understanding of each product", size=12, color=MUTED)

# 4 ─ one sentence + scenario
s = new(None, "What it does", notes="Say the sentence slowly. Then walk through Ayesha's evening: one sign-in, one request, a cited study guide.")
text(s, 0.7, 0.9, 11.9, 1.6, [[("ClassMind syncs your Google Classroom, works out which lectures belong to which exam, and turns them into ", {}),
                              ("cited answers, study guides and quizzes", {"color": ACCENT, "bold": True}), (" — with no downloading or uploading.", {})]],
     size=27, font=HEAD)
text(s, 0.7, 2.75, 6, 0.4, "USER SCENARIO · Ayesha, 5th-semester CS student", size=13, bold=True, color=ACCENT)
scen = [("Mon", "Signs in with Google once. ClassMind syncs 6 courses, 140 posts, 38 slide decks."),
        ("Tue", "Teacher posts: “Sessional 1 covers lectures 1 to 4.” ClassMind tags it as the syllabus."),
        ("Thu", "Ayesha types: “Make me a study guide for PDC Sessional 1.”"),
        ("Thu", "Gets topic summaries, Amdahl's & Gustafson's formulas and likely questions — each linked to its slide."),
        ("Fri", "Takes a 5-question practice quiz; asks “Explain false sharing” and gets a cited answer.")]
for i, (d, t) in enumerate(scen):
    x = 0.7 + i * 2.44
    rect(s, x, 3.3, 2.24, 3.3, SOFT if i != 3 else ACCENT)
    text(s, x + 0.2, 3.45, 1.9, 0.5, d, size=20, font=HEAD, bold=True, color=WHITE if i == 3 else ACCENT)
    text(s, x + 0.2, 4.05, 1.86, 2.5, t, size=15, color=WHITE if i == 3 else INK)

# 5 ─ technique
s = new("RAG + syllabus filter beats the alternatives", "Technique",
        notes="Two AI parts: an LLM classifier with JSON output that labels every post and extracts the syllabus map, and retrieval-augmented generation filtered by that map. Compare with the alternatives on the right.")
text(s, 0.7, 1.85, 5.6, 0.4, "OUR PIPELINE", size=13, bold=True, color=ACCENT)
pipe = [("Classify", "LLM → JSON {label, confidence, lecture} per post"),
        ("Map syllabus", "“Sessional 1 covers lectures 1–4” → exam→lecture map"),
        ("Retrieve", "one chunk per slide; BM25 + vectors, filtered by course & exam"),
        ("Generate", "Claude answers only from retrieved slides, cites [n], else “not found”")]
for i, (h, b) in enumerate(pipe):
    y = 2.35 + i * 1.08
    dot(s, 0.7, y, str(i + 1), d=0.55, size=16)
    text(s, 1.45, y - 0.03, 4.9, 1.0, [[(h, {"bold": True, "size": 18})], b], size=15, spacing=1)
alts = [("Fine-tuning", "Material changes weekly; can't cite sources; costly per course", False),
        ("Paste everything (long context)", "Pays for whole semester every question; loses exam boundaries", False),
        ("Plain chatbot", "No knowledge of your courses; manual uploads; hallucinations", False),
        ("RAG + syllabus filter", "Always current, cheap per question, cites slides, scoped to the exam", True)]
for i, (h, b, ok) in enumerate(alts):
    y = 1.85 + i * 1.2
    rect(s, 6.9, y, 5.75, 1.05, SOFT if ok else "F4F6F5", line=ACCENT if ok else None)
    text(s, 7.15, y + 0.13, 0.5, 0.8, "✓" if ok else "✗", size=24, bold=True, color=ACCENT if ok else "A33A3A")
    text(s, 7.7, y + 0.1, 4.8, 0.9, [[(h, {"bold": True})], b], size=15, spacing=1)

# 6 ─ data plan + metrics
s = new("Data plan and how we measure quality", "Technique · data & metrics",
        notes="All evaluation data comes from our own batch's Classroom with consent. Student corrections in the app become extra labelled data.")
stats = [("≥ 90%", "classification accuracy", "200 hand-labelled posts"),
         ("≥ 85%", "retrieval Hit@5", "100 questions with gold slide"),
         ("≥ 90%", "answer faithfulness", "claims supported by sources"),
         ("100%", "off-topic refusals", "30 out-of-course questions")]
for i, (n, l, d) in enumerate(stats):
    x = 0.7 + i * 3.02
    rect(s, x, 1.9, 2.8, 2.25, SOFT)
    text(s, x + 0.25, 2.05, 2.4, 0.9, n, size=44, font=HEAD, bold=True, color=ACCENT)
    text(s, x + 0.25, 3.0, 2.4, 1.1, [[(l, {"bold": True})], [(d, {"color": MUTED, "size": 13})]], size=16, spacing=2)
text(s, 0.7, 4.5, 6, 0.4, "DATA PLAN", size=13, bold=True, color=ACCENT)
text(s, 0.7, 4.9, 5.8, 2.0, ["Source: students' own Classroom via the official API (read-only)",
                             "Labels: 200 posts double-labelled by both team members",
                             "Questions: 100 real study questions with gold slides",
                             "Feedback loop: in-app label corrections → prompt tuning"], size=15)
text(s, 6.9, 4.5, 6, 0.4, "BASELINES WE COMPARE AGAINST", size=13, bold=True, color=ACCENT)
text(s, 6.9, 4.9, 5.7, 2.0, ["Keyword rules classifier (our offline engine)",
                             "Retrieval without the syllabus filter",
                             "LLM answer without retrieved sources (hallucination rate)"], size=15)

# 7 ─ AI system requirements
s = new("AI-specific system requirements", "System requirements",
        notes="These are the requirements that only exist because the system uses AI: quality targets, grounding, safety, latency and cost.")
reqs = [("Grounding", "Answers come only from retrieved course slides; every answer cites lecture + slide"),
        ("Calibrated confidence", "Every label carries a confidence; < 0.6 is shown to the student as “unsure”"),
        ("Refusal", "Below the evidence threshold the system says “not found” instead of guessing"),
        ("Structured output", "Classifier returns schema-valid JSON; invalid labels fall back safely"),
        ("Prompt-injection safe", "Slide/post text is passed as data; instructions inside it are ignored"),
        ("Latency & cost", "Chat p95 < 6 s; each file parsed & indexed once per course, shared by all students"),
        ("Privacy", "Read-only Google scopes; tokens in memory only; one-click delete"),
        ("Graceful degradation", "No API key or LLM outage → offline rules + BM25 engine keeps working")]
for i, (h, b) in enumerate(reqs):
    x, y = 0.7 + (i % 2) * 6.1, 1.9 + (i // 2) * 1.2
    rect(s, x, y, 5.85, 1.05, "F4F6F5")
    text(s, x + 0.25, y + 0.12, 5.4, 0.9, [[(h, {"bold": True, "color": ACCENT})], b], size=14, spacing=1)

# 8 ─ architecture
s = new("Architecture: ingest once, serve many", "Architecture",
        notes="Top row runs on each sync in background workers. Bottom row runs on each question. The knowledge base is the only link. Because course files are shared, each document is parsed and embedded once and reused by every enrolled student.")
s.shapes.add_picture(architecture(), Inches(0.7), Inches(1.9), width=Inches(11.9))
text(s, 0.7, 6.55, 11.9, 0.4, "Stack: Flask · Google Classroom & Drive APIs · python-pptx / pypdf / python-docx · BM25 (+ vector store in production) · Claude claude-opus-5-5",
     size=13, color=MUTED)

# 9 ─ when AI is wrong (1)
s = new("When the AI is wrong: detect it, show it, recover", "Failure handling",
        notes="Walk through each row. The principle: we never hide uncertainty. Every failure has a detection signal and a visible, safe response.")
fails = [("Post mislabelled", "confidence < 0.6", "⚠ “Unsure” badge; student relabels in one click; syllabus map rebuilt"),
         ("Syllabus not detected", "no exam entry for course", "Study tools refuse to guess which lectures; ask student to tag the post"),
         ("Question not in material", "top retrieval score < threshold", "“I could not find this in your course material.”"),
         ("Hallucinated detail", "citations + faithfulness eval", "Every claim links to its slide so the student can verify"),
         ("LLM / API outage", "exception or refusal", "Falls back to offline extractive engine; no crash")]
for j, h in enumerate(["What goes wrong", "How we detect it", "What the student sees"]):
    text(s, [0.7, 4.3, 7.6][j], 1.85, 4, 0.4, h.upper(), size=13, bold=True, color=ACCENT)
for i, (a, b, c) in enumerate(fails):
    y = 2.3 + i * 0.9
    rect(s, 0.7, y, 11.9, 0.78, "F4F6F5" if i % 2 else WHITE, line=LINE)
    text(s, 0.95, y, 3.3, 0.78, a, size=16, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 4.3, y, 3.2, 0.78, b, size=15, color=MUTED, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 7.6, y, 4.9, 0.78, c, size=15, anchor=MSO_ANCHOR.MIDDLE)

# 10 ─ when AI is wrong (2)
s = new("Human in the loop: corrections make it better", "Failure handling",
        notes="Left: what the student actually sees in the prototype. Right: the feedback loop. Corrections are logged and used to improve the classifier prompt; the faithfulness and refusal metrics are re-run each release.")
rect(s, 0.7, 1.9, 5.9, 1.55, WHITE, line=LINE)
text(s, 0.95, 2.05, 3.9, 1.3, [[("Important - read before Monday", {"bold": True})], [("Check the shared folder.", {"color": MUTED})]], size=15)
rect(s, 4.75, 2.1, 1.6, 0.4, WARN_SOFT)
text(s, 4.75, 2.1, 1.6, 0.4, "announcement", size=12, bold=True, color=WARN, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
text(s, 4.75, 2.6, 1.8, 0.7, [[("45% · ⚠ Unsure", {"color": WARN, "bold": True})], "relabel ▾"], size=12)
rect(s, 0.7, 3.7, 5.9, 0.6, ACCENT)
text(s, 0.95, 3.7, 5.5, 0.6, "Who won the football world cup?", size=15, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
rect(s, 0.7, 4.45, 5.9, 1.25, WARN_SOFT, line=WARN)
text(s, 0.95, 4.55, 5.5, 1.1, [[("I could not find this in your course material.", {"bold": True})],
                              [("Not answered: no supporting source in your material", {"color": MUTED, "size": 12})]], size=15)
rect(s, 0.7, 5.85, 5.9, 0.95, SOFT)
text(s, 0.95, 5.92, 5.5, 0.85, [[("Amdahl's law: S(p) = 1 / (f + (1−f)/p) … ", {}), ("[1]", {"bold": True, "color": ACCENT})],
                               [("[1] Lecture 3, slide 1 · Lecture03_Amdahl's.pptx", {"color": ACCENT, "size": 12})]], size=14)
loop = [("Flag", "low confidence or no evidence is shown, never hidden"), ("Correct", "student fixes a label in one click"),
        ("Log", "correction stored as a new labelled example"), ("Improve", "prompt + rules tuned; metrics re-run each release")]
for i, (h, b) in enumerate(loop):
    y = 1.9 + i * 1.22
    dot(s, 7.2, y + 0.1, str(i + 1))
    text(s, 8.05, y, 4.6, 1.1, [[(h, {"bold": True, "size": 19, "color": ACCENT})], b], size=15, spacing=1)

# 11 ─ demo
s = new(dark=True, notes="Switch to the live prototype (python app.py) or play docs/ClassMind_Walkthrough.mp4. 4-5 minutes.")
text(s, 0.9, 0.7, 11, 0.4, "PROTOTYPE WALKTHROUGH · 4–5 MIN", size=14, bold=True, color=MINT)
text(s, 0.9, 1.2, 11.5, 1.0, "Live demo", size=48, font=HEAD, bold=True, color=WHITE)
demo = [("Smart stream", "AI labels + confidence; fix the ⚠ unsure post"),
        ("Syllabus map", "Sessional 1 → lectures 1–4, from the teacher's post"),
        ("Ask your course", "cited answers; off-topic question refused"),
        ("Study tools", "guide, flashcards and quiz for Sessional 1")]
for i, (h, b) in enumerate(demo):
    x = 0.9 + i * 3.0
    rect(s, x, 2.75, 2.75, 2.5, "1C4A3F")
    text(s, x + 0.25, 2.95, 2.3, 0.6, str(i + 1), size=30, font=HEAD, bold=True, color=MINT)
    text(s, x + 0.25, 3.65, 2.3, 1.5, [[(h, {"bold": True, "size": 18})], b], size=15, color=WHITE, spacing=2)
text(s, 0.9, 5.8, 11.5, 0.9, [[("Run it:  ", {"bold": True, "color": MINT}), ("pip install -r requirements.txt  →  python app.py  →  localhost:5000", {})],
                             [("github.com/HamasNaveed/GenAI-Project", {"color": "C9D6D1"})]], size=17, color=WHITE)

out = os.path.join(HERE, "ClassMind_Presentation.pptx")
prs.save(out)
print(out)
