"use client";

import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";
import { DOCS } from "@/lib/docs";

const DOC_SLUGS = new Set(DOCS.map((d) => d.slug));

// Rewrite links that point at the Markdown docs so they resolve to site routes.
// A link like `docs/runtimes.md`, `./runtimes.md#foo`, or `runtimes.md` becomes
// `/docs/runtimes`. Links to source files (../loomcast/...) or external URLs are
// left as-is.
function resolveHref(href: string | undefined): { href: string; internal: boolean } {
  if (!href) return { href: "#", internal: false };
  if (/^https?:\/\//.test(href) || href.startsWith("#")) {
    return { href, internal: false };
  }
  const mdMatch = href.match(/([a-z0-9-]+)\.md(#.*)?$/i);
  if (mdMatch) {
    const slug = mdMatch[1];
    const anchor = mdMatch[2] ?? "";
    if (DOC_SLUGS.has(slug)) {
      return { href: `/docs/${slug}${anchor}`, internal: true };
    }
  }
  return { href, internal: false };
}

const components: Components = {
  a({ href, children, ...props }) {
    const { href: resolved, internal } = resolveHref(href);
    if (internal) {
      return (
        <Link href={resolved} {...props}>
          {children}
        </Link>
      );
    }
    const external = /^https?:\/\//.test(resolved);
    return (
      <a
        href={resolved}
        {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
        {...props}
      >
        {children}
      </a>
    );
  },
};

export default function Markdown({ children }: { children: string }) {
  return (
    <div className="doc-content">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  );
}
