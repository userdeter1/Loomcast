import Link from "next/link";
import CopyCommand from "@/components/CopyCommand";
import { SITE } from "@/lib/site";

export default function Hero() {
  return (
    <section className="relative overflow-hidden">
      {/* Ambient glow */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 -top-40 h-80 bg-[radial-gradient(50%_100%_at_50%_0%,rgba(109,99,242,0.25),transparent)]"
      />
      <div className="mx-auto max-w-6xl px-4 pb-16 pt-20 sm:px-6 sm:pt-28">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1 text-xs font-medium text-slate-300">
            <span className="h-1.5 w-1.5 rounded-full bg-loom-400" />
            Ollama · LM Studio · llama.cpp
          </span>

          <h1 className="mt-6 text-4xl font-bold tracking-tight text-white sm:text-6xl">
            One interface for every{" "}
            <span className="bg-gradient-to-r from-loom-300 to-loom-500 bg-clip-text text-transparent">
              local LLM runtime
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-300">
            {SITE.description}
          </p>

          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <CopyCommand command={SITE.install} />
            <Link
              href="/docs/getting-started"
              className="rounded-xl bg-loom-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-loom-400"
            >
              Get started →
            </Link>
          </div>
        </div>

        {/* Terminal preview */}
        <div className="mx-auto mt-14 max-w-3xl overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70 shadow-2xl shadow-loom-900/30">
          <div className="flex items-center gap-2 border-b border-slate-800 px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-red-500/70" />
            <span className="h-3 w-3 rounded-full bg-yellow-500/70" />
            <span className="h-3 w-3 rounded-full bg-green-500/70" />
            <span className="ml-2 text-xs text-slate-500">loomcast</span>
          </div>
          <pre className="thin-scroll overflow-x-auto p-5 text-sm leading-relaxed">
            <code className="font-mono">
              <span className="text-loom-400">$</span>{" "}
              <span className="text-slate-100">loomcast compare</span>{" "}
              <span className="text-emerald-300">
                &quot;Explain recursion in one sentence.&quot;
              </span>
              {"\n\n"}
              <span className="text-slate-500">
                ┌── OLLAMA (llama3) ──┐ ┌─ LMSTUDIO (qwen) ─┐ ┌─ LLAMACPP (gemma) ─┐
              </span>
              {"\n"}
              <span className="text-slate-300">
                │ A function that     │ │ When a function   │ │ Calling a func-    │
              </span>
              {"\n"}
              <span className="text-slate-300">
                │ calls itself...     │ │ calls itself...   │ │ tion from itself.  │
              </span>
              {"\n"}
              <span className="text-slate-500">
                └─────────────────────┘ └───────────────────┘ └────────────────────┘
              </span>
            </code>
          </pre>
        </div>
      </div>
    </section>
  );
}
