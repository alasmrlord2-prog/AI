"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

type SearchResults = {
  results?: unknown[];
  total?: number;
  query?: string;
};

export default function GlobalSearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const data = await apiRequest(`/api/search?q=${encodeURIComponent(query)}`, {}, 5000);
      setResults(data);
    } catch (error) {
      console.error("Error searching:", error);
      setResults(null);
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
                        <Card key={`search-result-${result.path || result.source || idx}-${idx}`} className="bg-slate-800 border-slate-700">
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

