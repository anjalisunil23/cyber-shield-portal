import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AuthenticatedShell } from "@/components/layouts/AuthenticatedShell";
import {
  EmptyState,
  GhostButton,
  LoadingBlock,
  PageScaffold,
  SelectFilter,
} from "@/components/ui-kit/PageKit";
import { investigationApi } from "@/services/investigationApi";
import type { NotificationItem } from "@/services/types";
import { CheckCheck } from "lucide-react";

export const Route = createFileRoute("/notifications")({ component: Page });

function Page() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const data = await investigationApi.notifications();
      setItems(data || []);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await investigationApi.markAllRead();
      setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {
      // fallback local update
      setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
    }
  };

  const handleMarkRead = async (id: string) => {
    try {
      await investigationApi.markRead(id);
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch {
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    }
  };

  const shown = items.filter((n) =>
    filter === "All" ? true : filter === "Unread" ? !n.is_read : n.is_read,
  );

  return (
    <AuthenticatedShell>
      <PageScaffold
        crumbs={[{ label: "Home", to: "/" }, { label: "Notifications" }]}
        title="Notifications"
        actions={
          <GhostButton onClick={handleMarkAllRead}>
            <CheckCheck className="mr-1.5 h-4 w-4" />
            Mark all read
          </GhostButton>
        }
      >
        <div className="mb-4">
          <SelectFilter value={filter} onChange={setFilter} options={["All", "Unread", "Read"]} />
        </div>
        {loading ? (
          <LoadingBlock rows={6} />
        ) : shown.length === 0 ? (
          <EmptyState title="No notifications." />
        ) : (
          <div className="space-y-2">
            {shown.map((n) => (
              <div
                key={n.id}
                onClick={() => !n.is_read && handleMarkRead(n.id)}
                className={`flex items-start justify-between rounded-xl border p-4 transition shadow-xs ${
                  n.is_read
                    ? "border-border bg-card/60 text-muted-foreground"
                    : "border-primary/30 bg-primary/10 text-foreground hover:border-primary/50 cursor-pointer"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm">{n.title}</span>
                    {!n.is_read && (
                      <span className="inline-block h-2 w-2 rounded-full bg-primary" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{n.message}</p>
                  <p className="text-[10px] text-muted-foreground">
                    {new Date(n.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </PageScaffold>
    </AuthenticatedShell>
  );
}
