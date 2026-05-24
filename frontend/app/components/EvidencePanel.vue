<template><section class="panel" v-if="answer"><h2>Answer</h2><p>{{ answer }}</p><p class="muted">Intent: {{ intent }}</p><details v-if="rows.length"><summary>Raw graph evidence ({{ rows.length }})</summary><pre>{{ JSON.stringify(rows, null, 2) }}</pre></details></section></template>
<script setup lang="ts">defineProps<{answer:string,intent:string,rows:any[]}>()</script>
