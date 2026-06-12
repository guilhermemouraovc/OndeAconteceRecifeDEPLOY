<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Cadastrar evento" />

      <q-card flat bordered class="form-card">
        <q-card-section>
          <p class="form-intro">
            Envie um flyer e revise manualmente os dados do evento. O cadastro vai para moderacao
            antes de aparecer no feed.
          </p>

          <div class="upload-block q-mb-lg">
            <q-file
              v-model="flyerFile"
              accept="image/*"
              outlined
              dark
              dense
              clearable
              label="Flyer do evento (opcional)"
            />

            <div class="upload-actions">
              <q-btn
                color="secondary"
                label="Preparar flyer"
                no-caps
                unelevated
                :disable="!flyerFile"
                :loading="uploadingFlyer"
                @click="prepareFlyer"
              />
              <q-badge v-if="flyerPath" color="accent" text-color="dark" rounded>
                Enviado via flyer
              </q-badge>
            </div>

            <q-img v-if="flyerPreviewUrl" :src="flyerPreviewUrl" class="flyer-preview" fit="contain" />
          </div>

          <q-form class="q-gutter-md" @submit.prevent="onSubmit">
            <q-input v-model="form.titulo" label="Titulo *" outlined dark dense />
            <q-input v-model="form.descricao" label="Descricao" type="textarea" outlined dark autogrow />
            <q-select
              v-model="form.categoria"
              :options="categorias"
              label="Categoria"
              outlined
              dark
              dense
              clearable
            />
            <q-input v-model="form.bairro" label="Bairro" outlined dark dense />
            <q-input v-model="form.local" label="Local" outlined dark dense />
            <q-input v-model="form.inicio_iso" label="Data/hora (ISO)" hint="Ex: 2026-06-15T19:00" outlined dark dense />
            <q-input v-model="form.preco" label="Preco (R$)" type="number" outlined dark dense />
            <q-toggle v-model="form.gratuito" label="Evento gratuito" color="primary" dark />
            <q-input
              v-model="form.observacoes_flyer"
              label="Observacoes do flyer"
              type="textarea"
              outlined
              dark
              autogrow
            />
            <q-input v-model="form.organizador" label="Organizador *" outlined dark dense />
            <q-input v-model="form.email_contato" label="E-mail de contato *" type="email" outlined dark dense />

            <q-banner v-if="error" class="bg-negative text-white" dense rounded>{{ error }}</q-banner>
            <q-banner v-if="message" class="bg-positive text-white" dense rounded>{{ message }}</q-banner>

            <q-btn
              type="submit"
              color="primary"
              label="Enviar para moderacao"
              no-caps
              unelevated
              :loading="loading"
            />
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useApi } from 'src/composables/useApi'
import { useEventsStore } from 'src/stores/events'
import { PRODUCER_CATEGORIES } from 'src/constants/config'
import PageHeader from 'components/PageHeader.vue'

const { postJson, postFormData, base } = useApi()
const store = useEventsStore()

const categorias = PRODUCER_CATEGORIES
const flyerFile = ref(null)
const flyerPath = ref('')
const flyerPreviewUrl = ref('')
const uploadingFlyer = ref(false)
const form = reactive({
  titulo: '',
  descricao: '',
  categoria: '',
  bairro: '',
  local: '',
  inicio_iso: '',
  preco: '',
  gratuito: false,
  observacoes_flyer: '',
  organizador: '',
  email_contato: '',
})

const loading = ref(false)
const message = ref('')
const error = ref('')

function validate() {
  if (form.titulo.trim().length < 3) return 'Informe um titulo com pelo menos 3 caracteres.'
  if (!form.organizador.trim()) return 'Informe o organizador.'
  if (!form.email_contato.includes('@')) return 'Informe um e-mail valido.'
  return ''
}

async function prepareFlyer() {
  if (!flyerFile.value) return
  uploadingFlyer.value = true
  error.value = ''
  try {
    const payload = new FormData()
    payload.append('file', flyerFile.value)
    const data = await postFormData('/events/flyer/preview', payload)
    flyerPath.value = data.flyer_path
    flyerPreviewUrl.value = `${base}${data.flyer_url}`
    Object.assign(form, {
      ...form,
      ...data.campos_sugeridos,
    })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Erro ao preparar flyer.'
  } finally {
    uploadingFlyer.value = false
  }
}

async function onSubmit() {
  message.value = ''
  error.value = ''
  const v = validate()
  if (v) {
    error.value = v
    return
  }

  loading.value = true
  try {
    const preco = form.preco === '' ? null : Number(form.preco)
    const payload = {
      titulo: form.titulo.trim(),
      descricao: form.descricao.trim(),
      categoria: form.categoria || null,
      bairro: form.bairro.trim() || null,
      local: form.local.trim(),
      inicio_iso: form.inicio_iso.trim() || null,
      preco: Number.isFinite(preco) ? preco : null,
      gratuito: form.gratuito || null,
      observacoes_flyer: form.observacoes_flyer.trim() || null,
      organizador: form.organizador.trim(),
      email_contato: form.email_contato.trim(),
      flyer_path: flyerPath.value || null,
    }

    if (flyerPath.value) await postJson('/events/flyer/submit', payload)
    else await postJson('/events', payload)

    message.value = 'Evento enviado para moderacao.'
    flyerFile.value = null
    flyerPath.value = ''
    flyerPreviewUrl.value = ''
    Object.assign(form, {
      titulo: '',
      descricao: '',
      categoria: '',
      bairro: '',
      local: '',
      inicio_iso: '',
      preco: '',
      gratuito: false,
      observacoes_flyer: '',
      organizador: '',
      email_contato: '',
    })
    await store.fetchEvents(true)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Erro ao cadastrar.'
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

.form-card {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(94, 234, 212, 0.15) !important;
  border-radius: 16px;
  max-width: 720px;
}

.form-intro {
  color: var(--oa-muted);
  margin: 0 0 20px;
  line-height: 1.6;
}

.upload-block {
  display: grid;
  gap: 12px;
}

.upload-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.flyer-preview {
  max-width: 360px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.04);
}
</style>
