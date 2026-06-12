<template>
  <div class="category-filter">
    <div class="filter-header">
      <q-icon name="category" size="20px" class="filter-header__icon" />
      <span class="filter-header__title">Categorias</span>
    </div>

    <div class="category-chips" role="group" aria-label="Seleção de categorias">
      <q-chip
        v-for="cat in categories"
        :key="cat"
        clickable
        flat
        :color="modelValue === cat ? 'primary' : 'grey-9'"
        :text-color="modelValue === cat ? 'white' : 'grey-4'"
        class="category-chip"
        @click="toggle(cat)"
      >
        {{ cat }}
      </q-chip>
    </div>

    <q-btn
      v-if="modelValue"
      flat
      dense
      no-caps
      label="Limpar categoria"
      icon="close"
      color="grey-5"
      size="sm"
      class="q-mt-sm"
      @click="$emit('update:modelValue', '')"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEventsStore } from 'src/stores/events'

const props = defineProps({
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const store = useEventsStore()
const categories = computed(() => store.categoriasDisponiveis)

function toggle(cat) {
  emit('update:modelValue', props.modelValue === cat ? '' : cat)
}
</script>

<style scoped>
.category-filter {
  padding: 8px 0;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: white;
  font-weight: 600;
}

.filter-header__icon {
  color: var(--oa-accent);
}

.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
