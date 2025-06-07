<!-- frontend/src/components/RegionLayer.vue -->
<template>
  <v-stage :config="stageConfig" class="absolute top-0 left-0 w-full h-full z-0">
    <v-layer ref="layerRef">
      <v-group
        v-for="region in regions"
        :key="region.id"
        :draggable="true"
        @click="selectRegion(region)"
        @dragend="onDragEnd(region, $event)"
      >
        <v-rect
          :config="{
            x: region.x,
            y: region.y,
            width: region.width,
            height: region.height,
            fill: region.color,
            stroke: '#333',
            strokeWidth: 1,
            name: 'region-rect'
          }"
        />
        <v-text
          :x="region.x + 5"
          :y="region.y + 5"
          :text="region.name"
          fontSize="14"
          fill="#000"
        />
      </v-group>

      <v-transformer v-if="selectedNode" :config="{ nodes: [selectedNode] }" />
    </v-layer>
  </v-stage>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'

const regions = ref([])
const selectedRegion = ref(null)
const selectedNode = ref(null)
const layerRef = ref(null)

const stageConfig = {
  width: window.innerWidth,
  height: window.innerHeight
}

async function loadRegions() {
  console.log("Загружаем регионы...")
  const res = await fetch("/api/regions")
  const raw = await res.json()
  console.log("Регионы с сервера:", raw)
  regions.value = raw
  selectedNode.value = null
  selectedRegion.value = null
}

function selectRegion(region) {
  selectedRegion.value = region
  nextTick(() => {
    const layer = layerRef.value.getNode()
    const rect = layer.findOne((n) =>
      n.getAttr("name") === "region-rect" &&
      n.x() === region.x &&
      n.y() === region.y
    )
    selectedNode.value = rect
  })
}

function onDragEnd(region, e) {
  region.x = e.target.x()
  region.y = e.target.y()
  saveRegion(region)
}

function onTransformEnd() {
  if (!selectedNode.value || !selectedRegion.value) return
  const node = selectedNode.value
  const region = selectedRegion.value

  region.x = node.x()
  region.y = node.y()
  region.width = node.width() * node.scaleX()
  region.height = node.height() * node.scaleY()

  node.scaleX(1)
  node.scaleY(1)

  saveRegion(region)
}

async function saveRegion(region) {
  await fetch("/api/regions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(region)
  })
}

onMounted(() => {
  loadRegions()
  const socket = new WebSocket(`ws://${location.host}/ws`)
  socket.onmessage = (event) => {
    if (event.data === "region_updated") loadRegions()
  }
})

watch(selectedNode, (node) => {
  if (!node) return
  node.on("transformend", onTransformEnd)
})
</script>

<style scoped>
.absolute {
  position: absolute;
}
.z-0 {
  z-index: 0;
}
</style>
