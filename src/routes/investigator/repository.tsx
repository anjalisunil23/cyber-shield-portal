import { createFileRoute } from "@tanstack/react-router";
import { EvidenceRepositoryPage } from "@/components/dashboard/EvidenceRepositoryPage";

export const Route = createFileRoute("/investigator/repository")({
  component: () => (
    <EvidenceRepositoryPage homeTo="/investigator/dashboard" homeLabel="Investigator" />
  ),
});
