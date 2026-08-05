import { createFileRoute } from "@tanstack/react-router";
import { RoleShell } from "@/components/layouts/RoleShell";

export const Route = createFileRoute("/investigator")({
  component: () => <RoleShell role="investigator" />,
});
