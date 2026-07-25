"use client";

import { useState } from "react";

export interface ActionDetail {
  id: string;
  name: string;
  category: "diagnostics" | "lifecycle" | "catalog" | "inference" | "config";
  categoryLabel: string;
  description: string;
  summary: string;
  cliCommand: string;
  sdkCode: string;
  options: { flag: string; type: string; description: string }[];
  terminalOutput: string;
  tags: string[];
}

const ACTIONS: ActionDetail[] = [
  // 1. Diagnostics & Health
  {
    id: "status",
    name: "Runtimes Status",
    category: "diagnostics",
    categoryLabel: "Diagnostics & Health",
    summary: "Live connectivity check across all local runtimes.",
    description:
      "Tests HTTP connection and operational state for Ollama, LM Studio, and llama.cpp on their respective ports. Displays default backend status.",
    cliCommand: "loomcast status",
    sdkCode: `from loomcast import LoomcastManager\n\nmanager = LoomcastManager()\nstatuses = manager.list_available_runtimes()\nfor runtime, is_online in statuses.items():\n    print(f"{runtime.value}: {'Online' if is_online else 'Offline'}")`,
    options: [],
    terminalOutput: `Loomcast Local Runtimes Status
┌──────────┬────────────────────────┬─────────┬────────┐
│ Runtime  │ Endpoint               │ Default │ Status │
├──────────┼────────────────────────┼─────────┼────────┤
│ OLLAMA   │ http://127.0.0.1:11434 │ Yes     │ Online │
│ LMSTUDIO │ http://127.0.0.1:1234  │ No      │ Online │
│ LLAMACPP │ http://127.0.0.1:8080  │ No      │ Offline│
└──────────┴────────────────────────┴─────────┴────────┘`,
    tags: ["Health", "Runtimes", "Detection"],
  },
  {
    id: "doctor",
    name: "System Doctor",
    category: "diagnostics",
    categoryLabel: "Diagnostics & Health",
    summary: "Comprehensive 5-level audit: config, env vars, connectivity, and SHA-256 integrity.",
    description:
      "Runs global integrity checks: configuration loading, environment variable audit (LOOMCAST_*), runtime ping, remote catalog reachability, and embedded static catalog SHA-256 checksum verification.",
    cliCommand: "loomcast doctor",
    sdkCode: `# Doctor diagnostics use LoomcastConfig and StaticCatalog
from loomcast.common.config import LoomcastConfig
from loomcast.adapters.catalog.static import StaticCatalog

config = LoomcastConfig.load()
catalog = StaticCatalog()  # Validates SHA-256 digest on load
print("System healthy!")`,
    options: [],
    terminalOutput: `Loomcast System Diagnostics

✓ Configuration: loaded successfully from ~/.config/loomcast/config.json
✓ Environment variables: none set, using defaults
✓ Runtime OLLAMA: available
⚠ Runtime LMSTUDIO: unavailable (not the default backend)
✓ Catalog: dynamic catalog reachable
✓ Static catalog integrity: SHA-256 check passed

0 problem(s) found, 1 warning(s)`,
    tags: ["Diagnostic", "SHA-256", "Security", "Audit"],
  },

  // 2. Lifecycle
  {
    id: "list",
    name: "List Models",
    category: "lifecycle",
    categoryLabel: "Model Lifecycle",
    summary: "Displays all locally installed AI models.",
    description:
      "Queries active local runtimes and lists model weights already downloaded and ready for inference.",
    cliCommand: "loomcast list --backend ollama",
    sdkCode: `import loomcast\n\n# List all models installed on Ollama\nmodels = loomcast.list_installed(runtime_type="ollama")\nprint("Installed models:", models)`,
    options: [
      { flag: "--backend, -b", type: "string", description: "Target backend (ollama | lmstudio | llamacpp)" },
    ],
    terminalOutput: `Installed Models
┌─────────┬──────────────────────┐
│ Runtime │ Model Name           │
├─────────┼──────────────────────┤
│ OLLAMA  │ llama3:latest        │
│ OLLAMA  │ qwen2.5-coder:7b     │
│ OLLAMA  │ mistral:7b           │
└─────────┴──────────────────────┘`,
    tags: ["Models", "Inventory", "Backends"],
  },
  {
    id: "install",
    name: "Install Model",
    category: "lifecycle",
    categoryLabel: "Model Lifecycle",
    summary: "Downloads and installs a new model into the target runtime.",
    description:
      "Drives direct download via runtime API with real-time multi-layered progress bar output.",
    cliCommand: "loomcast install llama3 --backend ollama",
    sdkCode: `import loomcast\n\n# Install llama3 model on Ollama\nloomcast.install("llama3", runtime_type="ollama")\nprint("Installation complete!")`,
    options: [
      { flag: "model", type: "argument", description: "Model identifier (e.g. llama3, mistral)" },
      { flag: "--backend, -b", type: "option", description: "Target backend (defaults to configured default backend)" },
    ],
    terminalOutput: `Installing model 'llama3'...
Downloading manifest  [====================================] 100%
pulling 00e1310c1821  [====================================] 4.7 GB / 4.7 GB (12 MB/s)
pulling 4fa551d4f938  [====================================] 12 KB / 12 KB
verifying sha256 digest...
Successfully installed model 'llama3'!`,
    tags: ["Installation", "Pull", "Progress"],
  },
  {
    id: "update",
    name: "Update Model",
    category: "lifecycle",
    categoryLabel: "Model Lifecycle",
    summary: "Verifies cryptographic digests and updates installed model.",
    description:
      "Compares local SHA-256 digest with remote registry. Atomically pulls latest weights if a new revision exists.",
    cliCommand: "loomcast update llama3 --backend ollama",
    sdkCode: `import loomcast\n\nchanged = loomcast.update("llama3", runtime_type="ollama")\nif changed:\n    print("Model updated!")\nelse:\n    print("Already up to date.")`,
    options: [
      { flag: "model", type: "argument", description: "Model identifier to update" },
      { flag: "--backend, -b", type: "option", description: "Target backend" },
    ],
    terminalOutput: `Updating model 'llama3'...
Checking manifest digest...
Already up to date, nothing to do for 'llama3'.`,
    tags: ["Update", "Digest", "SHA-256"],
  },
  {
    id: "verify",
    name: "Verify Integrity",
    category: "lifecycle",
    categoryLabel: "Model Lifecycle",
    summary: "Validates local model files against cryptographic SHA-256 signatures.",
    description:
      "Ensures local model weight files are uncorrupted by computing and validating SHA-256 digests.",
    cliCommand: "loomcast verify llama3 --backend ollama",
    sdkCode: `import loomcast\n\nres = loomcast.verify("llama3", runtime_type="ollama")\nprint(f"Verified: {res.verified}, Digest: {res.digest}")`,
    options: [
      { flag: "model", type: "argument", description: "Model name to verify" },
      { flag: "--backend, -b", type: "option", description: "Target backend" },
    ],
    terminalOutput: `Verification Result: llama3
┌──────────┬──────────────────────────────────────────────────────────────────┐
│ Property │ Value                                                            │
├──────────┼──────────────────────────────────────────────────────────────────┤
│ Model    │ llama3                                                           │
│ Runtime  │ ollama                                                           │
│ Status   │ Verified                                                         │
│ Digest   │ sha256:00e1310c1821a54d4b32a254e286d9a938...                       │
│ Message  │ Model integrity verified successfully against manifest            │
└──────────┴──────────────────────────────────────────────────────────────────┘`,
    tags: ["Verification", "Security", "Checksum"],
  },
  {
    id: "remove",
    name: "Remove Model",
    category: "lifecycle",
    categoryLabel: "Model Lifecycle",
    summary: "Permanently deletes a model from local storage.",
    description:
      "Frees up disk space by deleting local weights and manifests for target model, with safe confirmation prompts.",
    cliCommand: "loomcast remove llama3 --backend ollama --yes",
    sdkCode: `import loomcast\n\n# Remove a model without confirmation prompt\nloomcast.remove("llama3", runtime_type="ollama")\nprint("Model removed!")`,
    options: [
      { flag: "model", type: "argument", description: "Model name to remove" },
      { flag: "--yes, -y", type: "flag", description: "Skip confirmation prompt" },
      { flag: "--backend, -b", type: "option", description: "Target backend" },
    ],
    terminalOutput: `Successfully removed model 'llama3'!`,
    tags: ["Removal", "Cleanup", "Storage"],
  },

  // 3. Catalog & Discovery
  {
    id: "search",
    name: "Search Catalog",
    category: "catalog",
    categoryLabel: "Catalog & Discovery",
    summary: "Explores the model index catalog.",
    description:
      "Search catalog by keywords, publisher name, description, or functional tags with automatic offline fallback.",
    cliCommand: "loomcast search code",
    sdkCode: `import loomcast\n\nresults = loomcast.search("code")\nfor model in results:\n    print(f"{model.name} ({model.publisher}) - {model.description}")`,
    options: [
      { flag: "query", type: "argument", description: "Search query string (e.g. code, vision, math)" },
    ],
    terminalOutput: `Catalog Search Results for 'code'
┌────────────────┬───────────┬─────────┬───────────────────────────────┬─────────────────┐
│ Name           │ Publisher │ Backend │ Description                   │ Tags            │
├────────────────┼───────────┼─────────┼───────────────────────────────┼─────────────────┤
│ qwen2.5-coder  │ Qwen      │ ollama  │ Premier coding & agent model  │ coding, python  │
│ deepseek-coder │ DeepSeek  │ ollama  │ Specialist code generation    │ coding, math    │
│ codellama      │ Meta      │ ollama  │ Code generation & infilling   │ coding, multi   │
└────────────────┴───────────┴─────────┴───────────────────────────────┴─────────────────┘`,
    tags: ["Catalog", "Search", "Tags"],
  },
  {
    id: "recommend",
    name: "Recommend by Task",
    category: "catalog",
    categoryLabel: "Catalog & Discovery",
    summary: "Recommends best specialized models for a specific task.",
    description:
      "Filters intelligent catalog to suggest optimal models for use-cases: `coding`, `reasoning`, `math`, `vision`, `chat`.",
    cliCommand: "loomcast recommend coding",
    sdkCode: `import loomcast\n\n# Get model recommendations for coding\nrecs = loomcast.recommend("coding")\nfor m in recs:\n    print("Recommended:", m.name)`,
    options: [
      { flag: "task", type: "argument", description: "Task tag (coding, reasoning, math, vision...)" },
    ],
    terminalOutput: `Recommended Models for Task 'coding'
┌────────────────┬───────────┬─────────┬───────────────────────────────┬─────────────────┐
│ Name           │ Publisher │ Backend │ Description                   │ Tags            │
├────────────────┼───────────┼─────────┼───────────────────────────────┼─────────────────┤
│ qwen2.5-coder  │ Qwen      │ ollama  │ Top-tier coding assistant     │ coding, python  │
│ deepseek-coder │ DeepSeek  │ ollama  │ Expert in repository coding   │ coding, math    │
└────────────────┴───────────┴─────────┴───────────────────────────────┴─────────────────┘`,
    tags: ["AI", "Recommendations", "Tasks"],
  },
  {
    id: "install-category",
    name: "Batch Category Install",
    category: "catalog",
    categoryLabel: "Catalog & Discovery",
    summary: "Batch downloads an entire category of models.",
    description:
      "Installs all models under a category tag in a single command, with configurable concurrency and failure reporting.",
    cliCommand: "loomcast install-category code --backend ollama --max-concurrent 3",
    sdkCode: `import loomcast\n\n# Concurrent batch download of 'code' category\ninstalled, failed = loomcast.install_category(\n    "code",\n    runtime_type="ollama",\n    max_concurrent=3\n)\nprint(f"Installed: {installed}, Failed: {failed}")`,
    options: [
      { flag: "category", type: "argument", description: "Category tag to install" },
      { flag: "--max-concurrent, -c", type: "option", description: "Maximum parallel downloads (default: 3)" },
      { flag: "--sequential, -s", type: "flag", description: "Sequential execution (1 at a time)" },
    ],
    terminalOutput: `Batch installing category 'code' (max concurrent: 3)...
[1/3] Downloading qwen2.5-coder... [====================] 100%
[2/3] Downloading deepseek-coder... [====================] 100%
[3/3] Downloading codellama...      [====================] 100%

Category installation complete!
Successfully installed: 3 model(s) (qwen2.5-coder, deepseek-coder, codellama)
Failed installations: 0 model(s)`,
    tags: ["Batch", "Parallel", "Automation"],
  },

  // 4. Inference & Compare
  {
    id: "chat",
    name: "Unified Inference (Chat)",
    category: "inference",
    categoryLabel: "Inference & Comparison",
    summary: "Query any local model via a standardized API.",
    description:
      "Sends a single prompt or structured message list to target model, regardless of underlying backend (Ollama, LM Studio, llama.cpp).",
    cliCommand: "loomcast chat llama3 \"Explain recursion in one sentence.\" --backend ollama",
    sdkCode: `import loomcast\n\nreply = loomcast.chat(\n    "llama3",\n    [{"role": "user", "content": "Explain recursion in one sentence."}],\n    runtime_type="ollama"\n)\nprint(reply)`,
    options: [
      { flag: "model", type: "argument", description: "Target model name" },
      { flag: "prompt", type: "argument", description: "Prompt string text" },
      { flag: "--backend, -b", type: "option", description: "Specific backend" },
    ],
    terminalOutput: `Model: llama3
┌─────────────────────────────────────────────────────────────────────────────┐
│ Recursion is a programming concept where a function calls itself to solve   │
│ smaller instances of the same problem until a base condition is met.        │
└─────────────────────────────────────────────────────────────────────────────┘`,
    tags: ["Chat", "Inference", "API"],
  },
  {
    id: "compare",
    name: "Side-by-Side Comparison",
    category: "inference",
    categoryLabel: "Inference & Comparison",
    summary: "Executes a prompt across all runtimes simultaneously and compares answers.",
    description:
      "Sends the same prompt concurrently to Ollama, LM Studio, and llama.cpp, displaying outputs side-by-side in parallel panels to evaluate speed and output quality.",
    cliCommand: "loomcast compare \"Explain recursion in one sentence.\"",
    sdkCode: `import loomcast\n\nresults = loomcast.compare("Explain recursion in one sentence.")\nfor r in results:\n    print(f"[{r.runtime_type.value.upper()}] -> {r.response or r.error}")`,
    options: [
      { flag: "prompt", type: "argument", description: "Prompt sent to all selected runtimes" },
      { flag: "--model, -m", type: "option", description: "Force specific model across all runtimes" },
      { flag: "--backend, -b", type: "repeatable", description: "Restrict comparison to specific backends" },
    ],
    terminalOutput: `Querying runtimes...

┌── OLLAMA (llama3) ────────┐ ┌── LMSTUDIO (qwen) ────────┐ ┌── LLAMACPP (gemma) ───────┐
│ A function calling itself │ │ When a program function   │ │ Self-referencing function  │
│ until reaching a base     │ │ repeatedly invokes itself │ │ execution until base step  │
│ condition.                │ │ to solve sub-problems.    │ │ is reached.                │
└───────────────────────────┘ └───────────────────────────┘ └────────────────────────────┘`,
    tags: ["Benchmark", "Comparison", "Parallel", "Multi-runtime"],
  },

  // 5. Config
  {
    id: "config",
    name: "Global Configuration",
    category: "config",
    categoryLabel: "Configuration & Settings",
    summary: "Manages default backend, HTTP endpoints, and environment options.",
    description:
      "Displays active configuration, updates default backend, and sets custom endpoint URLs for Ollama, LM Studio, or llama.cpp.",
    cliCommand: "loomcast config --set-default lmstudio",
    sdkCode: `from loomcast.common.config import LoomcastConfig\nfrom loomcast.domain.entities import RuntimeType\n\nconfig = LoomcastConfig.load()\nconfig.default_backend = RuntimeType.LMSTUDIO\nconfig.save()\nprint("Default backend updated to LM Studio!")`,
    options: [
      { flag: "--set-default", type: "option", description: "Set default backend (ollama | lmstudio | llamacpp)" },
      { flag: "--show / --no-show", type: "flag", description: "Show or hide current configuration table" },
    ],
    terminalOutput: `Default backend updated to: lmstudio

Loomcast Configuration
┌──────────────────────────┬────────────────────────┐
│ Setting                  │ Value                  │
├──────────────────────────┼────────────────────────┤
│ default_backend          │ lmstudio               │
│ ollama_url               │ http://127.0.0.1:11434 │
│ lmstudio_url             │ http://127.0.0.1:1234  │
│ llamacpp_url             │ http://127.0.0.1:8080  │
│ catalog_source           │ dynamic                │
└──────────────────────────┴────────────────────────┘`,
    tags: ["Config", "Endpoints", "Routing"],
  },
];

const CATEGORIES = [
  { id: "all", label: "All Actions (13)" },
  { id: "diagnostics", label: "Diagnostics & Health" },
  { id: "lifecycle", label: "Model Lifecycle" },
  { id: "catalog", label: "Catalog & Discovery" },
  { id: "inference", label: "Inference & Comparison" },
  { id: "config", label: "Configuration" },
];

export default function InteractiveActions() {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [activeActionId, setActiveActionId] = useState<string>("compare");
  const [codeMode, setCodeMode] = useState<"cli" | "sdk">("cli");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredActions = ACTIONS.filter((action) => {
    const matchesCat =
      selectedCategory === "all" || action.category === selectedCategory;
    const matchesSearch =
      searchQuery === "" ||
      action.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      action.cliCommand.toLowerCase().includes(searchQuery.toLowerCase()) ||
      action.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      action.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCat && matchesSearch;
  });

  const activeAction =
    ACTIONS.find((a) => a.id === activeActionId) || ACTIONS[0];

  return (
    <section id="actions" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
      <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-loom-500/30 bg-loom-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-loom-300">
            Interactive Explorer
          </span>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            LoomCast Features & Actions Reference
          </h2>
          <p className="mt-2 text-base text-slate-400 max-w-2xl">
            Explore all 13 operations available across the CLI terminal interface and the LoomCast Python SDK.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <input
            type="text"
            placeholder="Search action or command..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2.5 pl-10 text-sm text-slate-200 placeholder-slate-500 focus:border-loom-500 focus:outline-none focus:ring-1 focus:ring-loom-500"
          />
          <svg
            className="absolute left-3 top-3 h-4 w-4 text-slate-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Category Pills */}
      <div className="mt-8 flex flex-wrap gap-2 border-b border-slate-800/80 pb-4">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
              selectedCategory === cat.id
                ? "bg-loom-500 text-white shadow-lg shadow-loom-500/25"
                : "bg-slate-900/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Grid Explorer Layout */}
      <div className="mt-8 grid gap-8 lg:grid-cols-12">
        {/* Left Side: Actions List */}
        <div className="space-y-2 lg:col-span-5 max-h-[640px] overflow-y-auto pr-1 thin-scroll">
          {filteredActions.length === 0 ? (
            <div className="rounded-xl border border-slate-800 bg-slate-900/30 p-8 text-center text-slate-500">
              No actions match your search query.
            </div>
          ) : (
            filteredActions.map((action) => {
              const isSelected = action.id === activeAction.id;
              return (
                <button
                  key={action.id}
                  onClick={() => setActiveActionId(action.id)}
                  className={`w-full text-left rounded-xl p-4 transition-all duration-200 border ${
                    isSelected
                      ? "border-loom-500/80 bg-slate-900/90 shadow-md shadow-loom-950/40"
                      : "border-slate-800/80 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/70"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-loom-400">
                      {action.categoryLabel}
                    </span>
                    <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-slate-300">
                      {action.cliCommand.split(" ")[1]}
                    </span>
                  </div>
                  <h3 className="mt-1 font-semibold text-white text-base">
                    {action.name}
                  </h3>
                  <p className="mt-1 text-xs text-slate-400 line-clamp-2">
                    {action.summary}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-1">
                    {action.tags.map((t) => (
                      <span
                        key={t}
                        className="rounded-full bg-slate-800/60 px-2 py-0.5 text-[10px] text-slate-400"
                      >
                        #{t}
                      </span>
                    ))}
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Right Side: Detailed Action View & Terminal Simulator */}
        <div className="lg:col-span-7">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
            {/* Header */}
            <div className="flex flex-col justify-between gap-4 border-b border-slate-800 pb-5 sm:flex-row sm:items-center">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-loom-400">
                  {activeAction.categoryLabel}
                </span>
                <h3 className="text-2xl font-bold text-white">
                  {activeAction.name}
                </h3>
              </div>

              {/* Mode Toggle: CLI vs SDK */}
              <div className="inline-flex rounded-xl bg-slate-950 p-1 border border-slate-800">
                <button
                  onClick={() => setCodeMode("cli")}
                  className={`rounded-lg px-3 py-1 text-xs font-medium transition ${
                    codeMode === "cli"
                      ? "bg-loom-500 text-white"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  CLI Terminal
                </button>
                <button
                  onClick={() => setCodeMode("sdk")}
                  className={`rounded-lg px-3 py-1 text-xs font-medium transition ${
                    codeMode === "sdk"
                      ? "bg-loom-500 text-white"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  Python SDK
                </button>
              </div>
            </div>

            {/* Description */}
            <p className="mt-4 text-sm leading-relaxed text-slate-300">
              {activeAction.description}
            </p>

            {/* Code / Command Display */}
            <div className="mt-6">
              <div className="flex items-center justify-between rounded-t-xl border border-b-0 border-slate-800 bg-slate-950 px-4 py-2">
                <span className="text-xs font-mono text-slate-400">
                  {codeMode === "cli" ? "CLI Command Syntax" : "Python SDK Code"}
                </span>
              </div>
              <pre className="thin-scroll overflow-x-auto rounded-b-xl border border-slate-800 bg-slate-950 p-4 text-xs font-mono text-emerald-400">
                <code>
                  {codeMode === "cli"
                    ? activeAction.cliCommand
                    : activeAction.sdkCode}
                </code>
              </pre>
            </div>

            {/* Options / Arguments Table */}
            {activeAction.options.length > 0 && (
              <div className="mt-6">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Options & Arguments
                </h4>
                <div className="mt-2 overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
                  <table className="w-full text-left text-xs">
                    <thead className="border-b border-slate-800 bg-slate-900/60 text-slate-300">
                      <tr>
                        <th className="p-2.5 font-medium">Option / Flag</th>
                        <th className="p-2.5 font-medium">Type</th>
                        <th className="p-2.5 font-medium">Description</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-400 font-mono">
                      {activeAction.options.map((opt) => (
                        <tr key={opt.flag}>
                          <td className="p-2.5 text-loom-300 font-semibold">{opt.flag}</td>
                          <td className="p-2.5 text-slate-500">{opt.type}</td>
                          <td className="p-2.5 font-sans text-slate-300">{opt.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Terminal Render Preview */}
            <div className="mt-6">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Simulated Terminal Output
              </h4>
              <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-2xl">
                <div className="flex items-center gap-1.5 border-b border-slate-800 px-3 py-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
                  <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/70" />
                  <span className="h-2.5 w-2.5 rounded-full bg-green-500/70" />
                  <span className="ml-2 text-[10px] font-mono text-slate-500">
                    loomcast execution output
                  </span>
                </div>
                <pre className="thin-scroll overflow-x-auto p-4 text-xs font-mono text-slate-300 leading-relaxed">
                  <code>{activeAction.terminalOutput}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
