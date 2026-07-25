import Link from "next/link";
import Logo from "@/components/Logo";
import { SITE } from "@/lib/site";

export default function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <Logo />
          <span className="text-lg font-semibold tracking-tight text-white">
            {SITE.name}
          </span>
        </Link>

        <div className="flex items-center gap-1 text-sm sm:gap-2">
          <Link
            href="/#features"
            className="hidden rounded-md px-3 py-2 text-slate-300 transition hover:text-white sm:block"
          >
            Features
          </Link>
          <Link
            href="/docs/getting-started"
            className="rounded-md px-3 py-2 text-slate-300 transition hover:text-white"
          >
            Docs
          </Link>
          <a
            href={SITE.pypi}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden rounded-md px-3 py-2 text-slate-300 transition hover:text-white sm:block"
          >
            PyPI
          </a>
          <a
            href={SITE.github}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-slate-700 px-3 py-2 font-medium text-white transition hover:border-loom-500 hover:bg-loom-500/10"
          >
            GitHub
          </a>
        </div>
      </nav>
    </header>
  );
}
