<template>
  <div class="page-header">
    <BackButton :use-history="useHistory" :to="backTo" />
    <div class="page-title font-display">{{ title }}</div>
    <div class="title-divider" />
  </div>
</template>

<script setup>
import BackButton from './BackButton.vue'

defineProps({
  title: { type: String, required: true },
  useHistory: { type: Boolean, default: false },
  backTo: { type: [String, Object], default: '/' },
})
</script>

<style scoped lang="scss">
.page-header {
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  text-align: center;
}

.title-divider {
  width: 100%;
  max-width: 1440px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(94, 234, 212, 0.35), transparent);
}
</style>
