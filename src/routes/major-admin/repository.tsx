import { createFileRoute } from "@tanstack/react-router";
import { EvidenceRepositoryPage } from "@/components/dashboard/EvidenceRepositoryPage";

export const Route = createFileRoute("/major-admin/repository")({
  component: () => (
    <EvidenceRepositoryPage homeTo="/major-admin/dashboard" homeLabel="Major Admin" />
  ),
});
