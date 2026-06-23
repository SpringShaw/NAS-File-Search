<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Index Progress -->
    <div v-if="stats.is_indexing" class="px-4 py-3 border-b border-gray-50">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-[#1d1d1f]">{{ $t('indexing') }}</span>
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
          <span class="font-medium text-[#1d1d1f]">{{ formatNumber(stats.total_files || 0) }}</span> {{ $t('filesUnit') }}
        </span>
        <span v-if="stats.dirs_count">
          {{ stats.dirs_count }} {{ $t('dirsUnit') }}
        </span>
        <span v-if="stats.fulltext_files">
          {{ formatNumber(stats.fulltext_files) }} {{ $t('fulltextUnit') }}
        </span>
      </div>
      <button
        @click="$emit('rebuild')"
        :disabled="stats.is_indexing"
        class="text-xs px-3 py-1.5 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ stats.is_indexing ? $t('indexingInProgress') : $t('rebuildIndex') }}
      </button>
    </div>

    <!-- Last rebuild time -->
    <div v-if="stats.last_rebuild && !stats.is_indexing" class="px-4 pb-2 text-xs text-gray-400">
      {{ $t('lastRebuild') }}: {{ formatTime(stats.last_rebuild) }}
    </div>
  </div>
</template>

<script>
import { getCurrentInstance } from 'vue'
import { i18n } from '../i18n.js'

export default {
  name: 'IndexStatus',
  props: {
    stats: { type: Object, default: () => ({}) },
  },
  emits: ['rebuild'],
  setup() {
    const { proxy } = getCurrentInstance()

    const formatNumber = (n) => {
      if (n >= 10000) {
        if (i18n.lang === 'zh') return (n / 10000).toFixed(1) + '万'
        return (n / 1000).toFixed(1) + 'k'
      }
      return n.toLocaleString()
    }

    const formatTime = (t) => {
      if (!t) return ''
      try {
        const d = new Date(t)
        const now = new Date()
        const diff = (now - d) / 1000
        if (diff < 60) return proxy.$t('justNow')
        if (diff < 3600) return proxy.$t('minutesAgo', { n: Math.floor(diff / 60) })
        if (diff < 86400) return proxy.$t('hoursAgo', { n: Math.floor(diff / 3600) })
        const locale = i18n.lang === 'zh' ? 'zh-CN' : 'en-US'
        return d.toLocaleDateString(locale) + ' ' + d.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
      } catch {
        return t
      }
    }

    return { formatNumber, formatTime }
  },
}
</script>
