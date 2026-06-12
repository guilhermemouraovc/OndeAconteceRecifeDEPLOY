<template>
  <div
    class="back-button-container"
    role="button"
    tabindex="0"
    :aria-label="ariaLabel"
    @click="handleClick"
    @keydown.enter="handleClick"
  >
    <div class="back-icon">
      <q-icon name="arrow_back" size="24px" class="back-arrow-icon" />
    </div>
    <span class="back-text">{{ label }}</span>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  label: { type: String, default: 'Voltar' },
  to: { type: [String, Object], default: '/' },
  useHistory: { type: Boolean, default: false },
})

const router = useRouter()
const ariaLabel = `Voltar para ${typeof props.to === 'string' ? props.to : 'página anterior'}`

function handleClick() {
  if (props.useHistory && window.history.length > 1) router.back()
  else router.push(props.to)
}
</script>

<style scoped lang="scss">
.back-button-container {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.08);
  }

  &:focus-visible {
    outline: 2px solid var(--oa-accent);
    outline-offset: 4px;
  }
}

.back-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-text {
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.back-arrow-icon {
  color: var(--oa-teal) !important;
}
</style>
