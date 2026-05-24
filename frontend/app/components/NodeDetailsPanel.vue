<template>
  <section v-if="node" class="panel detail-panel">
    <p class="section-label">Selected node</p>
    <div class="node-heading">
      <span class="node-dot" :style="{ background: nodeColor(node.type) }" />
      <div>
        <h2>{{ node.name }}</h2>
        <p class="muted">{{ nodeTypeLabel(node.type) }} · {{ node.degree || 0 }} visible connection(s)</p>
      </div>
    </div>

    <div v-if="details?.error" class="detail-warning">
      <p>{{ details.error }}</p>
      <details v-if="(details as any).diagnostic">
        <summary>Diagnostic details</summary>
        <p>{{ (details as any).diagnostic }}</p>
      </details>
    </div>

    <template v-else>
      <div v-if="details" class="resolution">
        <span v-if="details.stable_id">Stored ID: {{ details.stable_id }}</span>
        <span v-if="details.matched_by === 'stable_id'" class="ok">Resolved by stable ID</span>
        <span v-else-if="details.matched_by === 'exact_name_fallback'" class="fallback">
          Resolved from graph display name
        </span>
      </div>
      <p class="summary">{{ nodeSummary(node, details) }}</p>
      <dl v-if="properties.length" class="property-grid">
        <template v-for="property in properties" :key="property.key">
          <dt>{{ property.key }}</dt>
          <dd>{{ property.value }}</dd>
        </template>
      </dl>
    </template>
  </section>
  <section v-else class="panel detail-placeholder">
    <p class="section-label">Selected node</p>
    <p>Select a node in the graph or from the sidebar to inspect its context.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { nodeColor, nodeSummary, nodeTypeLabel, type GraphNode, type NodeDetails } from "~/utils/graphPresentation"

const props = defineProps<{ node: GraphNode | null; details: NodeDetails }>()

const properties = computed(() => {
  if (!props.details?.properties) return []
  const excluded = new Set(["name", "description", "task_summary"])
  return Object.entries(props.details.properties)
    .filter(([key, value]) => !excluded.has(key) && value !== null && value !== "")
    .slice(0, 8)
    .map(([key, value]) => ({
      key: key.replaceAll("_", " "),
      value: String(value),
    }))
})
</script>

<style scoped>
.section-label { margin: 0 0 13px; color: #7089a7; font-size: .7rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
.node-heading { display: flex; gap: 12px; align-items: start; }
.node-dot { height: 14px; width: 14px; margin-top: 7px; border-radius: 50%; box-shadow: 0 0 13px currentColor; }
.node-heading h2 { font-size: 1.12rem; margin: 0 0 4px; color: #edf4fc; }
.node-heading .muted { margin: 0; }
.resolution { display:flex; flex-wrap:wrap; gap:7px; margin:17px 0 0; }
.resolution span { padding:5px 9px; border-radius:999px; background:#102138; color:#93abc5; font-size:.72rem; }
.resolution .ok { color:#84f0c5; background:rgba(45,212,191,.14); border:1px solid rgba(45,212,191,.24); }
.resolution .fallback { color:#fde68a; background:rgba(250,204,21,.12); border:1px solid rgba(250,204,21,.22); }
.summary { margin: 18px 0; line-height: 1.55; color: #c1d0e2; }
.property-grid { display: grid; grid-template-columns: minmax(95px, .8fr) 1.4fr; gap: 9px 12px; margin: 18px 0 0; padding-top: 13px; border-top: 1px solid #182d47; font-size: .8rem; }
.property-grid dt { text-transform: capitalize; color: #7089a7; }
.property-grid dd { margin: 0; color: #dbe7f4; word-break: break-word; }
.detail-placeholder { color: #91a8c2; display: flex; flex-direction: column; justify-content: center; }
.detail-placeholder p:last-child { margin: 0; line-height: 1.5; }
.detail-warning {
  margin-top: 18px; padding: 12px; border-radius: 10px;
  border: 1px solid rgba(251,191,36,.25); background: rgba(251,191,36,.08);
  color: #fcd34d; font-size: .84rem; line-height: 1.45;
}
.detail-warning p { margin: 0; }
.detail-warning details { margin-top: 9px; color: #b7c9dc; }
.detail-warning details p { padding-top: 8px; font-size: .76rem; }
</style>
