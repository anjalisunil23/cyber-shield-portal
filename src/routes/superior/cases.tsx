import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/superior/cases")({
  component: () => <Outlet />,
});
