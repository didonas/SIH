import axios from "axios";

const API_URL = "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
});

export const getAlerts = () => api.get("/alerts");
export const getAlertById = (id: string) => api.get(`/alerts/${id}`);
export const getModels = () => api.get("/models");
export const getSystemStatus = () => api.get("/system");
export const getTrafficAnalytics = () => api.get("/dashboard/analytics");

export const uploadPcap = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/analyze/pcap", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getLiveInterfaces = () => api.get("/live/interfaces", { timeout: 5000 });
export const startLiveCapture = (iface: string) => api.post("/live/start", { interface: iface });
export const stopLiveCapture = () => api.post("/live/stop");
export const getLiveStatus = () => api.get("/live/status");

export default api;
