"""Build docs/ClassMind_Walkthrough.mp4: a ~4.5 min captioned walkthrough of the prototype.

Frames are drawn with Pillow from the REAL pipeline output (mock mode), so what the video shows
is what the app returns. Encoded with imageio-ffmpeg (bundled ffmpeg, no system install needed).
"""
import os
import sys
import textwrap

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
os.environ.pop("ANTHROPIC_API_KEY", None)  # always the deterministic offline engine

from classmind import mock_data, pipeline  # noqa: E402
from diagram import architecture, font  # noqa: E402

W, H, FPS = 1280, 720, 6
BG, PANEL, INK, MUTED, LINE = (246, 244, 239), (255, 253, 248), (29, 35, 32), (107, 113, 108), (227, 223, 213)
ACCENT, SOFT, WARN, WARN_SOFT, DARK, MINT = (31, 111, 92), (220, 239, 232), (180, 101, 27), (251, 234, 216), (18, 49, 42), (127, 209, 185)

# ---- real data from the pipeline
ITEMS = mock_data.ITEMS
LABELS = {it["id"]: pipeline.classify(it) for it in ITEMS}
SYL = pipeline.extract_syllabus(ITEMS, LABELS)
IDX = pipeline.Index(ITEMS, LABELS)
COURSE_NAME = {c["id"]: c["name"] for c in mock_data.COURSES}


def F(size, bold=False):
    return font(size, bold)


def SYM(size):
    """Segoe UI Symbol (Windows) has the check/warning glyphs Segoe UI lacks."""
    try:
        return ImageFont.truetype("seguisym.ttf", size)
    except OSError:
        return F(size)


def logo(d, x, y, s, color):
    d.polygon([(x + s / 2, y), (x + s, y + s / 2), (x + s / 2, y + s), (x, y + s / 2)], fill=color)


def wrap(d, xy, s, size=16, color=INK, width=60, bold=False, spacing=6):
    x, y = xy
    for para in s.split("\n"):
        for line in textwrap.wrap(para, width) or [""]:
            d.text((x, y), line, font=F(size, bold), fill=color)
            y += size + spacing
    return y


def caption(im, s):
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, H - 78, W, H), fill=(18, 49, 42, 235))
    wrap(d, (40, H - 66), s, 21, (255, 255, 255), 105, spacing=5)


def app(tab, course="pdc"):
    """Base app chrome: header, course sidebar, tabs."""
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 58), fill=PANEL)
    d.line((0, 58, W, 58), fill=LINE)
    logo(d, 26, 19, 20, ACCENT)
    d.text((54, 14), "ClassMind", font=F(24, True), fill=INK)
    d.text((190, 22), "AI study companion for Google Classroom", font=F(14), fill=MUTED)
    d.rounded_rectangle((930, 18, 1080, 42), 12, fill=SOFT)
    d.text((943, 21), "Google Classroom", font=F(14, True), fill=ACCENT)
    d.text((1095, 21), "ayesha@student.edu", font=F(14), fill=MUTED)
    d.line((240, 58, 240, H), fill=LINE)
    d.text((22, 76), "COURSES", font=F(12, True), fill=MUTED)
    for i, c in enumerate(mock_data.COURSES):
        y = 100 + i * 58
        if c["id"] == course:
            d.rounded_rectangle((12, y, 228, y + 52), 8, fill=SOFT)
        d.text((24, y + 6), textwrap.shorten(c["name"], 27, placeholder="…"), font=F(15), fill=INK)
        n = sum(1 for it in ITEMS if it["course_id"] == c["id"])
        d.text((24, y + 28), f"{c['section']} · {n} items", font=F(12), fill=MUTED)
    for i, t in enumerate(["Smart stream", "Syllabus map", "Ask your course", "Study tools"]):
        x = 270 + i * 150
        d.text((x, 74), t, font=F(15, t == tab), fill=INK if t == tab else MUTED)
        if t == tab:
            d.line((x, 100, x + d.textlength(t, font=F(15, True)), 100), fill=ACCENT, width=3)
    d.line((262, 101, W - 30, 101), fill=LINE)
    return im, d


# ------------------------------------------------------------------ scenes: (seconds, draw(t)->Image)
def title(t):
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    logo(d, 92, 195, 44, MINT)
    d.text((90, 250), "ClassMind", font=F(84, True), fill=(255, 255, 255))
    d.text((92, 360), "AI study companion for Google Classroom", font=F(30), fill=MINT)
    d.text((92, 470), "Prototype walkthrough", font=F(22, True), fill=(201, 214, 209))
    d.text((92, 505), "Hamas Naveed (23i-3014) · Azfaar Salahuddin (23i-3055)", font=F(20), fill=(201, 214, 209))
    return im


def problem(t):
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((80, 60), "THE PROBLEM", font=F(16, True), fill=ACCENT)
    d.text((80, 90), "Every study session starts with manual work", font=F(38, True), fill=INK)
    steps = ["Scroll the Classroom stream to find syllabus posts", "Download every PPTX and PDF, one by one",
             "Upload them to a chatbot that forgets them next chat", "Repeat for every course and every exam"]
    for i, s in enumerate(steps):
        if t < 2 + i * 3:
            break
        y = 190 + i * 95
        d.ellipse((80, y, 132, y + 52), fill=ACCENT)
        d.text((106, y + 26), str(i + 1), font=F(22, True), fill=(255, 255, 255), anchor="mm")
        d.text((160, y + 12), s, font=F(26), fill=INK)
    caption(im, "Course material is scattered across a dozen Classroom courses. ClassMind removes these four steps entirely.")
    return im


def signin(t):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((390, 120, 890, 560), 16, fill=PANEL, outline=LINE, width=2)
    d.text((640, 180), "ClassMind", font=F(34, True), fill=INK, anchor="mm")
    d.text((640, 228), "Connect your Google Classroom", font=F(18), fill=MUTED, anchor="mm")
    if t < 6:
        d.rounded_rectangle((470, 290, 810, 340), 10, fill=ACCENT)
        d.text((640, 315), "Sign in with Google", font=F(18, True), fill=(255, 255, 255), anchor="mm")
        d.text((640, 380), "Read-only access: courses, posts, coursework, files", font=F(14), fill=MUTED, anchor="mm")
        cap = "Step 1 — the student signs in once with Google. ClassMind only asks for read-only Classroom and Drive scopes."
    else:
        p = min(1, (t - 6) / 14)
        steps = ["Reading courses", "Reading announcements & coursework", "Downloading slide decks", "Parsing slides", "Classifying posts", "Building syllabus map"]
        for i, s in enumerate(steps):
            done = p * len(steps) > i + 1
            cur = int(p * len(steps)) == i
            d.text((450, 280 + i * 34), ("✓ " if done else "• ") + s, font=SYM(16) if done else F(16, cur), fill=ACCENT if done else INK if cur else MUTED)
        d.rounded_rectangle((450, 500, 830, 514), 7, fill=LINE)
        d.rounded_rectangle((450, 500, 450 + 380 * p, 514), 7, fill=ACCENT)
        n = sum(len(a["slides"]) for it in ITEMS for a in it["attachments"])
        cap = f"Sync: {len(mock_data.COURSES)} courses, {len(ITEMS)} posts and {n} slides are parsed and classified — no downloading or uploading."
    caption(im, cap)
    return im


def stream(course, hi=None, fixed=False, cap=""):
    def draw(t):
        im, d = app("Smart stream", course)
        items = sorted([i for i in ITEMS if i["course_id"] == course], key=lambda x: x["date"], reverse=True)
        scroll = int(min(max(0, t - 6) * 22, max(0, len(items) * 92 - 520))) if not hi else 0
        y = 118 - scroll
        for it in items:
            if y > H - 90:
                break
            lab = dict(LABELS[it["id"]])
            if fixed and it["id"] == hi:
                lab.update(confidence=1.0, source="student")
            low = lab["confidence"] < 0.6
            if y > 100:
                box = (262, y, W - 30, y + 82)
                d.rounded_rectangle(box, 10, fill=PANEL, outline=WARN if it["id"] == hi and not fixed else LINE, width=3 if it["id"] == hi else 1)
                d.text((280, y + 10), textwrap.shorten(it["title"], 60, placeholder="…"), font=F(16, True), fill=INK)
                d.text((280, y + 34), textwrap.shorten(it["description"], 80, placeholder="…"), font=F(13), fill=MUTED)
                if it["attachments"]:
                    a = it["attachments"][0]
                    d.text((280, y + 56), f"Attachment: {a['name']} · {len(a['slides'])} slides indexed", font=F(12), fill=ACCENT)
                lbl = lab["label"].replace("_", " ")
                tw = d.textlength(lbl, font=F(13, True))
                d.rounded_rectangle((W - 60 - tw - 20, y + 10, W - 60, y + 32), 6, fill=WARN_SOFT if low else SOFT)
                d.text((W - 70 - tw, y + 12), lbl, font=F(13, True), fill=WARN if low else ACCENT)
                info = "corrected by you" if lab["source"] == "student" else f"{round(lab['confidence'] * 100)}% · {lab['source']}"
                if lab["lecture"]:
                    info += f" · Lecture {lab['lecture']}"
                d.text((W - 60, y + 40), info, font=F(12), fill=MUTED, anchor="ra")
                if low:
                    d.text((W - 60, y + 58), "⚠ Unsure — please check", font=SYM(12), fill=WARN, anchor="ra")
            y += 92
        caption(im, cap)
        return im
    return draw


def syllabus(t):
    im, d = app("Syllabus map", "pdc")
    d.text((270, 118), "Detected automatically from teacher announcements.", font=F(15), fill=MUTED)
    y = 150
    for exam, s in SYL["pdc"].items():
        d.rounded_rectangle((262, y, W - 30, y + 150), 10, fill=PANEL, outline=LINE)
        d.text((282, y + 14), exam, font=F(24, True), fill=INK)
        d.text((282, y + 48), f"From teacher announcement on {s['date']}", font=F(13), fill=MUTED)
        x, yy = 282, y + 78
        for n in s["lectures"]:
            title = next((i["title"] for i in ITEMS if i["course_id"] == "pdc" and LABELS[i["id"]]["lecture"] == n), f"Lecture {n}")
            label = textwrap.shorten(title, 40, placeholder="…")
            tw = d.textlength(label, font=F(13))
            if x + tw + 24 > W - 40:
                x, yy = 282, yy + 34
            d.rounded_rectangle((x, yy, x + tw + 20, yy + 28), 6, fill=SOFT)
            d.text((x + 10, yy + 5), label, font=F(13), fill=INK)
            x += tw + 30
        y += 170
    src = next(i for i in ITEMS if i["id"] == "pdc-syl1")
    d.rounded_rectangle((262, y, W - 30, y + 80), 10, fill=(240, 240, 236))
    wrap(d, (282, y + 12), "Source post: “" + src["description"] + "”", 13, MUTED, 120)
    caption(im, "The classifier flagged the teacher's posts as syllabus, and extraction turned them into exam → lecture ranges.")
    return im


def chat(convo, cap):
    """convo: list of (question, answer_dict). Typing animation for the last question."""
    def draw(t):
        im, d = app("Ask your course", "pdc")
        y = 120
        for k, (q, r) in enumerate(convo):
            last = k == len(convo) - 1
            shown = q[: int(t * 18)] if last else q
            tw = min(560, d.textlength(shown, font=F(15)) + 30)
            d.rounded_rectangle((W - 40 - tw, y, W - 40, y + 38), 10, fill=ACCENT)
            d.text((W - 40 - tw + 15, y + 10), shown, font=F(15), fill=(255, 255, 255))
            y += 50
            if last and t < len(q) / 18 + 1.5:
                if t > len(q) / 18 + 0.3:
                    d.text((280, y + 6), "Searching your course material…", font=F(14), fill=MUTED)
                break
            lines = []
            for para in r["answer"].split("\n"):
                lines += textwrap.wrap(para, 105) or [""]
            lines = lines[:9]
            h = 24 + len(lines) * 22 + (34 if r["citations"] else 0) + 24
            d.rounded_rectangle((262, y, W - 120, y + h), 10, fill=PANEL if r["grounded"] else WARN_SOFT,
                                outline=LINE if r["grounded"] else WARN)
            yy = y + 12
            for ln in lines:
                d.text((280, yy), ln, font=F(14), fill=INK)
                yy += 22
            x = 280
            for i, c in enumerate(r["citations"][:3]):
                s = f"[{i + 1}] {c['label']} · {textwrap.shorten(c["file"], 28, placeholder="…")}"
                cw = d.textlength(s, font=F(12))
                d.rounded_rectangle((x, yy + 4, x + cw + 14, yy + 26), 6, outline=ACCENT)
                d.text((x + 7, yy + 7), s, font=F(12), fill=ACCENT)
                x += cw + 24
            yy += 34 if r["citations"] else 0
            d.text((280, yy), f"Retrieval confidence {round(r['confidence'] * 100)}%" if r["grounded"]
                   else "Not answered: no supporting source in your material", font=F(12), fill=MUTED)
            y += h + 16
        caption(im, cap)
        return im
    return draw


def guide(t):
    r = pipeline.study_tool("guide", "pdc", "Sessional 1", IDX, SYL)
    im, d = app("Study tools", "pdc")
    d.text((270, 118), f"Exam: Sessional 1   ·   lectures {', '.join(map(str, r['lectures']))}   ·   {len(r['citations'])} slides used",
           font=F(14, True), fill=ACCENT)
    lines = []
    for ln in r["markdown"].split("\n"):
        if ln.startswith("### "):
            lines.append(("h", ln[4:]))
        else:
            for w in textwrap.wrap(ln.replace("**", "").replace("`", ""), 118) or [""]:
                lines.append(("p", w))
    off = min(int(max(0, t - 5) * 1.5), max(0, len(lines) - 24))
    y = 150
    for kind, s in lines[off:]:
        if y > H - 100:
            break
        if kind == "h":
            y += 6
            d.text((280, y), s, font=F(18, True), fill=INK)
            y += 28
        else:
            d.text((280, y), s, font=F(13), fill=INK)
            y += 20
    caption(im, "“Make me a study guide for PDC Sessional 1” — summaries, key formulas and likely questions, each cited [n] to its slide.")
    return im


def cards(t):
    r = pipeline.study_tool("flashcards", "pdc", "Sessional 1", IDX, SYL)
    im, d = app("Study tools", "pdc")
    d.text((270, 118), f"Flashcards · Sessional 1 · {len(r['cards'])} cards (click to flip)", font=F(14, True), fill=ACCENT)
    for i, c in enumerate(r["cards"][:9]):
        x, y = 270 + (i % 3) * 330, 150 + (i // 3) * 158
        flip = t > 5 and i == int((t - 5) / 1.5) % 9
        d.rounded_rectangle((x, y, x + 310, y + 145), 10, fill=SOFT if flip else PANEL, outline=LINE)
        wrap(d, (x + 14, y + 12), c["a"] if flip else c["q"], 13, ACCENT if flip else INK, 40, bold=not flip, spacing=4)
        d.text((x + 14, y + 122), c["ref"], font=F(11), fill=MUTED)
    caption(im, "Flashcards are generated from exactly the Sessional 1 slides; each card shows the slide it came from.")
    return im


def quiz(t):
    r = pipeline.study_tool("quiz", "pdc", "Sessional 1", IDX, SYL)
    im, d = app("Study tools", "pdc")
    d.text((270, 118), "Practice quiz · Sessional 1", font=F(14, True), fill=ACCENT)
    y = 148
    for n, q in enumerate(r["questions"][:3]):
        y = wrap(d, (280, y), f"{n + 1}. {q['q']}", 14, INK, 120, bold=True, spacing=4) + 4
        for o in q["options"]:
            answered = t > 4 + n * 3
            col = ACCENT if answered and o == q["answer"] else INK
            d.text((300, y), ("● " if answered and o == q["answer"] else "○ ") + o, font=F(14, answered and o == q["answer"]), fill=col)
            y += 22
        if t > 4 + n * 3:
            d.text((300, y), q["why"], font=F(12), fill=MUTED)
        y += 30
    caption(im, "A practice quiz with answers and explanations that point back to the source slide.")
    return im


def arch(t):
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((60, 36), "How it works", font=F(34, True), fill=INK)
    a = Image.open(architecture())
    a.thumbnail((W - 100, 520))
    im.paste(a, ((W - a.width) // 2, 100))
    caption(im, "Ingestion runs on each sync; serving runs on each question. Files are indexed once per course and shared by all students.")
    return im


def end(t):
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    d.text((W // 2, 270), "ClassMind", font=F(64, True), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 350), "Your Classroom, organised and ready to study.", font=F(26), fill=MINT, anchor="mm")
    d.text((W // 2, 430), "github.com/HamasNaveed/GenAI-Project   ·   python app.py", font=F(20), fill=(201, 214, 209), anchor="mm")
    return im


Q1, Q2, Q3 = "What is covered in Sessional 1?", "Explain Amdahl's law with an example", "Who won the football world cup?"
A1, A2, A3 = (pipeline.answer(q, "pdc", IDX, SYL) for q in (Q1, Q2, Q3))

SCENES = [
    (10, title),
    (18, problem),
    (24, signin),
    (26, stream("pdc", cap="Smart stream — every post is labelled (slides, assignment, quiz, syllabus…) with a confidence score and lecture number.")),
    (18, stream("genai", hi="genai-misc", cap="When the AI is unsure (45%) it says so: this vague post is flagged “Unsure” instead of silently guessed.")),
    (14, stream("genai", hi="genai-misc", fixed=True, cap="The student confirms the label in one click. Corrections are logged and used to improve the classifier.")),
    (22, syllabus),
    (20, chat([(Q1, A1)], "Ask your course: syllabus questions are answered from the teacher's announcement, with the post cited.")),
    (24, chat([(Q2, A2)], "Concept questions retrieve the right slides with BM25 and answer only from them, citing lecture and slide.")),
    (20, chat([(Q2, A2), (Q3, A3)], "Off-topic or missing material? ClassMind refuses instead of hallucinating: “not found in your course material”.")),
    (28, guide),
    (16, cards),
    (18, quiz),
    (18, arch),
    (8, end),
]


def main():
    out = os.path.join(HERE, "ClassMind_Walkthrough.mp4")
    total = sum(s for s, _ in SCENES)
    with imageio.get_writer(out, fps=FPS, codec="libx264", quality=7, macro_block_size=16) as w:
        for secs, draw in SCENES:
            for f in range(secs * FPS):
                w.append_data(np.asarray(draw(f / FPS).convert("RGB")))
    print(f"{out}  ({total // 60}:{total % 60:02d})")


if __name__ == "__main__":
    main()
