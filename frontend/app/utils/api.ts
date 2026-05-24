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
    const detail =
      payload?.detail ||
      payload?.statusMessage ||
      payload?.message ||
      "Request failed"
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

    const statusText = status ? `HTTP ${status}` : "Network error"
    const reference = requestId ? ` Request ID: ${requestId}.` : ""
    throw new ApiRequestError(`${statusText}: ${detail}.${reference}`, status, requestId)
  }
}

export type KpiRecord = {
  total_systems: number
  covered_systems: number
  system_owner_coverage_pct: number
  systems_with_it_owner: number
  systems_with_business_owner: number
  business_owner_coverage_pct: number
  total_teams: number
  teams_with_support: number
  support_coverage_pct: number
  systems_with_access_governance: number
  access_governance_pct: number
  total_processes: number
  covered_processes: number
  process_owner_coverage_pct: number
  total_steps: number
  covered_steps: number
  step_responsibility_pct: number
}

export function useApi() {
  return {
    ask: (question: string) =>
      request<any>(`${API_BASE}/ask`, {
        method: "POST",
        body: { question },
      }),

    details: (label: string, id: string) =>
      request<any>(`${API_BASE}/nodes/${encodeURIComponent(label)}/${encodeURIComponent(id)}`),

    examples: () => request<string[]>(`${API_BASE}/examples`),

    kpis: () => request<KpiRecord[]>(`${API_BASE}/kpis`),
  }
}
