<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Moderação" />

      <q-card flat bordered class="moderacao-card">
        <q-card-section class="q-gutter-md">
          <q-input
            v-model="moderatorKey"
            label="Moderator key"
            hint="Padrao do projeto: demo-moderador"
            outlined
            dark
            dense
          />
          <q-btn color="primary" no-caps unelevated label="Carregar pendentes" :loading="loading" @click="load" />
          <q-banner v-if="error" class="bg-negative text-white" dense rounded>{{ error }}</q-banner>
        </q-card-section>

        <q-separator dark />

        <div class="moderacao-layout">
          <div class="moderacao-list">
            <q-list dark separator>
              <q-item
                v-for="event in pendentes"
                :key="event.id"
                clickable
                :active="selected?.id === event.id"
                active-class="moderacao-item--active"
                @click="selected = event"
              >
                <q-item-section>
                  <q-item-label>{{ event.titulo }}</q-item-label>
                  <q-item-label caption>{{ event.categoria || 'Sem categoria' }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
            <div v-if="!pendentes.length && !loading" class="empty-state">Nenhum evento pendente.</div>
          </div>

          <div class="moderacao-detail">
            <template v-if="selected">
              <q-img v-if="selected.flyer_path" :src="flyerUrl(selected.flyer_path)" class="detail-flyer" fit="contain" />
              <div class="detail-grid">
                <div><strong>Titulo:</strong> {{ selected.titulo }}</div>
                <div><strong>Categoria:</strong> {{ selected.categoria || 'Nao informada' }}</div>
                <div><strong>Bairro:</strong> {{ selected.bairro || 'Nao informado' }}</div>
                <div><strong>Local:</strong> {{ selected.local || 'Nao informado' }}</div>
                <div><strong>Inicio:</strong> {{ selected.inicio_iso || 'Nao informado' }}</div>
                <div><strong>Preco:</strong> {{ selected.gratuito ? 'Gratuito' : selected.preco ?? 'Nao informado' }}</div>
                <div><strong>Organizador:</strong> {{ selected.organizador }}</div>
                <div><strong>Canal:</strong> {{ selected.cadastro_via }}</div>
              </div>

              <q-input
                v-model="rejectionReason"
                label="Motivo da rejeicao"
                type="textarea"
                outlined
                dark
                autogrow
              />

              <div class="detail-actions">
                <q-btn color="positive" no-caps unelevated label="Aprovar" @click="approveSelected" />
                <q-btn color="negative" no-caps unelevated label="Rejeitar" @click="rejectSelected" />
              </div>
            </template>

            <div v-else class="empty-state">Selecione um evento pendente para moderar.</div>
          </div>
        </div>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useModerationApi } from 'src/composables/useModerationApi'
import PageHeader from 'components/PageHeader.vue'

const { base } = useApi()
const { loading, error, defaultKey, fetchPendentes, aprovar, rejeitar } = useModerationApi()

const moderatorKey = ref(defaultKey)
const pendentes = ref([])
const selected = ref(null)
const rejectionReason = ref('')

function flyerUrl(path) {
  return `${base}${path}`
}

async function load() {
  pendentes.value = await fetchPendentes(moderatorKey.value)
  selected.value = pendentes.value[0] || null
  rejectionReason.value = ''
}

async function approveSelected() {
  if (!selected.value) return
  await aprovar(selected.value.id, moderatorKey.value)
  await load()
}

async function rejectSelected() {
  if (!selected.value || rejectionReason.value.trim().length < 3) return
  await rejeitar(selected.value.id, rejectionReason.value.trim(), moderatorKey.value)
  await load()
}
</script>

<style scoped lang="scss">
.page-content {
  padding-top: 16px;
  padding-bottom: 48px;
}

.moderacao-card {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(94, 234, 212, 0.15) !important;
  border-radius: 16px;
}

.moderacao-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  min-height: 520px;
}

.moderacao-list {
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.moderacao-item--active {
  background: rgba(94, 234, 212, 0.12);
}

.moderacao-detail {
  padding: 20px;
  display: grid;
  gap: 16px;
}

.detail-flyer {
  max-width: 360px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
}

.detail-grid {
  display: grid;
  gap: 8px;
  color: #fff;
}

.detail-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.empty-state {
  color: var(--oa-muted);
  padding: 20px;
}

@media (max-width: 900px) {
  .moderacao-layout {
    grid-template-columns: 1fr;
  }

  .moderacao-list {
    border-right: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
}
</style>
