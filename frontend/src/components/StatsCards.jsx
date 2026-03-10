export default function StatsCards({ stats }) {
  const cards = [
    {
      key: "urgent",
      label: "דחופים",
      value: stats?.urgent ?? 0,
      borderColor: "border-red-500",
      iconColor: "text-red-400",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
      ),
    },
    {
      key: "bookmarked",
      label: "סימניות",
      value: stats?.bookmarked ?? 0,
      borderColor: "border-yellow-500",
      iconColor: "text-yellow-400",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
      ),
    },
    {
      key: "rulings",
      label: "פסקי דין",
      value: stats?.rulings ?? 0,
      borderColor: "border-purple-500",
      iconColor: "text-purple-400",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M3 6l9-3 9 3M3 6v12l9 3 9-3V6M12 3v18" />
        </svg>
      ),
    },
    {
      key: "bills",
      label: "הצעות חוק",
      value: stats?.bills ?? 0,
      borderColor: "border-blue-500",
      iconColor: "text-blue-400",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414A1 1 0 0120 9.414V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 px-6 py-4 max-w-7xl mx-auto w-full">
      {cards.map((c) => (
        <div
          key={c.key}
          className={`bg-slate-800 rounded-xl p-4 border-r-4 ${c.borderColor} flex items-center justify-between`}
        >
          <div>
            <p className="text-2xl font-bold text-white">{c.value}</p>
            <p className="text-sm text-slate-400 mt-0.5">{c.label}</p>
          </div>
          <span className={c.iconColor}>{c.icon}</span>
        </div>
      ))}
    </div>
  );
}
