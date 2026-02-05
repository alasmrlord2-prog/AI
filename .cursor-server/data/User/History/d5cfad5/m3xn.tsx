"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 
                process.env.NEXT_PUBLIC_BACKEND_URL || 
                "http://localhost:8000";

type KnowledgeItem = {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  embeddings?: number[];
};

type SearchResult = {
  item: KnowledgeItem;
  score: number;
  relevance: string;
};

export default function KnowledgePage() {
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"browse" | "search" | "add">("browse");
  const [selectedItem, setSelectedItem] = useState<KnowledgeItem | null>(null);
  const [newItem, setNewItem] = useState({
    title: "",
    content: "",
    category: "",
    tags: "",
  });

  useEffect(() => {
    loadKnowledgeBase();
  }, []);

  const getAuthToken = () => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  };

  const loadKnowledgeBase = async () => {
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/knowledge`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setKnowledgeItems(data.items || []);
      }
    } catch (err) {
      console.error("Failed to load knowledge base:", err);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/knowledge/search`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: searchQuery }),
      });
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results || []);
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async () => {
    if (!newItem.title || !newItem.content) return;
    setLoading(true);
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/knowledge`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: newItem.title,
          content: newItem.content,
          category: newItem.category,
          tags: newItem.tags.split(",").map(t => t.trim()).filter(t => t),
        }),
      });
      if (res.ok) {
        await loadKnowledgeBase();
        setNewItem({ title: "", content: "", category: "", tags: "" });
        setActiveTab("browse");
        alert("Knowledge item added successfully!");
      }
    } catch (err) {
      console.error("Failed to add item:", err);
      alert("Failed to add knowledge item");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (id: string) => {
    if (!confirm("Are you sure you want to delete this item?")) return;
    try {
      const token = getAuthToken();
      const res = await fetch(`${API_URL}/api/knowledge/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        await loadKnowledgeBase();
        setSelectedItem(null);
      }
    } catch (err) {
      console.error("Failed to delete item:", err);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              📚 RAG Knowledge Base
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Retrieve-Augmented Generation System for AI Agent
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b border-slate-800">
            {[
              { id: "browse", label: "Browse", icon: "📖" },
              { id: "search", label: "Search", icon: "🔍" },
              { id: "add", label: "Add Knowledge", icon: "➕" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? "border-purple-500 text-purple-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          {/* Browse Tab */}
          {activeTab === "browse" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Knowledge Items ({knowledgeItems.length})</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {knowledgeItems.map((item) => (
                        <div
                          key={item.id}
                          onClick={() => setSelectedItem(item)}
                          className={`p-4 border rounded-lg cursor-pointer hover:bg-slate-800 transition-all ${
                            selectedItem?.id === item.id
                              ? "border-purple-500 bg-purple-900/20"
                              : "border-slate-700"
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h3 className="font-bold text-purple-400 mb-1">{item.title}</h3>
                              <p className="text-sm text-slate-300 line-clamp-2">{item.content}</p>
                              <div className="flex gap-2 mt-2">
                                <span className="text-xs px-2 py-1 bg-slate-800 rounded">
                                  {item.category}
                                </span>
                                {item.tags.map((tag, idx) => (
                                  <span key={idx} className="text-xs px-2 py-1 bg-purple-900/30 rounded">
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {selectedItem && (
                <div className="md:col-span-1">
                  <Card className="bg-slate-900 border-slate-800">
                    <CardHeader>
                      <CardTitle>Details</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <h3 className="font-bold text-lg mb-2">{selectedItem.title}</h3>
                          <p className="text-sm text-slate-300 whitespace-pre-wrap">
                            {selectedItem.content}
                          </p>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Category</div>
                          <div className="text-sm text-slate-300">{selectedItem.category}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Tags</div>
                          <div className="flex flex-wrap gap-2">
                            {selectedItem.tags.map((tag, idx) => (
                              <span key={idx} className="text-xs px-2 py-1 bg-purple-900/30 rounded">
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="text-xs text-slate-400">
                          Created: {new Date(selectedItem.created_at).toLocaleString()}
                        </div>
                        <Button
                          onClick={() => handleDeleteItem(selectedItem.id)}
                          className="w-full bg-red-600 hover:bg-red-700"
                        >
                          Delete
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          )}

          {/* Search Tab */}
          {activeTab === "search" && (
            <div className="space-y-4">
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle>Semantic Search</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    <Input
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                      placeholder="Search knowledge base using natural language..."
                      className="bg-slate-800 border-slate-700"
                    />
                    <Button
                      onClick={handleSearch}
                      disabled={loading}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      {loading ? "Searching..." : "Search"}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {searchResults.length > 0 && (
                <Card className="bg-slate-900 border-slate-800">
                  <CardHeader>
                    <CardTitle>Search Results ({searchResults.length})</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {searchResults.map((result, idx) => (
                        <div
                          key={idx}
                          className="p-4 border border-slate-700 rounded-lg"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <h3 className="font-bold text-purple-400">{result.item.title}</h3>
                            <div className="flex items-center gap-2">
                              <span className="text-xs px-2 py-1 bg-green-900/30 text-green-400 rounded">
                                {(result.score * 100).toFixed(1)}% match
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-slate-300 mb-2">{result.item.content}</p>
                          <div className="text-xs text-slate-400">
                            Relevance: {result.relevance}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Add Knowledge Tab */}
          {activeTab === "add" && (
            <Card className="bg-slate-900 border-slate-800 max-w-2xl">
              <CardHeader>
                <CardTitle>Add Knowledge Item</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-slate-300 mb-2 block">Title</label>
                    <Input
                      value={newItem.title}
                      onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                      placeholder="Knowledge item title"
                      className="bg-slate-800 border-slate-700"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-300 mb-2 block">Content</label>
                    <textarea
                      value={newItem.content}
                      onChange={(e) => setNewItem({ ...newItem, content: e.target.value })}
                      placeholder="Knowledge content..."
                      rows={10}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-200"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-300 mb-2 block">Category</label>
                    <Input
                      value={newItem.category}
                      onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                      placeholder="e.g., Security, DevOps, General"
                      className="bg-slate-800 border-slate-700"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-300 mb-2 block">Tags (comma-separated)</label>
                    <Input
                      value={newItem.tags}
                      onChange={(e) => setNewItem({ ...newItem, tags: e.target.value })}
                      placeholder="tag1, tag2, tag3"
                      className="bg-slate-800 border-slate-700"
                    />
                  </div>
                  <Button
                    onClick={handleAddItem}
                    disabled={loading || !newItem.title || !newItem.content}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    {loading ? "Adding..." : "Add to Knowledge Base"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
}

