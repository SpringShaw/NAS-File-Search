<template>
  <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4">
    <button
      v-for="t in types"
      :key="t.key"
      @click="$emit('change', t.key)"
      class="flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
      :class="activeType === t.key
        ? 'bg-[#1d1d1f] text-white shadow-sm'
        : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'"
    >
      <span class="mr-1">{{ t.icon }}</span>
      {{ t.label }}
      <span v-if="t.count > 0" class="ml-1 text-xs opacity-60">{{ t.count }}</span>
    </button>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'TypeFilter',
  props: {
    activeType: { type: String, default: 'all' },
    typeStats: { type: Array, default: () => [] },
  },
  emits: ['change'],
  setup(props) {
    const iconMap = {
      '全部': '📋',
      '图片': '🖼️',
      '视频': '🎬',
      '文档': '📄',
      '日志': '📋',
      '脚本': '📜',
      '压缩包': '📦',
      '音频': '🎵',
      '其他': '📁',
    }
    const keyMap = {
      '全部': 'all',
      '图片': '图片',
      '视频': '视频',
      '文档': '文档',
      '日志': '日志',
      '脚本': '脚本',
      '压缩包': '压缩包',
      '音频': '音频',
      '其他': '其他',
    }

    const types = computed(() => {
      const all = { key: 'all', label: '全部', icon: '📋', count: 0 }
      const cats = Object.keys(iconMap).filter(k => k !== '全部').map(k => ({
        key: keyMap[k],
        label: k,
        icon: iconMap[k],
        count: 0,
      }))

      for (const s of props.typeStats) {
        const cat = cats.find(c => c.key === s.type)
        if (cat) {
          cat.count = s.count
          all.count += s.count
        }
      }
      return [all, ...cats]
    })

    return { types }
  },
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
