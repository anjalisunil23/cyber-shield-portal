import { createFileRoute } from "@tanstack/react-router";
import { RoleShell } from "@/components/layouts/RoleShell";

export const Route = createFileRoute("/superior")({
  component: () => <RoleShell role="superior_officer" />,
});
