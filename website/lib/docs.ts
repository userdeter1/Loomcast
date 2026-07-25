// Client-safe doc metadata. No Node built-ins here, so this module can be
// imported from both server and client components. Filesystem reads live in
// docs-server.ts, which must only be imported from server components.

export interface DocMeta {
  slug: string;
  title: string;
  file: string;
}

// Single source of truth for the sidebar order. The file names map to the
// repository's top-level docs/ directory, read at build time by docs-server.ts.
export const DOCS: DocMeta[] = [
  { slug: "getting-started", title: "Getting started", file: "getting-started.md" },
  { slug: "configuration", title: "Configuration", file: "configuration.md" },
  { slug: "runtimes", title: "Supported runtimes", file: "runtimes.md" },
  { slug: "cli-reference", title: "CLI reference", file: "cli-reference.md" },
  { slug: "extending", title: "Extending", file: "extending.md" },
];

export function getDocMeta(slug: string): DocMeta | null {
  return DOCS.find((d) => d.slug === slug) ?? null;
}
