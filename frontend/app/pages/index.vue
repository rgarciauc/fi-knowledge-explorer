<template>
  <main class="page">
    <BrandHero @explore="focusQuestion" @kpis="openKpis" />

    <QuestionPanel
      v-model="question"
      :examples="examples || []"
      :loading="loading"
      @select="selectExample"
      @ask="runQuestion"
    />

    <nav class="workspace-tabs" aria-label="Application sections">
      <button type="button" :class="{ active: activeTab === 'explorer' }" @click="activeTab = 'explorer'">
        Graph Explorer
      </button>
      <button type="button" :class="{ active: activeTab === 'kpis' }" @click="openKpis">
        KPI Dashboard
      </button>
    </nav>

    <section v-show="activeTab === 'explorer'" class="explorer">
      <section v-if="loading" class="loading-workspace" aria-live="polite" aria-busy="true">
        <div class="loading-spinner" />
        <div>
          <p class="loading-eyebrow">Preparing answer</p>
          <h2>Searching the knowledge graph…</h2>
          <p class="loading-question">{{ pendingQuestion }}</p>
          <div class="loading-steps">
            <span>Interpreting intent</span>
            <span>Retrieving evidence</span>
            <span>Preparing graph</span>
          </div>
        </div>
      </section>

      <template v-else>
        <div class="insight-grid">
          <EvidencePanel
            :answer="answer"
            :ai-explanation="aiExplanation"
            :explanation-status="explanationStatus"
            :intent="intent"
            :rows="rows"
            :query-trace="queryTrace"
          />
          <NodeDetailsPanel
            :node="selected"
            :details="details"
            :nodes="nodes"
            :edges="edges"
            :presentation="presentation"
            @select="selectNode"
            @clear="clearSelection"
            @open="openEntityDrawer"
          />
        </div>

        <GraphViewer
          :nodes="nodes"
          :edges="edges"
          :presentation="presentation"
          :selected-key="selectedKey"
          :hovered-node-key="hoveredNodeKey"
          :hover-details="hoverDetails"
          @select="selectNode"
          @hover="hoverNode"
        />
      </template>
    </section>

    <KpiDashboard
      v-show="activeTab === 'kpis'"
      :kpi="kpi"
      :loading="kpiLoading"
      :error="kpiError"
      @refresh="loadKpis"
    />

    <EntityDetailsDrawer
      :open="entityDrawerOpen"
      :node="selected"
      :details="details"
      :nodes="nodes"
      :edges="edges"
      @close="entityDrawerOpen = false"
    />
  </main>
</template>

<script setup lang="ts">
import { nextTick, ref } from "vue"
import type { KpiRecord } from "~/utils/api"

const api = useApi()
const { data: examples } = await useAsyncData("examples", () => api.examples())

const activeTab = ref<"explorer" | "kpis">("explorer")
const entityDrawerOpen = ref(false)
const kpi = ref<KpiRecord | null>(null)
const kpiLoading = ref(false)
const kpiError = ref("")

const {
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
  presentation,
  loading,
  selectedKey,
  selected,
  details,
  hoveredNodeKey,
  hoverDetails,
  ask,
  selectNode,
  clearSelection,
  hoverNode,
} = useSuperBankGraph()

function selectExample(value: string) {
  question.value = value
  void focusQuestion()
}

async function focusQuestion() {
  activeTab.value = "explorer"
  await nextTick()
  document.getElementById("graph-query")?.scrollIntoView({ behavior: "smooth", block: "center" })
  document.getElementById("graph-question-input")?.focus()
}

async function runQuestion() {
  activeTab.value = "explorer"
  entityDrawerOpen.value = false
  await ask()
}

function openEntityDrawer() {
  if (selected.value) entityDrawerOpen.value = true
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
  entityDrawerOpen.value = false
  activeTab.value = "kpis"
  if (!kpi.value) await loadKpis()
}
</script>
