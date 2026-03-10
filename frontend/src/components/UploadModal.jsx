import { useState, useRef } from "react";
import { createDocument } from "../services/api";

const DOC_TYPES = [
  { value: "legislation", label: "חקיקה / חוק" },
  { value: "bill", label: "הצעת חוק" },
  { value: "ruling", label: "פסק דין / פסיקה" },
];

export default function UploadModal({ onClose, onSaved }) {
  const [docType, setDocType] = useState("legislation");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [fileName, setFileName] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const fileRef = useRef();

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (ev) => setText(ev.target.result ?? "");
    reader.readAsText(file, "utf-8");
  }

  function handleDrop(e) {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (ev) => setText(ev.target.result ?? "");
    reader.readAsText(file, "utf-8");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim() && !url.trim()) {
      setError("יש להכניס טקסט או קישור");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const title =
        text.trim().split("\n")[0].slice(0, 120) ||
        url ||
        "מסמך חדש";

      await createDocument({
        type: docType,
        title,
        raw_content: text.trim() || null,
        source_url: url.trim() || null,
        summary: text.trim().slice(0, 300) || null,
        scraped_from: "manual",
      });
      onSaved?.();
      onClose();
    } catch (err) {
      setError("שגיאה בשמירת המסמך. נסה שוב.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-slate-800 border border-slate-600 rounded-2xl w-full max-w-lg mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-700">
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          <div className="flex items-center gap-2 text-white font-semibold text-lg">
            <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2zm7 4v8m-4-4h8" />
            </svg>
            העלאה וניתוח מסמך
          </div>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-5">
          {/* Doc type */}
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">סוג המסמך</label>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
            >
              {DOC_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* File upload zone */}
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">
              העלאת קובץ (PDF, תמונה, טקסט)
            </label>
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileRef.current?.click()}
              className="border-2 border-dashed border-slate-600 hover:border-indigo-500 rounded-xl p-6 text-center cursor-pointer transition-colors"
            >
              <svg className="w-8 h-8 text-slate-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1M12 12V4m0 0l-3 3m3-3l3 3" />
              </svg>
              <p className="text-sm text-slate-400">
                {fileName ? fileName : "לחץ לבחירת קובץ"}
              </p>
              <input
                ref={fileRef}
                type="file"
                accept=".txt,.pdf,.png,.jpg,.jpeg"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
          </div>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-slate-700" />
            <span className="text-xs text-slate-500">או</span>
            <div className="flex-1 h-px bg-slate-700" />
          </div>

          {/* Paste text */}
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">הדבקת טקסט</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              placeholder="הדבק כאן טקסט של הצעת חוק או פסק דין..."
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500 resize-none focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Source URL */}
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">
              קישור למקור (אופציונלי)
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-slate-600 hover:border-slate-400 text-slate-300 hover:text-white py-2.5 rounded-lg text-sm font-medium transition-colors"
            >
              ביטול
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white py-2.5 rounded-lg text-sm font-medium transition-colors"
            >
              {saving ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  שומר...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2zm7 4v8m-4-4h8" />
                  </svg>
                  נתח ושמור
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
