<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useEventsStore } from '@/stores/events.js'
import EventCard from '@/components/EventCard.vue'

const store = useEventsStore()
onMounted(() => store.fetchEvents())
</script>

<template>
  <div class="favs-page">
    <header class="top">
      <RouterLink to="/" class="back">← Voltar à agenda</RouterLink>
    </header>

    <div class="heading">
      <h1 class="titulo">Eventos salvos</h1>
      <p class="subtitulo" v-if="store.eventosFavoritos.length > 0">
        {{ store.eventosFavoritos.length }} evento{{ store.eventosFavoritos.length !== 1 ? 's' : '' }} na sua lista
      </p>
    </div>

    <p v-if="store.loading" class="estado">Carregando…</p>

    <template v-else-if="store.eventosFavoritos.length > 0">
      <ul class="grid">
        <li
          v-for="(ev, idx) in store.eventosFavoritos"
          :key="ev.titulo"
          :style="{ animationDelay: `${idx * 0.05}s` }"
          class="grid__item"
        >
          <EventCard :ev="ev" />
        </li>
      </ul>
    </template>

    <div v-else class="vazio">
      <span class="vazio__icon">♡</span>
      <p class="vazio__titulo">Você ainda não salvou nenhum evento</p>
      <p class="vazio__desc">Clique em ♡ nos cards da agenda para guardar os eventos que te interessam.</p>
      <RouterLink to="/" class="btn-voltar">Ver agenda</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.favs-page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 3rem;
}

.top { padding-bottom: 1rem; border-bottom: 1px solid rgba(148, 163, 184, 0.2); margin-bottom: 1.5rem; }
.back { color: var(--oa-muted); font-weight: 600; font-size: 0.92rem; transition: color 0.15s; }
.back:hover { color: var(--oa-text); }

.heading { margin-bottom: 1.25rem; }
.titulo { font-family: 'Fraunces', Georgia, serif; margin: 0 0 0.25rem; font-size: 1.85rem; }
.subtitulo { margin: 0; color: var(--oa-muted); font-size: 0.92rem; }

.estado { color: var(--oa-muted); }

.grid {
  list-style: none; padding: 0; margin: 0;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1rem;
}
.grid__item { animation: fadeUp 0.3s ease both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.vazio {
  display: flex; flex-direction: column; align-items: center; gap: 0.6rem;
  padding: 4rem 1rem; text-align: center;
}
.vazio__icon { font-size: 3rem; line-height: 1; color: #94a3b8; }
.vazio__titulo { margin: 0; font-size: 1.2rem; font-weight: 700; font-family: 'Fraunces', Georgia, serif; }
.vazio__desc { margin: 0; color: var(--oa-muted); font-size: 0.92rem; max-width: 26rem; }

.btn-voltar {
  margin-top: 0.5rem; padding: 0.6rem 1.4rem; border-radius: 999px;
  background: linear-gradient(120deg, var(--oa-teal), #0ea5e9);
  color: #042f2e; font-weight: 700; font-size: 0.92rem;
  transition: opacity 0.15s;
}
.btn-voltar:hover { opacity: 0.85; }
</style>
