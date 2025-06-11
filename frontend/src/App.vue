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
    <div v-if="showSettings && selectedRegion" class="settings-panel">
      <label>Цвет области: <input type="color" v-model="selectedRegion.color" /></label>
      <label>Прозрачность: <input type="range" min="0" max="1" step="0.05" v-model.number="selectedRegion.opacity" /></label>
      <label>Размер шрифта: <input type="number" min="8" max="48" v-model.number="selectedRegion.fontSize" /></label>
      <label>Положение текста:
        <select v-model="selectedRegion.labelAlign">
          <option value="top-left">Сверху слева</option>
          <option value="top-center">Сверху по центру</option>
          <option value="top-right">Сверху справа</option>
          <option value="bottom-left">Снизу слева</option>
          <option value="bottom-center">Снизу по центру</option>
          <option value="bottom-right">Снизу справа</option>
        </select>
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Network, DataSet } from 'vis-network/standalone/esm/vis-network'

const updateBtn = ref(null)
const networkContainer = ref(null)
const loading = ref(false)
let network = null
let regionsData = []
let draggingRegion = null
let draggingType = null
let resizeMode = null
let dragOffset = { x: 0, y: 0 }
let hoveredRegionId = null
const showSettings = ref(false)
const selectedRegion = ref(null)

function getMousePosition(event) {
  const canvas = network.canvas.frame.canvas
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  return network.DOMtoCanvas({ x, y })
}

function openSettings(region) {
  selectedRegion.value = region
  showSettings.value = true
}

watch(selectedRegion, (val) => {
  if (val) network.redraw()
})

function getResizeMode(mouse, region) {
  const edgeSize = 10
  const mx = mouse.x
  const my = mouse.y
  const x1 = region.x
  const y1 = region.y
  const x2 = region.x + region.width
  const y2 = region.y + region.height

  const nearLeft = mx >= x1 && mx <= x1 + edgeSize
  const nearRight = mx >= x2 - edgeSize && mx <= x2
  const nearTop = my >= y1 && my <= y1 + edgeSize
  const nearBottom = my >= y2 - edgeSize && my <= y2

  if (nearLeft && nearTop) return 'top-left'
  if (nearRight && nearTop) return 'top-right'
  if (nearLeft && nearBottom) return 'bottom-left'
  if (nearRight && nearBottom) return 'bottom-right'
  if (nearLeft) return 'left'
  if (nearRight) return 'right'
  if (nearTop) return 'top'
  if (nearBottom) return 'bottom'
  return null
}

function getCursorForResizeMode(mode) {
  switch (mode) {
    case 'top-left':
    case 'bottom-right':
      return 'nwse-resize'
    case 'top-right':
    case 'bottom-left':
      return 'nesw-resize'
    case 'left':
    case 'right':
      return 'ew-resize'
    case 'top':
    case 'bottom':
      return 'ns-resize'
    default:
      return 'default'
  }
}

function setupRegionEditingEvents() {
  const canvas = network.canvas.frame.canvas

  canvas.addEventListener('mousedown', (e) => {
    const mouse = getMousePosition(e)
    for (const region of regionsData.slice().reverse()) {
      const gearX = region.x + region.width - 20
      const gearY = region.y
      if (mouse.x >= gearX && mouse.x <= gearX + 16 && mouse.y >= gearY && mouse.y <= gearY + 16) {
        openSettings(region)
        return
      }

      const mode = getResizeMode(mouse, region)
      if (mode) {
        draggingRegion = region
        draggingType = 'resize'
        resizeMode = mode
        network.setOptions({ interaction: { dragView: false } })
        return
      } else if (
        mouse.x >= region.x &&
        mouse.x <= region.x + region.width &&
        mouse.y >= region.y &&
        mouse.y <= region.y + region.height
      ) {
        draggingRegion = region
        draggingType = 'move'
        dragOffset = { x: mouse.x - region.x, y: mouse.y - region.y }
        network.setOptions({ interaction: { dragView: false } })
        return
      }
    }
  })

  canvas.addEventListener('mousemove', (e) => {
    const mouse = getMousePosition(e)
    hoveredRegionId = null
    let cursor = 'default'
    for (const region of regionsData) {
      const gearX = region.x + region.width - 20
      const gearY = region.y
      if (mouse.x >= region.x && mouse.x <= region.x + region.width && mouse.y >= region.y && mouse.y <= region.y + region.height) {
        hoveredRegionId = region.id
      }
      const mode = getResizeMode(mouse, region)
      if (mode) {
        cursor = getCursorForResizeMode(mode)
        break
      }
    }
    canvas.style.cursor = cursor

    if (!draggingRegion) return
    const r = draggingRegion

    if (draggingType === 'move') {
      r.x = mouse.x - dragOffset.x
      r.y = mouse.y - dragOffset.y
    } else if (draggingType === 'resize') {
      const minSize = 10
      const dx = mouse.x - r.x
      const dy = mouse.y - r.y

      switch (resizeMode) {
        case 'right':
        case 'bottom-right':
          r.width = Math.max(minSize, dx)
          if (resizeMode === 'bottom-right') r.height = Math.max(minSize, dy)
          break
        case 'left': {
          const newWidth = Math.max(minSize, r.width + r.x - mouse.x)
          r.x = r.x + r.width - newWidth
          r.width = newWidth
          break
        }
        case 'top': {
          const newHeight = Math.max(minSize, r.height + r.y - mouse.y)
          r.y = r.y + r.height - newHeight
          r.height = newHeight
          break
        }
        case 'bottom':
          r.height = Math.max(minSize, dy)
          break
        case 'top-left': {
          const newWidth = Math.max(minSize, r.width + r.x - mouse.x)
          const newHeight = Math.max(minSize, r.height + r.y - mouse.y)
          r.x = r.x + r.width - newWidth
          r.y = r.y + r.height - newHeight
          r.width = newWidth
          r.height = newHeight
          break
        }
        case 'top-right': {
          const newWidth = Math.max(minSize, dx)
          const newHeight = Math.max(minSize, r.height + r.y - mouse.y)
          r.y = r.y + r.height - newHeight
          r.width = newWidth
          r.height = newHeight
          break
        }
        case 'bottom-left': {
          const newWidth = Math.max(minSize, r.width + r.x - mouse.x)
          const newHeight = Math.max(minSize, dy)
          r.x = r.x + r.width - newWidth
          r.width = newWidth
          r.height = newHeight
          break
        }
      }
    }
    network.redraw()
  })

  canvas.addEventListener('mouseup', async () => {
    if (!draggingRegion) return
    const region = draggingRegion
    draggingRegion = null
    draggingType = null
    resizeMode = null
    network.setOptions({ interaction: { dragView: true } })
    network.canvas.frame.canvas.style.cursor = 'default'
    await fetch('/api/regions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(region)
    })
  })
}

function drawRegionsOnBackground() {
  network.off('beforeDrawing')
  network.on('beforeDrawing', (ctx) => {
    for (const region of regionsData) {
      const color = region.color || '#cce'
      const opacity = region.opacity ?? 0.3
      ctx.fillStyle = color
      ctx.globalAlpha = opacity
      ctx.fillRect(region.x, region.y, region.width, region.height)
      ctx.globalAlpha = 1
      ctx.strokeStyle = '#444'
      ctx.lineWidth = 2
      ctx.strokeRect(region.x, region.y, region.width, region.height)

      const fontSize = region.fontSize || 14
      const text = region.name
      ctx.font = `${fontSize}px sans-serif`
      ctx.fillStyle = '#000'
      const metrics = ctx.measureText(text)
      let tx = region.x + 10
      let ty = region.y + fontSize + 4
      const align = region.labelAlign || 'top-left'

      if (align.includes('bottom')) ty = region.y + region.height - 10
      if (align.includes('top')) ty = region.y + fontSize + 4
      if (align.includes('center')) tx = region.x + region.width / 2 - metrics.width / 2
      if (align.includes('right')) tx = region.x + region.width - metrics.width - 10

      ctx.fillText(text, tx, ty)

      if (hoveredRegionId === region.id) {
        ctx.fillStyle = '#444'
        ctx.fillRect(region.x + region.width - 20, region.y, 16, 16)
        ctx.fillStyle = '#fff'
        ctx.font = '12px sans-serif'
        ctx.fillText('⚙', region.x + region.width - 18, region.y + 13)
      }
    }
  })
  network.redraw()
}

async function fetchGraph() {
  const [devRes, topoRes, posRes, regionRes] = await Promise.all([
    fetch('/api/devices'),
    fetch('/api/topology'),
    fetch('/api/positions'),
    fetch('/api/regions')
  ])
  const devices = await devRes.json()
  const topology = await topoRes.json()
  const positions = await posRes.json()
  regionsData = await regionRes.json()

  const nameToId = {}
  const nodes = new DataSet()

  devices.forEach(d => {
    nameToId[d.name] = d.id
    const node = { id: String(d.id), label: d.name }
    if (positions[d.id]) {
      node.x = positions[d.id].x
      node.y = positions[d.id].y
    }
    nodes.add(node)
  })

  const edges = topology.map(c => ({
    from: nameToId[c.port_a.device],
    to: nameToId[c.port_b.device],
    title: `${c.port_a.name} ⇄ ${c.port_b.name}`
  })).filter(e => e.from && e.to)

  const data = { nodes, edges }
  const options = {
    nodes: { shape: 'box', margin: 10 },
    edges: { smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 } },
    layout: { improvedLayout: true },
    physics: { enabled: false },
    interaction: { dragNodes: true, dragView: true, zoomView: true, hover: true }
  }

  if (!network) {
    network = new Network(networkContainer.value, data, options)
    setupRegionEditingEvents()
  } else {
    network.setData(data)
    network.setOptions(options)
  }

  drawRegionsOnBackground()

  // Сохраняем позиции узлов после перетаскивания
  network.on('dragEnd', async function (event) {
  if (!event.nodes || event.nodes.length === 0) return;
  const positions = network.getPositions();
  await fetch('/api/positions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(positions)
  });
});
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

onMounted(fetchGraph)
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
  cursor: default;
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
.settings-panel {
  position: absolute;
  top: 60px;
  right: 20px;
  background: #fff;
  padding: 12px;
  border: 1px solid #888;
  border-radius: 4px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
</style>
