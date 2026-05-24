<template>
  <section class="query-panel">
    <div class="query-copy">
      <p class="eyebrow">SUPER_BANK</p>
      <h1>Responsibility Graph</h1>
      <p class="subtitle">
        Ask about teams, employees, systems, processes, pipelines and downstream impact.
      </p>
    </div>
    <div class="examples">
      <button v-for="example in examples" :key="example" type="button" @click="$emit('select', example)">
        {{ example }}
      </button>
    </div>
    <div class="composer">
      <textarea
        :value="modelValue"
        rows="2"
        placeholder="Ask a governance question…"
        @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        @keydown.meta.enter.prevent="$emit('ask')"
        @keydown.ctrl.enter.prevent="$emit('ask')"
      />
      <button type="button" :disabled="loading || !modelValue.trim()" @click="$emit('ask')">
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
  padding: 30px 31px 27px;
  border: 1px solid #162a43;
  border-radius: 22px;
  background: linear-gradient(115deg, #091a30, #07111f 57%, #061422);
  box-shadow: 0 18px 52px rgba(2, 6, 23, .23);
}
.eyebrow { color: #38bdf8; font-size: .72rem; font-weight: 750; letter-spacing: .18em; margin: 0 0 8px; }
h1 { color: #f1f6fd; font-size: 2.2rem; margin: 0 0 9px; letter-spacing: -.04em; }
.subtitle { color: #93abc5; max-width: 660px; line-height: 1.5; margin: 0; }
.examples { display: flex; flex-wrap: wrap; gap: 8px; margin: 22px 0 18px; }
.examples button {
  border: 1px solid #203b59; background: #0d2036; color: #b8cde2;
  padding: 8px 12px; border-radius: 999px; font-size: .8rem; cursor: pointer;
}
.examples button:hover { border-color: #38bdf8; color: #e7f5fd; }
.composer { display: flex; gap: 11px; align-items: stretch; }
textarea {
  resize: vertical; flex: 1; min-height: 58px; border: 1px solid #203b59;
  background: #06101e; border-radius: 12px; color: #e1ebf7;
  font: inherit; font-size: .92rem; padding: 13px 14px; outline: none;
}
textarea:focus { border-color: #38bdf8; }
.composer button {
  min-width: 126px; border: 0; border-radius: 12px;
  background: #38bdf8; color: #04111f; font-weight: 740; cursor: pointer;
}
.composer button:disabled { opacity: .48; cursor: default; }
@media (max-width: 700px) {
  .query-panel { padding: 22px; }
  .composer { display: block; }
  .composer button { width: 100%; padding: 14px; margin-top: 10px; }
}
</style>
