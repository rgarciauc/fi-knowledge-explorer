export type GraphNode = {
  id?: string
  name: string
  type: string
  degree?: number
  key?: string
}

export type GraphEdge = {
  source: string
  target: string
  label?: string
}

export type NodeDetails = {
  labels?: string[]
  stable_id?: string
  matched_by?: "stable_id" | "exact_name_fallback"
  properties?: Record<string, unknown>
  relationships?: Array<Record<string, unknown>>
  error?: string
} | null

export const NODE_TYPE_STYLES: Record<string, { color: string; label: string }> = {
  Department: { color: "#55d6c9", label: "Departments" },
  Team: { color: "#2dd4bf", label: "Teams" },
  Employee: { color: "#fb7185", label: "Employees" },
  System: { color: "#fb923c", label: "Systems" },
  Project: { color: "#d38cff", label: "Projects" },
  BusinessProcess: { color: "#72e69b", label: "Business Processes" },
  ProcessStep: { color: "#60a5fa", label: "Process Steps" },
  DataPipeline: { color: "#38bdf8", label: "Data Pipelines" },
  Dataset: { color: "#facc15", label: "Datasets" },
  Risk: { color: "#94a3b8", label: "Risks" },
  Entity: { color: "#94a3b8", label: "Entities" },
}

export const STORED_NODE_TYPES = new Set([
  "Department",
  "Team",
  "Employee",
  "System",
  "Project",
  "BusinessProcess",
  "ProcessStep",
  "DataPipeline",
  "Dataset",
])

export function nodeColor(type: string): string {
  return NODE_TYPE_STYLES[type]?.color || "#94a3b8"
}

export function nodeTypeLabel(type: string): string {
  return NODE_TYPE_STYLES[type]?.label || type
}

export function nodeSummary(node: GraphNode | null | undefined, details: NodeDetails): string {
  if (!node) return ""
  const properties = details?.properties || {}
  const candidates = [
    properties.description,
    properties.task_summary,
    properties.role,
    properties.type,
    properties.criticality ? `Criticality: ${properties.criticality}` : null,
    properties.status ? `Status: ${properties.status}` : null,
  ]

  const first = candidates.find(value => typeof value === "string" && value.trim().length > 0)
  if (typeof first === "string") return first
  return `${nodeTypeLabel(node.type)} node returned by the graph query.`
}
