<!-- frontend/src/components/RegionsManager.vue -->
<template>
  <div class="absolute inset-0 pointer-events-none">
    <!-- рисуем области -->
    <div
      v-for="region in regions"
      :key="region.id"
      class="absolute border-2"
      :style="regionStyle(region)"
    >
      <div class="absolute top-0 left-0 p-1 font-bold bg-white bg-opacity-75">
        {{ region.name }}
      </div>
    </div>
  </div>
</template>

<script setup>
// Компонент только отображает зоны, управление (добавление/цвет/перетаскивание)
// пока реализуем позже
import { computed } from 'vue'
defineProps({
  regions: { type: Array, required: true }
})
const regionStyle = (r) => ({
  top: `${r.y}px`,
  left: `${r.x}px`,
  width: `${r.width}px`,
  height: `${r.height}px`,
  backgroundColor: r.color,
  pointerEvents: 'none'  // чтобы не блокировать перетаскивание узлов
})
</script>

<style>
/* по желанию можно добавить soft-shadow, закругления */
</style>
