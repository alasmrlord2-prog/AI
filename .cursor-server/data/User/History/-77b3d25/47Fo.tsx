"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { apiRequest } from "@/lib/api";

export default function CodeReviewPage() {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filePath, setFilePath] = useState("");
  const [locale, setLocale] = useState<"ar" | "en">("ar");

  useEffect(() => {
    loadReviews();
  }, []);

  const loadReviews = async () => {
    setLoading(true);
    try {
      // Code review API doesn't have a list endpoint, so we'll show empty state
      const data = await apiRequest("/api/code/review/", {}, 5000).catch(() => ({ reviews: [] }));
      setReviews(data.reviews || []);
    } catch (error) {
      console.error("Error loading reviews:", error);
      setReviews([]);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async () => {
    if (!filePath.trim()) {
      alert("يرجى إدخال مسار الملف");
      return;
    }

    setLoading(true);
    try {
      const data = await apiRequest("/api/code/review/review", {
        method: "POST",
        body: JSON.stringify({ file_path: filePath }),
      }, 30000);
      
      if (data.review) {
        setReviews((prev) => [data.review, ...prev]);
        setFilePath("");
        alert("تم مراجعة الكود بنجاح");
      }
    } catch (error) {
      console.error("Error reviewing code:", error);
      alert(`خطأ في مراجعة الكود: ${error instanceof Error ? error.message : "خطأ غير معروف"}`);
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
              <CardTitle>🔍 Code Review</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-slate-300">
                    مراجعة الكود بالذكاء الاصطناعي - اكتشاف الأخطاء والتحسينات
                  </p>
                  <Button onClick={loadReviews} disabled={loading}>
                    {loading ? "جاري التحميل..." : "تحديث"}
                  </Button>
                </div>

                <div className="flex gap-2">
                  <Input
                    value={filePath}
                    onChange={(e) => setFilePath(e.target.value)}
                    placeholder="مسار الملف (مثال: /app/main.py)"
                    className="flex-1 bg-slate-800 border-slate-700"
                  />
                  <Button onClick={handleReview} disabled={loading || !filePath.trim()}>
                    مراجعة
                  </Button>
                </div>

                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Code Reviews ({reviews.length})</h3>
                  <div className="space-y-3">
                    {reviews.length > 0 ? (
                      reviews.map((review, idx) => (
                        <Card key={`review-${review.id || review.file_path || idx}-${idx}`} className="bg-slate-800 border-slate-700">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <h4 className="font-semibold">{review.file_path || `Review ${idx + 1}`}</h4>
                                <p className="text-sm text-slate-400 mt-1">{review.summary || review.issues?.length || 0} issues found</p>
                                <div className="mt-2 flex gap-2">
                                  <span className={`px-2 py-1 rounded text-xs ${
                                    review.severity === "high" ? "bg-red-900 text-red-200" :
                                    review.severity === "medium" ? "bg-yellow-900 text-yellow-200" :
                                    "bg-green-900 text-green-200"
                                  }`}>
                                    {review.severity || "low"}
                                  </span>
                                  <span className="text-xs text-slate-500">
                                    {review.timestamp ? new Date(review.timestamp).toLocaleDateString() : "Recently"}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))
                    ) : (
                      <div className="text-slate-500 text-center py-8">No reviews found</div>
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

