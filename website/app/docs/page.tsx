import Link from "next/link";
import { DOCS } from "@/lib/docs";

export const metadata = {
  title: "Documentation Hub | LoomCast",
  description: "Complete guides, CLI reference, Python SDK, and troubleshooting for LoomCast.",
};

export default function DocsIndexPage() {
  return (
    <div className="space-y-8">
      <div>
        <span className="inline-flex items-center gap-2 rounded-full border border-loom-500/30 bg-loom-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-loom-300">
          Documentation Hub
        </span>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Official LoomCast Documentation
        </h1>
        <p className="mt-2 text-base text-slate-400 max-w-2xl leading-relaxed">
          Find getting started guides, complete CLI & Python SDK references, architecture guides, and troubleshooting resources.
        </p>
      </div>

      {/* Docs Grid */}
      <div className="grid gap-4 sm:grid-cols-2">
        {DOCS.map((doc) => (
          <Link
            key={doc.slug}
            href={`/docs/${doc.slug}`}
            className="group rounded-2xl border border-slate-800 bg-slate-900/60 p-6 transition-all duration-200 hover:border-loom-500/80 hover:bg-slate-900/90 shadow-lg hover:shadow-loom-950/40"
          >
            <h2 className="text-lg font-semibold text-white group-hover:text-loom-300 transition">
              {doc.title}
            </h2>
            <p className="mt-3 text-sm text-slate-400 leading-relaxed">
              {doc.description || "Read guide..."}
            </p>
            <div className="mt-4 flex items-center gap-1 text-xs font-semibold text-loom-400 group-hover:translate-x-1 transition-transform">
              Read guide →
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
