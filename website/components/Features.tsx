interface Feature {
  title: string;
  body: string;
  icon: string;
}

const FEATURES: Feature[] = [
  {
    title: "Unified interface",
    body: "Write manager.chat(model, messages) once. Loomcast routes it to the right runtime — no per-runtime ports, routes, or payload formats to learn.",
    icon: "M4 7h16M4 12h16M4 17h10",
  },
  {
    title: "Three runtimes",
    body: "Ollama, LM Studio, and llama.cpp are all supported from day one, each behind the same RuntimePort contract.",
    icon: "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z",
  },
  {
    title: "Catalog & search",
    body: "Search and recommend models from the catalog, with tags and descriptions kept clean and free of listing-page noise.",
    icon: "M21 21l-4.3-4.3M17 10a7 7 0 11-14 0 7 7 0 0114 0z",
  },
  {
    title: "Integrity verification",
    body: "Verify installed Ollama models against their SHA-256 digest, so you know what you are running.",
    icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  },
  {
    title: "Resilient by design",
    body: "The dynamic catalog falls back to a checksum-verified static catalog automatically when the network or the source misbehaves.",
    icon: "M12 3v18m0 0l-4-4m4 4l4-4M4 7l4-4 4 4",
  },
  {
    title: "Compare side by side",
    body: "Send one prompt to every runtime at once and read the answers in parallel panels — great for picking a model.",
    icon: "M4 5h6v14H4zM14 5h6v14h-6z",
  },
  {
    title: "CLI and SDK",
    body: "Drive it from the terminal with loomcast ..., or import loomcast and call the same operations from Python.",
    icon: "M8 9l3 3-3 3M13 15h4",
  },
  {
    title: "Clean architecture",
    body: "Ports and adapters throughout: the domain never imports the network. Add a new runtime in a single file.",
    icon: "M3 7h18M3 12h18M3 17h18",
  },
];

export default function Features() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
      <div className="max-w-2xl">
        <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Everything you need to run local models
        </h2>
        <p className="mt-4 text-lg text-slate-400">
          A thin, dependable layer over the runtimes you already run — not a
          server, not an inference engine.
        </p>
      </div>

      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((f) => (
          <div
            key={f.title}
            className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6 transition hover:border-loom-600/60 hover:bg-slate-900/70"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-loom-500/15 text-loom-300">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-5 w-5"
                aria-hidden="true"
              >
                <path d={f.icon} />
              </svg>
            </div>
            <h3 className="mt-4 font-semibold text-white">{f.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">{f.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
