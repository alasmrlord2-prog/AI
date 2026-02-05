"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function PluginsPage() {
  const [plugins, setPlugins] = useState<any[]>([]);
  const [installed, setInstalled] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadPlugins();
    loadInstalled();
  }, []);

  const loadPlugins = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/plugins`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setPlugins(data.plugins || []);
    } catch (error) {
      console.error("Error loading plugins:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadInstalled = async () => {
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/plugins/installed`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setInstalled(data.plugins || []);
    } catch (error) {
      console.error("Error loading installed:", error);
    }
  };

  const handleInstall = async (pluginId: string) => {
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/plugins/${pluginId}/install`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (data.success) {
        alert("تم التثبيت بنجاح");
        loadInstalled();
      }
    } catch (error) {
      console.error("Error installing:", error);
      alert("خطأ في التثبيت");
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  const isInstalled = (pluginId: string) => {
    return installed.some(p => p.plugin_id === pluginId);
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header locale={locale} setLocale={handleSetLocale} />
        <div className="p-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🧩 Plugin Store</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    متجر plugins داخلي - أدوات، Modules، Workflows، Monitoring plugins
                  </p>
                  <Button onClick={loadPlugins} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Plugins المتاحة ({plugins.length})</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {plugins.map((plugin, idx) => (
                      <Card key={idx} className="bg-slate-800 border-slate-700">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className="font-semibold">{plugin.name}</h4>
                              <p className="text-sm text-slate-400 mt-1">{plugin.description}</p>
                              <div className="mt-2 flex gap-2">
                                <span className="px-2 py-1 rounded text-xs bg-blue-900 text-blue-200">
                                  {plugin.type}
                                </span>
                                <span className="text-xs text-slate-400">v{plugin.version}</span>
                                {isInstalled(plugin.plugin_id) && (
                                  <span className="px-2 py-1 rounded text-xs bg-green-900 text-green-200">
                                    مثبت
                                  </span>
                                )}
                              </div>
                              <div className="mt-2 text-xs text-slate-500">
                                بواسطة: {plugin.author}
                              </div>
                            </div>
                            {!isInstalled(plugin.plugin_id) && (
                              <Button
                                onClick={() => handleInstall(plugin.plugin_id)}
                                className="bg-green-600 hover:bg-green-700"
                                size="sm"
                              >
                                تثبيت
                              </Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

