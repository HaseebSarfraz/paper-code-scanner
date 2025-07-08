// src/Components/WorkingPane.tsx
import React, { useCallback } from "react";
import Editor, { BeforeMount } from "@monaco-editor/react";

import { Camera, Play } from "lucide-react";
import { Button } from "./Button";

interface Props {
  code: string;
  onChangeCode: (v: string) => void;

  result: string;
  onScan: () => void;
  onCompile: () => void;

  language: string;      // “python”, “java”, …
}

/* ------------------------------------------------------------------ */
export default function WorkingPane({
  code,
  onChangeCode,
  result,
  onScan,
  onCompile,
  language,
}: Props) {
  /* 1️⃣  register a single-tone dark theme (bg matches RHS pane) */
  const beforeMount: BeforeMount = useCallback((monaco) => {
    monaco.editor.defineTheme("tailwind-dark-solid", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "", foreground: "a5b4fc" }, // indigo-300 – default text
      ],
      colors: {
        /* both gutter + code area use the same colour */
        "editor.background":       "#0f172a",   // slate-900
        "editorGutter.background": "#0f172a",

        "editor.foreground":       "#a5b4fc",   // indigo-300
        "editorLineNumber.foreground": "#475569", // slate-600
        "editorCursor.foreground": "#38bdf8",
        "editor.selectionBackground": "#1e40af40",
      },
    });
  }, []);

  return (
    <div className="w-full flex flex-col gap-6">
      {/* ---------- action bar ---------- */}
      <div className="flex gap-4">
        <Button icon={<Camera size={18} />} onClick={onScan}>
          Attach&nbsp;photo
        </Button>

        <Button
          variant="primary"
          icon={<Play size={18} />}
          onClick={onCompile}
        >
          Scan&nbsp;&amp;&nbsp;Compile
        </Button>
      </div>

      {/* ---------- split-pane ---------- */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* LEFT ▸ Monaco editor */}
        <div className="relative bg-slate-900/60 ring-1 ring-slate-700 rounded-md overflow-hidden">
          
          <Editor
            height="260px"
            defaultLanguage={language}
            theme="tailwind-dark-solid"
            beforeMount={beforeMount}
            value={code}
            onChange={(v) => onChangeCode(v ?? "")}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              fontFamily: "JetBrains Mono, monospace",
              automaticLayout: true,
            }}
          />
        </div>

        {/* RIGHT ▸ compile output */}
        <div className="bg-slate-900/60 ring-1 ring-slate-700 rounded-md p-4
                        overflow-auto text-sm leading-relaxed">
          {result || (
            <span className="opacity-60">
              Compilation output will appear here…
            </span>
          )}
        </div>
      </div>
    </div>
  );
}






// import React from "react";
// import { Camera, Play } from "lucide-react";   // little icon pack


// interface WorkingPaneProps {
//   code: string;                    // ← comes from App state
//   onChangeCode: (v: string) => void;

//   result: string;                  // ← also App state
//   onScan: () => void;              // stub actions
//   onCompile: () => void;
// }

// const WorkingPane: React.FC<WorkingPaneProps> = ({
//   code,
//   onChangeCode,
//   result,
//   onScan,
//   onCompile,
// }) => {
//   return (
//     <section className="flex flex-col flex-1 p-6">
//       {/* --- buttons row --- */}
//       <div className="flex gap-3 mb-4">
//         <button
//           onClick={onScan}
//           className="flex items-center gap-1 px-3 py-2 rounded bg-slate-800
//                      text-slate-200 hover:bg-slate-700"
//         >
//           <Camera size={18} />
//           <span className="text-sm">Attach&nbsp;photo</span>
//         </button>

//         <button
//           onClick={onCompile}
//           className="flex items-center gap-1 px-3 py-2 rounded bg-emerald-600
//                      text-white hover:bg-emerald-500"
//         >
//           <Play size={18} />
//           <span className="text-sm">Scan&nbsp;&amp;&nbsp;Compile</span>
//         </button>
//       </div>

//       {/* --- split pane --- */}
//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
//         {/* LEFT – editable */}
//         <textarea
//           value={code}
//           onChange={(e) => onChangeCode(e.target.value)}
//           placeholder="Paste or type your code…"
//           className="h-full w-full resize-none rounded border border-slate-700
//                      bg-slate-900 p-4 text-sm leading-relaxed focus:outline-none
//                      focus:ring-2 focus:ring-emerald-500"
//         />

//         {/* RIGHT – results */}
//         <pre className="h-full w-full rounded border border-slate-700
//                         bg-slate-900 p-4 text-sm overflow-auto">
// {result || "Compilation output will appear here…"}
//         </pre>
//       </div>
//     </section>
//   );
// };

// export default WorkingPane;