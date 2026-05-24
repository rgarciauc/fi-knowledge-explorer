<template>
  <section class="panel evidence-panel" v-if="answer">
    <p class="section-label">Answer</p>
    <h2>Graph explanation</h2>
    <p class="answer" :class="{ error: intent === 'error' }">{{ answer }}</p>
    <div class="answer-meta">
      <span>Intent: {{ intent }}</span>
      <span v-if="rows.length">{{ rows.length }} evidence row{{ rows.length === 1 ? "" : "s" }}</span>
    </div>
    <details v-if="rows.length">
      <summary>Raw graph evidence</summary>
      <pre>{{ JSON.stringify(rows, null, 2) }}</pre>
    </details>
  </section>
  <section v-else class="panel evidence-placeholder">
    <p class="section-label">Answer</p>
    <p>Ask a question to retrieve graph evidence and explore the connected entities.</p>
  </section>
</template>

<script setup lang="ts">
defineProps<{ answer: string; intent: string; rows: any[] }>()
</script>

<style scoped>
.section-label { margin: 0 0 12px; color: #7089a7; font-size: .7rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h2 { font-size: 1.14rem; color: #eef5fd; margin: 0 0 14px; }
.answer { color: #c7d6e7; line-height: 1.58; margin: 0 0 16px; }
.answer.error { color: #fda4af; }
.answer-meta { display: flex; gap: 13px; font-size: .75rem; color: #7290af; margin-bottom: 14px; }
.answer-meta span { border-radius: 999px; padding: 5px 9px; background: #102138; }
details { color: #aabed5; font-size: .82rem; }
summary { cursor: pointer; margin-bottom: 10px; }
pre { max-height: 270px; }
.evidence-placeholder { color: #91a8c2; display: flex; flex-direction: column; justify-content: center; }
.evidence-placeholder p:last-child { margin: 0; line-height: 1.5; }
</style>
