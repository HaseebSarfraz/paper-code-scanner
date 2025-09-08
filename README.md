# =========================
# Quick start (PowerShell)
# =========================
# Repo root assumed: paper-code-scanner
# Create three terminals and run each section in the indicated window.

# ------------------------------------------------------------
# Terminal A — MODEL SERVER (run first; keeps running)
# ------------------------------------------------------------
# 3) Start the llama.cpp server (adjust model path)
llama-server `
-m C:\models\codellama-13b.Q5_K_M.gguf `
--host 127.0.0.1 --port 8080 `
--seed 12345 --slots 1
# Health check (in a separate prompt if you want):
#   Invoke-RestMethod -Uri 'http://127.0.0.1:8080/health'

# ------------------------------------------------------------
# Terminal B — BACKEND (Flask API)
# ------------------------------------------------------------
# 1) Clone & enter (run once)
git clone <your-repo-url>
cd paper-code-scanner

# 2) Python venv & install deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# (Optional OCR: install PaddleOCR after installing the correct paddlepaddle / paddlepaddle-gpu wheel)
# pip install paddleocr opencv-python

# 4) Build the Docker runner (first time only)
docker build -t paper-runner:py310 runner/

# 5) Run the backend
$env:LLAMA_BASE_URL = "http://127.0.0.1:8080"
$env:LLAMA_TEST_N_PREDICT = "280"    # 240–320 is a good range
python -m backend
# → API on http://127.0.0.1:5000  (leave this running)

# ------------------------------------------------------------
# Terminal C — FRONTEND (Vite app)
# ------------------------------------------------------------
# 6) Start the frontend
cd paper-code-scanner   # only if you're not already in repo root
npm i
npm run dev
# Open the printed localhost URL

# ------------------------------------------------------------
# (Optional) Minimal API smoke tests (any terminal)
# ------------------------------------------------------------
# /api/run_tests
$objective = 'Return x*x'
$code = @'
def func(x: int) -> int:
return x*x
'@
$body = @{ code = $code; objective = $objective } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/run_tests' -Method Post -ContentType 'application/json' -Body $body

# /api/ocr (requires Pillow + PaddleOCR)
# Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/ocr' -Method Post -InFile .\sample.png -ContentType 'multipart/form-data'
