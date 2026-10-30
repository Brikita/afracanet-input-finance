import { createFileRoute } from "@tanstack/react-router";
import { CreditWorkspace } from "../features/credit/CreditWorkspace";
export const Route = createFileRoute("/history")({
  head: () => ({ meta: [{ title: "Lender review — AFRACANet AI" }] }),
  component: () => <CreditWorkspace history />,
});
