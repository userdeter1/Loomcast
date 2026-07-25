# Loomcast website

Showcase site and hosted documentation for Loomcast, built with
[Next.js](https://nextjs.org/) (App Router) and [Tailwind CSS](https://tailwindcss.com/).

## Documentation source

The documentation pages are **not** duplicated here. `lib/docs.ts` reads the
Markdown guides from the repository's top-level [`../docs`](../docs) directory at
build time, so the site and the repo docs never drift apart. To add a page, add
the Markdown file under `docs/` and one entry to the `DOCS` array in
`lib/docs.ts`.

## Local development

```bash
cd website
npm install
npm run dev
```

Then open http://localhost:3000.

## Build

```bash
npm run build
npm start
```

Because every page is rendered from build-time data (the Markdown files), the
site can also be exported as fully static output by adding `output: "export"` to
`next.config.mjs`, and hosted on any static host.

## Structure

```
app/
  layout.tsx            Root layout + metadata
  page.tsx              Landing page
  docs/
    layout.tsx          Docs shell with sidebar
    page.tsx            Redirects to the first guide
    [slug]/page.tsx     Renders one Markdown guide, statically generated
components/             Nav, Hero, Features, QuickStart, Footer, Markdown, ...
lib/
  docs.ts               Reads ../docs/*.md (single source of truth)
  site.ts               Project links and copy
```
