import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/dashboard/supervisor")({
  beforeLoad: () => {
    throw redirect({ to: "/superior/dashboard" });
  },
});
