import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const getDocuments = (params) => api.get("/documents", { params });
export const getStats = () => api.get("/documents/stats");
export const createDocument = (data) => api.post("/documents", data);
export const toggleBookmark = (id, bookmarked) =>
  api.patch(`/documents/${id}/bookmark`, { bookmarked });
export const updateUrgency = (id, urgency) =>
  api.patch(`/documents/${id}/urgency`, { urgency });
export const deleteDocument = (id) => api.delete(`/documents/${id}`);

export const triggerScrape = () => api.post("/scrape");
export const getScrapeStatus = () => api.get("/scrape/status");
