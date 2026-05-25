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
      payload?.request_id || payload?.data?.requestId || error?.response?.headers?.get?.("x-request-id")
    const statusText = status ? `HTTP ${status}` : "Network error"
    const reference = requestId ? ` Request ID: ${requestId}.` : ""
    throw new ApiRequestError(`${statusText}: ${detail}.${reference}`, status, requestId)
  }
}

export type ProgressiveEventHandlers = {
  evidenceReady: (data: any) => void
  answerDelta: (data: { delta: string }) => void
  answerComplete: (data: { llm_status: string; answer_ai?: string }) => void
  answerError: (data: { llm_status: string; message: string }) => void
}

async function readSseResponse(response: Response, handlers: ProgressiveEventHandlers): Promise<void> {
  if (!response.body) throw new ApiRequestError("Streaming response has no readable body.", response.status)
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { value, done } = await reader.read()
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done })

    const blocks = buffer.split("\n\n")
    buffer = blocks.pop() || ""

    for (const block of blocks) {
      let event = ""
      const dataLines: string[] = []
      for (const line of block.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim()
        if (line.startsWith("data:")) dataLines.push(line.slice(5).trim())
      }
      if (!event || !dataLines.length) continue
      const payload = JSON.parse(dataLines.join("\n"))
      if (event === "evidence_ready") handlers.evidenceReady(payload)
      else if (event === "answer_delta") handlers.answerDelta(payload)
      else if (event === "answer_complete") handlers.answerComplete(payload)
      else if (event === "answer_error") handlers.answerError(payload)
    }
    if (done) break
  }
}

export type KpiRecord = {
  total_systems: number
  covered_systems: number
  system_owner_coverage_pct: number
  systems_with_it_owner?: number
  systems_with_business_owner?: number
  business_owner_coverage_pct?: number
  total_teams?: number
  teams_with_support?: number
  support_coverage_pct?: number
  systems_with_access_governance?: number
  access_governance_pct?: number
  total_processes: number
  covered_processes: number
  process_owner_coverage_pct: number
  total_steps: number
  covered_steps: number
  step_responsibility_pct: number
}

export function useApi() {
  const config = useRuntimeConfig()
  const streamBase = String(config.public?.streamingApiBase || API_BASE).replace(/\/$/, "")

  return {
    ask: (question: string) =>
      request<any>(`${API_BASE}/ask`, { method: "POST", body: { question } }),

    askStream: async (question: string, handlers: ProgressiveEventHandlers, signal?: AbortSignal) => {
      const response = await fetch(`${streamBase}/ask/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify({ question }),
        signal,
      })
      if (!response.ok) {
        let detail = "Streaming request failed"
        try {
          const data = await response.json()
          detail = data?.detail || detail
        } catch {
          // Keep fallback detail.
        }
        throw new ApiRequestError(`HTTP ${response.status}: ${detail}.`, response.status)
      }
      await readSseResponse(response, handlers)
    },

    details: (label: string, id: string) =>
      request<any>(`${API_BASE}/nodes/${encodeURIComponent(label)}/${encodeURIComponent(id)}`),

    examples: () => request<string[]>(`${API_BASE}/examples`),

    kpis: () => request<KpiRecord[]>(`${API_BASE}/kpis`),
  }
}
