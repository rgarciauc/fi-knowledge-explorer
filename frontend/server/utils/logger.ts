import { appendFile, mkdir } from "node:fs/promises"
import { dirname } from "node:path"

const logFile = process.env.FRONTEND_LOG_FILE || "/app/logs/server.log"

type LogLevel = "info" | "error" | "warn"

export async function frontendLog(level: LogLevel, event: string, fields: Record<string, unknown> = {}) {
  const line = JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    event,
    ...fields,
  })

  if (level === "error") console.error(line)
  else if (level === "warn") console.warn(line)
  else console.info(line)

  try {
    await mkdir(dirname(logFile), { recursive: true })
    await appendFile(logFile, `${line}\n`, "utf8")
  } catch (error) {
    console.error(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: "error",
      event: "frontend_log_write_failed",
      message: error instanceof Error ? error.message : String(error),
    }))
  }
}
