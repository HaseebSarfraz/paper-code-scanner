Week	Dates (2025)	Mon – Fri learning + build targets (what you’ll actually do)	App state by Sunday evening	CSC209 Saturday lab (≈ 3 h)	Hours
0	25 Apr – 30 Apr	• Install VS Code, GitLens, ESLint, Prettier, Docker ext.
• git init, push empty repo, add GitHub Actions “hello” workflow.
• Create index.html + Live-Server.
• Copy roadmap → ROADMAP.md, Markdown preview.	Blank landing page with “Hello, world!”, repo shows green CI badge.	WSL + Linux tour, first 25 shell commands, write hello.sh.	38
1	01 May – 07 May	• Learn semantic HTML5 (header, main, footer).
• CSS Grid & Flexbox; Tailwind config.
• Build Apple-style hero: headline, sub-text, CTA button, responsive breakpoints.
• Add favicon + basic colour palette.	Polished hero page that scales from phone to desktop; Tailwind classes everywhere.	Write C “hello, world”; extend to line-counter that reads a file; first Makefile with all/clean.	31
2	08 May – 14 May	• ES 2023 JS: modules, const/let, arrow funcs, fetch.
• Add two-pane page: left <textarea>, right Prism.js syntax highlighter.
• Tailwind cards, dark-mode toggle.
• Lint with ESLint, format with Prettier.	Interactive highlighter — paste code, right pane colours instantly; dark-mode works.	Pointers & dynamic array in C; run under valgrind and note leaks.	15
3	15 May – 21 May	• Introduce TypeScript strict mode; set up tsconfig.json.
• Migrate all JS to TS; types for Prism & DOM.
• Swap dev server to Vite with hot-reload.
• Zero TS errors, ESLint passes in CI.	Same UI but TS-powered; fast Vite refresh; CI fails if types break.	Improve Makefile: pattern rules, .PHONY, make test.	15
4	22 May – 28 May	• Scaffold React 19 app with Vite TS template.
• Build Upload.tsx: drag-&-drop or camera input (via getUserMedia).
• Fake OCR: after upload show placeholder code.
• Add React Router & simple /about page.	React SPA: nav bar, upload zone, placeholder OCR appearing with skeleton loader.	fork → execvp → waitpid mini-cp; measure return codes.	15
5	29 May – 04 Jun	• Integrate Monaco Editor (@monaco-editor/react).
• Global state with React Context: CodeContext stores text.
• Theme sync (light/dark) with Tailwind.
• Disable Run button for now.	Split-pane IDE: left read-only OCR preview, right full Monaco editor; Run greyed-out.	Unix pipes & filters: build upper program; chain `cat file	upper
6	05 Jun – 11 Jun	• Install Node 18 LTS; set up Express server (/ping).
• Stub /ai/analyse route returns mock JSON advice.
• Front end polls /ping; green/red status dot.
• Show mock Insights card alongside editor.	API-connected UI: header dot shows live; Insights tab filled with dummy advice.	Add SIGINT handler to upper; press Ctrl-C to exit cleanly.	15
7	12 Jun – 18 Jun	• Add Prisma ORM, sqlite.db; define Run model.
• Migrate & seed dummy rows.
• Create /runs REST endpoints.
• Build History page (table, badges).	History view listing dummy runs (lang, hash, status).	POSIX threads: producer/consumer buffer with mutex + cond-var.	15
8	19 Jun – 25 Jun	• ng new scanner-ng (Angular 19).
• Build Material upload card + fake OCR.
• Route /ng served by Vite proxy.
• Compare Signals vs. React hooks.	Angular demo live at /ng with indigo toolbar; React app still default.	gdb: step through upper, inspect vars, errno, backtrace.	15
9	26 Jun – 02 Jul	• Decision doc: React or Angular as primary.
• Delete alt-framework code; refactor folders.
• Global style cleanup; create ESLint/Prettier monorepo config.
• Commit ARCHIVE.md for removed POC.	Unified code-base with one framework; cleaner repo tree and a new logo.	dup2, build mini tee clone; practice file-descriptor juggling.	15
10	03 Jul – 09 Jul	• FastAPI OCR endpoint live (Python, Tesseract).
• Front end posts image → gets real code.
• Add progress ring while waiting.
• Connect /ai/analyse to Llama-3 (8 B, quantised).	Real OCR + AI advice: user snaps photo, sees extracted code and edge-case tips.	TCP socket echo server & client in C.	15
11	10 Jul – 16 Jul	• Build Docker image for sandbox compiler.
• Node spawns container, streams stdout over SSE.
• Console drawer UI with ANSI colours; Stop btn.
• Time-out after 60 s.	Runnable code: click Run, console streams output/errors live.	Handle SIGTERM in echo server; graceful shutdown.	15
12	17 Jul – 23 Jul	• Add JWT auth (register/login).
• Prisma User model; link Runs ↔ Users.
• Personal history filter; avatar initials.
• AI route now suggests test cases.	User accounts: login modal, avatar, History shows only your runs; Insights suggests tests.	Bash script: git pull, tar compress, scp to remote for backups.	15
13	24 Jul – 30 Jul	• Add manifest.json, icons, service-worker (VitePWA).
• Cache UI & last run; offline snackbar.
• Fix a11y & colour-contrast to hit Lighthouse ≥ 90.	Installable PWA: “Add to Home Screen” works; app functions offline with cached runs.	Create crib-sheet of 20 key system calls; timed quiz.	15
14	31 Jul – 06 Aug	• Write docker-compose.yml (gateway, Python, db).
• Set GitHub Action: on tag → build & push Docker images, auto-deploy to Render.
• Draft & publish tech-blog (“Built a paper-scanner IDE in 14 weeks”).
• Tag repo v1.0.0.	Public URL live (https://scanmycode.app) with footer “v1.0.0 • Blog”.	Free week to revisit any weak CSC209 topic or polish UI.	15
