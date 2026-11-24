const $ = (s) => document.querySelector(s);
const LABELS = ["lecture_slides", "assignment", "quiz", "syllabus", "announcement", "reference"];
const nice = (l) => l.replace("_", " ");
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
let S = null, course = null, filter = "all";

const post = (url, body) =>
  fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then((r) => r.json());

async function refresh() {
  S = await (await fetch("/api/state")).json();
  course = course && S.courses.some((c) => c.id === course) ? course : S.courses[0]?.id;
  $("#mode").textContent = S.mode === "mock" ? `Demo data · ${S.llm === "claude" ? "Claude" : "offline AI"}` : `Google Classroom · ${S.llm}`;
  $("#user").textContent = S.user;
  $("#signin").hidden = S.mode !== "mock" || !S.google_ready;
  $("#signout").hidden = S.mode === "mock";
  render();
}

function render() {
  $("#courses").innerHTML = S.courses.map((c) =>
    `<li data-id="${c.id}" class="${c.id === course ? "on" : ""}">${esc(c.name)}<small>${esc(c.section)} · ${S.items.filter((i) => i.course_id === c.id).length} items</small></li>`).join("");
  const items = S.items.filter((i) => i.course_id === course);
  $("#filters").innerHTML = ["all", ...LABELS].map((l) =>
    `<button data-f="${l}" class="${l === filter ? "on" : ""}">${nice(l)} (${l === "all" ? items.length : items.filter((i) => i.label === l).length})</button>`).join("");
  $("#stream").innerHTML = items.filter((i) => filter === "all" || i.label === filter).map((i) => {
    const low = i.confidence < 0.6;
    return `<div class="item">
      <h3>${esc(i.title)}</h3>
      <p>${esc(i.description)}</p>
      ${i.attachments.map((a) => `<span class="att">📎 ${esc(a.name)} · ${a.slides} slides indexed</span>`).join(" ")}
      <div class="meta">
        <span class="badge ${low ? "low" : ""}">${nice(i.label)}</span>
        <span class="conf">${i.source === "student" ? "corrected by you" : `${Math.round(i.confidence * 100)}% · ${i.source}`}${i.lecture ? ` · Lecture ${i.lecture}` : ""}</span>
        ${low ? `<div class="lowwarn">⚠ Unsure — please check</div>` : ""}
        <select data-item="${i.id}" title="Wrong label? Correct it">
          ${LABELS.map((l) => `<option ${l === i.label ? "selected" : ""} value="${l}">${nice(l)}</option>`).join("")}
        </select>
        <div class="muted">${i.date}</div>
      </div></div>`;
  }).join("") || `<p class="muted">Nothing here.</p>`;

  const syl = S.syllabus[course] || {};
  const lecTitle = (n) => (items.find((i) => i.lecture === n && i.label === "lecture_slides") || {}).title || `Lecture ${n} (not posted yet)`;
  $("#syllabus").innerHTML = Object.keys(syl).length
    ? Object.entries(syl).map(([exam, s]) => `<div class="card exam"><h3>${exam}</h3>
        <p class="muted">From teacher announcement on ${s.date}</p>
        <div class="lecs">${s.lectures.map((n) => `<span class="lec">${esc(lecTitle(n))}</span>`).join("")}</div></div>`).join("")
    : `<div class="card"><p class="muted">No syllabus announcement detected for this course yet. If a post is a syllabus, relabel it as “syllabus” in the stream.</p></div>`;

  $("#exam").innerHTML = Object.keys(syl).map((e) => `<option>${e}</option>`).join("") || `<option value="">No exams detected</option>`;
  const name = S.courses.find((c) => c.id === course)?.name || "";
  $("#suggest").innerHTML = ["What is covered in Sessional 1?", course === "pdc" ? "Explain Amdahl's law with an example" : "Explain retrieval-augmented generation",
    "Who won the football world cup?"].map((q) => `<button>${q}</button>`).join("");
  $("#q").placeholder = `Ask about ${name}…`;
}

function addMsg(html, cls) {
  const d = document.createElement("div");
  d.className = `msg ${cls}`;
  d.innerHTML = html;
  $("#chatlog").appendChild(d);
  d.scrollIntoView({ behavior: "smooth" });
  return d;
}

async function ask(q) {
  addMsg(esc(q), "me");
  const wait = addMsg("Searching your course material…", "ai");
  const r = await post("/api/chat", { question: q, course_id: course });
  wait.className = `msg ai ${r.grounded ? "" : "nf"}`;
  wait.innerHTML = `${md(r.answer || r.error)}
    <div class="cites">${(r.citations || []).map((c, i) => `<span class="cite" title="${esc(c.title)}">[${i + 1}] ${esc(c.label)} · ${esc(c.file)}</span>`).join("")}</div>
    <div class="muted" style="font-size:12px;margin-top:6px">${r.grounded ? `Retrieval confidence ${Math.round(r.confidence * 100)}%` : "Not answered: no supporting source in your material"}</div>`;
}

function md(s) {
  return esc(s).split("\n").map((l) =>
    l.startsWith("### ") ? `<h3>${l.slice(4)}</h3>` : l.startsWith("- ") ? `<div>• ${l.slice(2)}</div>` : l ? `<div>${l}</div>` : "<br>")
    .join("").replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`(.+?)`/g, "<code>$1</code>");
}

async function runTool(tool) {
  const out = $("#toolout");
  out.innerHTML = `<p class="muted">Selecting syllabus lectures and generating…</p>`;
  const r = await post("/api/tool", { tool, course_id: course, exam: $("#exam").value });
  if (r.error) return (out.innerHTML = `<p class="err">${esc(r.error)}</p>`);
  const head = `<p class="muted">${r.exam}: lectures ${r.lectures.join(", ")} · ${r.citations.length} slides used</p>`;
  if (r.markdown) out.innerHTML = head + md(r.markdown) +
    `<h3>Sources</h3>${r.citations.map((c, i) => `<div class="muted">[${i + 1}] ${esc(c.label)} — ${esc(c.title)} (${esc(c.file)})</div>`).join("")}`;
  else if (r.cards) out.innerHTML = head + `<div class="flash">${r.cards.map((c) =>
    `<div class="fc"><div class="q"><b>${esc(c.q)}</b></div><div class="a">${esc(c.a)}</div><small>${esc(c.ref)} · click to flip</small></div>`).join("")}</div>`;
  else out.innerHTML = head + r.questions.map((q, n) => `<div class="qz card"><b>${n + 1}. ${esc(q.q)}</b>
    ${q.options.map((o) => `<label><input type="radio" name="q${n}" data-ok="${o === q.answer}"> ${esc(o)}</label>`).join("")}
    <div class="muted why" hidden>${esc(q.why)}</div></div>`).join("");
}

document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-tab],[data-id],[data-f],[data-tool],.suggest button,.fc,.qz input");
  if (!t) return;
  if (t.dataset.tab) {
    document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("on", b === t));
    document.querySelectorAll("main section").forEach((s) => (s.hidden = s.id !== `tab-${t.dataset.tab}`));
  } else if (t.dataset.id) { course = t.dataset.id; filter = "all"; $("#chatlog").innerHTML = ""; render(); }
  else if (t.dataset.f) { filter = t.dataset.f; render(); }
  else if (t.dataset.tool) runTool(t.dataset.tool);
  else if (t.classList.contains("fc")) t.classList.toggle("flip");
  else if (t.matches(".qz input")) {
    const card = t.closest(".qz");
    card.querySelectorAll("label").forEach((l) => l.className = l.firstElementChild.dataset.ok === "true" ? "right" : l.contains(t) ? "wrong" : "");
    card.querySelector(".why").hidden = false;
  } else ask(t.textContent);
});

document.addEventListener("change", async (e) => {
  if (!e.target.dataset.item) return;
  await post("/api/label", { item_id: e.target.dataset.item, label: e.target.value });
  refresh();
});

$("#chatform").addEventListener("submit", (e) => {
  e.preventDefault();
  const q = $("#q").value.trim();
  if (q) { $("#q").value = ""; ask(q); }
});

refresh();
