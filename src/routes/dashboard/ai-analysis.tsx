import { createFileRoute } from "@tanstack/react-router";
import { CaseIntelligenceHubPage } from "@/components/dashboard/IntelligenceHubPage";

export const Route = createFileRoute("/dashboard/ai-analysis")({
  component: CaseIntelligenceHubPage,
});
