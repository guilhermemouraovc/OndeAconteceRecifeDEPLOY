<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Cadastrar evento" />

      <q-card flat bordered class="form-card">
        <q-card-section>
          <p class="form-intro">
            Envie um flyer e revise manualmente os dados do evento. O cadastro vai para moderação
            antes de aparecer no feed.
          </p>

          <!-- Upload de flyer -->
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
                label="Preencher via flyer"
                icon="auto_fix_high"
                no-caps
                unelevated
                :disable="!flyerFile"
                :loading="uploadingFlyer"
                @click="prepareFlyer"
              />
              <q-badge v-if="flyerPath" color="accent" text-color="dark" rounded>
                Preenchido via flyer
              </q-badge>
            </div>

            <q-img v-if="flyerPreviewUrl" :src="flyerPreviewUrl" class="flyer-preview" fit="contain" />
          </div>

          <div class="q-gutter-md">
            <!-- Título -->
            <q-input v-model="form.titulo" label="Título *" outlined dark dense />

            <!-- Descrição -->
            <q-input v-model="form.descricao" label="Descrição" type="textarea" outlined dark autogrow />

            <!-- Categoria -->
            <q-select
              v-model="form.categoria"
              :options="categorias"
              label="Categoria"
              outlined
              dark
              dense
              clearable
            />

            <!-- Bairro + Local -->
            <div class="form-row">
              <q-input v-model="form.bairro" label="Bairro" outlined dark dense class="col" />
              <q-input v-model="form.local" label="Local / Endereço" outlined dark dense class="col" />
            </div>

            <!-- Data e Hora — picker visual -->
            <div class="form-row">
              <q-input
                v-model="form.data"
                label="Data *"
                outlined
                dark
                dense
                class="col"
                readonly
              >
                <template #append>
                  <q-icon name="event" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-date
                        v-model="form.data"
                        mask="YYYY-MM-DD"
                        dark
                        color="primary"
                        :locale="ptBRLocale"
                        minimal
                      />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>

              <q-input
                v-model="form.hora"
                label="Horário"
                outlined
                dark
                dense
                class="col"
                readonly
              >
                <template #append>
                  <q-icon name="schedule" class="cursor-pointer">
                    <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                      <q-time
                        v-model="form.hora"
                        mask="HH:mm"
                        dark
                        color="primary"
                        format24h
                      />
                    </q-popup-proxy>
                  </q-icon>
                </template>
              </q-input>
            </div>

            <!-- Preço -->
            <div class="form-row">
              <q-input
                v-model="form.preco"
                label="Preço (R$)"
                type="number"
                outlined
                dark
                dense
                class="col"
                :disable="form.gratuito"
              />
              <div class="col gratuito-toggle">
                <q-toggle v-model="form.gratuito" label="Evento gratuito" color="primary" dark />
              </div>
            </div>

            <!-- Observações do flyer -->
            <q-input
              v-model="form.observacoes_flyer"
              label="Observações do flyer"
              type="textarea"
              outlined
              dark
              autogrow
            />

            <!-- Organizador + e-mail -->
            <div class="form-row">
              <q-input v-model="form.organizador" label="Organizador *" outlined dark dense class="col" />
              <q-input v-model="form.email_contato" label="E-mail de contato *" type="email" outlined dark dense class="col" />
            </div>

            <q-banner v-if="error" class="bg-negative text-white" dense rounded>{{ error }}</q-banner>
            <q-banner v-if="message" class="bg-positive text-white" dense rounded>{{ message }}</q-banner>

            <q-btn
              color="primary"
              label="Enviar para moderação"
              no-caps
              unelevated
              :loading="loading"
              @click="onSubmit"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
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
  data: '',   // YYYY-MM-DD
  hora: '',   // HH:mm
  preco: '',
  gratuito: false,
  observacoes_flyer: '',
  organizador: '',
  email_contato: '',
})

// Zera preço quando gratuito é marcado
watch(() => form.gratuito, (val) => { if (val) form.preco = '' })

// Monta inicio_iso a partir de data + hora
const inicio_iso = computed(() => {
  if (!form.data) return ''
  return form.hora ? `${form.data}T${form.hora}` : `${form.data}T00:00`
})

const ptBRLocale = {
  days: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
  daysShort: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
  months: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
  monthsShort: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
  firstDayOfWeek: 0,
}

const loading = ref(false)
const message = ref('')
const error = ref('')

function validate() {
  if (form.titulo.trim().length < 3) return 'Informe um título com pelo menos 3 caracteres.'
  if (!form.organizador.trim()) return 'Informe o organizador.'
  if (!form.email_contato.includes('@')) return 'Informe um e-mail válido.'
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

    // Preenche campos com sugestões do OCR
    const s = data.campos_sugeridos || {}
    if (s.titulo) form.titulo = s.titulo
    if (s.descricao) form.descricao = s.descricao
    if (s.categoria) form.categoria = s.categoria
    if (s.bairro) form.bairro = s.bairro
    if (s.local) form.local = s.local
    if (s.organizador) form.organizador = s.organizador
    if (s.observacoes_flyer) form.observacoes_flyer = s.observacoes_flyer
    // Tenta extrair data e hora do inicio_iso sugerido
    if (s.inicio_iso) {
      const [datePart, timePart] = s.inicio_iso.split('T')
      if (datePart) form.data = datePart
      if (timePart) form.hora = timePart.slice(0, 5)
    }
    if (s.preco != null) form.preco = String(s.preco)
    if (s.gratuito != null) form.gratuito = Boolean(s.gratuito)
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
  if (v) { error.value = v; return }

  loading.value = true
  try {
    const preco = form.preco === '' ? null : Number(form.preco)
    const payload = {
      titulo: form.titulo.trim(),
      descricao: form.descricao.trim(),
      categoria: form.categoria || null,
      bairro: form.bairro.trim() || null,
      local: form.local.trim(),
      inicio_iso: inicio_iso.value || null,
      preco: Number.isFinite(preco) ? preco : null,
      gratuito: form.gratuito || null,
      observacoes_flyer: form.observacoes_flyer.trim() || null,
      organizador: form.organizador.trim(),
      email_contato: form.email_contato.trim(),
      flyer_path: flyerPath.value || null,
    }

    if (flyerPath.value) await postJson('/events/flyer/submit', payload)
    else await postJson('/events', payload)

    message.value = 'Evento enviado para moderação com sucesso!'
    flyerFile.value = null
    flyerPath.value = ''
    flyerPreviewUrl.value = ''
    Object.assign(form, {
      titulo: '', descricao: '', categoria: '', bairro: '', local: '',
      data: '', hora: '', preco: '', gratuito: false,
      observacoes_flyer: '', organizador: '', email_contato: '',
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.gratuito-toggle {
  display: flex;
  align-items: center;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>