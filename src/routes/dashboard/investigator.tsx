import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/dashboard/investigator")({
  beforeLoad: () => {
    throw redirect({ to: "/investigator/dashboard" });
  },
});
