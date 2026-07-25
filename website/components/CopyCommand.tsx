"use client";

import { useState } from "react";

export default function CopyCommand({ command }: { command: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard blocked (e.g. insecure context) — nothing to do.
    }
  }

  return (
    <div className="inline-flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3 font-mono text-sm">
      <span className="select-none text-loom-400">$</span>
      <code className="text-slate-100">{command}</code>
      <button
        type="button"
        onClick={copy}
        className="ml-1 rounded-md border border-slate-700 px-2 py-1 text-xs font-medium text-slate-300 transition hover:border-loom-500 hover:text-white"
        aria-label="Copy command"
      >
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}
