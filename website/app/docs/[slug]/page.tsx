import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Markdown from "@/components/Markdown";
import { DOCS, getDocMeta } from "@/lib/docs";
import { getDocContent } from "@/lib/docs-server";

// Next 15+ makes route params a Promise that must be awaited.
interface PageProps {
  params: Promise<{ slug: string }>;
}

// Pre-render one static page per doc at build time.
export function generateStaticParams() {
  return DOCS.map((doc) => ({ slug: doc.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const meta = getDocMeta(slug);
  return { title: meta?.title ?? "Documentation" };
}

export default async function DocPage({ params }: PageProps) {
  const { slug } = await params;
  const meta = getDocMeta(slug);
  if (!meta) notFound();

  const content = await getDocContent(slug);
  if (content === null) notFound();

  const index = DOCS.findIndex((d) => d.slug === slug);
  const prev = index > 0 ? DOCS[index - 1] : null;
  const next = index < DOCS.length - 1 ? DOCS[index + 1] : null;

  return (
    <article>
      <Markdown>{content}</Markdown>

      <nav className="mt-16 flex items-center justify-between gap-4 border-t border-slate-800 pt-6 text-sm">
        {prev ? (
          <a
            href={`/docs/${prev.slug}`}
            className="text-slate-400 transition hover:text-white"
          >
            ← {prev.title}
          </a>
        ) : (
          <span />
        )}
        {next ? (
          <a
            href={`/docs/${next.slug}`}
            className="text-right text-slate-400 transition hover:text-white"
          >
            {next.title} →
          </a>
        ) : (
          <span />
        )}
      </nav>
    </article>
  );
}
