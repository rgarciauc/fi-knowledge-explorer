<template>
  <main class="page">
    <QuestionPanel
      v-model="question"
      :examples="examples || []"
      :loading="loading"
      @select="selectExample"
      @ask="runQuestion"
    />

    <nav class="workspace-tabs" aria-label="Application sections">
      <button
        type="button"
        :class="{ active: activeTab === 'explorer' }"
        @click="activeTab = 'explorer'"
      >
        Graph Explorer
      </button>
      <button
        type="button"
        :class="{ active: activeTab === 'kpis' }"
        @click="openKpis"
      >
        KPI Dashboard
      </button>
    </nav>

    <section v-show="activeTab === 'explorer'" class="explorer">
      <div class="insight-grid">
        <EvidencePanel :answer="answer" :intent="intent" :rows="rows" />
        <NodeDetailsPanel :node="selected" :details="details" />
      </div>

      <GraphViewer
        :nodes="nodes"
        :edges="edges"
        :selected-key="selectedKey"
        :hovered-node-key="hoveredNodeKey"
        :hover-details="hoverDetails"
        @select="selectNode"
        @hover="hoverNode"
      />
    </section>

    <KpiDashboard
      v-show="activeTab === 'kpis'"
      :kpi="kpi"
      :loading="kpiLoading"
      :error="kpiError"
      @refresh="loadKpis"
    />
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue"
import type { KpiRecord } from "~/utils/api"

const api = useApi()
const { data: examples } = await useAsyncData("examples", () => api.examples())

const activeTab = ref<"explorer" | "kpis">("explorer")
const kpi = ref<KpiRecord | null>(null)
const kpiLoading = ref(false)
const kpiError = ref("")

const {
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
} = useSuperBankGraph()

function selectExample(value: string) {
  question.value = value
}

async function runQuestion() {
  activeTab.value = "explorer"
  await ask()
}

async function loadKpis() {
  kpiLoading.value = true
  kpiError.value = ""
  try {
    const rows = await api.kpis()
    kpi.value = rows[0] || null
    if (!kpi.value) kpiError.value = "No KPI result was returned from Neo4j."
  } catch (error) {
    kpiError.value = error instanceof Error ? error.message : "Unable to load KPI data."
  } finally {
    kpiLoading.value = false
  }
}

async function openKpis() {
  activeTab.value = "kpis"
  if (!kpi.value) await loadKpis()
}
</script>
