import { useState } from "react";
import { UserCheck, X } from "lucide-react";
import { PrimaryButton, GhostButton } from "@/components/ui-kit/PageKit";
import { addTaskItem, useCaseList } from "@/data/mock/platformState";
import { MOCK_USERS, MockTask } from "@/data/mock/platform";

export function AssignTaskModal({
  isOpen,
  onClose,
  defaultInvestigator,
  defaultCaseNumber,
  onAssigned,
}: {
  isOpen: boolean;
  onClose: () => void;
  defaultInvestigator?: string;
  defaultCaseNumber?: string;
  onAssigned?: (task: MockTask) => void;
}) {
  const cases = useCaseList();
  const investigators = MOCK_USERS.filter((u) => u.role === "Investigator" || u.role === "Forensic Officer" || u.role === "Superior Officer");

  const [title, setTitle] = useState("");
  const [assignee, setAssignee] = useState(defaultInvestigator || investigators[0]?.name || "Alex Mercer");
  const [caseNumber, setCaseNumber] = useState(defaultCaseNumber || cases[0]?.caseNumber || "CS-2026-0142");
  const [dueDate, setDueDate] = useState("2026-08-10");
  const [priority, setPriority] = useState("High");

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const created = addTaskItem({
      title: title.trim() || "Investigation follow-up",
      caseNumber,
      due: dueDate,
      status: "Open",
      assignee,
      priority,
    });

    if (onAssigned) onAssigned(created);
    onClose();
    setTitle("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-[#0f172a] p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-2">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-cyan/20 text-cyan">
              <UserCheck className="h-4 w-4" />
            </div>
            <h3 className="text-base font-semibold text-slate-100">Assign Task to Investigator</h3>
          </div>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-400">Target Investigator</label>
            <select
              value={assignee}
              onChange={(e) => setAssignee(e.target.value)}
              className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm text-slate-100 focus:border-cyan focus:outline-none"
            >
              {investigators.map((u) => (
                <option key={u.id} value={u.name}>
                  {u.name} ({u.department})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400">Task Title / Instructions</label>
            <input
              type="text"
              required
              placeholder="e.g. Extract CDN server logs for IP correlation"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-cyan focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-400">Target Case</label>
              <select
                value={caseNumber}
                onChange={(e) => setCaseNumber(e.target.value)}
                className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm text-slate-100 focus:border-cyan focus:outline-none"
              >
                {cases.map((c) => (
                  <option key={c.id} value={c.caseNumber}>
                    {c.caseNumber} - {c.title.slice(0, 15)}...
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400">Due Date</label>
              <input
                type="date"
                required
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm text-slate-100 focus:border-cyan focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400">Task Priority</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="mt-1 w-full rounded-xl border border-white/10 bg-[#0b1220] px-3 py-2 text-sm text-slate-100 focus:border-cyan focus:outline-none"
            >
              <option value="Low">Low Priority</option>
              <option value="Medium">Medium Priority</option>
              <option value="High">High Priority</option>
              <option value="Critical">Critical Priority</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <GhostButton type="button" onClick={onClose}>
              Cancel
            </GhostButton>
            <PrimaryButton type="submit">Assign Task</PrimaryButton>
          </div>
        </form>
      </div>
    </div>
  );
}
