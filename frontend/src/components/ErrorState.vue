<template>
  <div class="error-state" role="alert">
    <q-icon name="error_outline" size="48px" color="negative" />
    <p class="error-state__title">{{ title }}</p>
    <p class="error-state__msg">{{ message }}</p>
    <q-btn v-if="showRetry" color="primary" :label="retryLabel" no-caps unelevated @click="$emit('retry')" />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Algo deu errado' },
  message: { type: String, required: true },
  showRetry: { type: Boolean, default: true },
  retryLabel: { type: String, default: 'Tentar novamente' },
})

defineEmits(['retry'])
</script>

<style scoped>
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 20px;
  text-align: center;
}

.error-state__title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.error-state__msg {
  color: var(--oa-muted);
  max-width: 420px;
  margin: 0 0 8px;
}
</style>
