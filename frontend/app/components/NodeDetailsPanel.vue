<template><section class="panel" v-if="node"><h2>Selected node</h2><h3>{{ node.name }}</h3><p class="muted">{{ node.type }} · {{ node.degree || 0 }} visible connection(s)</p><pre v-if="details">{{ JSON.stringify(details, null, 2) }}</pre></section></template>
<script setup lang="ts">defineProps<{node:any,details:any}>()</script>
