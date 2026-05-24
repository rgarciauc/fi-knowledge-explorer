const API_BASE = "/api"

export function useApi() {
  return {
    ask: (question: string) =>
      $fetch(`${API_BASE}/ask`, {
        method: "POST",
        body: { question },
      }),

    details: (label: string, id: string) =>
      $fetch(`${API_BASE}/nodes/${encodeURIComponent(label)}/${encodeURIComponent(id)}`),

    examples: () => $fetch<string[]>(`${API_BASE}/examples`),
  }
}