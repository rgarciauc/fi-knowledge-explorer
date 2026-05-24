<template>
  <section class="kpi-surface">
    <div class="kpi-heading">
      <div>
        <p class="eyebrow">Governance coverage</p>
        <h2>KPI Dashboard</h2>
        <p class="description">Coverage calculated directly from the active Neo4j responsibility graph.</p>
      </div>
      <button type="button" class="refresh" :disabled="loading" @click="$emit('refresh')">
        {{ loading ? "Refreshing…" : "Refresh KPIs" }}
      </button>
    </div>

    <p v-if="error" class="kpi-error">{{ error }}</p>
    <div v-else-if="loading && !kpi" class="kpi-loading">Loading governance coverage…</div>

    <div v-else-if="kpi" class="kpi-grid">
      <article v-for="card in cards" :key="card.title" class="kpi-card">
        <div class="card-header">
          <span class="card-icon" :style="{ background: card.tint, color: card.color }">{{ card.icon }}</span>
          <span class="card-name">{{ card.title }}</span>
        </div>
        <div class="metric">{{ card.percent }}<span>%</span></div>
        <div class="progress" aria-hidden="true">
          <div :style="{ width: `${card.percent}%`, background: card.color }" />
        </div>
        <p><strong>{{ card.covered }}</strong> of <strong>{{ card.total }}</strong> {{ card.unit }} covered</p>
      </article>
    </div>

    <div v-if="kpi" class="kpi-footnote">
      <strong>Interpretation:</strong> system ownership is measured at team level, while process ownership and process-step responsibility are measured at employee level in the starter graph.
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue"
import type { KpiRecord } from "~/utils/api"

const props = defineProps<{
  kpi: KpiRecord | null
  loading: boolean
  error?: string
}>()

defineEmits<{ refresh: [] }>()

const cards = computed(() => {
  if (!props.kpi) return []
  return [
    {
      title: "System Owners",
      percent: props.kpi.system_owner_coverage_pct,
      covered: props.kpi.covered_systems,
      total: props.kpi.total_systems,
      unit: "systems",
      icon: "S",
      color: "#fb923c",
      tint: "rgba(251,146,60,.15)",
    },
    {
      title: "Process Owners",
      percent: props.kpi.process_owner_coverage_pct,
      covered: props.kpi.covered_processes,
      total: props.kpi.total_processes,
      unit: "processes",
      icon: "P",
      color: "#72e69b",
      tint: "rgba(114,230,155,.15)",
    },
    {
      title: "Step Responsibility",
      percent: props.kpi.step_responsibility_pct,
      covered: props.kpi.covered_steps,
      total: props.kpi.total_steps,
      unit: "steps",
      icon: "R",
      color: "#60a5fa",
      tint: "rgba(96,165,250,.15)",
    },
  ]
})
</script>

<style scoped>
.kpi-surface {
  padding: 28px;
  border: 1px solid #162a43;
  border-radius: 22px;
  background: #07111f;
  color: #e7f1fc;
}
.kpi-heading { display: flex; justify-content: space-between; align-items: start; gap: 18px; margin-bottom: 27px; }
.kpi-heading h2 { margin: 5px 0 8px; font-size: 1.7rem; }
.eyebrow { margin: 0; color: #38bdf8; text-transform: uppercase; letter-spacing: .13em; font-weight: 700; font-size: .72rem; }
.description { margin: 0; color: #8ea4be; }
.refresh {
  padding: 10px 15px; border-radius: 10px; border: 1px solid #264363;
  color: #bfeafd; background: #0e2036; cursor: pointer;
}
.refresh:disabled { opacity: .55; cursor: default; }
.kpi-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 17px; }
.kpi-card {
  border: 1px solid #172d46; border-radius: 17px; padding: 18px;
  background: #091627;
}
.card-header { display: flex; align-items: center; gap: 10px; color: #9db2ca; font-size: .88rem; font-weight: 650; }
.card-icon { width: 32px; height: 32px; border-radius: 9px; display: grid; place-items: center; font-weight: 800; }
.metric { margin: 19px 0 10px; font-size: 2.55rem; line-height: 1; font-weight: 780; letter-spacing: -.04em; }
.metric span { font-size: 1.15rem; color: #8ba2bd; margin-left: 3px; }
.progress { height: 8px; border-radius: 999px; overflow: hidden; background: #13263c; margin-bottom: 12px; }
.progress div { height: 100%; border-radius: inherit; transition: width .35s ease; }
.kpi-card p { color: #8ea4be; font-size: .82rem; margin: 0; }
.kpi-card p strong { color: #dce7f5; }
.kpi-footnote {
  margin-top: 22px; padding: 14px 16px; border-radius: 12px;
  background: #0b192c; color: #91a8c2; font-size: .84rem; line-height: 1.5;
}
.kpi-footnote strong { color: #dce7f5; }
.kpi-error { color: #fda4af; background: rgba(244,63,94,.12); border-radius: 10px; padding: 13px; }
.kpi-loading { color: #91a8c2; }
@media (max-width: 860px) {
  .kpi-heading { display: block; }
  .refresh { margin-top: 18px; }
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
