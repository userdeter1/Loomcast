import { redirect } from "next/navigation";

// The docs index sends visitors to the first guide.
export default function DocsIndex() {
  redirect("/docs/getting-started");
}
