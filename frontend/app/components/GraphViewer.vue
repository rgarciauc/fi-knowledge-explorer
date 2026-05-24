<template>
  <section v-if="nodeCount" class="network-shell">
    <aside class="network-sidebar">
      <div class="sidebar-header">
        <p class="eyebrow">Knowledge graph</p>
        <h2>Explorer</h2>
        <div class="sidebar-stats">
          <span><strong>{{ visibleNodeCount }}</strong> nodes</span>
          <span><strong>{{ visibleEdgeCount }}</strong> edges</span>
        </div>
      </div>

      <label class="search-wrap">
        <span class="sr-only">Search graph nodes</span>
        <input v-model="search" type="search" placeholder="Search nodes..." />
      </label>

      <section class="sidebar-block">
        <div class="block-heading">
          <h3>Entity types</h3>
          <button class="quiet-action" type="button" @click="enableAllTypes">Show all</button>
        </div>
        <button
          v-for="group in typeCounts"
          :key="group.type"
          type="button"
          class="type-row"
          :class="{ disabled: !enabledTypes.has(group.type) }"
          @click="toggleType(group.type)"
        >
          <span class="type-key">
            <span class="legend-dot" :style="{ background: group.color }" />
            {{ group.label }}
          </span>
          <span class="type-count">{{ group.count }}</span>
        </button>
      </section>

      <section class="sidebar-block node-block">
        <div class="block-heading">
          <h3>Nodes</h3>
          <span class="subtle">{{ filteredList.length }}</span>
        </div>
        <div class="node-list">
          <button
            v-for="node in filteredList"
            :key="node.key"
            type="button"
            class="node-item"
            :class="{ selected: selectedKey === node.key }"
            @mouseenter="hover(node.key)"
            @mouseleave="hover(null)"
            @click="select(node.key)"
          >
            <span class="legend-dot" :style="{ background: nodeColor(node.type) }" />
            <span class="node-copy">
              <strong>{{ node.name }}</strong>
              <small>{{ node.type }} · {{ node.degree || 0 }} connection{{ node.degree === 1 ? "" : "s" }}</small>
            </span>
          </button>
        </div>
      </section>

      <section class="sidebar-block controls">
        <div class="block-heading">
          <h3>Layout</h3>
          <span v-if="layoutDirty" class="pending">Apply changes</span>
        </div>

        <label>
          <span>
            Link distance <strong>{{ linkDistance }}</strong>
            <em title="Preferred spacing between nodes connected by a relationship.">?</em>
          </span>
          <input v-model.number="linkDistance" type="range" min="50" max="280" step="10" />
          <small>Spacing between connected nodes</small>
        </label>

        <label>
          <span>
            Repulsion <strong>{{ Math.abs(chargeStrength) }}</strong>
            <em title="Repulsive force between all nodes. Higher values separate crowded nodes.">?</em>
          </span>
          <input v-model.number="chargeStrength" type="range" min="-1400" max="-80" step="40" />
          <small>Higher values spread crowded nodes</small>
        </label>

        <div class="control-actions layout-actions">
          <button type="button" class="primary" @click="applyLayout">Apply layout</button>
          <button type="button" @click="resetLayout">Defaults</button>
        </div>

        <h3 class="interaction-title">Display & interaction</h3>
        <label class="check">
          <input v-model="showLabels" type="checkbox" />
          <span>Show node labels</span>
        </label>
        <label class="check">
          <input v-model="showEdgeLabels" type="checkbox" />
          <span>Show relationship labels</span>
        </label>
        <label class="check">
          <input v-model="wheelZoomEnabled" type="checkbox" />
          <span>Enable mouse-wheel zoom</span>
        </label>
        <p v-if="!wheelZoomEnabled" class="zoom-safe">Scroll zoom is locked to prevent accidental zooming.</p>

        <div class="control-actions">
          <button type="button" @click="zoomOut">− Zoom</button>
          <button type="button" @click="zoomIn">+ Zoom</button>
          <button type="button" @click="fitGraph">Fit</button>
        </div>
      </section>
    </aside>

    <div class="network-canvas">
      <div class="canvas-header">
        <h2>Graph evidence</h2>
        <span>Hover for context · Click for details</span>
      </div>

      <ClientOnly>
        <VNetworkGraph
          ref="graph"
          v-model:layouts="layouts"
          v-model:selected-nodes="selectedNodes"
          class="graph"
          :nodes="visibleNodes"
          :edges="visibleEdges"
          :configs="configs"
          :event-handlers="eventHandlers"
        >
          <template #edge-label="{ edge, ...slotProps }">
            <VEdgeLabel
              v-if="showEdgeLabels && edge.label"
              :text="edge.label"
              align="center"
              vertical-align="above"
              v-bind="slotProps"
            />
          </template>
        </VNetworkGraph>

        <div
          v-if="activeHoverNode"
          ref="tooltip"
          class="node-tooltip"
          :style="tooltipStyle"
        >
          <strong>{{ activeHoverNode.name }}</strong>
          <span class="tooltip-type" :style="{ color: nodeColor(activeHoverNode.type) }">
            {{ nodeTypeLabel(activeHoverNode.type) }}
          </span>
          <p>{{ nodeSummary(activeHoverNode, hoverDetails) }}</p>
          <small>{{ activeHoverNode.degree || 0 }} visible connection{{ activeHoverNode.degree === 1 ? "" : "s" }}</small>
        </div>
      </ClientOnly>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from "vue"
import { VEdgeLabel, VNetworkGraph } from "v-network-graph"
import * as vNG from "v-network-graph"
import { ForceLayout, type ForceEdgeDatum, type ForceNodeDatum } from "v-network-graph/lib/force-layout"
import "v-network-graph/lib/style.css"
import {
  NODE_TYPE_STYLES,
  nodeColor,
  nodeSummary,
  nodeTypeLabel,
  type GraphNode,
  type NodeDetails,
} from "~/utils/graphPresentation"

const props = defineProps<{
  nodes: Record<string, GraphNode>
  edges: Record<string, { source: string; target: string; label?: string }>
  selectedKey?: string | null
  hoveredNodeKey?: string | null
  hoverDetails?: NodeDetails
}>()

const emit = defineEmits<{
  select: [nodeKey: string]
  hover: [nodeKey: string | null]
}>()

const graph = ref<any>()
const tooltip = ref<HTMLDivElement>()
const layouts = ref<vNG.Layouts>({ nodes: {} })
const selectedNodes = ref<string[]>([])
const search = ref("")
const showLabels = ref(true)
const showEdgeLabels = ref(false)
const wheelZoomEnabled = ref(false)
const linkDistance = ref(125)
const chargeStrength = ref(-420)
const appliedLinkDistance = ref(linkDistance.value)
const appliedChargeStrength = ref(chargeStrength.value)
const enabledTypes = ref(new Set<string>())
const tooltipPosition = ref({ left: "24px", top: "72px" })

const layoutDirty = computed(
  () => linkDistance.value !== appliedLinkDistance.value || chargeStrength.value !== appliedChargeStrength.value,
)

const configs = reactive(vNG.getFullConfigs()) as any

function forceLayout() {
  return new ForceLayout({
    positionFixedByDrag: false,
    positionFixedByClickWithAltKey: true,
    createSimulation: (d3, nodes, edges) => {
      const link = d3
        .forceLink<ForceNodeDatum, ForceEdgeDatum>(edges)
        .id(node => node.id)
        .distance(appliedLinkDistance.value)
        .strength(0.62)

      return d3
        .forceSimulation(nodes)
        .force("edge", link)
        .force("charge", d3.forceManyBody().strength(appliedChargeStrength.value))
        .force("collide", d3.forceCollide().radius(34).strength(0.72))
        .force("center", d3.forceCenter().strength(0.06))
        .alphaMin(0.002)
    },
  })
}

function initializeConfigs() {
  configs.view.autoPanAndZoomOnLoad = "fit-content"
  configs.view.mouseWheelZoomEnabled = wheelZoomEnabled.value
  configs.view.doubleClickZoomEnabled = false
  configs.view.layoutHandler = forceLayout()
  configs.node.selectable = true
  configs.node.normal.radius = (node: GraphNode) => 12 + Math.min((node.degree || 0) * 3.5, 22)
  configs.node.normal.color = (node: GraphNode) => nodeColor(node.type)
  configs.node.normal.strokeWidth = 2
  configs.node.normal.strokeColor = "#071526"
  configs.node.hover.radius = (node: GraphNode) => 15 + Math.min((node.degree || 0) * 3.5, 22)
  configs.node.hover.strokeWidth = 3
  configs.node.hover.strokeColor = "#d9fcff"
  // Selected node emphasis uses the library's focus ring.
  // v-network-graph supports node.normal and node.hover appearance,
  // while selection is represented through node.focusring.
  configs.node.focusring.visible = true
  configs.node.focusring.width = 4
  configs.node.focusring.padding = 5
  configs.node.focusring.color = "#f8fafc"
  configs.node.label.visible = showLabels.value
  configs.node.label.color = "#d9e6f6"
  configs.node.label.fontSize = 11
  configs.node.label.direction = "south"
  configs.node.label.margin = 7
  configs.edge.normal.color = "#263a58"
  configs.edge.normal.width = 1.35
  configs.edge.hover.color = "#38bdf8"
  configs.edge.hover.width = 2.5
  configs.edge.selected.color = "#67e8f9"
  configs.edge.selected.width = 2.5
  configs.edge.label.color = "#99b2cd"
  configs.edge.label.fontSize = 9
  configs.edge.label.background.visible = true
  configs.edge.label.background.color = "#081221"
  configs.edge.label.background.padding = { vertical: 2, horizontal: 5 }
  configs.edge.label.background.borderRadius = 3
  configs.edge.marker.target.type = "arrow"
  configs.edge.marker.target.width = 5
  configs.edge.marker.target.height = 5
  configs.edge.marker.target.color = "#40597a"
}
initializeConfigs()

const allNodes = computed(() =>
  Object.entries(props.nodes).map(([key, node]) => ({ ...node, key })),
)
const nodeCount = computed(() => allNodes.value.length)

const typeCounts = computed(() => {
  const counts = new Map<string, number>()
  for (const node of allNodes.value) counts.set(node.type, (counts.get(node.type) || 0) + 1)
  return [...counts.entries()]
    .map(([type, count]) => ({
      type,
      count,
      color: nodeColor(type),
      label: NODE_TYPE_STYLES[type]?.label || type,
    }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))
})

watch(
  () => typeCounts.value.map(group => group.type).join("|"),
  () => {
    enabledTypes.value = new Set(typeCounts.value.map(group => group.type))
  },
  { immediate: true },
)

const enabledNodeMap = computed(() =>
  Object.fromEntries(
    Object.entries(props.nodes).filter(([, node]) => enabledTypes.value.has(node.type)),
  ),
)

const visibleEdges = computed(() =>
  Object.fromEntries(
    Object.entries(props.edges).filter(([, edge]) =>
      Boolean(enabledNodeMap.value[edge.source] && enabledNodeMap.value[edge.target]),
    ),
  ),
)

const visibleDegrees = computed(() => {
  const counts: Record<string, number> = Object.fromEntries(
    Object.keys(enabledNodeMap.value).map(key => [key, 0]),
  )
  for (const edge of Object.values(visibleEdges.value)) {
    counts[edge.source] = (counts[edge.source] || 0) + 1
    counts[edge.target] = (counts[edge.target] || 0) + 1
  }
  return counts
})

const visibleNodes = computed(() =>
  Object.fromEntries(
    Object.entries(enabledNodeMap.value).map(([key, node]) => [
      key,
      { ...node, degree: visibleDegrees.value[key] || 0 },
    ]),
  ),
)

const visibleNodeCount = computed(() => Object.keys(visibleNodes.value).length)
const visibleEdgeCount = computed(() => Object.keys(visibleEdges.value).length)

const filteredList = computed(() => {
  const term = search.value.trim().toLowerCase()
  return Object.entries(visibleNodes.value)
    .map(([key, node]) => ({ ...node, key }))
    .filter(node => !term || `${node.name} ${node.type}`.toLowerCase().includes(term))
    .sort((a, b) => (b.degree || 0) - (a.degree || 0) || a.name.localeCompare(b.name))
})

const activeHoverNode = computed(() => {
  if (!props.hoveredNodeKey) return null
  return visibleNodes.value[props.hoveredNodeKey] || null
})

const tooltipStyle = computed(() => ({
  left: tooltipPosition.value.left,
  top: tooltipPosition.value.top,
}))

function toggleType(type: string) {
  const next = new Set(enabledTypes.value)
  if (next.has(type) && next.size > 1) next.delete(type)
  else next.add(type)
  enabledTypes.value = next
  nextTick(applyLayout)
}

function enableAllTypes() {
  enabledTypes.value = new Set(typeCounts.value.map(group => group.type))
  nextTick(applyLayout)
}

function select(nodeKey: string) {
  selectedNodes.value = [nodeKey]
  emit("select", nodeKey)
}

function hover(nodeKey: string | null) {
  emit("hover", nodeKey)
}

function applyLayout() {
  appliedLinkDistance.value = linkDistance.value
  appliedChargeStrength.value = chargeStrength.value
  layouts.value = { nodes: {} }
  configs.view.layoutHandler = forceLayout()
  nextTick(() => graph.value?.fitToContents())
}

function resetLayout() {
  linkDistance.value = 125
  chargeStrength.value = -420
  applyLayout()
}

function fitGraph() {
  graph.value?.fitToContents()
}
function zoomIn() {
  graph.value?.zoomIn()
}
function zoomOut() {
  graph.value?.zoomOut()
}

watch(showLabels, value => {
  configs.node.label.visible = value
})
watch(wheelZoomEnabled, value => {
  configs.view.mouseWheelZoomEnabled = value
})
watch(
  () => props.selectedKey,
  key => {
    selectedNodes.value = key ? [key] : []
  },
  { immediate: true },
)
watch(
  () => Object.keys(props.nodes).join("|") + Object.keys(props.edges).join("|"),
  () => nextTick(applyLayout),
)

watch(
  () => [props.hoveredNodeKey, layouts.value.nodes[props.hoveredNodeKey || ""]],
  async () => {
    if (!props.hoveredNodeKey || !graph.value) return
    const position = layouts.value.nodes[props.hoveredNodeKey]
    if (!position) return
    await nextTick()
    const dom = graph.value.translateFromSvgToDomCoordinates(position)
    const width = tooltip.value?.offsetWidth || 300
    const height = tooltip.value?.offsetHeight || 140
    tooltipPosition.value = {
      left: `${Math.max(16, dom.x - width / 2)}px`,
      top: `${Math.max(62, dom.y - height - 28)}px`,
    }
  },
  { deep: true },
)

const eventHandlers: vNG.EventHandlers = {
  "node:click": ({ node }) => select(node),
  "node:pointerover": ({ node }) => hover(node),
  "node:pointerout": () => hover(null),
}
</script>

<style scoped>
.network-shell { display:grid; grid-template-columns:326px minmax(0,1fr); min-height:735px; border:1px solid #162a43; border-radius:22px; overflow:hidden; background:#050d1b; box-shadow:0 24px 58px rgba(2,6,23,.3); }
.network-sidebar { min-height:735px; display:flex; flex-direction:column; padding:20px 16px 16px; background:#091423; color:#dce7f5; border-right:1px solid #162a43; overflow:auto; }
.sidebar-header h2 { margin:3px 0 12px; color:#f2f7fd; font-size:1.3rem; }
.sidebar-header .eyebrow { color:#38bdf8; margin:0; }
.sidebar-stats { display:flex; gap:16px; color:#8ea4be; font-size:.84rem; margin-bottom:18px; }
.sidebar-stats strong { color:#e9f2fc; }
.search-wrap input { width:100%; background:#07101e; color:#dce7f5; border:1px solid #1c304a; border-radius:11px; padding:11px 12px; font-size:.9rem; outline:none; }
.search-wrap input:focus { border-color:#38bdf8; }
.sidebar-block { border-top:1px solid #172a43; padding-top:16px; margin-top:16px; }
.block-heading { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
.sidebar-block h3 { color:#8199b7; text-transform:uppercase; letter-spacing:.1em; font-size:.72rem; margin:0 0 10px; }
.block-heading h3 { margin:0; }
.quiet-action { color:#38bdf8; border:0; background:transparent; font-size:.75rem; cursor:pointer; }
.type-row,.node-item { width:100%; border:0; background:transparent; color:inherit; cursor:pointer; }
.type-row { display:flex; justify-content:space-between; align-items:center; padding:7px 2px; font-size:.85rem; }
.type-row.disabled { opacity:.36; }
.type-key { display:inline-flex; align-items:center; gap:9px; }
.legend-dot { width:10px; height:10px; border-radius:50%; flex:none; box-shadow:0 0 9px currentColor; }
.type-count,.subtle { color:#7e94ad; font-size:.8rem; }
.node-block { flex:1; min-height:126px; display:flex; flex-direction:column; }
.node-list { min-height:90px; max-height:215px; overflow:auto; padding-right:3px; }
.node-item { display:flex; align-items:start; gap:10px; padding:9px 8px; margin-bottom:5px; border-radius:10px; text-align:left; }
.node-item:hover,.node-item.selected { background:#12243a; }
.node-copy { min-width:0; display:flex; flex-direction:column; gap:3px; }
.node-copy strong { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:.84rem; }
.node-copy small { color:#7f98b5; font-size:.72rem; }
.controls label { display:block; font-size:.76rem; color:#8fa5bf; margin:10px 0; }
.controls label span { display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; }
.controls label em { border:1px solid #29425f; color:#9bb5cf; border-radius:50%; width:15px; height:15px; display:inline-grid; place-items:center; font-style:normal; font-size:.68rem; margin-left:auto; margin-right:6px; }
.controls label small { display:block; color:#627c9a; font-size:.68rem; margin-top:3px; }
.controls input[type=range] { width:100%; accent-color:#38bdf8; }
.controls label.check { display:flex; align-items:center; gap:8px; }
.controls label.check span { display:inline; margin:0; }
.pending { font-size:.66rem; color:#facc15; }
.interaction-title { margin-top:18px !important; }
.zoom-safe { margin:7px 0 11px; padding:7px 9px; border-radius:8px; color:#7ea0c1; font-size:.7rem; background:#0b1b30; }
.control-actions { display:flex; gap:7px; margin-top:13px; }
.control-actions button { flex:1; padding:8px 5px; color:#bfeafd; border:1px solid #203958; background:#0b192c; border-radius:8px; cursor:pointer; font-size:.75rem; }
.control-actions button.primary { background:#12324c; border-color:#38bdf8; color:#e6f7fe; }
.network-canvas { position:relative; min-width:0; background:radial-gradient(circle at 48% 44%, rgba(34,211,238,.06), transparent 34%), #050d1b; }
.canvas-header { position:absolute; z-index:2; top:0; left:0; right:0; display:flex; justify-content:space-between; align-items:baseline; height:55px; padding:16px 21px 0; pointer-events:none; }
.canvas-header h2 { color:#e8f2fd; font-size:1rem; margin:0; }
.canvas-header span { color:#7891ae; font-size:.76rem; }
.graph { height:735px; }
.node-tooltip { position:absolute; z-index:5; pointer-events:none; width:min(330px, calc(100% - 32px)); padding:15px 16px; background:rgba(9,20,35,.96); border:1px solid #203a58; border-radius:13px; color:#e4edf8; box-shadow:0 18px 48px rgba(0,0,0,.42); }
.node-tooltip strong { display:block; font-size:1rem; }
.tooltip-type { display:block; margin:5px 0 10px; font-size:.74rem; font-weight:750; text-transform:uppercase; letter-spacing:.09em; }
.node-tooltip p { color:#becdde; line-height:1.45; font-size:.84rem; margin:0 0 10px; }
.node-tooltip small { color:#829ab7; border-top:1px solid #182c45; display:block; padding-top:9px; }
.sr-only { position:absolute; overflow:hidden; width:1px; height:1px; clip-path:inset(50%); }
@media (max-width:980px) { .network-shell { display:block; } .network-sidebar { min-height:auto; } .node-list { max-height:180px; } .graph { height:600px; } }
</style>
