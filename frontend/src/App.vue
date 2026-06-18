<template>
  <div class="min-h-screen bg-[#f5f5f7]">
    <!-- Header -->
    <header class="bg-white/80 backdrop-blur-xl border-b border-gray-100 sticky top-0 z-50">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🔍</span>
          <h1 class="text-lg font-semibold text-[#1d1d1f]">NAS Searcher</h1>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="stats.total_files > 0"
            class="text-xs text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full hover:bg-gray-200 transition"
          >
            {{ formatNumber(stats.total_files) }} 个文件已索引
          </button>
          <button
            @click="showSettings = !showSettings"
            class="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 transition text-lg"
          >
            ⚙️
          </button>
        </div>
      </div>
    </header>

    <!-- Settings Panel -->
    <SettingsPanel
      v-if="showSettings"
      @close="showSettings = false"
      @dirs-updated="fetchStats"
    />

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-4 pb-24">
      <!-- Search Bar -->
      <SearchBar v-model="query" @search="doSearch" />

      <!-- Type Filter -->
      <TypeFilter
        :active-type="activeType"
        :type-stats="stats.type_distribution || []"
        @change="onTypeChange"
      />

      <!-- Index Status -->
      <IndexStatus :stats="stats" @rebuild="rebuildIndex" />

      <!-- Search Results -->
      <SearchResults
        :results="results"
        :total="totalResults"
        :page="page"
        :loading="loading"
        :query="query"
        @page-change="onPageChange"
      />
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { api } from './services/api.js'
import SearchBar from './components/SearchBar.vue'
import TypeFilter from './components/TypeFilter.vue'
import IndexStatus from './components/IndexStatus.vue'
import SearchResults from './components/SearchResults.vue'
import SettingsPanel from './components/SettingsPanel.vue'

export default {
  name: 'App',
  components: { SearchBar, TypeFilter, IndexStatus, SearchResults, SettingsPanel },
  setup() {
    const query = ref('')
    const activeType = ref('all')
    const results = ref([])
    const totalResults = ref(0)
    const page = ref(1)
    const loading = ref(false)
    const showSettings = ref(false)
    const stats = ref({})

    let searchTimer = null

    const fetchStats = async () => {
      try {
        stats.value = await api.getStats()
      } catch (e) {
        console.error('Failed to fetch stats:', e)
      }
    }

    const doSearch = async () => {
      if (!query.value.trim()) {
        results.value = []
        totalResults.value = 0
        return
      }
      loading.value = true
      try {
        const res = await api.search(query.value, activeType.value, page.value)
        results.value = res.results
        totalResults.value = res.total
      } catch (e) {
        console.error('Search failed:', e)
        results.value = []
      } finally {
        loading.value = false
      }
    }

    const onTypeChange = (type) => {
      activeType.value = type
      page.value = 1
      doSearch()
    }

    const onPageChange = (p) => {
      page.value = p
      doSearch()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const rebuildIndex = async () => {
      try {
        await api.rebuildIndex()
        // Poll status
        const poll = setInterval(async () => {
          await fetchStats()
          const s = await api.getIndexStatus()
          if (!s.is_indexing) {
            clearInterval(poll)
            if (query.value) doSearch()
          }
        }, 2000)
      } catch (e) {
        console.error('Rebuild failed:', e)
      }
    }

    const formatNumber = (n) => {
      if (n >= 10000) return (n / 10000).toFixed(1) + '万'
      return n.toLocaleString()
    }

    onMounted(() => {
      fetchStats()
    })

    return {
      query, activeType, results, totalResults, page,
      loading, showSettings, stats,
      doSearch, onTypeChange, onPageChange, rebuildIndex, fetchStats, formatNumber,
    }
  },
}
</script>
