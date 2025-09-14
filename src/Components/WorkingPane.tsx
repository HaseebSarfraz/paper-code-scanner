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

  language:   string;
  canScan:    boolean;
  canEdit:    boolean;
  canRun:     boolean;
  isReadOnly: boolean;
  scanBusy:   boolean;
}


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

        {/* 2 ▸ Monaco editor */}
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

