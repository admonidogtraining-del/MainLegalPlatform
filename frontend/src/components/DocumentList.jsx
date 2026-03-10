import DocumentCard from "./DocumentCard";

export default function DocumentList({ documents, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-500 text-sm">
        <svg className="animate-spin w-5 h-5 ml-2" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor"
            d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        טוען נתונים...
      </div>
    );
  }

  if (!documents.length) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-500">
        <svg className="w-12 h-12 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414A1 1 0 0120 9.414V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-sm">לא נמצאו מסמכים תואמים</p>
        <p className="text-xs text-slate-600 mt-1">נסה לשנות את הפילטרים או הפעל סריקה</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 pb-10 space-y-4">
      {documents.map((doc) => (
        <DocumentCard key={doc.id} doc={doc} onRefresh={onRefresh} />
      ))}
    </div>
  );
}
