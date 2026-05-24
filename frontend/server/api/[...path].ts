export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  const path = getRouterParam(event, "path") || ""
  const apiTarget = String(config.apiTarget).replace(/\/$/, "")

  return proxyRequest(event, `${apiTarget}/${path}`)
})
