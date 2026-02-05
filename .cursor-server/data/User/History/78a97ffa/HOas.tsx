"use client";

import ChatMessage from "./ChatMessage";

interface ChatMessage {
  role: string;
  content: string;
}

interface Props {
  messages: ChatMessage[];
  locale: string;
}

export default function ChatContainer({ messages, locale }: Props) {
  return (
     <div className="mt-5 max-h-[320px] overflow-y-auto bg-sw-bg-soft p-4 rounded-md border border-sw-border">
 
     {messages.map((m, i) => (
        <ChatMessage key={i} role={m.role} content={m.content} locale={locale} />
      ))}
    </div>
  );
}
