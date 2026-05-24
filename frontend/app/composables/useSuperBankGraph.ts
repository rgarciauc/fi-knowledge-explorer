import type { NodeDetails } from "~/utils/graphPresentation"
import { STORED_NODE_TYPES } from "~/utils/graphPresentation"

export function useSuperBankGraph() {
  const api = useApi()
  const question = ref("What is affected if system EMBARGO fails?")
  const answer = ref("")
  const intent = ref("")
  const rows = ref<any[]>([])
  const nodes = ref<Record<string, any>>({})
  const edges = ref<Record<string, any>>({})
  const loading = ref(false)

  const selectedKey = ref<string | null>(null)
  const selected = computed(() => selectedKey.value ? nodes.value[selectedKey.value] : null)
  const details = ref<NodeDetails>(null)

  const hoveredNodeKey = ref<string | null>(null)
  const hoverDetails = ref<NodeDetails>(null)
  const detailCache = new Map<string, NodeDetails>()
  let hoverSequence = 0

  function detailKey(node: any): string {
    return `${node.type}:${node.id}`
  }

  async function fetchNodeDetails(nodeKey: string): Promise<NodeDetails> {
    const node = nodes.value[nodeKey]
    if (!node?.id || !STORED_NODE_TYPES.has(node.type)) return null

    const key = detailKey(node)
    if (detailCache.has(key)) return detailCache.get(key) ?? null

    const data = await api.details(node.type, node.id)
    detailCache.set(key, data)
    return data
  }

  async function ask() {
    loading.value = true
    selectedKey.value = null
    details.value = null
    hoveredNodeKey.value = null
    hoverDetails.value = null

    try {
      const data = await api.ask(question.value)
      answer.value = data.answer
      intent.value = data.intent
      rows.value = data.rows || []
      nodes.value = data.graph?.nodes || {}
      edges.value = data.graph?.edges || {}
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown application error."
      answer.value = `Request could not be completed. ${message}`
      intent.value = "error"
      rows.value = []
      nodes.value = {}
      edges.value = {}
    } finally {
      loading.value = false
    }
  }

  async function selectNode(nodeKey: string) {
    selectedKey.value = nodeKey
    details.value = null

    try {
      details.value = await fetchNodeDetails(nodeKey)
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to load node details."
      details.value = { error: message }
    }
  }

  async function hoverNode(nodeKey: string | null) {
    const sequence = ++hoverSequence
    hoveredNodeKey.value = nodeKey
    hoverDetails.value = null
    if (!nodeKey) return

    // Avoid one network request for every node crossed quickly by the cursor.
    await new Promise(resolve => setTimeout(resolve, 140))
    if (sequence !== hoverSequence || hoveredNodeKey.value !== nodeKey) return

    try {
      const result = await fetchNodeDetails(nodeKey)
      if (sequence === hoverSequence) hoverDetails.value = result
    } catch {
      if (sequence === hoverSequence) hoverDetails.value = null
    }
  }

  return {
    question,
    answer,
    intent,
    rows,
    nodes,
    edges,
    loading,
    selectedKey,
    selected,
    details,
    hoveredNodeKey,
    hoverDetails,
    ask,
    selectNode,
    hoverNode,
  }
}
