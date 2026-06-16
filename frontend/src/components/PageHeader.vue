<template>
  <div class="page-header">
    <div class="page-header__back">
      <BackButton :use-history="useHistory" :to="backTo" />
    </div>
    <h1 class="page-header__title font-display">{{ title }}</h1>
    <!-- Espaço espelhado para manter o título realmente centrado -->
    <div class="page-header__spacer" aria-hidden="true" />
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
  display: flex;
  align-items: center;
  padding: 20px 0 16px;
  gap: 12px;
  border-bottom: 1px solid linear-gradient(90deg, transparent, rgba(94, 234, 212, 0.35), transparent);
  position: relative;

  &::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(94, 234, 212, 0.35), transparent);
  }
}

.page-header__back {
  flex-shrink: 0;
}

.page-header__title {
  flex: 1;
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  text-align: center;
  margin: 0;
  line-height: 1.2;
}

/* Espelha a largura do BackButton para manter o título no centro real */
.page-header__spacer {
  flex-shrink: 0;
  width: 120px; /* aprox. largura do BackButton */
}

@media (max-width: 480px) {
  .page-header__title {
    font-size: 1.35rem;
  }

  .page-header__spacer {
    display: none;
  }

  .page-header__title {
    text-align: left;
  }
}
</style>