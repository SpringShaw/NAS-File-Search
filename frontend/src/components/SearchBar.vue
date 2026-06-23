<template>
  <div class="my-6">
    <div
      class="relative bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transition-all duration-200"
      :class="{ 'ring-2 ring-blue-400/30 shadow-md': focused }"
    >
      <div class="flex items-center px-4 py-3">
        <span class="text-gray-400 text-xl mr-3 flex-shrink-0">🔍</span>
        <input
          ref="inputEl"
          v-model="localQuery"
          type="text"
          :placeholder="$t('searchPlaceholder')"
          class="flex-1 text-lg text-[#1d1d1f] placeholder-gray-400 outline-none bg-transparent"
          @input="onInput"
          @keydown.enter="onSearch"
          @focus="focused = true"
          @blur="focused = false"
        />
        <button
          v-if="localQuery"
          @click="clearQuery"
          class="ml-2 w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 text-gray-500 text-sm hover:bg-gray-200 transition"
        >
          ✕
        </button>
      </div>
    </div>
    <p v-if="!query" class="text-center text-xs text-gray-400 mt-2">
      {{ $t('searchHint') }}
    </p>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'SearchBar',
  props: {
    modelValue: { type: String, default: '' },
  },
  emits: ['update:modelValue', 'search'],
  setup(props, { emit }) {
    const localQuery = ref(props.modelValue)
    const focused = ref(false)
    const inputEl = ref(null)
    let debounceTimer = null

    watch(() => props.modelValue, (v) => { localQuery.value = v })

    const onInput = () => {
      emit('update:modelValue', localQuery.value)
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        emit('search')
      }, 300)
    }

    const onSearch = () => {
      clearTimeout(debounceTimer)
      emit('search')
    }

    const clearQuery = () => {
      localQuery.value = ''
      emit('update:modelValue', '')
      emit('search')
      inputEl.value?.focus()
    }

    return { localQuery, focused, inputEl, onInput, onSearch, clearQuery }
  },
}
</script>
