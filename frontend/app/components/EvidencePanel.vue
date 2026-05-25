<template>
  <section class="panel evidence-panel" v-if="answer">
    <p class="section-label">Answer</p>
    <h2>Evidence-backed response</h2>

    <div v-if="queryTrace" class="trace-badges">
      <span class="ready">Evidence ready</span>
      <span class="method" :class="methodClass">{{ methodLabel }}</span>
      <span v-if="rows.length" class="confidence">{{ rows.length }} evidence link{{ rows.length === 1 ? "" : "s" }}</span>
    </div>

    <div class="summary-block">
      <p class="answer-title">Immediate graph summary</p>
      <p class="answer" :class="{ error: intent === 'error' }">{{ answer }}</p>
    </div>

    <div v-if="intent !== 'error' && explanationStatus !== 'skipped'" class="ai-block" :class="explanationStatus">
      <div class="ai-header">
        <p class="answer-title">AI explanation</p>
        <span v-if="explanationStatus === 'generating'" class="stream-status"><i /> Generating</span>
        <span v-else-if="explanationStatus === 'complete'" class="done-status">Complete</span>
        <span v-else-if="explanationStatus === 'unavailable'" class="failed-status">Unavailable</span>
      </div>
      <p v-if="aiExplanation" class="ai-answer">{{ aiExplanation }}<span v-if="explanationStatus === 'generating'" class="cursor" /></p>
      <p v-else-if="explanationStatus === 'generating'" class="ai-waiting">Preparing a grounded explanation from the retrieved evidence…</p>
      <p v-else-if="explanationStatus === 'unavailable'" class="ai-waiting">
        The evidence summary and interactive graph remain available.
      </p>
    </div>

    <p v-if="queryTrace?.corrected_question && queryTrace.corrected_question !== queryTrace.resolved_term" class="interpretation">
      Interpreted question: <strong>{{ queryTrace.corrected_question }}</strong>
    </p>

    <details v-if="queryTrace" class="diagnostic">
      <summary>Show query details</summary>
      <div class="diagnostic-body">
        <dl>
          <dt>Method</dt><dd>{{ methodLabel }}</dd>
          <dt>Intent</dt><dd>{{ queryTrace.interpreted_intent }}</dd>
          <dt v-if="queryTrace.resolved_term">Resolved term</dt><dd v-if="queryTrace.resolved_term">{{ queryTrace.resolved_term }}</dd>
          <dt v-if="queryTrace.fallback_reason">Reason</dt><dd v-if="queryTrace.fallback_reason">{{ queryTrace.fallback_reason }}</dd>
        </dl>
        <div v-if="queryTrace.entity_candidates?.length" class="candidates">
          <p>Entity matches considered</p>
          <div v-for="candidate in queryTrace.entity_candidates" :key="`${candidate.label}:${candidate.node_id}`">
            <strong>{{ candidate.name }}</strong>
            <span>{{ candidate.label }} · {{ Math.round(candidate.score * 100) }}% match</span>
          </div>
        </div>
        <div v-if="queryTrace.generated_cypher" class="generated">
          <p>Validated generated read-only query</p>
          <pre>{{ queryTrace.generated_cypher }}</pre>
        </div>
      </div>
    </details>

    <details v-if="rows.length">
      <summary>Raw graph evidence ({{ rows.length }})</summary>
      <pre>{{ JSON.stringify(rows, null, 2) }}</pre>
    </details>
  </section>

  <section v-else class="panel evidence-placeholder">
    <p class="section-label">Answer</p>
    <p>Ask a question to retrieve graph evidence and receive an AI-supported explanation.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{
  answer: string
  aiExplanation?: string
  explanationStatus?: "idle" | "generating" | "complete" | "unavailable" | "skipped"
  intent: string
  rows: any[]
  queryTrace?: any
}>()

const methodLabel = computed(() => {
  const method = props.queryTrace?.query_method
  const labels: Record<string, string> = {
    fast_concept_definition: "Instant concept explanation",
    approved_template_v2: "Approved bank-model query",
    approved_template: "Approved query",
    global_search: "Broad graph search",
    global_search_after_empty_template: "Broad search fallback",
    validated_generated_read: "Validated exploratory query",
    validated_generated_read_after_empty_retrieval: "Validated exploratory fallback",
    global_search_after_generated_query: "Broad search after exploratory query",
    clarification_with_related_evidence: "Clarification evidence",
  }
  return labels[method] || method || "Graph retrieval"
})

const methodClass = computed(() => {
  const method = props.queryTrace?.query_method || ""
  if (method.includes("generated")) return "generated"
  if (method.includes("global") || method.includes("clarification")) return "fallback"
  return "template"
})
</script>

<style scoped>
.section-label { margin: 0 0 12px; color: #7089a7; font-size: .7rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h2 { font-size: 1.14rem; color: #eef5fd; margin: 0 0 14px; }
.trace-badges { display:flex; flex-wrap:wrap; gap:7px; margin-bottom:15px; }
.trace-badges span { padding:6px 10px; border-radius:999px; font-size:.73rem; font-weight:650; }
.ready { color:#84f0c5; background:rgba(45,212,191,.14); border:1px solid rgba(45,212,191,.24); }
.method.template { color:#93c5fd; background:rgba(96,165,250,.13); border:1px solid rgba(96,165,250,.25); }
.method.fallback { color:#fde68a; background:rgba(250,204,21,.12); border:1px solid rgba(250,204,21,.22); }
.method.generated { color:#c4b5fd; background:rgba(196,181,253,.13); border:1px solid rgba(196,181,253,.24); }
.confidence { color:#abc1d9; background:#102138; border:1px solid #19304a; }
.answer-title { margin:0 0 8px; color:#7996b5; font-size:.71rem; font-weight:750; letter-spacing:.12em; text-transform:uppercase; }
.summary-block { padding:13px 14px; border-radius:12px; background:#091a2e; border:1px solid #15304c; margin-bottom:13px; }
.answer { color:#d6e4f3; line-height:1.6; margin:0; }
.answer.error { color:#fda4af; }
.ai-block { padding:13px 14px; border-radius:12px; border:1px solid #163149; background:#071727; margin-bottom:14px; }
.ai-block.complete { border-color:rgba(45,212,191,.25); }
.ai-block.unavailable { border-color:rgba(251,191,36,.22); }
.ai-header { display:flex; justify-content:space-between; align-items:center; gap:10px; }
.stream-status,.done-status,.failed-status { font-size:.72rem; padding:4px 8px; border-radius:999px; }
.stream-status { color:#7dd3fc; background:rgba(56,189,248,.12); }
.stream-status i { display:inline-block; width:6px; height:6px; border-radius:50%; background:#38bdf8; animation:pulse 1s infinite; }
.done-status { color:#84f0c5; background:rgba(45,212,191,.12); }
.failed-status { color:#fde68a; background:rgba(250,204,21,.12); }
.ai-answer,.ai-waiting { color:#c3d4e6; line-height:1.62; white-space:pre-wrap; margin:10px 0 0; }
.ai-waiting { color:#8ca5c1; }
.cursor { display:inline-block; width:7px; height:1.05em; margin-left:3px; background:#38bdf8; vertical-align:-2px; animation:blink .8s steps(2) infinite; }
.interpretation { margin:0 0 15px; padding:10px 12px; color:#98b2cf; font-size:.82rem; border-left:2px solid #38bdf8; background:rgba(14,32,54,.55); }
.interpretation strong { color:#d8e7f5; }
details { color:#aabed5; font-size:.82rem; margin-top:10px; }
summary { cursor:pointer; margin-bottom:10px; }
.diagnostic { padding:10px 12px; border:1px solid #162c46; border-radius:11px; background:#081522; }
.diagnostic-body dl { display:grid; grid-template-columns:120px 1fr; gap:7px 12px; margin:8px 0 14px; font-size:.8rem; }
.diagnostic-body dt { color:#7290af; }
.diagnostic-body dd { margin:0; color:#d3e1f0; }
.candidates,.generated { border-top:1px solid #152a43; padding-top:12px; margin-top:8px; }
.candidates p,.generated p { margin:0 0 9px; color:#7894b2; font-size:.74rem; text-transform:uppercase; letter-spacing:.08em; }
.candidates div { display:flex; gap:9px; align-items:baseline; margin:5px 0; }
.candidates div span { color:#7f98b6; }
pre { max-height:270px; }
.evidence-placeholder { color:#91a8c2; display:flex; flex-direction:column; justify-content:center; }
.evidence-placeholder p:last-child { margin:0; line-height:1.5; }
@keyframes blink { 50% { opacity:0; } }
@keyframes pulse { 50% { opacity:.35; } }
</style>
