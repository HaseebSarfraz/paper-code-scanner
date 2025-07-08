// src/Components/Button.tsx
import React from "react";

export function Button({
  children,
  onClick,
  variant = "secondary",
  icon,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  icon?: React.ReactNode;
  variant?: "primary" | "secondary";
}) {
  const base =
    "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium";
  const styles =
    variant === "primary"
      ? "bg-accent text-white hover:bg-accent/90"
      : "bg-surface-3 hover:bg-surface-4 ring-1 ring-accent-ring/30";

  return (
    <button onClick={onClick} className={`${base} ${styles}`}>
      {icon}
      {children}
    </button>
  );
}