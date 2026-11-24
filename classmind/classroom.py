"""Real Google Classroom sync (read-only). Produces the same item shape as mock_data.ITEMS."""
import glob
import io
import os

SCOPES = [
    "openid", "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def secret_file():
    """Path to the OAuth client JSON: $GOOGLE_CLIENT_SECRET_FILE or the first client_secret*.json in the repo root."""
    path = os.getenv("GOOGLE_CLIENT_SECRET_FILE")
    if path:
        return path if os.path.exists(path) else None
    found = glob.glob(os.path.join(os.path.dirname(__file__), "..", "client_secret*.json"))
    return found[0] if found else None


def flow(redirect_uri, state=None):
    from google_auth_oauthlib.flow import Flow
    return Flow.from_client_secrets_file(secret_file(), scopes=SCOPES, redirect_uri=redirect_uri, state=state)


def _pages(call, key, **kw):
    token = None
    while True:
        r = call(pageToken=token, **kw).execute()
        yield from r.get(key, [])
        token = r.get("nextPageToken")
        if not token:
            return


def _parse_file(drive, f):
    """Download a Drive attachment and return slides [{slide,title,text}]. PPTX, Google Slides, PDF, DOCX."""
    fid, title = f["id"], f.get("title", "file")
    meta = drive.files().get(fileId=fid, fields="mimeType,name").execute()
    mime = meta["mimeType"]
    if mime == "application/vnd.google-apps.presentation":
        data = drive.files().export(fileId=fid, mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation").execute()
        mime = "pptx"
    elif mime.startswith("application/vnd.google-apps"):
        data = drive.files().export(fileId=fid, mimeType="text/plain").execute()
        return [{"slide": 1, "title": title, "text": data.decode("utf-8", "ignore")[:20000]}]
    else:
        data = drive.files().get_media(fileId=fid).execute()
    buf = io.BytesIO(data)
    if mime == "pptx" or title.lower().endswith(".pptx"):
        from pptx import Presentation
        out = []
        for i, s in enumerate(Presentation(buf).slides, 1):
            texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
            notes = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
            out.append({"slide": i, "title": texts[0][:120] if texts else f"Slide {i}",
                        "text": " ".join(texts[1:] + [notes]).strip()})
        return out
    if title.lower().endswith(".pdf"):
        from pypdf import PdfReader
        return [{"slide": i, "title": f"{title} p.{i}", "text": p.extract_text() or ""}
                for i, p in enumerate(PdfReader(buf).pages, 1)]
    if title.lower().endswith(".docx"):
        from docx import Document
        return [{"slide": 1, "title": title, "text": "\n".join(p.text for p in Document(buf).paragraphs)}]
    return []  # ponytail: slide images / vision captions not parsed yet; add a vision pass for diagram-heavy decks


def sync(creds):
    """Read courses, announcements, coursework and materials. ponytail: full re-sync each time;
    use updateTime filters for incremental sync once courses get large."""
    from googleapiclient.discovery import build
    cls = build("classroom", "v1", credentials=creds, cache_discovery=False)
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    c = cls.courses()
    courses, items = [], []
    for co in _pages(c.list, "courses", studentId="me", courseStates=["ACTIVE"]):
        courses.append({"id": co["id"], "name": co["name"], "section": co.get("section", ""), "teacher": ""})
        sources = [
            ("announcement", c.announcements().list, "announcements", lambda x: ("", x.get("text", ""))),
            ("assignment", c.courseWork().list, "courseWork", lambda x: (x.get("title", ""), x.get("description", ""))),
            ("material", c.courseWorkMaterials().list, "courseWorkMaterial", lambda x: (x.get("title", ""), x.get("description", ""))),
        ]
        for kind, call, key, text in sources:
            for x in _pages(call, key, courseId=co["id"]):
                title, desc = text(x)
                atts = []
                for m in x.get("materials", []):
                    f = m.get("driveFile", {}).get("driveFile")
                    if f:
                        try:
                            atts.append({"name": f.get("title", "file"), "mime": "", "slides": _parse_file(drive, f)})
                        except Exception as e:  # one broken file must not stop the sync
                            atts.append({"name": f.get("title", "file"), "mime": "", "slides": [], "error": str(e)})
                items.append({"id": x["id"], "course_id": co["id"], "type": kind,
                              "title": title or desc[:60], "description": desc,
                              "date": x.get("creationTime", "")[:10], "attachments": atts})
    return courses, items
