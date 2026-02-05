"use client";

import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface Props {
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
  loading: boolean;
  locale: string;
}

export default function ChatBox({ input, setInput, onSend, loading, locale }: Props) {
  const t = (en: string, ar: string) => (locale === "ar" ? ar : en);

  return (
    <div className="space-y-3">
      <Textarea
        className="bg-[#0f172a] text-[#e2e8f0] min-h-[130px] border border-[#1e293b] focus:ring-2 focus:ring-indigo-500"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        }}
        placeholder={
          locale === "ar"
            ? "اكتب سؤالك للـ Agent…"
            : "Write your question to the Agent…"
        }
      />

      <Button 
        onClick={onSend}
        disabled={loading || !input.trim()}
        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? t("Processing…", "يتم المعالجة…") : t("Run", "تشغيل")}
      </Button>
    </div>
  );
}
