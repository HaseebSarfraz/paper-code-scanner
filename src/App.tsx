// src/App.tsx
import React, { useState, useRef } from "react";
import Header       from "./Components/Header";
import WorkingPane  from "./Components/WorkingPane";

/* ------------------------------------------------------------------ */

const LANGUAGES = [
  "Python",
  "Java",
  "C",
  "C++",
  "JavaScript",
] as const;

export default function App() {
  /* UI state -------------------------------------------------------- */
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

  /* stub actions ---------------------------------------------------- */
  /* ----- handlers for the buttons ----- */
  function handleAttach() {
    fileInputRef.current?.click();
  }

  async function handleScan() {
    if (!photoFile) return;
    try {
      setScanBusy(true);
      setResult("⏳ Scanning…");

      /* temporary 1-second fake delay */
      await new Promise(r => setTimeout(r, 1000));

      // later replace with real OCR fetch + setCode(text);
      setResult("✅ Scan complete (stub)");
      setStep("scanned");
    } finally {
      setScanBusy(false);
    }
  }
  

  function handleEdit() {
    setStep("editing");   // unlocks the editor
  }

  function handleRun() {
    // 👉 later: send code to Llama tests endpoint
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
            setPhotoFile(f);      // store for Step 2
           setStep("picked");    // enables Scan button
          }
        }}
      />
      

      {/* ――― page body (centred, capped at 6xl) ――― */}
      <main className="pt-20 min-h-[calc(100vh-5rem)]
                 flex items-center w-full max-w-8xl mx-auto px-4">
        <WorkingPane
          code={code}
          onChangeCode={setCode}

          objective={objective}
          onChangeObjective={setObjective}


          result={result}
         
          language={language.toLowerCase()}  /* Monaco expects lowercase ids */
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



// // src/App.tsx

// import React, { useState } from "react";
// import Header from "./Components/Header";
// import WorkingPane from "./Components/WorkingPane";


// export default function App() {

//   const LANGUAGES = 
//   [ "Python", 
//     "Java", 
//     "C", 
//     "C++", 
//     "JavaScript",
//   ]
//   const [sidebarOpen, setSidebarOpen] = useState(false);
//   const [language, setLanguage] = useState<typeof LANGUAGES[number]>(
//     LANGUAGES[0]
//   );

//    // code / compile result for the new pane
//   const [code, setCode] = useState("");
//   const [result, setResult] = useState("");

//   /* 3️⃣  stub actions (replace later) */
//   function handleScan() {
//     alert("TODO: open camera / file picker 🚧");
//   }
//   function handleCompile() {
//     setResult(`You typed ${code.length} characters.`);
//   }

//   return (
//     <div className="min-h-screen bg-slate-950 text-white">
//       <Header
//         onToggleSidebar={() => setSidebarOpen((p) => !p)}
//         language={language}
//         onToggleLanguage={setLanguage}
        
//       />

//       {/* push content down by header height */}
//       <div className="pt-20 flex">
//         {/* Sidebar + main work area here */}
//       </div>

//       {/* ---------- main row under header ---------- */}
//       <div className="pt-20 flex">
//         {/* (Sidebar component would go here when you build it) */}

//         {/* Main work area */}
//         <WorkingPane
//           code={code}
//           onChangeCode={setCode}
//           result={result}
//           onScan={handleScan}
//           onCompile={handleCompile}
//         />
//       </div>
//     </div>
//   );
// }