import { createFileRoute } from "@tanstack/react-router";
import { AuthenticatedShell } from "@/components/layouts/AuthenticatedShell";
import { PageScaffold, Panel } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/help")({ component: Page });

const FAQS = [
  ["How do I upload evidence?", "Open Upload, select a case, then add files."],
  ["Who can create admins?", "Only Major Admin can create Admin accounts."],
  ["How do I assign investigators?", "Open a case and use Add investigator, or use Assignments."],
];

function Page() {
  return (
    <AuthenticatedShell>
      <PageScaffold crumbs={[{ label: "Home", to: "/" }, { label: "Help" }]} title="Help">
        <div className="space-y-3">
          {FAQS.map(([q, a]) => (
            <Panel key={q} title={q}>
              <p className="text-sm text-muted-foreground">{a}</p>
            </Panel>
          ))}
        </div>
      </PageScaffold>
    </AuthenticatedShell>
  );
}
