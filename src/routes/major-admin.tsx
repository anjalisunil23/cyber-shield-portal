import { createFileRoute } from "@tanstack/react-router";
import { RoleShell } from "@/components/layouts/RoleShell";

export const Route = createFileRoute("/major-admin")({
  component: () => <RoleShell role="major_admin" />,
});
