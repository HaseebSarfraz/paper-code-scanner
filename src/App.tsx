// src/App.tsx
import React, { useState } from "react";
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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [language, setLanguage] = useState<(typeof LANGUAGES)[number]>(
    LANGUAGES[0]
  );
  const [code,   setCode]   = useState("");
  const [result, setResult] = useState("");

  /* stub actions ---------------------------------------------------- */
  function handleScan()    { alert("TODO: open camera / file picker 🚧"); }
  function handleCompile() { setResult(`You typed ${code.length} characters.`); }

  /* render ---------------------------------------------------------- */
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Header
        onToggleSidebar={() => setSidebarOpen(p => !p)}
        language={language}
        onToggleLanguage={setLanguage}
      />

      {/* ――― page body (centred, capped at 6xl) ――― */}
      <main className="pt-20 min-h-[calc(100vh-5rem)] flex items-center w-full max-w-6xl mx-auto px-4">
        <WorkingPane
          code={code}
          onChangeCode={setCode}
          result={result}
          onScan={handleScan}
          onCompile={handleCompile}
          language={language.toLowerCase()}  /* Monaco expects lowercase ids */
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