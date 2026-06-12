<template>
  <section :id="sectionId" class="event-section">
    <div class="section-header">
      <div class="section-info">
        <span class="section-dash" aria-hidden="true" />
        <div class="section-title font-display">{{ title }}</div>
        <q-btn
          v-if="seeAllLink"
          flat
          dense
          no-caps
          class="see-all"
          :label="seeAllLabel"
          :to="seeAllLink"
        />
      </div>

      <div class="nav-buttons" role="group" aria-label="Navegação do carrossel">
        <button class="nav-btn" :disabled="!canScrollLeft" aria-label="Anterior" @click="scroll(-scrollStep)">
          <q-icon name="chevron_left" size="28px" />
        </button>
        <button class="nav-btn" :disabled="!canScrollRight" aria-label="Próximo" @click="scroll(scrollStep)">
          <q-icon name="chevron_right" size="28px" />
        </button>
      </div>
    </div>

    <div
      ref="viewport"
      class="cards-viewport"
      :class="{ 'fade-right': showRightFade, 'fade-left': showLeftFade }"
      @scroll="updateScrollState"
    >
      <div class="cards-row">
        <EventCard
          v-for="card in items"
          :key="card.id"
          :event="card"
          variant="carousel"
          @click="openCard(card)"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import EventCard from './EventCard.vue'

const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
  seeAllLabel: { type: String, default: 'Ver tudo' },
  seeAllLink: { type: [String, Object], default: null },
  sectionId: { type: String, default: null },
})

const router = useRouter()
const viewport = ref(null)
const scrollStep = 344
const canScrollLeft = ref(false)
const canScrollRight = ref(false)
const showRightFade = ref(true)
const showLeftFade = ref(false)

function openCard(card) {
  if (card?.link) router.push(card.link)
}

function updateScrollState() {
  const el = viewport.value
  if (!el) return
  const max = el.scrollWidth - el.clientWidth - 1
  canScrollLeft.value = el.scrollLeft > 0
  canScrollRight.value = el.scrollLeft < max
  showRightFade.value = el.scrollLeft < 40
  showLeftFade.value = el.scrollLeft > 40
}

function scroll(offset) {
  viewport.value?.scrollBy({ left: offset, behavior: 'smooth' })
}

watch(
  () => props.items,
  () => nextTick().then(updateScrollState),
)

onMounted(() => nextTick().then(updateScrollState))
</script>

<style scoped lang="scss">
.event-section {
  margin-top: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  color: white;
}

.section-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-dash {
  width: 26px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--frevo-2), var(--frevo-4));
  flex-shrink: 0;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 600;
}

.see-all {
  color: var(--oa-accent) !important;
  font-weight: 600;
}

.nav-buttons {
  display: flex;
  gap: 8px;
}

.nav-btn {
  width: 40px;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
}

.cards-viewport {
  overflow-x: auto;
  scrollbar-width: none;
  --fade: 28px;
  padding-top: 8px;
  padding-bottom: 12px;

  &::-webkit-scrollbar { display: none; }

  &.fade-right {
    mask-image: linear-gradient(to right, #000 calc(100% - var(--fade)), transparent 100%);
  }

  &.fade-left {
    mask-image: linear-gradient(to right, transparent 0, #000 var(--fade));
  }

  &.fade-left.fade-right {
    mask-image: linear-gradient(to right, transparent 0, #000 var(--fade), #000 calc(100% - var(--fade)), transparent 100%);
  }
}

.cards-row {
  display: flex;
  gap: 24px;
  padding-right: 80px;
}

@media (max-width: 599px) {
  .nav-buttons { display: none; }
  .cards-row { gap: 16px; padding-right: 16px; }
}
</style>
