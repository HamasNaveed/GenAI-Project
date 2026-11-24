"""ClassMind web app. `python app.py` -> http://localhost:5000 (mock mode unless you sign in with Google)."""
import os
import secrets

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from classmind import classroom, mock_data, pipeline

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")  # localhost only; use HTTPS in production
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")  # user may untick a scope on Google's consent screen

# ponytail: single in-process store (one user at a time); per-user DB + shared per-course index for multi-user
STORE = {}


def load(courses, items, mode, user="Demo Student"):
    labels = {it["id"]: pipeline.classify(it) for it in items}
    STORE.update(courses=courses, items=items, labels=labels, mode=mode, user=user,
                 corrections={}, syllabus=pipeline.extract_syllabus(items, labels),
                 index=pipeline.Index(items, labels))


load(mock_data.COURSES, mock_data.ITEMS, "mock")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/state")
def state():
    return jsonify(
        mode=STORE["mode"], user=STORE["user"], llm="claude" if pipeline.llm() else "mock",
        google_ready=bool(classroom.secret_file()), courses=STORE["courses"], syllabus=STORE["syllabus"],
        items=[{**it, "attachments": [{"name": a["name"], "slides": len(a.get("slides", []))} for a in it["attachments"]],
                **STORE["labels"][it["id"]], "corrected": it["id"] in STORE["corrections"]}
               for it in sorted(STORE["items"], key=lambda x: x["date"], reverse=True)])


@app.post("/api/chat")
def chat():
    b = request.get_json(force=True)
    q = (b.get("question") or "").strip()[:2000]
    if not q:
        return jsonify(error="Empty question"), 400
    return jsonify(pipeline.answer(q, b.get("course_id"), STORE["index"], STORE["syllabus"]))


@app.post("/api/tool")
def tool():
    b = request.get_json(force=True)
    if b.get("tool") not in ("guide", "flashcards", "quiz"):
        return jsonify(error="Unknown tool"), 400
    return jsonify(pipeline.study_tool(b["tool"], b.get("course_id"), b.get("exam"), STORE["index"], STORE["syllabus"]))


@app.post("/api/label")
def relabel():
    """Student corrects a wrong label -> syllabus map and index are rebuilt from the corrected labels."""
    b = request.get_json(force=True)
    if b.get("item_id") not in STORE["labels"] or b.get("label") not in pipeline.LABELS:
        return jsonify(error="Bad label"), 400
    lab = STORE["labels"][b["item_id"]]
    STORE["corrections"][b["item_id"]] = {"from": lab["label"], "to": b["label"]}  # feedback log for prompt tuning
    lab.update(label=b["label"], confidence=1.0, source="student")
    STORE["syllabus"] = pipeline.extract_syllabus(STORE["items"], STORE["labels"])
    return jsonify(ok=True)


# ---------------------------------------------------------------- Google sign-in (real mode)
@app.get("/login")
def login():
    if not classroom.secret_file():
        return "No Google OAuth client file found. See README > Real Google Classroom mode.", 400
    f = classroom.flow(url_for("oauth2callback", _external=True))
    auth_url, session["state"] = f.authorization_url(access_type="offline", prompt="consent")
    session["code_verifier"] = getattr(f, "code_verifier", None)
    return redirect(auth_url)


@app.get("/oauth2callback")
def oauth2callback():
    f = classroom.flow(url_for("oauth2callback", _external=True), state=session.get("state"))
    if session.get("code_verifier"):
        f.code_verifier = session["code_verifier"]
    f.fetch_token(authorization_response=request.url)
    creds = f.credentials  # kept in memory only, never written to disk
    from googleapiclient.discovery import build
    email = build("oauth2", "v2", credentials=creds, cache_discovery=False).userinfo().get().execute().get("email", "")
    courses, items = classroom.sync(creds)
    load(courses, items, "google", email)
    return redirect("/")


@app.get("/logout")
def logout():
    """Disconnect: drop tokens and all synced data, back to demo data."""
    session.clear()
    load(mock_data.COURSES, mock_data.ITEMS, "mock")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
