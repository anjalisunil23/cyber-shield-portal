import { createFileRoute, Link } from "@tanstack/react-router";
import { GhostButton, PageScaffold, Panel, PrimaryButton } from "@/components/ui-kit/PageKit";

export const Route = createFileRoute("/superior/cases/create")({ component: Page });

function Page() {
  return (
    <PageScaffold crumbs={[{ label: "Cases", to: "/superior/cases" }, { label: "Create" }]} title="Create Case" subtitle="Open a new investigation" actions={<Link to={"/superior/cases" as "/"}><GhostButton>Cancel</GhostButton></Link>}>
      <Panel>
        <form className="mx-auto grid max-w-2xl gap-3" onSubmit={(e) => e.preventDefault()}>
          <input required placeholder="Title" className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <textarea placeholder="Description" rows={4} className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>Low</option><option>Medium</option><option>High</option><option>Critical</option></select>
            <select className="rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"><option>Open</option><option>Under Review</option></select>
          </div>
          <PrimaryButton type="submit">Create case (UI)</PrimaryButton>
        </form>
      </Panel>
    </PageScaffold>
  );
}
