"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

type Settings = {
  allow_shell: boolean;
  allow_read_file: boolean;
  allow_doc_search: boolean;
  allow_logs: boolean;
  long_memory_enabled: boolean;
  agent_mode: string;
  memory_mode: string;
  require_approval: string[];
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [saving, setSaving] = useState(false);

  const loadSettings = async () => {
    const res = await fetch(`${API_URL}/api/settings`);
    const data = await res.json();
    setSettings(data);
  };

  const saveSettings = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await fetch(`${API_URL}/api/settings`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      alert("تم حفظ الإعدادات بنجاح");
    } catch (error) {
      alert("خطأ في حفظ الإعدادات");
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  if (!settings) {
    return (
      <main className="p-6 text-slate-200">
        <h1 className="text-2xl mb-4">Settings</h1>
        <p>Loading…</p>
      </main>
    );
  }

  const toggle = (key: keyof Settings) => {
    setSettings((prev) => (prev ? { ...prev, [key]: !prev[key] } : prev));
  };

  return (
    <main className="p-6 text-slate-200">
      <h1 className="text-2xl mb-6">Settings</h1>

      <Card className="bg-slate-900 border-slate-800 max-w-xl">
        <CardHeader>
          <CardTitle>Agent Permissions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Agent Mode</h3>
            <div className="space-y-2">
              <Label className="text-sm text-slate-300">Agent Mode</Label>
              <select
                value={settings.agent_mode || "devops"}
                onChange={(e) =>
                  setSettings((prev) =>
                    prev ? { ...prev, agent_mode: e.target.value } : prev
                  )
                }
                className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-slate-200"
              >
                <option value="safe">Safe (آمن - بدون run_shell)</option>
                <option value="devops">DevOps (محدود + approval)</option>
                <option value="root">Root (خطير - فقط للمسؤولين)</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Memory Settings</h3>
            <div className="space-y-2">
              <Label className="text-sm text-slate-300">Memory Mode</Label>
              <select
                value={settings.memory_mode || "short"}
                onChange={(e) =>
                  setSettings((prev) =>
                    prev ? { ...prev, memory_mode: e.target.value } : prev
                  )
                }
                className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-slate-200"
              >
                <option value="off">Off (لا تخزن)</option>
                <option value="short">Short (جلسة واحدة)</option>
                <option value="long">Long (طويل الأمد + DB)</option>
              </select>
            </div>
            <div className="flex items-center justify-between space-x-4">
              <Label className="text-sm text-slate-300">
                Enable long-term memory
              </Label>
              <Switch
                checked={settings.long_memory_enabled}
                onCheckedChange={() => toggle("long_memory_enabled")}
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Tool Permissions</h3>
            {[
              ["allow_shell", "Allow run_shell (خطير)"],
              ["allow_read_file", "Allow read_file"],
              ["allow_doc_search", "Allow doc_search"],
              ["allow_logs", "Allow logs access"],
            ].map(([key, label]) => (
              <div
                key={key}
                className="flex items-center justify-between space-x-4"
              >
                <Label className="text-sm text-slate-300">{label}</Label>
                <Switch
                  checked={(settings as any)[key]}
                  onCheckedChange={() => toggle(key as keyof Settings)}
                />
              </div>
            ))}
          </div>

          <Button className="mt-4 w-full" onClick={saveSettings} disabled={saving}>
            {saving ? "جاري الحفظ..." : "حفظ الإعدادات"}
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}

