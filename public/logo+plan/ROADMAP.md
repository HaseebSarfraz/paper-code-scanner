# Paper-to-Compiler — **Revised Road Map (MVP-first)**  

**Profile & Assumptions**

| Skill              | Level | Notes |
|--------------------|-------|-------|
| Python + FastAPI   | ✅ good | use for all back-end work |
| Java / JavaFX      | ✅ good | not needed for this project |
| React (Vite + TS)  | 🚩 new | assume 8-10 h to reach “comfortable basics” |
| Tailwind CSS       | ☑ basics | can read classes, will reinforce while coding |
| Docker             | 🚩 new | postpone sandbox work until last sprint |

> **Total runway:** ~ 5½ weeks of focused evenings / weekends (≈ 15 h / wk)  
> **Goal:** Public demo URL + GitHub repo that a prof/employer can clone & run.

---

## Sprint Plan

| Sprint | Calendar (2025) | Deliverable by Sunday | Key Tasks | Est. hrs |
|:------:|:---------------:|-----------------------|-----------|:-------:|
| **A** | **24 Jun → 30 Jun** | Vite + React TS project that replicates your current static page | * Kick-start project: `npm create vite@latest scanner -- --template react-ts`  <br> * Install Tailwind + daisyUI (or shadcn)  <br> * Break existing HTML into `<Header/>`, `<EditorPane/>`, `<ResultPane/>`  <br> * Static layout only; no state yet | **18 h** |
| **B** | **01 Jul → 07 Jul** | “Fake OCR” flow end-to-end | * Add drag-drop/camera (`react-dropzone`, `getUserMedia`)  <br> * Stub FastAPI `/api/ocr/fake` → returns dummy code  <br> * Wire React fetch; display code in a **Monaco** read-only editor  <br> * Buttons: **Upload**, **Reset** | **15 h** |
| **C** | **08 Jul → 14 Jul** | Real PaddleOCR + LLM “fix indentation” API | * Package your finetuned PaddleOCR in FastAPI route `/ocr`  <br> * Call GPT-4o (or local model) in `/fix`; return JSON `{fixed_code}`  <br> * React: editable Monaco pane; “Apply Fixes” button | **20 h** |
| **D** | **15 Jul → 21 Jul** | Test-runner MVP (no sandbox) | * Hard-code 5–7 pytest test-files per exercise  <br> * FastAPI `/analyse` runs `pytest`, parses results → JSON  <br> * UI: **Analyse** button, progress spinner, results panel (“3/7 passed…”) | **17 h** |
| **E** | **22 Jul → 27 Jul** | Public deploy + UI polish | * GitHub Actions: lint, `npm test`, `pytest`  <br> * Deploy front-end to **Vercel**; API to **Render**/**Railway**  <br> * Add dark-mode toggle, better spacing, favicon, README GIF  <br> * Record 30-sec Loom demo; share with profs | **16 h** |
| **F** *(optional)* | **29 Jul → 06 Aug** | Secure code-exec (Docker sandbox) & PWA niceties | * Create minimal `Dockerfile` (python:3.11-slim + pytest)  <br> * Spawn container per run (timeout 8 s)  <br> * Add service-worker, offline cache, Lighthouse ≥ 90 | **??** |

---

## UI Cleanup Checklist (you’ll chip away each sprint)

- [ ] Replace textarea with **Monaco Editor** (theme matches Tailwind dark/light)
- [ ] Align header nav: logo left, menu (“Upload / Sample”) right
- [ ] Convert hard-coded sizes to responsive Tailwind classes
- [ ] Add **Toast** component for errors / success
- [ ] Disable buttons while network request in flight
- [ ] `react-router-dom` route structure: `/` • `/about` (optional)
- [ ] Accessibility: semantic `button`, `label`, `aria-busy`

---

### Deployment Quick-Start (for Sprint E)

```bash
# front-end
npm run build         # outputs dist/
vercel deploy         # detects Vite

# back-end
# on Render/Railway
gunicorn -k uvicorn.workers.UvicornWorker api:app