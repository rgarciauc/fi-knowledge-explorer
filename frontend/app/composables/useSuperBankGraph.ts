const STORED_NODE_TYPES = new Set([
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

export function useSuperBankGraph() {
  const api = useApi()
  const question = ref("What is affected if system EMBARGO fails?")
  const answer = ref("")
  const intent = ref("")
  const rows = ref<any[]>([])
  const nodes = ref<Record<string, any>>({})
  const edges = ref<Record<string, any>>({})
  const loading = ref(false)
  const selected = ref<any>(null)
  const details = ref<any>(null)

  async function ask() {
    loading.value = true
    details.value = null
    selected.value = null
    try {
      const data: any = await api.ask(question.value)
      answer.value = data.answer
      intent.value = data.intent
      rows.value = data.rows || []
      nodes.value = data.graph?.nodes || {}
      edges.value = data.graph?.edges || {}
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown application error"
      answer.value = `Request could not be completed. ${message} Check logs/frontend/server.log and logs/backend/backend.log.`
      intent.value = "error"
      rows.value = []
      nodes.value = {}
      edges.value = {}
    } finally {
      loading.value = false
    }
  }

  async function selectNode(nodeKey: string) {
    selected.value = nodes.value[nodeKey]
    details.value = null
    if (!selected.value?.id || !STORED_NODE_TYPES.has(selected.value.type)) return

    try {
      details.value = await api.details(selected.value.type, selected.value.id)
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to load node details"
      details.value = { error: message }
    }
  }

  return { question, answer, intent, rows, nodes, edges, loading, selected, details, ask, selectNode }
}
