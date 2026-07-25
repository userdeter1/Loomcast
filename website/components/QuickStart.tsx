const CLI_EXAMPLE = `# Check which runtimes are up
loomcast status

# Send one prompt to every runtime, side by side
loomcast compare "Explain recursion in one sentence."

# Chat with a specific model on a specific backend
loomcast chat llama3 "Hello world!" --backend ollama`;

const SDK_EXAMPLE = `import loomcast

# Search the catalog
for model in loomcast.search("code"):
    print(model.name, model.description)

# Send a chat prompt
reply = loomcast.chat(
    "llama3",
    [{"role": "user", "content": "Hello!"}],
    runtime_type="ollama",
)

# Compare the same prompt across runtimes
for r in loomcast.compare("Explain recursion in one sentence."):
    print(r.runtime_type.value, "->", r.response or r.error)`;

function CodeCard({ label, code }: { label: string; code: string }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
      <div className="flex items-center gap-2 border-b border-slate-800 px-4 py-2.5">
        <span className="text-xs font-semibold uppercase tracking-wide text-loom-300">
          {label}
        </span>
      </div>
      <pre className="thin-scroll overflow-x-auto p-5 text-sm leading-relaxed">
        <code className="font-mono text-slate-200">{code}</code>
      </pre>
    </div>
  );
}

export default function QuickStart() {
  return (
    <section className="border-t border-slate-800/80 bg-slate-950">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <div className="max-w-2xl">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            The same operations, two ways
          </h2>
          <p className="mt-4 text-lg text-slate-400">
            Everything the CLI does is available from the Python SDK, backed by
            the same manager.
          </p>
        </div>

        <div className="mt-10 grid gap-6 lg:grid-cols-2">
          <CodeCard label="Command line" code={CLI_EXAMPLE} />
          <CodeCard label="Python SDK" code={SDK_EXAMPLE} />
        </div>
      </div>
    </section>
  );
}
