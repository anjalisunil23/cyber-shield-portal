import { createFileRoute } from "@tanstack/react-router";
import { ChatInterface } from "@/components/chat/ChatInterface";

export const Route = createFileRoute("/investigator/messages")({
  component: InvestigatorMessagesPage,
});

function InvestigatorMessagesPage() {
  return (
    <div className="h-full min-h-0">
      <ChatInterface />
    </div>
  );
}
