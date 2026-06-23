<template>
  <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4">
    <button
      v-for="item in types"
      :key="item.key"
      @click="$emit('change', item.key)"
      class="flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
      :class="activeType === item.key
        ? 'bg-[#1d1d1f] text-white shadow-sm'
        : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'"
    >
      <span class="mr-1">{{ item.icon }}</span>
      {{ categoryLabel(item.key) }}
      <span v-if="item.count > 0" class="ml-1 text-xs opacity-60">{{ item.count }}</span>
    </button>
  </div>
</template>

<script>
import { computed } from 'vue'
import { CATEGORY_KEYS } from '../i18n.js'

// 图标按分类中文键固定映射，不受语言影响
const ICON_MAP = {
  '图片': '🖼️',
  '视频': '🎬',
  '文档': '📄',
  '日志': '📋',
  '脚本': '📜',
  '压缩包': '📦',
  '音频': '🎵',
  '其他': '📁',
}

export default {
  name: 'TypeFilter',
  props: {
    activeType: { type: String, default: 'all' },
    typeStats: { type: Array, default: () => [] },
  },
  emits: ['change'],
  setup(props) {
    const types = computed(() => {
      const all = { key: 'all', label: '全部', icon: '📋', count: 0 }
      // 中文键保持不变（与后端 /api/search?type= 契约一致），仅 label 走 i18n
      const cats = Object.keys(ICON_MAP).map((zhKey) => ({
        key: zhKey,
        label: '', // 在下面用 $t 填充
        icon: ICON_MAP[zhKey],
        count: 0,
      }))

      for (const s of props.typeStats) {
        const cat = cats.find((c) => c.key === s.type)
        if (cat) {
          cat.count = s.count
          all.count += s.count
        }
      }
      return [all, ...cats]
    })

    return { types }
  },
  methods: {
    categoryLabel(zhKey) {
      if (zhKey === 'all') return this.$t('cat_all')
      return this.$t(CATEGORY_KEYS[zhKey] || 'cat_other')
    },
  },
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
