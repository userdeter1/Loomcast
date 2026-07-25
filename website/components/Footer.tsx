import Link from "next/link";
import Logo from "@/components/Logo";
import { SITE } from "@/lib/site";
import { DOCS } from "@/lib/docs";

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-2.5">
            <Logo />
            <span className="text-lg font-semibold text-white">{SITE.name}</span>
          </div>
          <p className="mt-3 max-w-xs text-sm text-slate-400">{SITE.tagline}</p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-200">Documentation</h3>
          <ul className="mt-3 space-y-2 text-sm">
            {DOCS.map((doc) => (
              <li key={doc.slug}>
                <Link
                  href={`/docs/${doc.slug}`}
                  className="text-slate-400 transition hover:text-white"
                >
                  {doc.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-slate-200">Project</h3>
          <ul className="mt-3 space-y-2 text-sm">
            <li>
              <a
                href={SITE.github}
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 transition hover:text-white"
              >
                GitHub
              </a>
            </li>
            <li>
              <a
                href={SITE.pypi}
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 transition hover:text-white"
              >
                PyPI
              </a>
            </li>
            <li>
              <a
                href={`${SITE.github}/blob/main/LICENSE`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 transition hover:text-white"
              >
                MIT License
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-800/80">
        <p className="mx-auto max-w-6xl px-4 py-6 text-xs text-slate-500 sm:px-6">
          Loomcast is an open-source project. Not affiliated with Ollama, LM
          Studio, or llama.cpp.
        </p>
      </div>
    </footer>
  );
}
