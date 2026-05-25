import type { NodeDetails } from "~/utils/graphPresentation"
import { STORED_NODE_TYPES } from "~/utils/graphPresentation"

type ExplanationStatus = "idle" | "generating" | "complete" | "unavailable" | "skipped"

export function useSuperBankGraph() {
  const api = useApi()
  const question = ref("Show the end-to-end payment flow and explain where a payment can be blocked.")
  const pendingQuestion = ref("")
  const answer = ref("")
  const aiExplanation = ref("")
  const explanationStatus = ref<ExplanationStatus>("idle")
  const intent = ref("")
  const rows = ref<any[]>([])
  const queryTrace = ref<any>(null)
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
  let activeRequest: AbortController | null = null

  function detailKey(node: any): string {
    return `${node.type}:${node.id}`
  }

  function clearResult() {
    answer.value = ""
    aiExplanation.value = ""
    explanationStatus.value = "idle"
    intent.value = ""
    rows.value = []
    queryTrace.value = null
    nodes.value = {}
    edges.value = {}
    selectedKey.value = null
    details.value = null
    hoveredNodeKey.value = null
    hoverDetails.value = null
    detailCache.clear()
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
    const submitted = question.value.trim()
    if (!submitted) return

    activeRequest?.abort()
    activeRequest = new AbortController()
    pendingQuestion.value = submitted
    loading.value = true
    clearResult()

    try {
      await api.askStream(
        submitted,
        {
          evidenceReady(data) {
            answer.value = data.answer || ""
            intent.value = data.intent || ""
            rows.value = data.rows || []
            queryTrace.value = data.query_trace || null
            nodes.value = data.graph?.nodes || {}
            edges.value = data.graph?.edges || {}
            explanationStatus.value = data.llm_status === "generating" ? "generating" : "skipped"
            loading.value = false
            pendingQuestion.value = ""
          },
          answerDelta(data) {
            explanationStatus.value = "generating"
            aiExplanation.value += data.delta
          },
          answerComplete(data) {
            explanationStatus.value = data.llm_status === "available" ? "complete" : "skipped"
            if (data.answer_ai && !aiExplanation.value) aiExplanation.value = data.answer_ai
          },
          answerError(data) {
            explanationStatus.value = "unavailable"
            if (!aiExplanation.value) aiExplanation.value = data.message
          },
        },
        activeRequest.signal,
      )
    } catch (error: any) {
      if (error?.name === "AbortError") return
      const message = error instanceof Error ? error.message : "Unknown application error."
      answer.value = `Request could not be completed. ${message}`
      intent.value = "error"
      explanationStatus.value = "unavailable"
      loading.value = false
      pendingQuestion.value = ""
    }
  }

  async function selectNode(nodeKey: string) {
    selectedKey.value = nodeKey
    details.value = null
    try {
      details.value = await fetchNodeDetails(nodeKey)
    } catch (error) {
      const diagnostic = error instanceof Error ? error.message : "Unable to load node details."
      details.value = {
        error: "Detailed properties are temporarily unavailable for this node. Its graph connections remain visible.",
        diagnostic,
      } as any
    }
  }

  async function hoverNode(nodeKey: string | null) {
    const sequence = ++hoverSequence
    hoveredNodeKey.value = nodeKey
    hoverDetails.value = null
    if (!nodeKey) return
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
    pendingQuestion,
    answer,
    aiExplanation,
    explanationStatus,
    intent,
    rows,
    queryTrace,
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
