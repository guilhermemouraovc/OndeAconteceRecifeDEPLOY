<template>
  <q-page class="bg-landing">
    <div class="main-container page-content">
      <section class="hero">
        <div class="hero__copy">
          <span class="section-eyebrow">Agenda cultural · Recife</span>
          <h1 class="hero__title font-display">
            O que tá rolando<br />
            <em class="hero__highlight">na cidade</em> hoje?
          </h1>
          <p class="hero__subtitle">
            Shows, teatro, dança, exposições e festivais — da Prefeitura aos produtores
            independentes, tudo num feed só.
          </p>
          <div class="hero__actions">
            <q-btn
              color="primary"
              label="Explorar programação"
              no-caps
              unelevated
              size="md"
              padding="10px 22px"
              :to="{ name: 'programacao' }"
            />
            <q-btn
              flat
              label="Ver no mapa"
              icon="map"
              no-caps
              class="hero__btn-ghost"
              :to="{ name: 'mapa' }"
            />
          </div>

          <div v-if="quickCats.length" class="hero__cats">
            <button
              v-for="cat in quickCats"
              :key="cat"
              class="hero__cat-pill"
              type="button"
              @click="goCategoria(cat)"
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <div class="hero__art" aria-hidden="true">
          <div class="hero__blob hero__blob--1" />
          <div class="hero__blob hero__blob--2" />
          <div class="hero__frame">
            <template v-if="featured">
              <q-img :src="featured.image" :alt="featured.title" ratio="4/5" class="hero__img" />
              <div class="hero__frame-info" @click="goToEvent(featured)">
                <span class="hero__frame-date">{{ featured.date }}</span>
                <span class="hero__frame-title">{{ featured.title }}</span>
              </div>
            </template>
            <div v-else class="hero__frame-placeholder font-display">
              Recife<br />em cartaz
            </div>
          </div>
        </div>
      </section>

      <ErrorState v-if="store.error" :message="store.error" @retry="store.fetchEvents(true)" />

      <template v-else>
        <SkeletonLoader v-if="store.loading && !store.eventCards.length" variant="carousel" />

        <EventSectionCarousel
          v-for="[cat, items] in categorySections"
          :key="cat"
          :title="cat"
          :items="items"
          :section-id="`cat-${cat}`"
          :see-all-link="{ name: 'programacao', query: { categoria: cat } }"
        />

        <div v-if="!store.loading && !store.eventCards.length" class="empty-wrap">
          <div class="empty-card">
            <div class="empty-card__icon" aria-hidden="true">
              <q-icon name="celebration" size="40px" />
            </div>
            <h2 class="empty-card__title font-display">A agenda ainda está vazia</h2>
            <p class="empty-card__text">
              Rode a coleta para puxar eventos da TicketPE, ou cadastre o primeiro evento
              manualmente.
            </p>
            <div class="empty-card__actions">
              <q-btn
                color="primary"
                label="Rodar coleta"
                icon="sync"
                no-caps
                unelevated
                :to="{ name: 'scraper' }"
              />
              <q-btn
                outline
                color="accent"
                label="Cadastrar evento"
                no-caps
                :to="{ name: 'cadastro' }"
              />
            </div>
          </div>
        </div>
      </template>
    </div>
  </q-page>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEventsStore } from 'src/stores/events'
import EventSectionCarousel from 'components/EventSectionCarousel.vue'
import SkeletonLoader from 'components/SkeletonLoader.vue'
import ErrorState from 'components/ErrorState.vue'

const store = useEventsStore()
const router = useRouter()

const featured = computed(() => store.eventCards[0] || null)
const quickCats = computed(() => store.categoriasDisponiveis.slice(0, 5))

const categorySections = computed(() => {
  const entries = [...store.eventsByCategory.entries()].filter(([, items]) => items.length > 0)
  return entries.slice(0, 6)
})

function goToEvent(ev) {
  if (ev?.link) router.push(ev.link)
}

function goCategoria(cat) {
  router.push({ name: 'programacao', query: { categoria: cat } })
}
</script>

<style scoped lang="scss">
.page-content {
  padding-top: 40px;
  padding-bottom: 64px;
}

.hero {
  display: grid;
  grid-template-columns: 1.25fr 0.75fr;
  align-items: center;
  gap: 48px;
  padding: 24px 0 48px;
}

.hero__title {
  font-size: clamp(2.4rem, 5.5vw, 3.8rem);
  font-weight: 600;
  line-height: 1.08;
  color: #fff;
  margin: 18px 0 0;
  letter-spacing: -0.01em;
}

.hero__highlight {
  font-style: italic;
  color: var(--oa-gold);
}

.hero__subtitle {
  color: var(--oa-muted);
  font-size: 1.1rem;
  line-height: 1.65;
  max-width: 480px;
  margin: 18px 0 28px;
}

.hero__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.hero__btn-ghost {
  color: rgba(248, 250, 252, 0.85);
}

.hero__cats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 28px;
}

.hero__cat-pill {
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--oa-accent);
  background: rgba(94, 234, 212, 0.08);
  border: 1px solid rgba(94, 234, 212, 0.25);
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(94, 234, 212, 0.16);
    border-color: rgba(94, 234, 212, 0.5);
  }
}

/* arte do hero */
.hero__art {
  position: relative;
  display: flex;
  justify-content: center;
}

.hero__blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  pointer-events: none;
}

.hero__blob--1 {
  width: 240px;
  height: 240px;
  background: var(--frevo-4);
  top: -30px;
  right: -20px;
  opacity: 0.25;
}

.hero__blob--2 {
  width: 200px;
  height: 200px;
  background: var(--frevo-2);
  bottom: -20px;
  left: 0;
  opacity: 0.18;
}

.hero__frame {
  position: relative;
  width: min(300px, 100%);
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  transform: rotate(2.5deg);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
  transition: transform 0.3s ease;

  &:hover {
    transform: rotate(0deg) scale(1.02);
  }
}

.hero__img {
  display: block;
}

.hero__frame-info {
  position: absolute;
  inset: auto 0 0 0;
  padding: 40px 16px 14px;
  background: linear-gradient(to top, rgba(4, 16, 29, 0.95), transparent);
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
}

.hero__frame-date {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--oa-gold);
}

.hero__frame-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
}

.hero__frame-placeholder {
  aspect-ratio: 4 / 5;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 2rem;
  font-style: italic;
  color: rgba(248, 250, 252, 0.35);
  background:
    radial-gradient(circle at 30% 25%, rgba(46, 196, 182, 0.18), transparent 55%),
    radial-gradient(circle at 75% 80%, rgba(245, 166, 35, 0.14), transparent 55%),
    rgba(255, 255, 255, 0.03);
}

/* empty state */
.empty-wrap {
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

.empty-card {
  max-width: 480px;
  width: 100%;
  text-align: center;
  padding: 44px 32px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.empty-card__icon {
  width: 76px;
  height: 76px;
  margin: 0 auto 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--oa-gold);
  background: rgba(234, 179, 8, 0.1);
  border: 1px solid rgba(234, 179, 8, 0.25);
}

.empty-card__title {
  font-size: 1.5rem;
  color: #fff;
  margin: 0 0 10px;
}

.empty-card__text {
  color: var(--oa-muted);
  line-height: 1.6;
  margin: 0 0 24px;
}

.empty-card__actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    gap: 36px;
    padding-bottom: 32px;
  }

  .hero__art {
    order: -1;
  }

  .hero__frame {
    width: min(260px, 80%);
  }
}
</style>
