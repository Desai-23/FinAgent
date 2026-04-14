// api/finagent.js
// All FinAgent API calls — now includes Authorization header with JWT token

const BASE = "/api";

/**
 * Send a chat message to FinAgent.
 * Supports streaming for AGENTIC mode.
 * @param {string} text - The user's message
 * @param {string} mode - "auto" | "llm" | "rag" | "agentic"
 * @param {string} token - JWT access token
 * @param {object} callbacks - { onStep, onDone, onError }
 */
export async function sendMessage(text, mode = "auto", token, { onStep, onDone, onError } = {}) {
  try {
    const res = await fetch(`${BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ message: text, mode }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Request failed");
    }

    const contentType = res.headers.get("content-type") || "";

    // AGENTIC mode returns a stream of JSON lines
    if (contentType.includes("text/plain")) {
      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n").filter((l) => l.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);

            if (data.type === "step" && onStep) {
              onStep(data);
            } else if (data.type === "done" && onDone) {
              onDone(data);
            } else if (data.type === "error" && onError) {
              onError(new Error(data.message));
            }
          } catch {
            // skip malformed lines
          }
        }
      }
    } else {
      // LLM or RAG mode — regular JSON response
      const data = await res.json();
      if (onDone) onDone({ type: "done", mode_used: data.mode_used, data: { final_report: data.response } });
    }
  } catch (err) {
    if (onError) onError(err);
  }
}

/**
 * Clear the current user's conversation history.
 */
export async function clearHistory(token) {
  await fetch(`${BASE}/chat/history`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}

/**
 * Upload a PDF file to the user's knowledge base.
 */
export async function uploadPDF(file, token) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE}/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Upload failed");
  return data;
}

/**
 * Get the list of uploaded documents for the current user.
 */
export async function getDocuments(token) {
  const res = await fetch(`${BASE}/documents`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch documents");
  return data;
}

/**
 * Delete an uploaded document.
 */
export async function deleteDocument(filename, token) {
  const res = await fetch(`${BASE}/documents/${filename}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Delete failed");
  return data;
}
