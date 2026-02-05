"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8001/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: query }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      alert("Failed to connect to backend. Is it running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-900 text-white p-8 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
        Secure Personal Agentic Platform
      </h1>

      <div className="w-full max-w-2xl bg-slate-800 rounded-xl p-6 shadow-2xl border border-slate-700">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <textarea
            className="bg-slate-700 border border-slate-600 rounded-lg p-4 text-white resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ask your agent anything (Private, Coding, Financial...)"
            rows={4}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 transition-colors py-3 rounded-lg font-semibold disabled:opacity-50"
          >
            {loading ? "Processing Securely..." : "Send Request"}
          </button>
        </form>

        {response && (
          <div className="mt-8 space-y-4 animate-in fade-in duration-500">
            <div className="p-4 bg-slate-700 rounded-lg border border-slate-600">
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Routing Info</h2>
              <div className="flex gap-4 items-center">
                <span className="px-2 py-1 bg-blue-900 text-blue-200 text-xs rounded uppercase">{response.routing.intent}</span>
                <span className="px-2 py-1 bg-purple-900 text-purple-200 text-xs rounded uppercase">{response.routing.adapter}</span>
                {response.security && !response.security.is_safe && (
                  <span className="px-2 py-1 bg-red-900 text-red-200 text-xs rounded uppercase">Security Warning</span>
                )}
              </div>
            </div>

            <div className="p-6 bg-slate-900 rounded-lg border border-slate-700">
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Answer</h2>
              <div className="text-slate-200 whitespace-pre-wrap leading-relaxed">
                {response.answer}
              </div>
              {response.security && !response.security.is_safe && (
                <p className="mt-4 text-xs text-red-400 font-mono italic">
                  Note: Output flagged by Judge: {response.security.reason}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
