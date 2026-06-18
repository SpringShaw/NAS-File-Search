<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Index Progress -->
    <div v-if="stats.is_indexing" class="px-4 py-3 border-b border-gray-50">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-[#1d1d1f]">🔄 正在建立索引...</span>
        <span class="text-xs text-gray-500">{{ Math.round(stats.progress || 0) }}%</span>
      </div>
      <div class="w-full bg-gray-100 rounded-full h-1.5">
        <div
          class="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
          :style="{ width: (stats.progress || 0) + '%' }"
        ></div>
      </div>
      <p v-if="stats.current_file" class="text-xs text-gray-400 mt-1 truncate">
        {{ stats.current_file }}
      </p>
    </div>

    <!-- Stats Bar -->
    <div class="px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-4 text-sm text-gray-500">
        <span>
          <span class="font-medium text-[#1d1d1f]">{{ formatNumber(stats.total_files || 0) }}</span> 个文件
        </span>
        <span v-if="stats.dirs_count">
          {{ stats.dirs_count }} 个目录
        </span>
        <span v-if="stats.fulltext_files">
          {{ formatNumber(stats.fulltext_files) }} 个全文索引
        </span>
      </div>
      <button
        @click="$emit('rebuild')"
        :disabled="stats.is_indexing"
        class="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ stats.is_indexing ? '索引中...' : '🔄 重建索引' }}
      </button>
    </div>

    <!-- Last rebuild time -->
    <div v-if="stats.last_rebuild && !stats.is_indexing" class="px-4 pb-2 text-xs text-gray-400">
      最后索引: {{ formatTime(stats.last_rebuild) }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'IndexStatus',
  props: {
    stats: { type: Object, default: () => ({}) },
  },
  emits: ['rebuild'],
  setup() {
    const formatNumber = (n) => {
      if (n >= 10000) return (n / 10000).toFixed(1) + '万'
      return n.toLocaleString()
    }

    const formatTime = (t) => {
      if (!t) return ''
      try {
        const d = new Date(t)
        const now = new Date()
        const diff = (now - d) / 1000
        if (diff < 60) return '刚刚'
        if (diff < 3600) return Math.floor(diff / 60) + ' 分钟前'
        if (diff < 86400) return Math.floor(diff / 3600) + ' 小时前'
        return d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      } catch {
        return t
      }
    }

    return { formatNumber, formatTime }
  },
}
</script>
