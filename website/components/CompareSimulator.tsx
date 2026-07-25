"use client";

import { useState } from "react";

interface SamplePrompt {
  label: string;
  prompt: string;
  responses: {
    ollama: { model: string; text: string; time: string };
    lmstudio: { model: string; text: string; time: string };
    llamacpp: { model: string; text: string; time: string };
  };
}

const SAMPLE_PROMPTS: SamplePrompt[] = [
  {
    label: "Recursion (1 sentence)",
    prompt: "Explain recursion in one sentence.",
    responses: {
      ollama: {
        model: "llama3:8b",
        text: "Recursion is a programming concept where a function calls itself until reaching a base condition that stops execution.",
        time: "1.2s",
      },
      lmstudio: {
        model: "qwen2.5-7b",
        text: "It occurs when a subprogram repeatedly invokes itself to break a complex problem into identical smaller subproblems.",
        time: "0.9s",
      },
      llamacpp: {
        model: "gemma-2b",
        text: "A function is recursive when its body directly or indirectly calls itself until a termination base case.",
        time: "0.6s",
      },
    },
  },
  {
    label: "Python Decorator",
    prompt: "Write a simple Python decorator that measures execution time.",
    responses: {
      ollama: {
        model: "llama3:8b",
        text: `import time

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        print(f"{func.__name__}: {time.time()-start:.4f}s")
        return res
    return wrapper`,
        time: "1.8s",
      },
      lmstudio: {
        model: "qwen2.5-coder:7b",
        text: `import time, functools

def timer(func):
    @functools.wraps(func)
    def inner(*a, **kw):
        t0 = time.perf_counter()
        val = func(*a, **kw)
        print(f"Elapsed: {time.perf_counter()-t0:.6f}s")
        return val
    return inner`,
        time: "1.4s",
      },
      llamacpp: {
        model: "mistral-7b-v0.3",
        text: `import time

def measure_time(fn):
    def exec_fn(*args, **kwargs):
        t1 = time.time()
        out = fn(*args, **kwargs)
        print("Duration:", time.time() - t1)
        return out
    return exec_fn`,
        time: "1.1s",
      },
    },
  },
  {
    label: "Local LLM Benefits",
    prompt: "What are the 3 main benefits of running local LLMs?",
    responses: {
      ollama: {
        model: "llama3:8b",
        text: "1. Complete Privacy (your data never leaves your machine).\n2. Zero API costs and no internet dependency.\n3. Full customization and choice of models.",
        time: "1.5s",
      },
      lmstudio: {
        model: "qwen2.5-7b",
        text: "1. Zero data leakage for sensitive code.\n2. Predictable latency and offline access.\n3. Full hardware control over VRAM & compute.",
        time: "1.1s",
      },
      llamacpp: {
        model: "gemma-2b",
        text: "1. Enterprise data security compliance.\n2. Zero per-token API billing.\n3. Complete execution autonomy.",
        time: "0.8s",
      },
    },
  },
];

export default function CompareSimulator() {
  const [selectedPromptIndex, setSelectedPromptIndex] = useState<number>(0);
  const [customPrompt, setCustomPrompt] = useState<string>("");
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const currentPreset = SAMPLE_PROMPTS[selectedPromptIndex];
  const activePromptText = customPrompt.trim() !== "" ? customPrompt : currentPreset.prompt;

  const handleRun = () => {
    setIsRunning(true);
    setTimeout(() => {
      setIsRunning(false);
    }, 600);
  };

  return (
    <section id="compare-demo" className="border-t border-slate-800/80 bg-slate-950/60 py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="text-center max-w-3xl mx-auto">
          <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Benchmarking Playground
          </span>
          <h2 className="mt-4 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Multi-Runtime Comparison Simulator
          </h2>
          <p className="mt-3 text-slate-400 text-base">
            The <code className="font-mono text-loom-300">loomcast compare</code> command queries all your active local runtimes in parallel. Test the interactive preview below:
          </p>
        </div>

        {/* Preset Prompt Selector */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
            Preset Prompts:
          </span>
          {SAMPLE_PROMPTS.map((p, idx) => (
            <button
              key={p.label}
              onClick={() => {
                setSelectedPromptIndex(idx);
                setCustomPrompt("");
              }}
              className={`rounded-xl px-4 py-2 text-xs font-semibold transition border ${
                selectedPromptIndex === idx && customPrompt === ""
                  ? "border-loom-500 bg-loom-500/20 text-loom-300 shadow-md shadow-loom-950"
                  : "border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700 hover:text-white"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="mt-6 mx-auto max-w-3xl flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={customPrompt !== "" ? customPrompt : currentPreset.prompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Type a custom prompt..."
            className="flex-1 rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-white placeholder-slate-500 focus:border-loom-500 focus:outline-none focus:ring-1 focus:ring-loom-500 font-mono"
          />
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="inline-flex items-center justify-center rounded-xl bg-loom-500 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-loom-400 active:scale-95 disabled:opacity-50"
          >
            {isRunning ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Executing...
              </span>
            ) : (
              "Run loomcast compare"
            )}
          </button>
        </div>

        {/* Side-by-Side Runtime Grid */}
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {/* Panel 1: Ollama */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
                  <span className="font-bold text-white text-sm">OLLAMA</span>
                </div>
                <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-loom-300">
                  {currentPreset.responses.ollama.model}
                </span>
              </div>

              <div className="mt-4">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-mono">Prompt sent</p>
                <p className="mt-1 text-xs text-slate-300 font-mono line-clamp-1">
                  &quot;{activePromptText}&quot;
                </p>
              </div>

              <div className="mt-4">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-mono">Generated response</p>
                <div className="mt-2 min-h-[140px] rounded-xl border border-slate-800/80 bg-slate-950 p-3 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {isRunning ? (
                    <span className="animate-pulse text-slate-500">Generating response...</span>
                  ) : (
                    currentPreset.responses.ollama.text
                  )}
                </div>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between text-[11px] text-slate-400 font-mono border-t border-slate-800/60 pt-3">
              <span>Status: <strong className="text-emerald-400">200 OK</strong></span>
              <span>Time: <strong className="text-white">{currentPreset.responses.ollama.time}</strong></span>
            </div>
          </div>

          {/* Panel 2: LM Studio */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-blue-500 shadow-sm shadow-blue-500/50" />
                  <span className="font-bold text-white text-sm">LM STUDIO</span>
                </div>
                <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-blue-300">
                  {currentPreset.responses.lmstudio.model}
                </span>
              </div>

              <div className="mt-4">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-mono">Prompt sent</p>
                <p className="mt-1 text-xs text-slate-300 font-mono line-clamp-1">
                  &quot;{activePromptText}&quot;
                </p>
              </div>

              <div className="mt-4">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-mono">Generated response</p>
                <div className="mt-2 min-h-[140px] rounded-xl border border-slate-800/80 bg-slate-950 p-3 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {isRunning ? (
                    <span className="animate-pulse text-slate-500">Generating response...</span>
                  ) : (
                    currentPreset.responses.lmstudio.text
                  )}
                </div>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between text-[11px] text-slate-400 font-mono border-t border-slate-800/60 pt-3">
              <span>Status: <strong className="text-emerald-400">200 OK</strong></span>
              <span>Time: <strong className="text-white">{currentPreset.responses.lmstudio.time}</strong></span>
            </div>
          </div>

          {/* Panel 3: llama.cpp */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-purple-500 shadow-sm shadow-purple-500/50" />
                  <span className="font-bold text-white text-sm">LLAMA.CPP</span>
                </div>
                <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-purple-300">
                  {currentPreset.responses.llamacpp.model}
                </span>
              </div>

              <div className="mt-4">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-mono">Prompt sent</p>
                <p className="mt-1 text-xs text-slate-300 font-mono line-clamp-1">
                  &quot;{activePromptText}&quot;
                </p>
              </div>

              <div className="mt-4">
                <p className="text-xs text-slate-500 uppercase tracking-wider font-mono">Generated response</p>
                <div className="mt-2 min-h-[140px] rounded-xl border border-slate-800/80 bg-slate-950 p-3 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {isRunning ? (
                    <span className="animate-pulse text-slate-500">Generating response...</span>
                  ) : (
                    currentPreset.responses.llamacpp.text
                  )}
                </div>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between text-[11px] text-slate-400 font-mono border-t border-slate-800/60 pt-3">
              <span>Status: <strong className="text-emerald-400">200 OK</strong></span>
              <span>Time: <strong className="text-white">{currentPreset.responses.llamacpp.time}</strong></span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
