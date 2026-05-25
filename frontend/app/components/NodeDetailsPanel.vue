<template>
  <section class="panel explorer-panel" aria-label="Entity explorer panel">
    <div class="panel-head">
      <div>
        <p class="section-label">Explorer panel</p>
        <h2>{{ node ? "Entity context" : "Inspect graph entities" }}</h2>
      </div>
      <button v-if="node" type="button" class="clear-action" @click="emit('clear')">Clear</button>
    </div>

    <template v-if="node">
      <div class="node-heading">
        <span class="node-dot" :style="{ background: nodeColor(node.type) }" />
        <div>
          <h3>{{ node.name }}</h3>
          <p class="muted">{{ nodeTypeLabel(node.type) }} · {{ node.degree || 0 }} visible connection{{ node.degree === 1 ? "" : "s" }}</p>
        </div>
      </div>

      <div v-if="details?.error" class="detail-warning">
        <p>{{ details.error }}</p>
        <details v-if="details.diagnostic">
          <summary>Diagnostic details</summary>
          <p>{{ details.diagnostic }}</p>
        </details>
      </div>

      <div v-else-if="!details" class="detail-loading">
        <span class="loading-bar" />
        <p>Loading recorded context…</p>
      </div>

      <template v-else>
        <div class="resolution">
          <span v-if="details.stable_id">Stored ID: {{ details.stable_id }}</span>
          <span v-if="details.matched_by === 'stable_id'" class="ok">Verified entity</span>
          <span v-else-if="details.matched_by === 'exact_name_fallback'" class="fallback">Resolved by name</span>
        </div>

        <p class="summary">{{ nodeSummary(node, details) }}</p>

        <dl v-if="properties.length" class="property-grid">
          <template v-for="property in properties" :key="property.key">
            <dt>{{ property.key }}</dt>
            <dd>{{ property.value }}</dd>
          </template>
        </dl>

        <div v-if="visibleNeighbours.length" class="connected">
          <div class="connected-head">
            <h4>Visible connections</h4>
            <span>{{ visibleNeighbours.length }}</span>
          </div>
          <button
            v-for="item in visibleNeighbours.slice(0, 5)"
            :key="item.key"
            type="button"
            class="connected-row"
            @click="emit('select', item.key)"
          >
            <span class="mini-dot" :style="{ background: nodeColor(item.node.type) }" />
            <span>
              <strong>{{ item.node.name }}</strong>
              <small>{{ humanize(item.relationship) }} · {{ nodeTypeLabel(item.node.type) }}</small>
            </span>
          </button>
        </div>

        <button type="button" class="open-detail" @click="emit('open')">
          Open full details
          <span aria-hidden="true">→</span>
        </button>
      </template>
    </template>

    <template v-else>
      <p class="empty-copy">
        Click any node to inspect its ownership, relationships and operational context.
        Hover remains available for a quick preview.
      </p>

      <div v-if="nodeCount" class="graph-overview">
        <div class="overview-stat">
          <strong>{{ nodeCount }}</strong>
          <span>visible nodes</span>
        </div>
        <div class="overview-stat">
          <strong>{{ edgeCount }}</strong>
          <span>relationships</span>
        </div>
        <div class="overview-stat view">
          <strong>{{ layoutLabel }}</strong>
          <span>current view</span>
        </div>
      </div>

      <div v-if="suggestedNodes.length" class="suggestions">
        <div class="suggestion-head">
          <h4>Start with a key entity</h4>
          <span>Most connected</span>
        </div>
        <button
          v-for="item in suggestedNodes"
          :key="item.key"
          type="button"
          class="suggested-node"
          @click="emit('select', item.key)"
        >
          <span class="node-dot small" :style="{ background: nodeColor(item.node.type) }" />
          <span class="suggested-copy">
            <strong>{{ item.node.name }}</strong>
            <small>{{ nodeTypeLabel(item.node.type) }} · {{ item.node.degree || 0 }} links</small>
          </span>
        </button>
      </div>

      <div v-else class="start-guide">
        <p class="guide-title">How to explore</p>
        <div><span>01</span>Ask a banking governance question.</div>
        <div><span>02</span>Inspect the evidence graph and summary.</div>
        <div><span>03</span>Select an entity for recorded context.</div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { nodeColor, nodeSummary, nodeTypeLabel, type GraphEdge, type GraphNode, type NodeDetails } from "~/utils/graphPresentation"

const props = defineProps<{
  node: GraphNode | null
  details: NodeDetails
  nodes?: Record<string, GraphNode>
  edges?: Record<string, GraphEdge>
  presentation?: { layout_mode?: string; root_key?: string | null } | null
}>()

const emit = defineEmits<{
  clear: []
  open: []
  select: [nodeKey: string]
}>()

const allNodes = computed(() => props.nodes || {})
const allEdges = computed(() => props.edges || {})
const nodeCount = computed(() => Object.keys(allNodes.value).length)
const edgeCount = computed(() => Object.keys(allEdges.value).length)
const layoutLabel = computed(() => ({
  ordered_flow: "Process flow",
  radial_impact: "Impact radius",
  accountability: "Accountability",
  network: "Network",
}[props.presentation?.layout_mode || "network"] || "Network"))

const properties = computed(() => {
  if (!props.details?.properties) return []
  const excluded = new Set(["name", "description", "task_summary"])
  return Object.entries(props.details.properties)
    .filter(([key, value]) => !excluded.has(key) && value !== null && value !== "")
    .slice(0, 6)
    .map(([key, value]) => ({
      key: key.replaceAll("_", " "),
      value: String(value),
    }))
})

const selectedKey = computed(() => {
  if (!props.node) return null
  return Object.entries(allNodes.value).find(([, node]) => node === props.node)?.[0]
    || Object.entries(allNodes.value).find(([, node]) => node.id === props.node?.id && node.type === props.node?.type)?.[0]
    || null
})

const visibleNeighbours = computed(() => {
  const key = selectedKey.value
  if (!key) return []
  const items: Array<{ key: string; node: GraphNode; relationship: string }> = []
  for (const edge of Object.values(allEdges.value)) {
    const neighbourKey = edge.source === key ? edge.target : edge.target === key ? edge.source : null
    const neighbour = neighbourKey ? allNodes.value[neighbourKey] : undefined
    if (neighbourKey && neighbour) {
      items.push({ key: neighbourKey, node: neighbour, relationship: edge.label || "RELATED_TO" })
    }
  }
  return items
    .sort((left, right) => (right.node.degree || 0) - (left.node.degree || 0))
    .filter((item, index, list) => list.findIndex(other => other.key === item.key) === index)
})

const suggestedNodes = computed(() =>
  Object.entries(allNodes.value)
    .map(([key, node]) => ({ key, node }))
    .sort((left, right) => (right.node.degree || 0) - (left.node.degree || 0))
    .slice(0, 3),
)

function humanize(value: string): string {
  return value.toLowerCase().replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase())
}
</script>

<style scoped>
.explorer-panel { min-height: 100%; }
.panel-head { display:flex; justify-content:space-between; align-items:start; gap:12px; margin-bottom:17px; }
.section-label { margin:0 0 7px; color:#38bdf8; font-size:.67rem; font-weight:750; letter-spacing:.16em; text-transform:uppercase; }
.panel-head h2 { margin:0; color:#edf4fc; font-size:1.13rem; letter-spacing:-.02em; }
.clear-action {
  border:1px solid #1d3854; background:#091a2d; color:#90aac4;
  border-radius:8px; padding:7px 10px; cursor:pointer; font-size:.74rem;
}
.clear-action:hover { border-color:#38bdf8; color:#e6f2fb; }
.node-heading { display:flex; gap:12px; align-items:start; }
.node-dot { flex:0 0 auto; height:14px; width:14px; margin-top:7px; border-radius:50%; box-shadow:0 0 13px rgba(56,189,248,.32); }
.node-dot.small { margin-top:3px; width:10px; height:10px; }
.node-heading h3 { font-size:1.1rem; margin:0 0 4px; color:#edf4fc; }
.node-heading .muted { margin:0; }
.resolution { display:flex; flex-wrap:wrap; gap:7px; margin:16px 0 0; }
.resolution span { padding:5px 9px; border-radius:999px; background:#102138; color:#93abc5; font-size:.7rem; }
.resolution .ok { color:#84f0c5; background:rgba(45,212,191,.14); border:1px solid rgba(45,212,191,.24); }
.resolution .fallback { color:#fde68a; background:rgba(250,204,21,.12); border:1px solid rgba(250,204,21,.22); }
.summary { margin:15px 0; line-height:1.55; color:#c1d0e2; font-size:.86rem; }
.property-grid {
  display:grid; grid-template-columns:minmax(94px,.75fr) 1.35fr; gap:8px 11px;
  margin:15px 0 0; padding-top:13px; border-top:1px solid #182d47; font-size:.78rem;
}
.property-grid dt { text-transform:capitalize; color:#7089a7; }
.property-grid dd { margin:0; color:#dbe7f4; word-break:break-word; }
.connected { margin-top:17px; border-top:1px solid #182d47; padding-top:13px; }
.connected-head, .suggestion-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:9px; }
.connected-head h4, .suggestion-head h4 { margin:0; font-size:.77rem; color:#b6c9dd; text-transform:uppercase; letter-spacing:.08em; }
.connected-head span, .suggestion-head span { color:#728ca7; font-size:.7rem; }
.connected-row {
  display:flex; align-items:start; width:100%; gap:9px; padding:8px 6px;
  border:0; border-radius:9px; background:transparent; color:#dbe8f5; text-align:left; cursor:pointer;
}
.connected-row:hover { background:#0d1e32; }
.mini-dot { flex:0 0 auto; width:8px; height:8px; margin-top:6px; border-radius:50%; }
.connected-row strong { display:block; font-size:.8rem; font-weight:610; }
.connected-row small { display:block; margin-top:3px; color:#7894af; font-size:.69rem; }
.open-detail {
  display:flex; justify-content:space-between; width:100%; margin-top:18px;
  border:1px solid #1f405e; background:#0c2035; color:#bfe6f5;
  border-radius:10px; padding:11px 13px; font-size:.8rem; font-weight:680; cursor:pointer;
}
.open-detail:hover { border-color:#38bdf8; color:#edf7fd; }
.empty-copy { color:#9aafc6; font-size:.86rem; line-height:1.55; margin:0 0 17px; }
.graph-overview { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:17px; }
.overview-stat {
  padding:12px; border:1px solid #162c45; border-radius:10px; background:#081727;
}
.overview-stat.view { grid-column:1 / -1; }
.overview-stat strong { display:block; color:#e7f3fb; font-size:1.14rem; margin-bottom:3px; }
.overview-stat.view strong { font-size:.89rem; color:#72dfda; }
.overview-stat span { color:#738ea9; font-size:.69rem; text-transform:uppercase; letter-spacing:.08em; }
.suggestions { border-top:1px solid #182d47; padding-top:13px; }
.suggested-node {
  display:flex; width:100%; gap:10px; align-items:start; padding:9px 7px;
  background:transparent; border:0; border-radius:9px; color:#dce8f5; cursor:pointer; text-align:left;
}
.suggested-node:hover { background:#0d1e32; }
.suggested-copy strong { display:block; font-size:.84rem; font-weight:620; }
.suggested-copy small { display:block; color:#7894af; font-size:.7rem; margin-top:3px; }
.start-guide { margin-top:8px; padding:14px; border-radius:12px; background:#09192b; border:1px solid #142b44; }
.guide-title { margin:0 0 10px; color:#bdcee0; font-size:.78rem; font-weight:670; }
.start-guide div { display:flex; align-items:center; gap:9px; color:#8ea7c1; font-size:.78rem; padding:5px 0; }
.start-guide div span {
  width:23px; height:23px; display:grid; place-items:center; border-radius:50%;
  background:#0d243a; color:#38bdf8; font-size:.68rem; font-weight:720;
}
.detail-loading { margin-top:16px; color:#7894af; font-size:.79rem; }
.detail-loading p { margin:8px 0 0; }
.loading-bar {
  display:block; height:5px; width:88px; border-radius:999px;
  background:linear-gradient(90deg, #0e2439, #38bdf8, #0e2439);
  background-size:170% auto; animation:loading 1.2s linear infinite;
}
.detail-warning {
  margin-top:18px; padding:12px; border-radius:10px;
  border:1px solid rgba(251,191,36,.25); background:rgba(251,191,36,.08);
  color:#fcd34d; font-size:.84rem; line-height:1.45;
}
.detail-warning p { margin:0; }
.detail-warning details { margin-top:9px; color:#b7c9dc; }
.detail-warning details p { padding-top:8px; font-size:.76rem; }
@keyframes loading { to { background-position:-170% 0; } }
</style>
