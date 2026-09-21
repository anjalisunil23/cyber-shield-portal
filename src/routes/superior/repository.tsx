import { createFileRoute } from "@tanstack/react-router";
import { EvidenceRepositoryPage } from "@/components/dashboard/EvidenceRepositoryPage";

export const Route = createFileRoute("/superior/repository")({
  component: () => <EvidenceRepositoryPage homeTo="/superior/dashboard" homeLabel="Supervisor" />,
});
