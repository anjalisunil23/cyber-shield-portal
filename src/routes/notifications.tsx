import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { MOCK_NOTIFICATIONS } from "@/data/mock/platform";
import { PageScaffold, GhostButton, SelectFilter } from "@/components/ui-kit/PageKit";
import { NotificationCard } from "@/components/ui-kit/Cards";

export const Route = createFileRoute("/notifications")({ component: Page });

function Page() {
  const [items, setItems] = useState(MOCK_NOTIFICATIONS);
  const [filter, setFilter] = useState("All");
  const shown = items.filter((n) => filter === "All" || (filter === "Unread" ? !n.read : n.read));
  return (
    <div className="min-h-screen bg-[#020617] px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-3xl">
        <PageScaffold crumbs={[{ label: "App" }, { label: "Notifications" }]} title="Notification Center" subtitle="Alerts and unread items" actions={<GhostButton onClick={() => setItems((p) => p.map((n) => ({ ...n, read: true })))}>Mark all read</GhostButton>}>
          <div className="mb-4"><SelectFilter value={filter} onChange={setFilter} options={["All", "Unread", "Read"]} /></div>
          <div className="space-y-2">{shown.map((n) => <NotificationCard key={n.id} item={n} />)}</div>
        </PageScaffold>
      </div>
    </div>
  );
}
