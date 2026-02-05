"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type Secret = {
  id?: string;
  name?: string;
  type?: string;
  value?: string;
  created_at?: string;
};

export default function SecretsPage() {
  const [secrets, setSecrets] = useState<Secret[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSecret, setNewSecret] = useState({ name: "", value: "", type: "api_key" });
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadSecrets();
  }, []);

  const loadSecrets = async () => {
    setLoading(true);
    try {
      const data = await apiRequest("/api/secrets/", {}, 5000).catch(() => ({ secrets: [] }));
      setSecrets(data.secrets || []);
    } catch (error) {
      console.error("Error loading secrets:", error);
      setSecrets([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSecret = async () => {
    if (!newSecret.name || !newSecret.value) {
      alert("يرجى إدخال اسم وقيمة السر");
      return;
    }

    setLoading(true);
    try {
      const data = await apiRequest("/api/secrets/store", {
        method: "POST",
        body: JSON.stringify(newSecret),
      }, 10000);
      
      if (data.success) {
        alert("تم إضافة السر بنجاح");
        setNewSecret({ name: "", value: "", type: "api_key" });
        setShowAddForm(false);
        loadSecrets();
      }
    } catch (error) {
      console.error("Error adding secret:", error);
      alert(`خطأ في إضافة السر: ${error instanceof Error ? error.message : "خطأ غير معروف"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 h-screen w-screen overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header locale={locale} setLocale={handleSetLocale} />
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 space-y-4 md:space-y-6 scrollbar-thin min-h-0">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🔐 Secrets Manager</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    إدارة الأسرار - تخزين وإدارة API keys والكلمات السرية بشكل آمن
                  </p>
                  <div className="flex gap-2">
                    <Button onClick={loadSecrets} disabled={loading}>
                      {loading ? "جاري التحميل..." : "تحديث"}
                    </Button>
                    <Button onClick={() => setShowAddForm(!showAddForm)} className="bg-green-600 hover:bg-green-700">
                      إضافة سر
                    </Button>
                  </div>
                </div>

                {/* Add Form */}
                {showAddForm && (
                  <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <Input
                          value={newSecret.name}
                          onChange={(e) => setNewSecret({ ...newSecret, name: e.target.value })}
                          placeholder="اسم السر"
                          className="bg-slate-700 border-slate-600"
                        />
                        <Input
                          value={newSecret.value}
                          onChange={(e) => setNewSecret({ ...newSecret, value: e.target.value })}
                          placeholder="قيمة السر"
                          type="password"
                          className="bg-slate-700 border-slate-600"
                        />
                        <select
                          value={newSecret.type}
                          onChange={(e) => setNewSecret({ ...newSecret, type: e.target.value })}
                          className="w-full p-2 bg-slate-700 border border-slate-600 rounded text-slate-200"
                        >
                          <option value="api_key">API Key</option>
                          <option value="password">Password</option>
                          <option value="token">Token</option>
                          <option value="certificate">Certificate</option>
                        </select>
                        <div className="flex gap-2">
                          <Button onClick={handleAddSecret} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
                            حفظ
                          </Button>
                          <Button onClick={() => setShowAddForm(false)} variant="outline">
                            إلغاء
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Secrets List */}
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Secrets ({secrets.length})</h3>
                  <div className="space-y-3">
                    {secrets.length > 0 ? (
                      secrets.map((secret, idx) => (
                        <Card key={`secret-${secret.secret_id || secret.id || secret.name || idx}-${idx}`} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <h4 className="font-semibold">{secret.name || `Secret ${idx + 1}`}</h4>
                                <p className="text-sm text-slate-400 mt-1">Type: {secret.secret_type || secret.type || "api_key"}</p>
                                <div className="mt-2 flex gap-2">
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    secret.exposed || secret.risk === "high" ? "bg-red-900 text-red-200" :
                                    secret.risk === "medium" ? "bg-yellow-900 text-yellow-200" :
                                    "bg-green-900 text-green-200"
                                  }`}>
                                    {secret.exposed ? "Exposed" : secret.risk || "Safe"}
                                  </span>
                                  <span className="text-xs text-slate-500">
                                    {secret.created_at ? new Date(secret.created_at).toLocaleDateString() : "Recently"}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-8">No secrets found</div>
                    )}
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

