<template>
  <section class="panel">
    <h1>SUPER_BANK Responsibility Graph</h1>
    <p class="subtitle">
      Ask about teams, employees, systems, business processes, pipelines and affected data flows.
    </p>
    <div class="examples">
      <button v-for="example in examples" :key="example" type="button" @click="$emit('select', example)">
        {{ example }}
      </button>
    </div>
    <textarea :value="modelValue" rows="3" placeholder="Ask a governance question..." @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)" />
    <button class="ask" type="button" :disabled="loading" @click="$emit('ask')">
      {{ loading ? "Searching graph..." : "Ask" }}
    </button>
  </section>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ modelValue: string; loading: boolean; examples?: string[] }>(), {
  examples: () => [
    "Who owns system EMBARGO?",
    "Who is responsible for Sanctions Screening?",
    "What is affected if system EMBARGO fails?",
    "Show the pipeline for Payment Processing",
    "Show missing system owners",
    "Show KPI summary",
  ],
})
defineEmits(["update:modelValue", "ask", "select"])
</script>
