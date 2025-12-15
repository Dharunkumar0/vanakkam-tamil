const API_BASE_URL = import.meta.env.DEV 
  ? "http://localhost:8000" 
  : import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function sendMessage(message) {
  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error: ${res.status}`);
    }

    const data = await res.json();
    return data.response;
  } catch (error) {
    throw new Error(error.message || "Connection failed. Is the backend running?");
  }
}
