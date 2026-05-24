<template>
  <section v-if="Object.keys(nodes).length" class="panel graph-panel">
    <div class="heading">
      <h2>Graph evidence</h2>
      <span>Node size = number of returned connections</span>
    </div>
    <ClientOnly>
      <VNetworkGraph
        class="graph"
        :nodes="displayNodes"
        :edges="edges"
        :configs="configs"
        @node-click="(event) => emit('select', event.node)"
      />
    </ClientOnly>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { VNetworkGraph } from "v-network-graph"
import "v-network-graph/lib/style.css"

const props = defineProps<{
  nodes: Record<string, any>
  edges: Record<string, any>
}>()
const emit = defineEmits<{ select: [nodeKey: string] }>()

const displayNodes = computed(() =>
  Object.fromEntries(
    Object.entries(props.nodes).map(([id, node]) => [id, { ...node, id }]),
  ),
)

const configs = {
  node: {
    label: { visible: true, fontSize: 12, direction: "south" },
    normal: { radius: (node: any) => 16 + Math.min((node.degree || 0) * 5, 30) },
  },
  edge: {
    label: { visible: true, fontSize: 10 },
    marker: { target: { type: "arrow" } },
  },
}
</script>
