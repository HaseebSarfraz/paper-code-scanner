// src/Components/Button.tsx
import React from "react";

export function Button({
  children,
  onClick,
  variant = "secondary",
  icon,
  disabled = false,          
}: {
  children: React.ReactNode;
  onClick?: () => void;
  icon?: React.ReactNode;
  variant?: "primary" | "secondary";
  disabled?: boolean;      
}) {

  const base =
    "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition";

  const activeStyles =
    variant === "primary"
      ? "bg-emerald-500 text-white hover:bg-emerald-400"
      : "bg-surface-3 hover:bg-surface-4 ring-1 ring-accent-ring/30";

  const disabledStyles = disabled
    ? "bg-slate-600/40 text-slate-300 opacity-60 cursor-not-allowed pointer-events-none"
    : "";

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${activeStyles} ${disabledStyles}`}
    >
      {icon}
      {children}
    </button>
  );
}