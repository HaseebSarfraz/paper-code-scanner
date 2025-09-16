# Paper → Compiler

## 🎬 Demos

<video controls width="840"
  src="https://github.com/HaseebSarFraz/paper-code-scanner/releases/latest/download/Demo.mp4"></video>
<p><a href="https://github.com/HaseebSarFraz/paper-code-scanner/releases/latest/download/Demo.mp4">Download Demo 1 (mp4)</a></p>

Turn a **code screenshot** into runnable **Python**, auto-generate **pytest** suites with a local **CodeLlama** (llama.cpp) server, and execute them inside a locked **Docker** runner. Frontend is Vite/React; backend is Flask (served via **waitress** for the web app).

---

## What’s inside

- **Backend (Flask)** – `backend/__init__.py` (API) + `backend/llm.py` (syntax fix + test generation)
- **Frontend (Vite/React/Monaco)** – `src/` (upload screenshot, edit code, run tests)
- **Model server** – `llama.cpp` running CodeLlama 13B (GGUF)
- **Runner** – Docker image `paper-runner:py310` runs `pytest` with no network & strict limits

---

## Requirements

- Windows (PowerShell) or macOS/Linux
- Python **3.10+**
- Node **18+**
- Docker Desktop / Docker Engine
- `llama.cpp` built for your GPU/CPU + a **CodeLlama 13B** GGUF (e.g. `codellama-13b-instruct.Q5_K_M.gguf`)

> **OCR (optional)** — If you want OCR inside the app, install the correct **paddlepaddle / paddlepaddle-gpu** wheel for your OS/CUDA first, then:
>
> ```powershell
> pip install paddleocr opencv-python
> ```
>
> (They’re also listed in `requirements.txt`.)

---

## Quick start (3 terminals)

### Terminal A — Model server (llama.cpp)

#### Start the server
> Adjust the `-m` path to your GGUF model.
```powershell
llama-server `
  -m C:\models\codellama-13b-instruct.Q5_K_M.gguf `
  --host 127.0.0.1 --port 8080 `
  --seed 12345 --slots 1
```

#### Health check
```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/health'
```

#### (Optional) Faster CUDA flags
```powershell
llama-server `
  -m C:\models\codellama-13b-instruct.Q5_K_M.gguf `
  -ngl 40 -c 1024 -b 512 `
  --host 127.0.0.1 --port 8080 --seed 12345
```

---

### Terminal B — Backend (Flask via waitress)

#### Setup (first time)
```powershell
# From repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Build the Docker runner (first time)
```powershell
docker build -t paper-runner:py310 runner/
```

#### Run the backend with waitress (recommended)
```powershell
# Point backend to llama.cpp
$env:LLAMA_BASE_URL = "http://127.0.0.1:8080"
# Optional: control tokens for test generation
$env:LLAMA_TEST_N_PREDICT = "280"

# Serve Flask via waitress (WSGI)
waitress-serve --listen=127.0.0.1:5000 backend:app
# → API available at http://127.0.0.1:5000
```

#### Dev alternative
```powershell
python -m backend
```

---

### Terminal C — Frontend (Vite)
```powershell
npm i
npm run dev
# Open the printed http://localhost:5173 (or similar)
```

---

## Minimal API smoke tests (optional)

### `/api/run_tests`
```powershell
$objective = 'Return x*x'
$code = @'
def func(x: int) -> int:
    return x * x
'@
$body = @{ code = $code; objective = $objective } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/run_tests' -Method Post -ContentType 'application/json' -Body $body
```

### `/api/ocr` (requires Pillow + PaddleOCR)
```powershell
Invoke-RestMethod `
  -Uri 'http://127.0.0.1:5000/api/ocr' `
  -Method Post `
  -InFile .\sample.png `
  -ContentType 'multipart/form-data'
```

---

## Environment knobs (optional)

These are read by `backend/llm.py`:

```powershell
$env:LLAMA_BASE_URL     = "http://127.0.0.1:8080"
$env:LLAMA_TEMPERATURE  = "0.3"
$env:LLAMA_TOP_P        = "0.85"
$env:LLAMA_TOP_K        = "30"
$env:LLAMA_N_PREDICT    = "280"   # 240–320 is a good range
$env:LLAMA_SEED         = "12345"
$env:LLAMA_HTTP_TIMEOUT = "300"
```

---

## Troubleshooting

- **Only smoke test appears** — Increase `LLAMA_N_PREDICT` (e.g., 280–320), keep stop tokens as configured, and make sure the model server health endpoint returns `{"status":"ok"}`.
- **`docker` not found** — Start Docker Desktop and rebuild the runner:
  ```powershell
  docker build -t paper-runner:py310 runner/.
  ```
- **OCR empty/odd** — Verify the correct `paddlepaddle` wheel for your OS/CUDA is installed, then:
  ```powershell
  pip install paddleocr opencv-python
  ```
- **CORS / frontend can’t hit API** — Ensure waitress is serving on `127.0.0.1:5000` and you’re opening the Vite dev URL from the same machine.
