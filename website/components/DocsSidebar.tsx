"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { DOCS } from "@/lib/docs";

export default function DocsSidebar() {
  const pathname = usePathname();
  const isOverview = pathname === "/docs";

  return (
    <nav className="space-y-1">
      <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Documentation
      </p>

      {/* Overview Hub Link */}
      <Link
        href="/docs"
        aria-current={isOverview ? "page" : undefined}
        className={
          isOverview
            ? "block rounded-lg bg-loom-500/15 px-3 py-2 text-sm font-medium text-loom-200"
            : "block rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-slate-900 hover:text-white"
        }
      >
        Overview
      </Link>

      <div className="my-2 border-t border-slate-800/80" />

      {DOCS.map((doc) => {
        const href = `/docs/${doc.slug}`;
        const active = pathname === href;
        return (
          <Link
            key={doc.slug}
            href={href}
            aria-current={active ? "page" : undefined}
            className={
              active
                ? "block rounded-lg bg-loom-500/15 px-3 py-2 text-sm font-medium text-loom-200"
                : "block rounded-lg px-3 py-2 text-sm text-slate-400 transition hover:bg-slate-900 hover:text-white"
            }
          >
            {doc.title}
          </Link>
        );
      })}
    </nav>
  );
}
