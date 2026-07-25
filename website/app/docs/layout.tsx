import Nav from "@/components/Nav";
import Footer from "@/components/Footer";
import DocsSidebar from "@/components/DocsSidebar";

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <Nav />
      <div className="mx-auto flex max-w-6xl gap-10 px-4 py-10 sm:px-6">
        <aside className="hidden w-56 shrink-0 md:block">
          <div className="sticky top-24">
            <DocsSidebar />
          </div>
        </aside>
        <main className="min-w-0 flex-1">{children}</main>
      </div>
      <Footer />
    </>
  );
}
