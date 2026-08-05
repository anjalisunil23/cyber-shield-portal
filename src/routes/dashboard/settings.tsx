import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { apiMessage } from "@/services/apiClient";
import { investigationApi } from "@/services/investigationApi";

export const Route = createFileRoute("/dashboard/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["me"], queryFn: () => investigationApi.me() });
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");

  const save = useMutation({
    mutationFn: () =>
      investigationApi.updateMe({
        full_name: name || data?.full_name,
        department: department || data?.department || undefined,
      }),
    onSuccess: () => {
      toast.success("Profile updated");
      void qc.invalidateQueries({ queryKey: ["me"] });
    },
    onError: (e) => toast.error(apiMessage(e)),
  });

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-50">Settings</h1>
        <p className="text-sm text-slate-400">Update your investigator profile</p>
      </div>
      <div className="max-w-lg space-y-4 rounded-2xl border border-white/10 bg-[#111827]/90 p-6">
        <p className="text-sm text-slate-300">
          Signed in as <span className="text-cyan">{data?.email}</span> ({data?.role})
        </p>
        <label className="block text-xs text-slate-400">
          Full name
          <input
            defaultValue={data?.full_name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"
          />
        </label>
        <label className="block text-xs text-slate-400">
          Department
          <input
            defaultValue={data?.department || ""}
            onChange={(e) => setDepartment(e.target.value)}
            className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm"
          />
        </label>
        <button
          type="button"
          onClick={() => save.mutate()}
          className="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          Save profile
        </button>
      </div>
    </div>
  );
}
