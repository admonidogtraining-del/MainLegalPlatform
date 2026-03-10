const TABS = [
  { label: "הכל", value: "all" },
  { label: "חקיקה", value: "legislation" },
  { label: "פסיקה", value: "ruling" },
  { label: "סימניות", value: "bookmarked" },
];

const URGENCY_OPTIONS = [
  { label: "כל הדחיפות", value: "all" },
  { label: "דחופה", value: "high" },
  { label: "בינונית", value: "medium" },
  { label: "נמוכה", value: "low" },
];

const COURT_OPTIONS = [
  { label: "כל הערכאות", value: "all" },
  { label: "בית המשפט העליון", value: "בית המשפט העליון" },
  { label: "בית משפט מחוזי", value: "בית משפט מחוזי" },
  { label: "בית משפט שלום", value: "בית משפט שלום" },
  { label: "כנסת ישראל", value: "כנסת ישראל" },
];

export default function FilterBar({ filters, onChange }) {
  const { tab, urgency, court, q } = filters;

  function set(key, val) {
    onChange({ ...filters, [key]: val });
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-3 space-y-3">
      {/* Tab row */}
      <div className="flex gap-1 border-b border-slate-700 pb-3">
        {TABS.map((t) => (
          <button
            key={t.value}
            onClick={() => set("tab", t.value)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              tab === t.value
                ? "bg-indigo-600 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Search + dropdowns row */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <svg
            className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
          <input
            type="text"
            placeholder="חיפוש..."
            value={q}
            onChange={(e) => set("q", e.target.value)}
            className="w-full bg-slate-800 border border-slate-600 rounded-lg pr-9 pl-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Court filter */}
        <select
          value={court}
          onChange={(e) => set("court", e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          {COURT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        {/* Urgency filter */}
        <select
          value={urgency}
          onChange={(e) => set("urgency", e.target.value)}
          className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          {URGENCY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
