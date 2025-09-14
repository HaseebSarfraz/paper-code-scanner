// src/Components/Panel.tsx
import React from "react";

export function Panel({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-full min-h-[260px] rounded-md ring-1 ring-slate-700
                    bg-slate-900/60 overflow-hidden
                    focus-within:ring-2 focus-within:ring-emerald-500">
      <div className="px-3 py-1 text-xs font-semibold tracking-wide text-slate-200 bg-slate-900">
        {title}
      </div>
      <div className="flex-1">{children}</div>
    </div>
  );
}