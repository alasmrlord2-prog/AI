"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === "ai-agent.bankid-sy.com" || hostname.includes("bankid-sy.com")) {
      return "http://ai-agent.bankid-sy.com";
    }
    return "http://localhost:8000";
  }
  return "http://localhost:8000";
};

export default function GlobalSearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem("auth_token");
      const res = await fetch(`${getApiUrl()}/api/search?q=${encodeURIComponent(query)}`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      setResults(data);
    } catch (error) {
      console.error("Error searching:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSetLocale = (newLocale: string) => {
    setLocale(newLocale as "ar" | "en");
  };

  return (
    <main className="flex bg-slate-950 text-slate-200 min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header locale={locale} setLocale={handleSetLocale} />
        <div className="p-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle>🔍 Global Search</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="ابحث في Logs, Files, Workflows, Docs, Configs..."
                    className="bg-slate-800 border-slate-700 text-slate-200"
                  />
                  <Button onClick={handleSearch} disabled={loading}>
                    {loading ? "جاري البحث..." : "بحث"}
                  </Button>
                </div>

                {results && (
                  <div className="mt-6">
                    <div className="mb-4 text-slate-400">
                      تم العثور على {results.total_results} نتيجة (عرض {results.returned_results})
                    </div>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {results.results.map((result: any, idx: number) => (
                        <Card key={idx} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="px-2 py-1 rounded text-xs bg-blue-900 text-blue-200">
                                    {result.source}
                                  </span>
                                  {result.path && (
                                    <span className="text-xs text-slate-400">{result.path}</span>
                                  )}
                                  {result.line_number && (
                                    <span className="text-xs text-slate-500">Line {result.line_number}</span>
                                  )}
                                </div>
                                <p className="text-sm text-slate-300">{result.content}</p>
                                <div className="mt-2 text-xs text-slate-500">
                                  Score: {result.score?.toFixed(2)}
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

