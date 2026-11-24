"""Architecture diagram as a PNG (Pillow), shared by the report, slides and video."""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ACCENT, INK, MUTED, LINE, SOFT = (31, 111, 92), (29, 35, 32), (107, 113, 108), (190, 186, 176), (220, 239, 232)


def font(size, bold=False):
    for name in (("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def box(d, xy, title, sub, hi=False):
    d.rounded_rectangle(xy, 14, fill=SOFT if hi else (255, 255, 255), outline=ACCENT if hi else LINE, width=3 if hi else 2)
    cx = (xy[0] + xy[2]) / 2
    d.text((cx, xy[1] + 30), title, font=font(22, True), fill=INK, anchor="mm")
    d.text((cx, xy[1] + 60), sub, font=font(17), fill=MUTED, anchor="mm")


def arrow(d, a, b):
    d.line([a, b], fill=MUTED, width=3)
    (x1, y1), (x2, y2) = a, b
    if x1 == x2:
        s = 1 if y2 > y1 else -1
        d.polygon([(x2, y2), (x2 - 8, y2 - 12 * s), (x2 + 8, y2 - 12 * s)], fill=MUTED)
    else:
        s = 1 if x2 > x1 else -1
        d.polygon([(x2, y2), (x2 - 12 * s, y2 - 8), (x2 - 12 * s, y2 + 8)], fill=MUTED)


def architecture(path=os.path.join(HERE, "img", "architecture.png")):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    W, H = 1600, 640
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    bw, bh, gap, x0 = 330, 92, 60, 40
    xs = [x0 + i * (bw + gap) for i in range(4)]
    d.text((x0, 40), "INGESTION  ·  runs on each sync (background workers)", font=font(18, True), fill=ACCENT)
    top = [("Google Classroom API", "OAuth 2.0 · read-only scopes"), ("Sync worker", "courses, posts, Drive files"),
           ("Parser", "PPTX · PDF · DOCX → slide chunks"), ("AI classifier", "label · confidence · syllabus map")]
    for i, (t, s) in enumerate(top):
        box(d, (xs[i], 80, xs[i] + bw, 80 + bh), t, s, hi=i == 3)
        if i:
            arrow(d, (xs[i - 1] + bw, 80 + bh / 2), (xs[i], 80 + bh / 2))
    d.text((x0, 300), "SERVING  ·  runs on each question", font=font(18, True), fill=ACCENT)
    bottom = [("Student web app", "cited answers · study tools"), ("LLM generation", "Claude · grounded prompt"),
              ("Retrieval", "BM25 / hybrid · exam filter"), ("Knowledge base", "chunks + metadata per course")]
    for i, (t, s) in enumerate(bottom):
        box(d, (xs[i], 340, xs[i] + bw, 340 + bh), t, s, hi=i in (1, 2))
        if i:
            arrow(d, (xs[i], 340 + bh / 2), (xs[i - 1] + bw, 340 + bh / 2))
    arrow(d, (xs[3] + bw / 2, 80 + bh), (xs[3] + bw / 2, 340))
    d.text((xs[3] + bw / 2 + 12, 250), "indexed once,\nshared per course", font=font(16), fill=MUTED)
    d.rounded_rectangle((x0, 480, W - x0, 600), 14, outline=(180, 101, 27), width=2)
    d.text((x0 + 20, 498), "Guardrails", font=font(20, True), fill=(180, 101, 27))
    d.text((x0 + 20, 532), "Low-confidence labels flagged → student correction loop  ·  answer only above evidence threshold, else \"not found\"\n"
                           "every claim cites a slide  ·  no syllabus → no guessing  ·  slide text treated as data, never as instructions",
           font=font(17), fill=INK, spacing=8)
    im.save(path)
    return path


if __name__ == "__main__":
    print(architecture())
