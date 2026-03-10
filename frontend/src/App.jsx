import { useState, useEffect, useCallback } from "react";
import Header from "./components/Header";
import StatsCards from "./components/StatsCards";
import FilterBar from "./components/FilterBar";
import DocumentList from "./components/DocumentList";
import UploadModal from "./components/UploadModal";
import { getDocuments, getStats } from "./services/api";

const DEFAULT_FILTERS = {
  tab: "all",       // all | legislation | ruling | bookmarked
  urgency: "all",
  court: "all",
  q: "",
};

export default function App() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};

      if (filters.tab === "bookmarked") {
        params.bookmarked = true;
      } else if (filters.tab !== "all") {
        params.type = filters.tab;
      }

      if (filters.urgency !== "all") params.urgency = filters.urgency;
      if (filters.q.trim()) params.q = filters.q.trim();
      // court filter is client-side since backend doesn't have a dedicated court param
      const [docsRes, statsRes] = await Promise.all([
        getDocuments(params),
        getStats(),
      ]);

      let docs = docsRes.data;

      // Client-side court filter
      if (filters.court !== "all") {
        docs = docs.filter((d) => d.court === filters.court);
      }

      setDocuments(docs);
      setStats(statsRes.data);
    } catch (err) {
      console.error("Failed to fetch:", err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Header onNewDocument={() => setShowModal(true)} />

      <main className="py-4">
        <StatsCards stats={stats} />
        <FilterBar filters={filters} onChange={setFilters} />
        <DocumentList
          documents={documents}
          loading={loading}
          onRefresh={fetchData}
        />
      </main>

      {showModal && (
        <UploadModal
          onClose={() => setShowModal(false)}
          onSaved={fetchData}
        />
      )}
    </div>
  );
}
