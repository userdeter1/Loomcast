// Client-safe doc metadata. No Node built-ins here, so this module can be
// imported from both server and client components. Filesystem reads live in
// docs-server.ts, which must only be imported from server components.

export interface DocMeta {
  slug: string;
  title: string;
  file: string;
  description?: string;
}

// Single source of truth for the sidebar order. The file names map to the
// repository's top-level docs/ directory, read at build time by docs-server.ts.
export const DOCS: DocMeta[] = [
  {
    slug: "getting-started",
    title: "Getting started",
    file: "getting-started.md",
    description: "Installation, initial configuration, and your first chat via CLI & Python.",
  },
  {
    slug: "configuration",
    title: "Configuration",
    file: "configuration.md",
    description: "Config file settings, LOOMCAST_* environment variables, and default backend management.",
  },
  {
    slug: "runtimes",
    title: "Supported runtimes",
    file: "runtimes.md",
    description: "Integration details and runtime specifics for Ollama, LM Studio, and llama.cpp.",
  },
  {
    slug: "cli-reference",
    title: "CLI reference",
    file: "cli-reference.md",
    description: "Exhaustive command-line guide covering all Loomcast terminal commands.",
  },
  {
    slug: "python-sdk-reference",
    title: "Python SDK reference",
    file: "python-sdk-reference.md",
    description: "Complete Python library guide: LoomcastManager, module functions, and exception types.",
  },
  {
    slug: "extending",
    title: "Extending",
    file: "extending.md",
    description: "Ports and adapters architecture overview and guide to adding new runtimes.",
  },
  {
    slug: "troubleshooting",
    title: "Troubleshooting & FAQ",
    file: "troubleshooting.md",
    description: "Resolving connection errors, running system diagnostics, and frequently asked questions.",
  },
];

export function getDocMeta(slug: string): DocMeta | null {
  return DOCS.find((d) => d.slug === slug) ?? null;
}
