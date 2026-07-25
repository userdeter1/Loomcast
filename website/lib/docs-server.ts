import "server-only";

import { promises as fs } from "fs";
import path from "path";
import { getDocMeta } from "@/lib/docs";

// The docs live in the repository's top-level docs/ directory. Reading them at
// build time keeps a single source of truth with no second copy to sync. This
// module uses Node's fs, so it must only be imported from server components.
const DOCS_DIR = path.join(process.cwd(), "..", "docs");

export async function getDocContent(slug: string): Promise<string | null> {
  const meta = getDocMeta(slug);
  if (!meta) return null;
  const filePath = path.join(DOCS_DIR, meta.file);
  return fs.readFile(filePath, "utf8");
}
