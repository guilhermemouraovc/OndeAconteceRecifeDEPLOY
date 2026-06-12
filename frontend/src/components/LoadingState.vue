<template>
  <div class="loading-state" role="status" aria-live="polite">
    <q-spinner-dots color="primary" size="48px" />
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: 'Carregando...' },
})
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 64px 20px;
  color: var(--oa-muted);
}
</style>
