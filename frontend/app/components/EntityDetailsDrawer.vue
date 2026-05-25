<template>
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div v-if="open && node" class="drawer-backdrop" @click.self="emit('close')">
        <aside class="drawer" role="dialog" aria-modal="true" :aria-label="`Full details for ${node.name}`">
          <header class="drawer-header">
            <div class="entity-title">
              <span class="node-dot" :style="{ background: nodeColor(node.type) }" />
              <div>
                <p>Full entity details</p>
                <h2>{{ node.name }}</h2>
                <span>{{ nodeTypeLabel(node.type) }} · {{ node.degree || 0 }} visible connections</span>
              </div>
            </div>
            <button type="button" class="close" aria-label="Close entity details" @click="emit('close')">×</button>
          </header>

          <div class="drawer-content">
            <section class="overview">
              <h3>Operational context</h3>
              <p>{{ nodeSummary(node, details) }}</p>
              <div v-if="details?.stable_id" class="id-tag">Stored identifier: {{ details.stable_id }}</div>
            </section>

            <section v-if="propertyList.length" class="detail-section">
              <h3>Recorded properties</h3>
              <dl class="properties">
                <template v-for="item in propertyList" :key="item.key">
                  <dt>{{ item.key }}</dt>
                  <dd>{{ item.value }}</dd>
                </template>
              </dl>
            </section>

            <section class="detail-section">
              <h3>Visible evidence relationships</h3>
              <div v-if="neighbours.length" class="relationship-list">
                <article v-for="item in neighbours" :key="`${item.key}-${item.relationship}`">
                  <span class="node-dot small" :style="{ background: nodeColor(item.node.type) }" />
                  <div>
                    <strong>{{ item.node.name }}</strong>
                    <p>{{ humanize(item.relationship) }} · {{ nodeTypeLabel(item.node.type) }}</p>
                  </div>
                </article>
              </div>
              <p v-else class="empty">No related nodes are visible in the current evidence graph.</p>
            </section>

            <section v-if="storedRelationships.length" class="detail-section">
              <h3>Stored neighbouring records</h3>
              <div class="relationship-list stored">
                <article v-for="(relationship, index) in storedRelationships.slice(0, 12)" :key="index">
                  <div>
                    <strong>{{ relationship.name }}</strong>
                    <p>{{ humanize(relationship.relationship) }} · {{ relationship.type }}</p>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from "vue"
import { nodeColor, nodeSummary, nodeTypeLabel, type GraphEdge, type GraphNode, type NodeDetails } from "~/utils/graphPresentation"

const props = defineProps<{
  open: boolean
  node: GraphNode | null
  details: NodeDetails
  nodes?: Record<string, GraphNode>
  edges?: Record<string, GraphEdge>
}>()
const emit = defineEmits<{ close: [] }>()

const selectedKey = computed(() => {
  if (!props.node) return null
  return Object.entries(props.nodes || {}).find(([, item]) => item.id === props.node?.id && item.type === props.node?.type)?.[0] || null
})

const propertyList = computed(() =>
  Object.entries(props.details?.properties || {})
    .filter(([, value]) => value !== null && value !== "")
    .map(([key, value]) => ({ key: humanize(key), value: String(value) })),
)

const neighbours = computed(() => {
  const key = selectedKey.value
  if (!key) return []
  const found: Array<{ key: string; node: GraphNode; relationship: string }> = []
  for (const edge of Object.values(props.edges || {})) {
    const neighbourKey = edge.source === key ? edge.target : edge.target === key ? edge.source : null
    const node = neighbourKey ? props.nodes?.[neighbourKey] : undefined
    if (neighbourKey && node) found.push({ key: neighbourKey, node, relationship: edge.label || "RELATED_TO" })
  }
  return found.filter((item, index, all) => all.findIndex(other => other.key === item.key && other.relationship === item.relationship) === index)
})

const storedRelationships = computed(() =>
  (props.details?.relationships || []).map((item: any) => {
    const properties = item.connected_properties || {}
    return {
      relationship: String(item.relationship || "RELATED_TO"),
      type: String(item.connected_labels?.[0] || "Entity"),
      name: String(properties.name || properties.system_id || properties.employee_id || "Related record"),
    }
  }),
)

function humanize(value: string): string {
  return value.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, letter => letter.toUpperCase())
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && props.open) emit("close")
}

watch(() => props.open, value => {
  if (value) document.addEventListener("keydown", handleKeydown)
  else document.removeEventListener("keydown", handleKeydown)
})

onBeforeUnmount(() => document.removeEventListener("keydown", handleKeydown))
</script>

<style scoped>
.drawer-backdrop {
  position:fixed; z-index:80; inset:0; display:flex; justify-content:flex-end;
  background:rgba(2, 6, 17, .7); backdrop-filter:blur(4px);
}
.drawer {
  width:min(540px, 100vw); height:100%; overflow:auto;
  border-left:1px solid #1a3856; background:#07111f;
  box-shadow:-22px 0 70px rgba(0,0,0,.42); color:#e8f1fb;
}
.drawer-header {
  position:sticky; top:0; z-index:1; display:flex; justify-content:space-between; gap:16px;
  padding:24px; border-bottom:1px solid #162d46; background:rgba(7,17,31,.97);
}
.entity-title { display:flex; gap:13px; align-items:start; }
.node-dot { flex:0 0 auto; width:15px; height:15px; margin-top:8px; border-radius:50%; }
.node-dot.small { width:9px; height:9px; margin-top:6px; }
.entity-title p { margin:0 0 6px; color:#38bdf8; font-size:.68rem; letter-spacing:.15em; text-transform:uppercase; }
.entity-title h2 { margin:0 0 5px; font-size:1.25rem; }
.entity-title span { color:#879fb9; font-size:.79rem; }
.close {
  width:37px; height:37px; border:1px solid #1b3651; border-radius:9px;
  background:#0b1c30; color:#b5cada; font-size:1.45rem; cursor:pointer;
}
.close:hover { color:#fff; border-color:#38bdf8; }
.drawer-content { display:grid; gap:15px; padding:21px 24px 28px; }
.overview, .detail-section {
  padding:17px; border:1px solid #152d47; border-radius:13px; background:#09182a;
}
.overview h3, .detail-section h3 {
  margin:0 0 12px; color:#9ab2ca; font-size:.7rem; letter-spacing:.13em; text-transform:uppercase;
}
.overview p { color:#d1deed; line-height:1.58; margin:0 0 14px; }
.id-tag { display:inline-flex; padding:6px 10px; border-radius:999px; background:#102339; color:#8be2dc; font-size:.72rem; }
.properties { display:grid; grid-template-columns:minmax(112px,.8fr) 1.3fr; gap:9px 13px; margin:0; font-size:.82rem; }
.properties dt { color:#738faa; }
.properties dd { margin:0; color:#e0ebf6; word-break:break-word; }
.relationship-list { display:grid; gap:8px; }
.relationship-list article {
  display:flex; gap:10px; align-items:start; padding:10px;
  border:1px solid #112840; border-radius:9px; background:#071322;
}
.relationship-list strong { font-size:.83rem; font-weight:640; }
.relationship-list p { margin:4px 0 0; color:#7591ac; font-size:.72rem; }
.empty { color:#8099b4; font-size:.82rem; margin:0; }
.drawer-fade-enter-active, .drawer-fade-leave-active { transition:opacity .18s ease; }
.drawer-fade-enter-from, .drawer-fade-leave-to { opacity:0; }
</style>
