<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <PageHeader title="Eventos salvos" />

      <LoadingState v-if="store.loading" message="Carregando favoritos..." />

      <div v-else-if="store.eventosFavoritos.length" class="cards-grid">
        <EventCard
          v-for="card in store.eventosFavoritos"
          :key="card.id"
          :event="card"
          variant="grid"
          @click="goToEvent(card)"
        />
      </div>

      <EmptyState
        v-else
        title="Nenhum evento salvo"
        message="Toque no ícone de coração nos cards da agenda para guardar eventos."
        button-label="Ver agenda"
        :button-to="{ name: 'home' }"
      />
    </div>
  </q-page>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEventsStore } from 'src/stores/events'
import PageHeader from 'components/PageHeader.vue'
import EventCard from 'components/EventCard.vue'
import EmptyState from 'components/EmptyState.vue'
import LoadingState from 'components/LoadingState.vue'

const store = useEventsStore()
const router = useRouter()

function goToEvent(card) {
  if (card?.link) router.push(card.link)
}

onMounted(() => store.fetchEvents())
</script>

<style scoped>
.page-content {
  padding-top: 16px;
  padding-bottom: 48px;
}
</style>
