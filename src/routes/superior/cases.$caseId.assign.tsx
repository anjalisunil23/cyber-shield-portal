import { createFileRoute, Link } from "@tanstack/react-router";
import { MOCK_CASES, MOCK_USERS } from "@/data/mock/platform";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/cases/$caseId/assign")({ component: Page });

function Page() {
  const { caseId } = Route.useParams();
  const c = MOCK_CASES.find((x) => x.id === caseId) || MOCK_CASES[0];
  const investigators = MOCK_USERS.filter((u) => u.role === "Investigator");
  return (
    <PageScaffold crumbs={[{ label: c.caseNumber, to: `/superior/cases/${c.id}` }, { label: "Assign" }]} title="Assign Investigator" subtitle={c.title}>
      <Panel>
        <form className="mx-auto grid max-w-lg gap-3" onSubmit={(e) => e.preventDefault()}>
          <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm">{investigators.map((u) => <option key={u.id}>{u.name}</option>)}</select>
          <label className="flex items-center gap-2 text-sm text-slate-300"><input type="checkbox" defaultChecked className="accent-cyan" /> Primary assignee</label>
          <div className="flex gap-2"><PrimaryButton type="submit">Assign (UI)</PrimaryButton><Link to={"/superior/cases/$caseId" as "/"} params={{ caseId: c.id } as never}><GhostButton>Back</GhostButton></Link></div>
        </form>
      </Panel>
    </PageScaffold>
  );
}
