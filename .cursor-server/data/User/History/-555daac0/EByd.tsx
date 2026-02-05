"use client";

interface ChatMessageProps {
  role: "user" | "agent";
  content: string;
  locale: string;
}

export default function ChatMessage({ role, content, locale }: ChatMessageProps) {
  const isUser = role === "user";
  const t = (en: string, ar: string) => (locale === "ar" ? ar : en);

  return (
    <div className={`mb-3 ${isUser ? "text-right" : "text-left"}`}>
      <strong className={isUser ? "text-sw-success" : "text-sw-blue"}>
        {isUser ? t("You", "أنت") : t("Agent", "الوكيل")}:
      </strong>
      <div className="whitespace-pre-wrap p-3 mt-1 rounded-md border border-sw-border bg-sw-bg-card text-sw-text">
        {content}
      </div>
    </div>
  );
}
