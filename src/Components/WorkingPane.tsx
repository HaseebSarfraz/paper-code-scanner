// src/Components/WorkingPane.tsx
import React, { useCallback } from "react";
import Editor, { BeforeMount } from "@monaco-editor/react";
import { Camera, Play } from "lucide-react";      // Save icon no longer needed
import { Button } from "./Button";
import { Panel }  from "./Panel";

interface Props {
  /* code pane */
  code: string;
  onChangeCode: (v: string) => void;

  /* objective pane */
  objective: string;
  onChangeObjective: (v: string) => void;

  /* compile result */
  result: string;

  /* actions */
  onAttach: () => void;
  onScan:   () => void;
  onEdit:   () => void;
  onRun:    () => void;

  /* misc */
  language:   string;
  canScan:    boolean;
  canEdit:    boolean;
  canRun:     boolean;
  isReadOnly: boolean;
  scanBusy:   boolean;
}

/* ------------------------------------------------------------------ */
export default function WorkingPane({
  code,
  onChangeCode,
  objective,
  onChangeObjective,
  result,

  onAttach,
  onScan,
  onEdit,
  onRun,

  language,
  canScan,
  canEdit,
  canRun,
  isReadOnly,
  scanBusy,
}: Props) {
  /* 1️⃣  one-off dark theme */
  const beforeMount: BeforeMount = useCallback((monaco) => {
    monaco.editor.defineTheme("tailwind-dark-solid", {
      base: "vs-dark",
      inherit: true,
      rules: [{ token: "", foreground: "a5b4fc" }],
      colors: {
        "editor.background": "#0f172a",
        "editorGutter.background": "#0f172a",
        "editor.foreground": "#a5b4fc",
        "editorLineNumber.foreground": "#475569",
        "editorCursor.foreground": "#38bdf8",
        "editor.selectionBackground": "#1e40af40",
      },
    });
  }, []);

  /* ---------------------------------------------------------------- */

  return (
    <div className="w-full flex flex-col gap-6">
      {/* ---------- action bar ---------- */}
      <div className="flex flex-wrap gap-4 bg-slate-900/80 px-4 py-2
                      inline-flex w-max rounded-md ring-1 ring-slate-700 items-center">
        <Button icon={<Camera size={18} />} onClick={onAttach}>
          Attach&nbsp;photo
        </Button>

        <Button variant="primary" icon={<Play size={18} />}
                onClick={onScan} disabled={!canScan || scanBusy}> 
              Scan
        </Button>

        <Button variant={scanBusy ? "secondary" : "primary"}
                onClick={onEdit}
                disabled={scanBusy}>  
              Edit
          
        </Button>

        <Button variant="primary" icon={<Play size={18} />}
                onClick={onRun}  disabled={!canRun  || scanBusy}>
          Run&nbsp;tests
        </Button>
      </div>

      {/* ---------- triple-pane ---------- */}
      <div className="grid grid-cols-1 md:grid-cols-2
                      lg:grid-cols-[1.35fr_2fr_1.35fr] gap-6">

        {/* 1 ▸ Objective */}
        <Panel title="1. Objective">
          <textarea
            value={objective}
            onChange={(e) => onChangeObjective(e.target.value)}
            placeholder="Describe what your function should do…"
            className="h-32 md:h-[260px] xl:h-[300px] w-full resize-none
                       bg-transparent p-3 text-sm leading-relaxed
                       focus:outline-none"
          />
        </Panel>

        {/* 2 ▸ Monaco editor (wrapper kept as in your original) */}
        <div className="relative bg-slate-900/60 ring-1 ring-slate-700 rounded-md overflow-hidden
                        focus-within:ring-2 focus-within:ring-emerald-500">
          <Panel title="2. Scanned Code">
            <Editor
              height="100%"
              defaultLanguage={language}
              theme="tailwind-dark-solid"
              beforeMount={beforeMount}
              value={code}
              onChange={(v) => onChangeCode(v ?? "")}
              options={{
                readOnly: isReadOnly,
                readOnlyMessage: { value: "Press Edit** to edit" },
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "JetBrains Mono, monospace",
                automaticLayout: true,
              }}
            />
          </Panel>
        </div>

        {/* 3 ▸ test output */}
      <Panel title="3. Test results">
        <div className="flex-1 p-4 overflow-auto">
          <pre className="whitespace-pre-wrap break-words font-mono text-sm leading-6">
            {result || "Compilation / test output will appear here…"}
          </pre>
        </div>
      </Panel>
      </div>
    </div>
  );
}

















// Version 2
// import React, { useCallback } from "react";
// import Editor, { BeforeMount } from "@monaco-editor/react";

// import { Camera, Play } from "lucide-react";
// import { Button } from "./Button";

// interface Props {
//   code: string;
//   onChangeCode: (v: string) => void;

//   result: string;
//   onScan: () => void;
//   onCompile: () => void;

//   language: string;      // “python”, “java”, …
// }

// /* ------------------------------------------------------------------ */
// export default function WorkingPane({
//   code,
//   onChangeCode,
//   result,
//   onScan,
//   onCompile,
//   language,
// }: Props) {
//   /* 1️⃣  register a single-tone dark theme (bg matches RHS pane) */
//   const beforeMount: BeforeMount = useCallback((monaco) => {
//     monaco.editor.defineTheme("tailwind-dark-solid", {
//       base: "vs-dark",
//       inherit: true,
//       rules: [
//         { token: "", foreground: "a5b4fc" }, // indigo-300 – default text
//       ],
//       colors: {
//         /* both gutter + code area use the same colour */
//         "editor.background":       "#0f172a",   // slate-900
//         "editorGutter.background": "#0f172a",

//         "editor.foreground":       "#a5b4fc",   // indigo-300
//         "editorLineNumber.foreground": "#475569", // slate-600
//         "editorCursor.foreground": "#38bdf8",
//         "editor.selectionBackground": "#1e40af40",
//       },
//     });
//   }, []);

//   return (
//     <div className="w-full flex flex-col gap-6">
//       {/* ---------- action bar ---------- */}
//       <div className="flex gap-4">
//         <Button icon={<Camera size={18} />} onClick={onScan}>
//           Attach&nbsp;photo
//         </Button>

//         <Button
//           variant="primary"
//           icon={<Play size={18} />}
//           onClick={onCompile}
//         >
//           Scan&nbsp;&amp;&nbsp;Compile
//         </Button>
//       </div>

//       {/* ---------- split-pane ---------- */}
//       <div className="grid md:grid-cols-2 gap-6">
//         {/* LEFT ▸ Monaco editor */}
//         <div className="relative bg-slate-900/60 ring-1 ring-slate-700 rounded-md overflow-hidden">
          
//           <Editor
//             height="260px"
//             defaultLanguage={language}
//             theme="tailwind-dark-solid"
//             beforeMount={beforeMount}
//             value={code}
//             onChange={(v) => onChangeCode(v ?? "")}
//             options={{
//               minimap: { enabled: false },
//               fontSize: 14,
//               fontFamily: "JetBrains Mono, monospace",
//               automaticLayout: true,
//             }}
//           />
//         </div>

//         {/* RIGHT ▸ compile output */}
//         <div className="bg-slate-900/60 ring-1 ring-slate-700 rounded-md p-4
//                         overflow-auto text-sm leading-relaxed">
//           {result || (
//             <span className="opacity-60">
//               Compilation output will appear here…
//             </span>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// Version 1

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