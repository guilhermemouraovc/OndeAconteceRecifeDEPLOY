<template>
  <div class="chatbot-panel">
    <q-btn
      fab
      color="accent"
      icon="smart_toy"
      class="chatbot-fab"
      :style="{ bottom: fabBottom }"
      aria-label="Abrir chatbot"
      @click="open = !open"
    />

    <q-drawer
      v-model="open"
      side="right"
      overlay
      bordered
      dark
      :width="$q.screen.lt.md ? 320 : 380"
      class="chatbot-drawer"
    >
      <div class="chatbot-shell">
        <div class="chatbot-header">
          <div>
            <div class="chatbot-title font-display">Assistente de agenda</div>
            <div class="chatbot-subtitle">Busca simples nos eventos aprovados</div>
          </div>
          <q-btn flat round dense icon="close" @click="open = false" />
        </div>

        <div class="chatbot-suggestions">
          <q-btn
            v-for="suggestion in suggestions"
            :key="suggestion"
            outline
            no-caps
            dense
            color="accent"
            :label="suggestion"
            @click="useSuggestion(suggestion)"
          />
        </div>

        <q-scroll-area class="chatbot-messages">
          <div class="chatbot-stack">
            <div
              v-for="(message, idx) in messages"
              :key="idx"
              class="chatbot-message"
              :class="`chatbot-message--${message.role}`"
            >
              <div class="chatbot-bubble">{{ message.text }}</div>
            </div>
          </div>
        </q-scroll-area>

        <q-banner v-if="error" rounded dense class="bg-negative text-white">
          {{ error }}
        </q-banner>

        <q-form class="chatbot-form" @submit.prevent="submit">
          <q-input
            v-model="draft"
            dense
            outlined
            dark
            placeholder="Pergunte por shows, teatro, gratis..."
            :disable="loading"
          />
          <q-btn type="submit" color="primary" no-caps unelevated :loading="loading" label="Enviar" />
        </q-form>
      </div>
    </q-drawer>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useChatbot } from 'src/composables/useChatbot'

const open = ref(false)
const draft = ref('')
const suggestions = ['Eventos gratuitos', 'Teatro no Recife', 'O que tem hoje?']
const { loading, error, messages, sendMessage } = useChatbot()

const fabBottom = ref('20px')
let observer = null

function updateFabPosition() {
  const footer = document.querySelector('.oa-footer')
  if (footer) {
    const h = footer.getBoundingClientRect().height
    fabBottom.value = `${h + 16}px`
  } else {
    fabBottom.value = '20px'
  }
}

onMounted(() => {
  updateFabPosition()

  const footer = document.querySelector('.oa-footer')
  if (footer && window.ResizeObserver) {
    observer = new ResizeObserver(updateFabPosition)
    observer.observe(footer)
  }

  window.addEventListener('resize', updateFabPosition)
})

onUnmounted(() => {
  observer?.disconnect()
  window.removeEventListener('resize', updateFabPosition)
})

async function submit() {
  const text = draft.value.trim()
  if (!text) return
  draft.value = ''
  await sendMessage(text)
}

async function useSuggestion(text) {
  open.value = true
  draft.value = text
  await submit()
}
</script>

<style lang="scss">
.chatbot-drawer {
  background: #0b1624 !important;
  color: var(--oa-text);
}
</style>

<style scoped lang="scss">
.chatbot-fab {
  position: fixed;
  right: 20px;
  z-index: 1200;
  transition: bottom 0.2s ease;
}

.chatbot-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
  gap: 14px;
}

.chatbot-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.chatbot-title {
  font-size: 1.1rem;
  font-weight: 700;
}

.chatbot-subtitle {
  color: var(--oa-muted);
  font-size: 0.82rem;
}

.chatbot-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chatbot-messages {
  flex: 1;
  min-height: 260px;
}

.chatbot-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chatbot-message {
  display: flex;
}

.chatbot-message--user {
  justify-content: flex-end;
}

.chatbot-message--assistant {
  justify-content: flex-start;
}

.chatbot-bubble {
  max-width: 92%;
  padding: 12px 14px;
  border-radius: 14px;
  white-space: pre-line;
  background: rgba(255, 255, 255, 0.08);
}

.chatbot-message--user .chatbot-bubble {
  background: rgba(94, 234, 212, 0.18);
}

.chatbot-form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: center;
}
</style>