"use client";

import { useState } from "react";

export default function DoctorDemo() {
  const [activeTab, setActiveTab] = useState<"doctor" | "status">("doctor");

  return (
    <section id="diagnostics" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
      <div className="grid gap-10 lg:grid-cols-12 lg:items-center">
        {/* Left text column */}
        <div className="lg:col-span-5">
          <span className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-400">
            System Integrity & Resiliency
          </span>
          <h2 className="mt-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Automated System Diagnostics
          </h2>
          <p className="mt-4 text-base text-slate-400 leading-relaxed">
            LoomCast includes an automated self-diagnostic suite. Validate your configuration, runtime HTTP connectivity, and catalog integrity in a single command.
          </p>

          {/* 5 Points Checklist */}
          <div className="mt-6 space-y-3">
            {[
              "Configuration file audit (~/.config/loomcast/config.json)",
              "Environment variable inspection (LOOMCAST_*)",
              "HTTP connectivity test on every runtime port",
              "Dynamic catalog access check with automatic static fallback",
              "SHA-256 cryptographic verification of embedded static catalog",
            ].map((check, i) => (
              <div key={i} className="flex items-start gap-3 text-sm text-slate-300">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold">
                  ✓
                </span>
                <span>{check}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right terminal simulation column */}
        <div className="lg:col-span-7">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/90 shadow-2xl overflow-hidden">
            {/* Top Toolbar */}
            <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3 bg-slate-950">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-red-500/80" />
                <span className="h-3 w-3 rounded-full bg-yellow-500/80" />
                <span className="h-3 w-3 rounded-full bg-green-500/80" />
                <span className="ml-2 text-xs font-mono text-slate-400">loomcast diagnostics</span>
              </div>

              <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800">
                <button
                  onClick={() => setActiveTab("doctor")}
                  className={`rounded px-3 py-1 text-xs font-mono transition ${
                    activeTab === "doctor"
                      ? "bg-loom-500 text-white"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  loomcast doctor
                </button>
                <button
                  onClick={() => setActiveTab("status")}
                  className={`rounded px-3 py-1 text-xs font-mono transition ${
                    activeTab === "status"
                      ? "bg-loom-500 text-white"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  loomcast status
                </button>
              </div>
            </div>

            {/* Console Output */}
            <pre className="thin-scroll overflow-x-auto p-6 font-mono text-xs leading-relaxed text-slate-200 bg-slate-950">
              {activeTab === "doctor" ? (
                <code>
                  <span className="text-loom-400">$</span> loomcast doctor{"\n\n"}
                  <span className="text-cyan-400 font-bold">Loomcast System Diagnostics</span>{"\n\n"}
                  <span className="text-emerald-400">✓</span> Configuration: loaded successfully from <span className="text-cyan-300">C:\Users\User\.config\loomcast\config.json</span>{"\n"}
                  <span className="text-emerald-400">✓</span> Environment variables: none set, using defaults{"\n"}
                  <span className="text-emerald-400">✓</span> Runtime OLLAMA: available (<span className="text-slate-400">http://127.0.0.1:11434</span>){"\n"}
                  <span className="text-emerald-400">✓</span> Runtime LMSTUDIO: available (<span className="text-slate-400">http://127.0.0.1:1234</span>){"\n"}
                  <span className="text-yellow-400">⚠</span> Runtime LLAMACPP: unavailable (not default backend){"\n"}
                  <span className="text-emerald-400">✓</span> Catalog: dynamic catalog reachable{"\n"}
                  <span className="text-emerald-400">✓</span> Static catalog integrity: <span className="text-emerald-300 font-semibold">SHA-256 check passed</span>{"\n\n"}
                  <span className="text-white font-bold">0 problem(s) found, 1 warning(s)</span>
                </code>
              ) : (
                <code>
                  <span className="text-loom-400">$</span> loomcast status{"\n\n"}
                  <span className="text-cyan-400 font-bold">Loomcast Local Runtimes Status</span>{"\n"}
                  ┌──────────┬────────────────────────┬─────────┬────────┐{"\n"}
                  │ <span className="text-cyan-300">Runtime</span>  │ <span className="text-blue-300">Endpoint</span>               │ <span className="text-purple-300">Default</span> │ <span className="text-white">Status</span> │{"\n"}
                  ├──────────┼────────────────────────┼─────────┼────────┤{"\n"}
                  │ OLLAMA   │ http://127.0.0.1:11434 │ <span className="text-cyan-400 font-bold">Yes</span>     │ <span className="text-emerald-400 font-bold">Online</span> │{"\n"}
                  │ LMSTUDIO │ http://127.0.0.1:1234  │ No      │ <span className="text-emerald-400 font-bold">Online</span> │{"\n"}
                  │ LLAMACPP │ http://127.0.0.1:8080  │ No      │ <span className="text-red-400 font-bold">Offline</span>│{"\n"}
                  └──────────┴────────────────────────┴─────────┴────────┘
                </code>
              )}
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}
