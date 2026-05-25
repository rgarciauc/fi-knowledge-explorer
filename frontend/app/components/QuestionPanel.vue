<template>
  <section id="graph-query" class="query-panel" aria-labelledby="query-title">
    <div class="query-heading">
      <div>
        <p class="eyebrow">ASK THE GRAPH</p>
        <h2 id="query-title">Investigate evidence</h2>
        <p class="subtitle">Evidence appears first. A grounded AI explanation follows without blocking exploration.</p>
      </div>
      <span class="shortcut">⌘ / Ctrl + Enter</span>
    </div>

    <div class="examples" aria-label="Suggested questions">
      <button v-for="example in examples" :key="example" type="button" @click="$emit('select', example)">
        {{ example }}
      </button>
    </div>

    <div class="composer">
      <textarea
        id="graph-question-input"
        :value="modelValue"
        rows="2"
        placeholder="Ask about a process, affected system, owner, team or regulatory dependency…"
        @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        @keydown.meta.enter.prevent="$emit('ask')"
        @keydown.ctrl.enter.prevent="$emit('ask')"
      />
      <button type="button" :disabled="loading || !modelValue.trim()" @click="$emit('ask')">
        <span v-if="loading" class="spinner" />
        {{ loading ? "Searching…" : "Ask graph" }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ modelValue: string; loading: boolean; examples?: string[] }>(), {
  examples: () => [],
})
defineEmits(["update:modelValue", "ask", "select"])
</script>

<style scoped>
.query-panel {
  padding: 20px 23px 22px;
  border: 1px solid #162a43;
  border-radius: 18px;
  background: #07111f;
}
.query-heading {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 20px;
}
.eyebrow {
  margin: 0 0 7px;
  color: #38bdf8;
  font-size: .67rem;
  font-weight: 750;
  letter-spacing: .18em;
}
h2 {
  margin: 0 0 5px;
  color: #edf4fc;
  font-size: 1.16rem;
  letter-spacing: -.02em;
}
.subtitle {
  margin: 0;
  color: #89a4bf;
  font-size: .82rem;
  line-height: 1.45;
}
.shortcut {
  flex: 0 0 auto;
  padding: 7px 9px;
  border: 1px solid #1c3650;
  border-radius: 8px;
  color: #718da8;
  background: #091a2d;
  font-size: .7rem;
}
.examples { display: flex; flex-wrap: wrap; gap: 7px; margin: 17px 0 14px; }
.examples button {
  max-width: 100%;
  border: 1px solid #1d3956;
  background: #0a1b30;
  color: #acc3d9;
  padding: 7px 11px;
  border-radius: 999px;
  font-size: .76rem;
  cursor: pointer;
}
.examples button:hover { border-color: #38bdf8; color: #ebf5fd; }
.composer { display: flex; gap: 10px; align-items: stretch; }
textarea {
  resize: vertical;
  flex: 1;
  min-height: 57px;
  border: 1px solid #203b59;
  background: #050e1b;
  border-radius: 12px;
  color: #e1ebf7;
  font: inherit;
  font-size: .9rem;
  padding: 12px 13px;
  outline: none;
}
textarea:focus { border-color: #38bdf8; box-shadow: 0 0 0 3px rgba(56,189,248,.1); }
.composer > button {
  min-width: 126px;
  border: 0;
  border-radius: 12px;
  background: #38bdf8;
  color: #04111f;
  font-weight: 740;
  cursor: pointer;
}
.composer > button:disabled { opacity: .48; cursor: default; }
.spinner {
  display: inline-block; width: 13px; height: 13px; margin-right: 6px;
  border: 2px solid rgba(4,17,31,.27); border-top-color: #04111f;
  border-radius: 50%; animation: spin .8s linear infinite; vertical-align: -2px;
}
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 700px) {
  .query-heading { display: block; }
  .shortcut { display: inline-block; margin-top: 12px; }
  .composer { display: block; }
  .composer > button { width: 100%; padding: 14px; margin-top: 10px; }
}
</style>
