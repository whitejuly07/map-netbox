<!-- frontend/src/App.vue -->
<template>
  <div class="app-container">
    <button
      ref="updateBtn"
      class="update-button"
      :disabled="loading"
      @click.stop.prevent="onClickUpdate"
    >
      {{ loading ? 'Обновление...' : 'Обновить из NetBox' }}
    </button>
    <div ref="networkContainer" class="network-map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Network } from 'vis-network/standalone/esm/vis-network'

const updateBtn = ref(null)
const networkContainer = ref(null)
const loading = ref(false)
let network = null

let currentPositions = {}

async function fetchGraph() {
  const [devRes, topoRes, posRes] = await Promise.all([
    fetch('/api/devices'),
    fetch('/api/topology'),
    fetch('/api/positions')
  ])
  const devices = await devRes.json()
  const topology = await topoRes.json()
  const positions = await posRes.json()

  currentPositions = positions

  const nameToId = {}
  const nodes = devices.map(d => {
    nameToId[d.name] = d.id
    const node = { id: String(d.id), label: d.name }
    if (positions[d.id]) {
      node.x = positions[d.id].x
      node.y = positions[d.id].y
    }
    node.group = d.location?.name || null
    return node
  })

  const edges = topology
    .map(c => ({
      from: nameToId[c.port_a.device],
      to: nameToId[c.port_b.device],
      title: `${c.port_a.name} ⇄ ${c.port_b.name}`
    }))
    .filter(e => e.from && e.to)

  const data = { nodes, edges }
  const options = {
    nodes: {
      shape: 'box',
      margin: 10
    },
    edges: {
      smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 }
    },
    layout: {
      improvedLayout: true
    },
    physics: {
      enabled: false
    },
    interaction: {
      dragNodes: true,
      dragView: true,
      zoomView: true,
      hover: true
    }
  }

  if (!network) {
    network = new Network(networkContainer.value, data, options)
    network.on('dragEnd', () => {
      const newPos = network.getPositions()
      const toSave = {}
      Object.entries(newPos).forEach(([id, pos]) => {
        toSave[id] = pos
        currentPositions[id] = pos
      })
      fetch('/api/positions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(toSave)
      }).catch(e => console.error('Ошибка сохранения позиций:', e))
    })
  } else {
    network.setData(data)
    network.setOptions(options)
  }

  drawRegionAroundGroup('Московский офис', data.nodes)
}

function drawRegionAroundGroup(groupName, nodes) {
  const OFFSET = 200
  const groupNodes = nodes.filter(n => n.group === groupName && typeof n.x === 'number' && typeof n.y === 'number')
  if (groupNodes.length === 0) return

  const xs = groupNodes.map(n => n.x)
  const ys = groupNodes.map(n => n.y)
  const minX = Math.min(...xs) - OFFSET
  const maxX = Math.max(...xs) + OFFSET
  const minY = Math.min(...ys) - OFFSET
  const maxY = Math.max(...ys) + OFFSET

  network.off('beforeDrawing')
  network.on('beforeDrawing', (ctx) => {
    ctx.fillStyle = 'rgba(200, 200, 255, 0.2)'
    ctx.strokeStyle = '#444'
    ctx.lineWidth = 2
    ctx.fillRect(minX, minY, maxX - minX, maxY - minY)
    ctx.strokeRect(minX, minY, maxX - minX, maxY - minY)
    ctx.font = '16px sans-serif'
    ctx.fillStyle = '#000'
    ctx.fillText(groupName, minX + 10, minY + 20)
  })
  network.redraw()
}

async function onClickUpdate() {
  if (loading.value) return
  loading.value = true
  try {
    await fetch('/api/update', { method: 'POST' })
    await fetchGraph()
  } catch (e) {
    console.error('Ошибка обновления из NetBox:', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchGraph()
  updateBtn.value.style.position = 'absolute'
  updateBtn.value.addEventListener('mousedown', (e) => {
    const el = updateBtn.value
    const offsetX = e.clientX - el.offsetLeft
    const offsetY = e.clientY - el.offsetTop
    function onMouseMove(ev) {
      el.style.left = `${ev.clientX - offsetX}px`
      el.style.top = `${ev.clientY - offsetY}px`
    }
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove)
    }, { once: true })
  })
})
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
.app-container {
  width: 100%;
  height: 100%;
}
.network-map {
  position: absolute;
  width: 100%;
  height: 100%;
}
.update-button {
  padding: 0.5rem 1rem;
  background: #eee;
  border: 1px solid #888;
  border-radius: 4px;
  cursor: move;
  z-index: 1000;
  user-select: none;
  left: 10px;
  top: 10px;
  position: absolute;
}
.update-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
