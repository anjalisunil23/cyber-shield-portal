import { createFileRoute } from "@tanstack/react-router";
import { CaseDetailPage } from "@/components/dashboard/CaseDetailPage";

export const Route = createFileRoute("/investigator/cases/$caseId")({
  component: CaseDetailPage,
});
