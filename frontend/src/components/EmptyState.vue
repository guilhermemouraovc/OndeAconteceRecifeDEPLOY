<template>
  <div class="empty-state" role="status">
    <q-icon :name="icon" :size="iconSize" color="grey-5" aria-hidden="true" />
    <div class="empty-state-title font-display">{{ title }}</div>
    <div class="empty-state-text">{{ message }}</div>
    <q-btn
      v-if="showButton"
      :color="buttonColor"
      :label="buttonLabel"
      :to="buttonTo"
      no-caps
      unelevated
      :aria-label="buttonAriaLabel"
      class="q-mt-md"
      @click="$emit('button-click')"
    />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  message: { type: String, required: true },
  icon: { type: String, default: 'search_off' },
  iconSize: { type: String, default: '64px' },
  showButton: { type: Boolean, default: true },
  buttonLabel: { type: String, default: 'Ver todos os eventos' },
  buttonColor: { type: String, default: 'primary' },
  buttonTo: { type: [String, Object], default: null },
  buttonAriaLabel: { type: String, default: 'Ver todos os eventos' },
})

defineEmits(['button-click'])
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-state-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin-top: 24px;
  margin-bottom: 8px;
}

.empty-state-text {
  font-size: 1rem;
  color: var(--oa-muted);
  max-width: 400px;
  line-height: 1.6;
}
</style>
