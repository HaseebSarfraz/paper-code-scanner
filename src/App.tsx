// src/App.tsx
import React, { useState, useRef } from "react";
import Header       from "./Components/Header";
import WorkingPane  from "./Components/WorkingPane";


const LANGUAGES = [
  "Python",
  "Java",
  "C",
  "C++",
  "JavaScript",
] as const;

export default function App() {

  const [objective, setObjective] = useState("");          
  
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [language, setLanguage] = useState<(typeof LANGUAGES)[number]>(
    LANGUAGES[0]
  );
  const [code,   setCode]   = useState("");
  const [result, setResult] = useState("");
  const [photoFile, setPhotoFile] = useState<File | null>(null);

  const [step, setStep] = useState<"idle" | "picked" | "scanned" | "editing">(
  "idle"
);

  const [scanBusy, setScanBusy] = useState(false);
  const canScan    = step === "picked";
  const canEdit = true;
  const canRun     = step === "editing" && code.trim() !== "";
  const isReadOnly = step !== "editing";
  const fileInputRef = useRef<HTMLInputElement>(null);

  /* ----- handlers for the buttons ----- */
  function handleAttach() {
    fileInputRef.current?.click();
  }

  async function handleScan() {
    if (!photoFile) return;                 

  try {
    setScanBusy(true);
    setResult("⏳ Scanning…");

    const fd = new FormData();
    fd.append("file", photoFile, photoFile.name);

    const resp  = await fetch("http://localhost:5000/api/ocr", {
      method: "POST",
      body:   fd,
    });

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

    const { text } = await resp.json();   
    setCode(text);
    setResult("✅ Scan complete");

    setStep("scanned");                   // enables Edit button
  } catch (err: unknown) {
    console.error(err);
    const msg =
    err instanceof Error ? err.message : String(err);
    setResult(`❌ OCR failed: ${msg}`);
  } finally {
    setScanBusy(false);
  }
}
  

  function handleEdit() {
    setStep("editing");   // unlocks the editor
  }


  type TestCase = {
    name: string;
    status: "passed" | "failed" | "skipped" | "error";
    message?: string;        // short reason (from JUnit)
    classname?: string;
    duration?: number;       // seconds
  };

  function bucketFor(name: string): "normal" | "edge" | "adversarial" {
    const n = (name || "").toLowerCase();
    if (/\b(adversarial|invalid|negative|malformed|exception|error)\b/.test(n)) return "adversarial";
    if (/\b(edge|boundary|zero|max|min|empty|null)\b/.test(n)) return "edge";
   
    return "normal";
  }

  function iconFor(status: TestCase["status"]) {
    return status === "passed" ? "✅"
        : status === "skipped" ? "⚠️"
        : "❌"; // failed/error
  }

  async function handleRun() {
  try {
    setResult("⏳ Running tests…");

    const resp = await fetch("http://localhost:5000/api/run_tests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, objective }),
    });

    if (!resp.ok) {
      let msg = `HTTP ${resp.status}`;
      try {
        const j = await resp.json();
        if (j && (j.error || j.detail)) msg += ` — ${j.error || j.detail}`;
      } catch {
        try {
          const t = await resp.text();
          if (t) msg += ` — ${t.slice(0, 400)}`;
        } catch {}
      }
      throw new Error(msg);
    }

    const data = await resp.json();

  
    if (data.syntax_error) {
      const se = data.syntax_error as {
        message: string; lineno?: number; offset?: number; line?: string; caret?: string;
      };
      setResult(["❌ Syntax error", se.message, "", se.line ?? "", se.caret ?? ""].join("\n"));
      return;
    }

    const s = data.summary ?? {};
    const total = (s.passed ?? 0) + (s.failed ?? 0) + (s.errors ?? 0) + (s.skipped ?? 0);
    const header =
      `${(s.failed ?? 0) === 0 && (s.errors ?? 0) === 0 ? "✅" : "❌"} ` +
      `${s.passed ?? 0}/${total} passed ` +
      `(failed: ${s.failed ?? 0}, errors: ${s.errors ?? 0}, skipped: ${s.skipped ?? 0})`;


    const cases: TestCase[] = Array.isArray(data.cases) ? data.cases : [];
    const buckets: Record<"normal"|"edge"|"adversarial", TestCase[]> = {
      normal: [], edge: [], adversarial: [],
    };
    for (const tc of cases) buckets[bucketFor(tc.name)].push(tc);

    function renderBucket(title: string, items: TestCase[]) {
      if (!items.length) return "";
      const lines = items.map(tc => {
        const name = tc.name?.replace(/^test_/, "");
        const reason = tc.status === "passed" ? ""
          : (tc.message || "").split("\n")[0].trim();
        return `${iconFor(tc.status)} ${name}${reason ? ` — ${reason}` : ""}`;
      });
      return [`${title}:`, ...lines.map(l => `  • ${l}`)].join("\n");
    }

    const pretty =
      [
        header,
        renderBucket("Normal", buckets.normal),
        renderBucket("Edge", buckets.edge),
        renderBucket("Adversarial", buckets.adversarial),
      ]
      .filter(Boolean)
      .join("\n\n");

   
    const blocks: string[] = [
      pretty,
      "— output —",
      (data.output || "").trim(),
    ];
    if ((data.tests || "").trim()) {
      blocks.push("— generated tests —", (data.tests as string).trim());
    }

    setResult(blocks.join("\n\n"));
  } catch (err) {
    console.error(err);
    setResult(`❌ Test run failed: ${err instanceof Error ? err.message : String(err)}`);
  }
}


  /* render ---------------------------------------------------------- */
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Header
        onToggleSidebar={() => setSidebarOpen(p => !p)}
        language={language}
        onToggleLanguage={setLanguage}
      />
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) {
            setPhotoFile(f);      
           setStep("picked");    // enables Scan button
          }
        }}
      />
      

      <main className="pt-20 min-h-[calc(100vh-5rem)]
                 flex items-center w-full max-w-8xl mx-auto px-4">
        <WorkingPane
          code={code}
          onChangeCode={setCode}

          objective={objective}
          onChangeObjective={setObjective}


          result={result}
         
          language={language.toLowerCase()}  
          onAttach={handleAttach}
          onScan={handleScan}
          onEdit={handleEdit}
          onRun={handleRun}
          isReadOnly={isReadOnly}

          canScan={canScan}               
          canEdit={canEdit}               
          canRun={canRun}
          scanBusy={scanBusy}
        />
      </main>
    </div>
  );
}


