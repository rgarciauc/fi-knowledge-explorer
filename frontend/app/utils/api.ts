const API_BASE = "/api"

export class ApiRequestError extends Error {
  status?: number
  requestId?: string

  constructor(message: string, status?: number, requestId?: string) {
    super(message)
    this.name = "ApiRequestError"
    this.status = status
    this.requestId = requestId
  }
}

async function request<T>(url: string, options?: Record<string, unknown>): Promise<T> {
  try {
    return await $fetch<T>(url, options)
  } catch (error: any) {
    const status = error?.response?.status || error?.statusCode
    const payload = error?.response?._data || error?.data || {}
    const detail = payload?.detail || payload?.statusMessage || payload?.message || "Request failed"
    const requestId =
      payload?.request_id ||
      payload?.data?.requestId ||
      error?.response?.headers?.get?.("x-request-id")

    console.error("[SUPER_BANK API ERROR]", {
      url,
      status,
      requestId,
      detail,
      rawError: error,
    })

    const statusText = status ? `HTTP ${status}` : "network error"
    const reference = requestId ? ` Request ID: ${requestId}.` : ""
    throw new ApiRequestError(`${statusText}: ${detail}.${reference}`, status, requestId)
  }
}

export function useApi() {
  return {
    ask: (question: string) =>
      request(`${API_BASE}/ask`, {
        method: "POST",
        body: { question },
      }),

    details: (label: string, id: string) =>
      request(`${API_BASE}/nodes/${encodeURIComponent(label)}/${encodeURIComponent(id)}`),

    examples: () => request<string[]>(`${API_BASE}/examples`),
  }
}
