<template>
  <section class="panel evidence-panel" v-if="answer">
    <p class="section-label">Answer</p>
    <h2>Graph explanation</h2>

    <div v-if="queryTrace" class="trace-badges">
      <span class="method" :class="methodClass">{{ methodLabel }}</span>
      <span v-if="typeof queryTrace.confidence === 'number'" class="confidence">
        {{ Math.round(queryTrace.confidence * 100) }}% intent confidence
      </span>
      <span v-if="queryTrace.resolved_term" class="entity">
        Matched: {{ queryTrace.resolved_term }}
      </span>
    </div>

    <p class="answer" :class="{ error: intent === 'error' }">{{ answer }}</p>

    <p v-if="queryTrace?.corrected_question && queryTrace.corrected_question !== queryTrace.resolved_term" class="interpretation">
      Interpreted question: <strong>{{ queryTrace.corrected_question }}</strong>
    </p>

    <div class="answer-meta">
      <span>Intent: {{ intent }}</span>
      <span v-if="rows.length">{{ rows.length }} evidence row{{ rows.length === 1 ? "" : "s" }}</span>
      <span v-if="queryTrace?.fallback_reason">Fallback used</span>
    </div>

    <details v-if="queryTrace" class="diagnostic">
      <summary>How this answer was retrieved</summary>
      <div class="diagnostic-body">
        <dl>
          <dt>Method</dt>
          <dd>{{ methodLabel }}</dd>
          <dt>Interpreted intent</dt>
          <dd>{{ queryTrace.interpreted_intent }}</dd>
          <dt v-if="queryTrace.resolved_term">Resolved term</dt>
          <dd v-if="queryTrace.resolved_term">{{ queryTrace.resolved_term }}</dd>
          <dt v-if="queryTrace.fallback_reason">Reason</dt>
          <dd v-if="queryTrace.fallback_reason">{{ queryTrace.fallback_reason }}</dd>
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
          <ul v-if="queryTrace.generated_query_validation?.length">
            <li v-for="item in queryTrace.generated_query_validation" :key="item">{{ item }}</li>
          </ul>
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
    <p>Ask a question to retrieve graph evidence and explore the connected entities.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue"

const props = defineProps<{
  answer: string
  intent: string
  rows: any[]
  queryTrace?: any
}>()

const methodLabel = computed(() => {
  const method = props.queryTrace?.query_method
  const labels: Record<string, string> = {
    fast_concept_definition: "Instant concept explanation",
    approved_template_v2: "Approved bank-model v2 query",
    approved_template: "Approved query template",
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
  if (method === "fast_concept_definition") return "template"
  if (method.includes("generated")) return "generated"
  if (method.includes("global") || method.includes("clarification")) return "fallback"
  return "template"
})
</script>

<style scoped>
.section-label { margin: 0 0 12px; color: #7089a7; font-size: .7rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h2 { font-size: 1.14rem; color: #eef5fd; margin: 0 0 14px; }
.trace-badges { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 15px; }
.trace-badges span { padding: 6px 10px; border-radius: 999px; font-size: .73rem; font-weight: 650; }
.method.template { color: #84f0c5; background: rgba(45,212,191,.14); border: 1px solid rgba(45,212,191,.24); }
.method.fallback { color: #fde68a; background: rgba(250,204,21,.12); border: 1px solid rgba(250,204,21,.22); }
.method.generated { color: #93c5fd; background: rgba(96,165,250,.13); border: 1px solid rgba(96,165,250,.25); }
.confidence, .entity { color: #abc1d9; background: #102138; border: 1px solid #19304a; }
.answer { color: #c7d6e7; line-height: 1.58; margin: 0 0 16px; }
.answer.error { color: #fda4af; }
.interpretation {
  margin: 0 0 15px; padding: 10px 12px; color: #98b2cf; font-size: .82rem;
  border-left: 2px solid #38bdf8; background: rgba(14,32,54,.55);
}
.interpretation strong { color: #d8e7f5; }
.answer-meta { display: flex; flex-wrap: wrap; gap: 8px; font-size: .75rem; color: #7290af; margin-bottom: 14px; }
.answer-meta span { border-radius: 999px; padding: 5px 9px; background: #102138; }
details { color: #aabed5; font-size: .82rem; margin-top: 10px; }
summary { cursor: pointer; margin-bottom: 10px; }
.diagnostic { padding: 10px 12px; border: 1px solid #162c46; border-radius: 11px; background: #081522; }
.diagnostic-body dl {
  display: grid; grid-template-columns: 120px 1fr; gap: 7px 12px;
  margin: 8px 0 14px; font-size: .8rem;
}
.diagnostic-body dt { color: #7290af; }
.diagnostic-body dd { margin: 0; color: #d3e1f0; }
.candidates { border-top: 1px solid #152a43; padding-top: 12px; margin-top: 8px; }
.candidates p, .generated p { margin: 0 0 9px; color: #7894b2; font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; }
.candidates div { display: flex; gap: 9px; align-items: baseline; margin: 5px 0; }
.candidates div span { color: #7f98b6; }
.generated { border-top: 1px solid #152a43; margin-top: 12px; padding-top: 12px; }
.generated ul { margin: 8px 0 0; color: #8ca5c1; padding-left: 18px; }
pre { max-height: 270px; }
.evidence-placeholder { color: #91a8c2; display: flex; flex-direction: column; justify-content: center; }
.evidence-placeholder p:last-child { margin: 0; line-height: 1.5; }
</style>
