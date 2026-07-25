import Link from "next/link";

interface Feature {
  title: string;
  body: string;
  icon: string;
  actionAnchor?: string;
}

const FEATURES: Feature[] = [
  {
    title: "Unified Interface",
    body: "Write manager.chat(model, messages) once. Loomcast routes it to the right runtime — no per-runtime ports, routes, or payload formats to learn.",
    icon: "M4 7h16M4 12h16M4 17h10",
    actionAnchor: "#actions",
  },
  {
    title: "Three Local Runtimes",
    body: "Ollama, LM Studio, and llama.cpp supported from day one, each behind the same RuntimePort contract.",
    icon: "M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z",
    actionAnchor: "#diagnostics",
  },
  {
    title: "Catalog & Recommendations",
    body: "Search and filter models by task (code, math, vision) with a dynamic catalog and offline static fallback.",
    icon: "M21 21l-4.3-4.3M17 10a7 7 0 11-14 0 7 7 0 0114 0z",
    actionAnchor: "#actions",
  },
  {
    title: "SHA-256 Verification",
    body: "Verify installed model integrity against SHA-256 digests and update models seamlessly.",
    icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
    actionAnchor: "#actions",
  },
  {
    title: "Resilient by Design",
    body: "The dynamic catalog automatically falls back to a checksum-verified static catalog when the network misbehaves.",
    icon: "M12 3v18m0 0l-4-4m4 4l4-4M4 7l4-4 4 4",
    actionAnchor: "#diagnostics",
  },
  {
    title: "Side-by-Side Comparison",
    body: "Send one prompt to every runtime at once and compare responses in parallel panels.",
    icon: "M4 5h6v14H4zM14 5h6v14h-6z",
    actionAnchor: "#compare-demo",
  },
  {
    title: "CLI and SDK",
    body: "Drive it from the terminal with loomcast ..., or import loomcast and call the same operations from Python.",
    icon: "M8 9l3 3-3 3M13 15h4",
    actionAnchor: "#actions",
  },
  {
    title: "Clean Architecture",
    body: "Ports and adapters throughout: the domain never imports the network. Add a new runtime in a single file.",
    icon: "M3 7h18M3 12h18M3 17h18",
    actionAnchor: "#actions",
  },
];

export default function Features() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 max-w-6xl">
        <div className="max-w-2xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-loom-500/30 bg-loom-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-loom-300">
            Key Features
          </span>
          <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Everything you need to run local models
          </h2>
          <p className="mt-4 text-lg text-slate-400">
            A thin, dependable layer over the runtimes you already run — not a server, not an inference engine.
          </p>
        </div>

        <Link
          href="#actions"
          className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:border-loom-500 hover:bg-slate-800"
        >
          Explore all actions →
        </Link>
      </div>

      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((f) => (
          <Link
            key={f.title}
            href={f.actionAnchor || "#actions"}
            className="group rounded-2xl border border-slate-800 bg-slate-900/40 p-6 transition hover:border-loom-500/60 hover:bg-slate-900/70"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-loom-500/15 text-loom-300 transition group-hover:scale-110">
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
            <h3 className="mt-4 font-semibold text-white group-hover:text-loom-300 transition">
              {f.title}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">{f.body}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
