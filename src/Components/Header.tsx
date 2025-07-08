import React from "react";
import { Menu, Languages } from "lucide-react"; // optional icon lib

 const LANGUAGES = 
  [ "Python", 
    "Java", 
    "C", 
    "C++", 
    "JavaScript",
  ] as const;

interface HeaderProps {
  onToggleSidebar: () => void;
  language: (typeof LANGUAGES)[number]
  onToggleLanguage: (lang: (typeof LANGUAGES)[number]) => void;
}

const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  language,
  onToggleLanguage,
}) => {
  return (
    <header className="fixed inset-x-0 top-0 z-50 h-20 flex items-center justify-between 
    px-4 sm:px-6 bg-slate-900/90 backdrop-blur border-b border-slate-800">
      {/* Left – burger */}
      <button
        onClick={onToggleSidebar}
        aria-label="Toggle sidebar"
        className="text-2xl text-slate-200 hover:text-slate-50"
      >
        <Menu strokeWidth={2} size={24} />
      </button>

      {/* Center – logo */}
      <h1 className="text-2xl sm:text-3xl font-extrabold tracking-wide text-slate-100 font-marker">
        Paper&nbsp;→&nbsp;Compiler
      </h1>

      {/* language picker */}
      <select
        value={language}
        onChange={e => onToggleLanguage(e.target.value as typeof language)}
        className="bg-transparent text-sm font-medium
                   hover:text-slate-50 focus:outline-none"
      >
        {LANGUAGES.map(lang => (
          <option key={lang} value={lang} className="bg-slate-900">
            {lang}
          </option>
        ))}
      </select>
    </header>
  );
};

export default Header;