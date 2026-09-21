import { createFileRoute } from "@tanstack/react-router";
import { EvidenceRepositoryPage } from "@/components/dashboard/EvidenceRepositoryPage";

export const Route = createFileRoute("/admin/repository")({
  component: () => <EvidenceRepositoryPage homeTo="/admin/dashboard" homeLabel="Admin" />,
});
