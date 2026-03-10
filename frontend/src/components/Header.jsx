import { useState } from "react";
import { triggerScrape } from "../services/api";

export default function Header({ onNewDocument }) {
  const [scraping, setScraping] = useState(false);
  const [scrapeMsg, setScrapeMsg] = useState(null);

  async function handleScrape() {
    setScraping(true);
    setScrapeMsg(null);
    try {
      const res = await triggerScrape();
      setScrapeMsg("סריקה החלה ברקע");
    } catch {
      setScrapeMsg("שגיאה בהפעלת סריקה");
    } finally {
      setScraping(false);
      setTimeout(() => setScrapeMsg(null), 4000);
    }
  }

  return (
    <header className="bg-slate-900 border-b border-slate-700 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left – action buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={onNewDocument}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <span className="text-base">+</span>
            ניתוח מסמך חדש
          </button>
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="flex items-center gap-2 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            {/* database/sources icon */}
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <ellipse cx="12" cy="5" rx="9" ry="3" strokeWidth="2" />
              <path d="M3 5v6c0 1.657 4.03 3 9 3s9-1.343 9-3V5" strokeWidth="2" />
              <path d="M3 11v6c0 1.657 4.03 3 9 3s9-1.343 9-3v-6" strokeWidth="2" />
            </svg>
            {scraping ? "סורק..." : "מקורות"}
          </button>
          {scrapeMsg && (
            <span className="text-xs text-indigo-400">{scrapeMsg}</span>
          )}
        </div>

        {/* Right – title + subtitle */}
        <div className="text-right">
          <h1 className="text-xl font-bold text-white tracking-tight">
            Legal Intelligence Hub
          </h1>
          <p className="text-sm text-slate-400 mt-0.5">
            עדכוני חקיקה ופסיקה – סריקה חכמה לעורכי דין
          </p>
        </div>
      </div>
    </header>
  );
}
