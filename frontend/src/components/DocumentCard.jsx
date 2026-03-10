import { useState } from "react";
import { toggleBookmark } from "../services/api";

const TYPE_LABELS = {
  legislation: { label: "חקיקה", color: "bg-green-900 text-green-300" },
  ruling: { label: "פסיקה", color: "bg-purple-900 text-purple-300" },
  bill: { label: "הצעת חוק", color: "bg-blue-900 text-blue-300" },
};

const URGENCY_LABELS = {
  high: { label: "דחופה", color: "bg-red-900 text-red-300" },
  medium: { label: "בינונית", color: "bg-yellow-900 text-yellow-300" },
  low: { label: "נמוכה", color: "bg-slate-700 text-slate-400" },
};

export default function DocumentCard({ doc, onRefresh }) {
  const [expanded, setExpanded] = useState(false);
  const [bookmarked, setBookmarked] = useState(doc.bookmarked);
  const [bookmarkLoading, setBookmarkLoading] = useState(false);

  const typeInfo = TYPE_LABELS[doc.type] ?? { label: doc.type, color: "bg-slate-700 text-slate-300" };
  const urgencyInfo = URGENCY_LABELS[doc.urgency] ?? URGENCY_LABELS.low;
  const areas = doc.law_area ? doc.law_area.split(",").map((a) => a.trim()).filter(Boolean) : [];

  async function handleBookmark(e) {
    e.stopPropagation();
    setBookmarkLoading(true);
    try {
      await toggleBookmark(doc.id, !bookmarked);
      setBookmarked(!bookmarked);
      onRefresh?.();
    } catch {
      /* silent */
    } finally {
      setBookmarkLoading(false);
    }
  }

  return (
    <div
      className="bg-slate-800 border border-slate-700 rounded-xl p-5 hover:border-slate-500 transition-colors cursor-pointer"
      onClick={() => setExpanded((e) => !e)}
    >
      {/* Top row: title + bookmark */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-white font-semibold text-base leading-snug flex-1">
          {doc.title}
        </h3>
        <button
          onClick={handleBookmark}
          disabled={bookmarkLoading}
          className={`flex-shrink-0 mt-0.5 transition-colors ${
            bookmarked ? "text-yellow-400" : "text-slate-500 hover:text-yellow-400"
          }`}
          title={bookmarked ? "הסר סימנייה" : "הוסף סימנייה"}
        >
          <svg className="w-5 h-5" fill={bookmarked ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
        </button>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-2 mt-3">
        <span className={`badge ${typeInfo.color}`}>{typeInfo.label}</span>
        {doc.court && (
          <span className="badge bg-slate-700 text-slate-300">{doc.court}</span>
        )}
        {areas.map((a) => (
          <span key={a} className="badge bg-teal-900 text-teal-300">{a}</span>
        ))}
        {doc.urgency !== "low" && (
          <span className={`badge ${urgencyInfo.color}`}>{urgencyInfo.label}</span>
        )}
      </div>

      {/* Summary */}
      {doc.summary && (
        <p className="mt-3 text-sm text-slate-400 leading-relaxed">{doc.summary}</p>
      )}

      {/* Footer meta */}
      <div className="flex items-center flex-wrap gap-x-4 gap-y-1 mt-4 text-xs text-slate-500">
        {doc.case_number && <span>תיק: {doc.case_number}</span>}
        {doc.judge && <span>שופט/ת: {doc.judge}</span>}
        {doc.pub_date && <span>{doc.pub_date}</span>}
        {doc.source_url && (
          <a
            href={doc.source_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-indigo-400 hover:text-indigo-300 underline"
          >
            מקור
          </a>
        )}
      </div>

      {/* Expanded raw content */}
      {expanded && doc.raw_content && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
            {doc.raw_content}
          </p>
        </div>
      )}

      {expanded && !doc.raw_content && (
        <p className="mt-4 text-xs text-slate-600 pt-4 border-t border-slate-700">
          אין תוכן מלא זמין למסמך זה.
        </p>
      )}
    </div>
  );
}
