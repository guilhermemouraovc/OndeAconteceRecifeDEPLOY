<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Coleta de eventos" />

      <q-card flat bordered class="scraper-card">
        <q-card-section>
          <p class="scraper-intro">
            Recarrega eventos da API TicketPE (Recife), processa pelo pipeline e atualiza o feed.
          </p>

          <q-list dark bordered class="rounded-borders q-mb-lg">
            <q-item>
              <q-item-section avatar>
                <q-icon name="sync" color="accent" />
              </q-item-section>
              <q-item-section>
                <q-item-label>TicketPE</q-item-label>
                <q-item-label caption>GET /api/v1/events?city=Recife</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>

          <q-btn
            color="primary"
            :label="loading ? 'Coletando...' : 'Executar coleta'"
            icon="play_arrow"
            no-caps
            unelevated
            :loading="loading"
            @click="executarScraper"
          />

          <q-banner v-if="erro" class="bg-negative text-white q-mt-md" dense rounded>{{ erro }}</q-banner>

          <q-card v-if="resultado" flat bordered class="result-card q-mt-lg">
            <q-card-section>
              <div class="text-h6 text-white">Resultado</div>
              <pre class="result-json">{{ JSON.stringify(resultado, null, 2) }}</pre>
            </q-card-section>
          </q-card>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useEventsStore } from 'src/stores/events'
import PageHeader from 'components/PageHeader.vue'

const { postJson } = useApi()
const store = useEventsStore()

const loading = ref(false)
const resultado = ref(null)
const erro = ref('')

async function executarScraper() {
  loading.value = true
  erro.value = ''
  resultado.value = null
  try {
    resultado.value = await postJson('/scraper/run')
    await store.fetchEvents(true)
  } catch (e) {
    erro.value = e instanceof Error ? e.message : 'Erro ao executar scraper.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-content {
  padding-top: 16px;
  padding-bottom: 48px;
}

.scraper-card,
.result-card {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(94, 234, 212, 0.15) !important;
  border-radius: 16px;
  max-width: 720px;
}

.scraper-intro {
  color: var(--oa-muted);
  margin: 0 0 20px;
}

.result-json {
  margin: 12px 0 0;
  padding: 12px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  font-size: 0.8rem;
  overflow-x: auto;
  color: var(--oa-accent);
}
</style>
