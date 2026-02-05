"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

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
  email_alerts?: {
    enabled: boolean;
    smtp_server: string;
    smtp_port: number;
    smtp_username: string;
    smtp_password: string;
    from_email: string;
    recipients: string[];
    alert_types: {
      critical: boolean;
      high: boolean;
      medium: boolean;
      low: boolean;
    };
  };
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

  const [activeTab, setActiveTab] = useState<"agent" | "email">("agent");

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <h1 className="text-2xl mb-6">Settings</h1>
          
          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-slate-800">
            <button
              onClick={() => setActiveTab("agent")}
              className={`px-4 py-2 border-b-2 transition-colors ${
                activeTab === "agent"
                  ? "border-cyan-500 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Agent Settings
            </button>
            <button
              onClick={() => setActiveTab("email")}
              className={`px-4 py-2 border-b-2 transition-colors ${
                activeTab === "email"
                  ? "border-cyan-500 text-cyan-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              📧 Email Alerts
            </button>
          </div>

          {activeTab === "agent" && (

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
          )}

          {activeTab === "email" && (
            <Card className="bg-slate-900 border-slate-800 max-w-2xl">
              <CardHeader>
                <CardTitle>Email Alerts Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <Label className="text-sm text-slate-300">Enable Email Alerts</Label>
                  <Switch
                    checked={settings.email_alerts?.enabled || false}
                    onCheckedChange={(checked) =>
                      setSettings((prev) =>
                        prev
                          ? {
                              ...prev,
                              email_alerts: {
                                ...prev.email_alerts,
                                enabled: checked,
                                smtp_server: prev.email_alerts?.smtp_server || "",
                                smtp_port: prev.email_alerts?.smtp_port || 587,
                                smtp_username: prev.email_alerts?.smtp_username || "",
                                smtp_password: prev.email_alerts?.smtp_password || "",
                                from_email: prev.email_alerts?.from_email || "",
                                recipients: prev.email_alerts?.recipients || [],
                                alert_types: prev.email_alerts?.alert_types || {
                                  critical: true,
                                  high: true,
                                  medium: false,
                                  low: false,
                                },
                              },
                            }
                          : prev
                      )
                    }
                  />
                </div>

                {settings.email_alerts?.enabled && (
                  <>
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">SMTP Configuration</h3>
                      <div className="space-y-2">
                        <Label className="text-sm text-slate-300">SMTP Server</Label>
                        <Input
                          value={settings.email_alerts?.smtp_server || ""}
                          onChange={(e) =>
                            setSettings((prev) =>
                              prev
                                ? {
                                    ...prev,
                                    email_alerts: {
                                      ...prev.email_alerts!,
                                      smtp_server: e.target.value,
                                    },
                                  }
                                : prev
                            )
                          }
                          placeholder="smtp.gmail.com"
                          className="bg-slate-800 border-slate-700"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-sm text-slate-300">SMTP Port</Label>
                          <Input
                            type="number"
                            value={settings.email_alerts?.smtp_port || 587}
                            onChange={(e) =>
                              setSettings((prev) =>
                                prev
                                  ? {
                                      ...prev,
                                      email_alerts: {
                                        ...prev.email_alerts!,
                                        smtp_port: parseInt(e.target.value) || 587,
                                      },
                                    }
                                  : prev
                              )
                            }
                            className="bg-slate-800 border-slate-700"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-sm text-slate-300">From Email</Label>
                          <Input
                            type="email"
                            value={settings.email_alerts?.from_email || ""}
                            onChange={(e) =>
                              setSettings((prev) =>
                                prev
                                  ? {
                                      ...prev,
                                      email_alerts: {
                                        ...prev.email_alerts!,
                                        from_email: e.target.value,
                                      },
                                    }
                                  : prev
                              )
                            }
                            placeholder="alerts@example.com"
                            className="bg-slate-800 border-slate-700"
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm text-slate-300">SMTP Username</Label>
                        <Input
                          value={settings.email_alerts?.smtp_username || ""}
                          onChange={(e) =>
                            setSettings((prev) =>
                              prev
                                ? {
                                    ...prev,
                                    email_alerts: {
                                      ...prev.email_alerts!,
                                      smtp_username: e.target.value,
                                    },
                                  }
                                : prev
                            )
                          }
                          className="bg-slate-800 border-slate-700"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-sm text-slate-300">SMTP Password</Label>
                        <Input
                          type="password"
                          value={settings.email_alerts?.smtp_password || ""}
                          onChange={(e) =>
                            setSettings((prev) =>
                              prev
                                ? {
                                    ...prev,
                                    email_alerts: {
                                      ...prev.email_alerts!,
                                      smtp_password: e.target.value,
                                    },
                                  }
                                : prev
                            )
                          }
                          className="bg-slate-800 border-slate-700"
                        />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Recipients</h3>
                      <div className="space-y-2">
                        <Input
                          placeholder="Enter email address and press Enter"
                          className="bg-slate-800 border-slate-700"
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && e.currentTarget.value) {
                              const email = e.currentTarget.value.trim();
                              if (email && email.includes("@")) {
                                setSettings((prev) =>
                                  prev
                                    ? {
                                        ...prev,
                                        email_alerts: {
                                          ...prev.email_alerts!,
                                          recipients: [
                                            ...(prev.email_alerts?.recipients || []),
                                            email,
                                          ],
                                        },
                                      }
                                    : prev
                                );
                                e.currentTarget.value = "";
                              }
                            }
                          }}
                        />
                        <div className="flex flex-wrap gap-2">
                          {settings.email_alerts?.recipients?.map((email, idx) => (
                            <div
                              key={idx}
                              className="flex items-center gap-2 px-3 py-1 bg-slate-800 rounded text-sm"
                            >
                              <span>{email}</span>
                              <button
                                onClick={() =>
                                  setSettings((prev) =>
                                    prev
                                      ? {
                                          ...prev,
                                          email_alerts: {
                                            ...prev.email_alerts!,
                                            recipients:
                                              prev.email_alerts?.recipients?.filter(
                                                (_, i) => i !== idx
                                              ) || [],
                                          },
                                        }
                                      : prev
                                  )
                                }
                                className="text-red-400 hover:text-red-300"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Alert Types</h3>
                      {[
                        ["critical", "Critical Alerts"],
                        ["high", "High Severity"],
                        ["medium", "Medium Severity"],
                        ["low", "Low Severity"],
                      ].map(([key, label]) => (
                        <div
                          key={key}
                          className="flex items-center justify-between"
                        >
                          <Label className="text-sm text-slate-300">{label}</Label>
                          <Switch
                            checked={
                              settings.email_alerts?.alert_types?.[key as keyof typeof settings.email_alerts.alert_types] ||
                              false
                            }
                            onCheckedChange={(checked) =>
                              setSettings((prev) =>
                                prev
                                  ? {
                                      ...prev,
                                      email_alerts: {
                                        ...prev.email_alerts!,
                                        alert_types: {
                                          ...prev.email_alerts!.alert_types,
                                          [key]: checked,
                                        },
                                      },
                                    }
                                  : prev
                              )
                            }
                          />
                        </div>
                      ))}
                    </div>

                    <Button
                      className="mt-4 w-full bg-cyan-600 hover:bg-cyan-700"
                      onClick={async () => {
                        // Test email configuration
                        const token = localStorage.getItem("auth_token");
                        try {
                          const res = await fetch(
                            `${API_URL}/api/settings/test-email`,
                            {
                              method: "POST",
                              headers: {
                                "Content-Type": "application/json",
                                Authorization: `Bearer ${token}`,
                              },
                              body: JSON.stringify(settings.email_alerts),
                            }
                          );
                          if (res.ok) {
                            alert("Test email sent successfully!");
                          } else {
                            alert("Failed to send test email");
                          }
                        } catch (err) {
                          alert("Error testing email configuration");
                        }
                      }}
                    >
                      Send Test Email
                    </Button>
                  </>
                )}

                <Button className="mt-4 w-full" onClick={saveSettings} disabled={saving}>
                  {saving ? "جاري الحفظ..." : "حفظ الإعدادات"}
                </Button>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
}

