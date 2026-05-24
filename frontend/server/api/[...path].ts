import { randomUUID } from "node:crypto"
import { frontendLog } from "../utils/logger"

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const path = getRouterParam(event, "path") || ""
  const apiTarget = String(config.apiTarget).replace(/\/$/, "")
  const targetUrl = `${apiTarget}/${path}`
  const requestId = getHeader(event, "x-request-id") || randomUUID()
  const started = Date.now()

  setResponseHeader(event, "x-request-id", requestId)
  await frontendLog("info", "proxy_request_started", {
    requestId,
    method: getMethod(event),
    path: getRequestURL(event).pathname,
    targetUrl,
  })

  try {
    const result = await proxyRequest(event, targetUrl, {
      headers: { "x-request-id": requestId },
    })
    await frontendLog("info", "proxy_request_completed", {
      requestId,
      targetUrl,
      durationMs: Date.now() - started,
    })
    return result
  } catch (error: any) {
    const upstreamStatus = Number(error?.statusCode || error?.response?.status || 0) || undefined
    const message = error?.message || "Unable to contact backend"
    await frontendLog("error", "proxy_request_failed", {
      requestId,
      targetUrl,
      upstreamStatus,
      durationMs: Date.now() - started,
      message,
    })

    throw createError({
      statusCode: upstreamStatus || 502,
      statusMessage: "Backend request failed",
      data: {
        requestId,
        message,
      },
    })
  }
})
