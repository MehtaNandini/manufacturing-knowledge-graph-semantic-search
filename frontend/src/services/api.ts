const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const fetchDocuments = async () => {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_URL}/api/documents/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Network response was not ok");
  return response.json();
};

export const fetchEntities = async () => {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_URL}/api/entities/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Network response was not ok");
  return response.json();
};

export const approveEntity = async (id: string) => {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_URL}/api/entities/${id}/approve`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Network response was not ok");
  return response.json();
};

export const semanticSearch = async (query: string) => {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_URL}/api/search/semantic`, {
    method: "POST",
    headers: { 
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query, limit: 5 }),
  });
  if (!response.ok) throw new Error("Network response was not ok");
  return response.json();
};
