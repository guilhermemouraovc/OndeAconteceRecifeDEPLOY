<template>
  <div class="event-card-wrapper">
    <q-card
      class="event-card"
      :class="[`event-card--${variant}`, { 'event-card--clickable': clickable }]"
      flat
      :clickable="clickable"
      v-ripple="clickable"
      :role="clickable ? 'button' : undefined"
      :tabindex="clickable ? 0 : -1"
      :aria-label="clickable ? `Evento: ${event.title || 'Sem nome'}. ${event.date || ''}` : undefined"
      @click="handleClick"
      @touchstart.passive="handleTouchStart"
      @touchmove.passive="handleTouchMove"
    >
      <div class="event-card__media">
        <q-img
          :src="event.image || defaultImage"
          :alt="`Imagem do evento ${event.title || 'Sem nome'}`"
          class="event-card__image"
          :height="resolvedImageHeight"
          ratio="16/9"
          spinner-color="primary"
          loading="lazy"
        />
        <span v-if="event.categoria" class="event-card__cat" :style="{ '--cat-color': catColor }">
          {{ event.categoria }}
        </span>
        <span class="event-card__date-badge">
          <q-icon name="event" size="13px" />
          {{ event.date }}
        </span>

        <!-- Botão de favoritar -->
        <button
          class="event-card__fav"
          :class="{ 'event-card__fav--active': isFav }"
          type="button"
          :aria-label="isFav ? 'Remover dos salvos' : 'Salvar evento'"
          @click.stop="handleFav"
        >
          <q-icon :name="isFav ? 'favorite' : 'favorite_border'" size="18px" />
        </button>
      </div>

      <q-card-section class="event-card__body">
        <div class="event-card__title">{{ event.title || 'Evento sem nome' }}</div>

        <div class="event-card__footer">
          <span class="event-card__place">
            <q-icon name="place" size="14px" />
            {{ event.cityState || event.location || 'Recife' }}
          </span>
          <span v-if="showPrice" class="event-card__price" :class="{ 'event-card__price--free': !event.hasPrice }">
            {{ event.hasPrice ? event.formattedFullPrice : 'Gratuito' }}
          </span>
        </div>
      </q-card-section>

      <span class="event-card__accent" :style="{ background: catColor }" />
    </q-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { DEFAULT_IMAGES } from 'src/constants/config'
import { categoryColor } from 'src/utils/eventMapper'
import { useEventsStore } from 'src/stores/events'

const props = defineProps({
  event: { type: Object, required: true },
  imageHeight: { type: String, default: null },
  variant: {
    type: String,
    default: 'carousel',
    validator: (v) => ['carousel', 'grid'].includes(v),
  },
  defaultImage: { type: String, default: DEFAULT_IMAGES.eventPlaceholder },
  clickable: { type: Boolean, default: true },
  showPrice: { type: Boolean, default: true },
})

const emit = defineEmits(['click'])
const store = useEventsStore()

const touchStartPos = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const resolvedImageHeight = computed(() => props.imageHeight ?? '180px')
const catColor = computed(() => categoryColor(props.event?.categoria))
const isFav = computed(() => store.isFavorito(props.event?.title))

function handleTouchStart(e) {
  isDragging.value = false
  if (e.touches?.[0]) {
    touchStartPos.value = { x: e.touches[0].clientX, y: e.touches[0].clientY }
  }
}

function handleTouchMove(e) {
  if (isDragging.value || !e.touches?.[0]) return
  const dx = Math.abs(e.touches[0].clientX - touchStartPos.value.x)
  const dy = Math.abs(e.touches[0].clientY - touchStartPos.value.y)
  if (dx > 10 || dy > 10) isDragging.value = true
}

function handleClick(e) {
  if (isDragging.value) {
    e?.preventDefault()
    e?.stopPropagation()
    return
  }
  if (props.clickable) emit('click', props.event)
}

function handleFav(e) {
  e?.stopPropagation()
  if (props.event?.title) store.toggleFavorito(props.event.title)
}
</script>

<style scoped lang="scss">
.event-card-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.event-card {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: var(--oa-radius);
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
  transition: transform 0.25s ease, border-color 0.25s ease, background 0.25s ease;
  overflow: hidden;
  height: 100%;

  &--clickable {
    cursor: pointer;

    &:hover {
      transform: translateY(-4px);
      border-color: rgba(94, 234, 212, 0.35);
      background: rgba(255, 255, 255, 0.07);
    }
  }

  &:focus-visible {
    outline: 2px solid var(--oa-accent);
    outline-offset: 2px;
  }
}

.event-card-wrapper:has(.event-card--carousel) {
  flex: 0 0 300px;
  width: 300px;
}

.event-card-wrapper:has(.event-card--grid) {
  width: 100%;
}

.event-card__media {
  position: relative;
}

.event-card__cat {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--cat-color);
  background: rgba(6, 22, 38, 0.82);
  border: 1px solid color-mix(in srgb, var(--cat-color) 50%, transparent);
  padding: 3px 10px;
  border-radius: 999px;
  backdrop-filter: blur(4px);
}

.event-card__date-badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  background: rgba(6, 22, 38, 0.82);
  padding: 4px 10px;
  border-radius: 999px;
  backdrop-filter: blur(4px);
}

/* ---- Botão de favoritar ---- */
.event-card__fav {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(6, 22, 38, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.2s ease, background 0.2s ease, transform 0.15s ease;

  &:hover {
    color: #f87171;
    background: rgba(248, 113, 113, 0.15);
  }

  &--active {
    color: #f87171;

    &:hover {
      transform: scale(1.15);
    }
  }
}

.event-card__body {
  flex: 1;
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-card__title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.12rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--oa-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-card__footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.event-card__place {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.82rem;
  color: var(--oa-muted);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-card__price {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--oa-gold);
  flex-shrink: 0;

  &--free {
    color: var(--oa-accent);
  }
}

.event-card__accent {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  opacity: 0.85;
}

@media (max-width: 599px) {
  .event-card-wrapper:has(.event-card--carousel) {
    flex: 0 0 270px;
    width: 270px;
  }
}
</style>