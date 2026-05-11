<script setup>
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useApi } from '@/composables/useApi.js'

const { postJson } = useApi()

const form = reactive({
  titulo: '',
  descricao: '',
  categoria: '',
  bairro: '',
  local: '',
  inicio_iso: '',
  preco: '',
  gratuito: null,
  organizador: '',
  email_contato: '',
})

const loading = ref(false)
const message = ref('')
const error = ref('')
const resultado = ref(null)

const categorias = [
  '',
  'Música ao vivo',
  'Teatro',
  'Dança',
  'Cinema',
  'Exposição',
  'Literatura',
  'Oficina',
  'Festival',
  'Feira cultural',
  'Patrimônio e memória',
  'Infantil',
  'Outros',
]

function parsePreco() {
  if (form.preco === '' || form.preco == null) return null
  const n = Number(String(form.preco).replace(',', '.'))
  return Number.isFinite(n) ? n : null
}

function validate() {
  if (form.titulo.trim().length < 3) return 'Informe um título com pelo menos 3 caracteres.'
  if (!form.organizador.trim()) return 'Informe o nome do organizador.'
  if (!form.email_contato.includes('@')) return 'Informe um e-mail de contato válido.'
  return ''
}

async function onSubmit() {
  message.value = ''
  error.value = ''
  resultado.value = null
  const v = validate()
  if (v) {
    error.value = v
    return
  }
  loading.value = true
  try {
    const body = {
      titulo: form.titulo.trim(),
      descricao: form.descricao.trim(),
      categoria: form.categoria || null,
      bairro: form.bairro.trim() || null,
      local: form.local.trim(),
      inicio_iso: form.inicio_iso.trim() || null,
      preco: parsePreco(),
      gratuito:
        form.gratuito === true ? true : form.gratuito === false ? false : null,
      organizador: form.organizador.trim(),
      email_contato: form.email_contato.trim(),
    }
    const row = await postJson('/events', body)
    resultado.value = row
    message.value = 'Evento cadastrado. O pipeline normalizou bairro e categoria e estimou gratuito/pago pelo texto.'
    form.titulo = ''
    form.descricao = ''
    form.categoria = ''
    form.bairro = ''
    form.local = ''
    form.inicio_iso = ''
    form.preco = ''
    form.gratuito = null
    form.organizador = ''
    form.email_contato = ''
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Falha ao enviar.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <header class="top">
      <RouterLink to="/" class="back">← Voltar à agenda</RouterLink>
      <h1 class="title">Cadastro de evento cultural</h1>
      <p class="lead">
        Formulário autônomo para produtoras (SCRUM-14). Os dados são enviados à API, normalizados
        (bairros e categorias) e classificados por texto (SCRUM-33).
      </p>
    </header>

    <form class="form" @submit.prevent="onSubmit" novalidate>
      <label class="field">
        <span>Título do evento *</span>
        <input v-model="form.titulo" type="text" required maxlength="200" autocomplete="off" />
      </label>

      <label class="field">
        <span>Descrição</span>
        <textarea v-model="form.descricao" rows="4" maxlength="4000" placeholder="Inclua se é gratuito, valores de ingresso, local de retirada..." />
      </label>

      <div class="row">
        <label class="field">
          <span>Categoria</span>
          <select v-model="form.categoria">
            <option v-for="c in categorias" :key="c || 'empty'" :value="c">{{ c || 'Selecione' }}</option>
          </select>
        </label>
        <label class="field">
          <span>Bairro</span>
          <input v-model="form.bairro" type="text" maxlength="120" placeholder="Ex.: Boa Viagem" />
        </label>
      </div>

      <label class="field">
        <span>Local / endereço</span>
        <input v-model="form.local" type="text" maxlength="300" />
      </label>

      <div class="row">
        <label class="field">
          <span>Início (data e hora)</span>
          <input v-model="form.inicio_iso" type="datetime-local" />
        </label>
        <label class="field">
          <span>Preço (R$)</span>
          <input v-model="form.preco" type="text" inputmode="decimal" placeholder="Vazio = não informado" />
        </label>
      </div>

      <fieldset class="fieldset" role="radiogroup" aria-labelledby="gratuito-legend">
        <legend id="gratuito-legend">Gratuito?</legend>
        <label class="radio"><input v-model="form.gratuito" type="radio" name="gratuito" :value="true" /> Sim</label>
        <label class="radio"><input v-model="form.gratuito" type="radio" name="gratuito" :value="false" /> Não</label>
        <label class="radio"><input v-model="form.gratuito" type="radio" name="gratuito" :value="null" /> Não informar</label>
      </fieldset>

      <div class="row">
        <label class="field">
          <span>Organizador *</span>
          <input v-model="form.organizador" type="text" maxlength="200" />
        </label>
        <label class="field">
          <span>E-mail de contato *</span>
          <input v-model="form.email_contato" type="email" maxlength="200" autocomplete="email" />
        </label>
      </div>

      <button class="submit" type="submit" :disabled="loading">
        {{ loading ? 'Enviando…' : 'Publicar evento' }}
      </button>

      <p v-if="message" class="ok" role="status">{{ message }}</p>
      <p v-if="error" class="err" role="alert">{{ error }}</p>
    </form>

    <section v-if="resultado" class="preview" aria-label="Último evento processado">
      <h2>Último registro processado</h2>
      <pre>{{ JSON.stringify(resultado, null, 2) }}</pre>
    </section>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
}

.top {
  margin-bottom: 1.5rem;
}

.back {
  display: inline-block;
  margin-bottom: 0.75rem;
  color: var(--oa-muted);
  font-weight: 600;
}

.title {
  font-family: 'Fraunces', Georgia, serif;
  margin: 0 0 0.5rem;
  font-size: 1.85rem;
}

.lead {
  margin: 0;
  color: var(--oa-muted);
  line-height: 1.5;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: var(--radius);
  padding: 1.25rem 1.35rem;
  box-shadow: var(--shadow);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.9rem;
}

.field span {
  font-weight: 600;
  color: #e2e8f0;
}

input,
select,
textarea {
  font: inherit;
  padding: 0.55rem 0.65rem;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(2, 6, 23, 0.55);
  color: var(--oa-text);
}

textarea {
  resize: vertical;
  min-height: 96px;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

@media (max-width: 640px) {
  .row {
    grid-template-columns: 1fr;
  }
}

.fieldset {
  border: 1px dashed rgba(148, 163, 184, 0.35);
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  margin: 0;
}

.fieldset legend {
  padding: 0 0.35rem;
  font-weight: 600;
}

.radio {
  margin-right: 1rem;
  font-size: 0.9rem;
}

.submit {
  margin-top: 0.25rem;
  padding: 0.7rem 1rem;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  font-weight: 800;
  font-size: 1rem;
  background: linear-gradient(120deg, var(--oa-teal), #0ea5e9);
  color: #042f2e;
}

.submit:disabled {
  opacity: 0.65;
  cursor: wait;
}

.ok {
  color: #6ee7b7;
  margin: 0;
}

.err {
  color: #fecaca;
  margin: 0;
}

.preview {
  margin-top: 2rem;
}

.preview h2 {
  font-size: 1.1rem;
  margin: 0 0 0.5rem;
}

.preview pre {
  margin: 0;
  padding: 1rem;
  border-radius: var(--radius);
  background: #020617;
  border: 1px solid rgba(148, 163, 184, 0.25);
  overflow: auto;
  font-size: 0.78rem;
  line-height: 1.35;
}
</style>
