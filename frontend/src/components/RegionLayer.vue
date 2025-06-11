// RegionLayer.vue
<template>
  <div>
    <v-stage :config="stageConfig">
      <v-layer>
        <!-- Отрисовка регионов -->
        <v-rect
          v-for="region in regions"
          :key="region.id"
          :x="region.x"
          :y="region.y"
          :width="region.width"
          :height="region.height"
          :fill="region.color || '#b8b8b853'"
          :stroke="'black'"
          :strokeWidth="1"
          @click="selectRegion(region)"
        />

        <!-- Подписи регионов -->
        <v-text
          v-for="region in regions"
          :key="region.id + '-label'"
          :x="region.x + 5"
          :y="region.y + 5"
          :text="region.name"
          fontSize="14"
          fill="black"
        />
      </v-layer>
    </v-stage>

    <!-- Форма редактирования региона -->
    <div v-if="editingRegion" class="region-editor">
      <label>Имя:</label>
      <input v-model="editingRegion.name" />

      <label>X:</label>
      <input type="number" v-model.number="editingRegion.x" />

      <label>Y:</label>
      <input type="number" v-model.number="editingRegion.y" />

      <label>Ширина:</label>
      <input type="number" v-model.number="editingRegion.width" />

      <label>Высота:</label>
      <input type="number" v-model.number="editingRegion.height" />

      <label>Цвет:</label>
      <input type="color" v-model="editingRegion.color" />

      <button @click="saveRegion">OK</button>
    </div>
  </div>
</template>

<script>
import { Stage, Layer, Rect, Text } from 'vue-konva';

export default {
  components: { 'v-stage': Stage, 'v-layer': Layer, 'v-rect': Rect, 'v-text': Text },
  data() {
    return {
      regions: [],
      editingRegion: null,
      stageConfig: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    };
  },
  mounted() {
    this.loadRegions();
  },
  methods: {
    async loadRegions() {
      const res = await fetch('/api/regions');
      this.regions = await res.json();
    },
    selectRegion(region) {
      this.editingRegion = { ...region };
    },
    async saveRegion() {
      await fetch('/api/regions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.editingRegion)
      });
      this.editingRegion = null;
      await this.loadRegions();
    }
  }
};
</script>

<style scoped>
.region-editor {
  position: absolute;
  top: 20px;
  left: 20px;
  background: white;
  padding: 10px;
  border: 1px solid #ccc;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 200px;
}

.region-editor input[type="text"],
.region-editor input[type="number"],
.region-editor input[type="color"] {
  width: 100%;
}
</style>
