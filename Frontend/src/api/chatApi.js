const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

/**
 * Send a chat message to the backend.
 * @param {{ message: string, session_id?: string }} payload
 */
export async function sendChatMessage(payload) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    const detail = error.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d) => d.msg).join(", ")
          : `Request failed (${response.status})`;
    throw new Error(message);
  }

  return response.json();
}
