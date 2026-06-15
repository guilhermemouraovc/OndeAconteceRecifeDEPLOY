<template>
  <div class="skeleton-loader" :class="[`skeleton-loader--${variant}`]">
    <div v-if="variant === 'event-card'" class="skeleton-event-card">
      <div class="skeleton-image" />
      <div class="skeleton-body">
        <div class="skeleton-title" />
        <div class="skeleton-text skeleton-text--short" />
      </div>
    </div>

    <div v-else-if="variant === 'hero'" class="skeleton-hero">
      <div class="skeleton-hero-image" />
      <div class="skeleton-hero-content">
        <div class="skeleton-hero-title" />
        <div class="skeleton-text" />
        <div class="skeleton-button" />
      </div>
    </div>

    <div v-else-if="variant === 'list'" class="skeleton-list">
      <div v-for="i in count" :key="i" class="skeleton-event-card">
        <div class="skeleton-image" />
        <div class="skeleton-body">
          <div class="skeleton-title" />
          <div class="skeleton-text skeleton-text--short" />
        </div>
      </div>
    </div>

    <div v-else-if="variant === 'carousel'" class="skeleton-carousel">
      <div class="skeleton-carousel-header">
        <div class="skeleton-carousel-title" />
      </div>
      <div class="skeleton-carousel-items">
        <div v-for="i in carouselCount" :key="i" class="skeleton-event-card">
          <div class="skeleton-image" />
          <div class="skeleton-body">
            <div class="skeleton-title" />
            <div class="skeleton-text skeleton-text--short" />
          </div>
        </div>
      </div>
    </div>

    <!-- Skeleton para página de detalhe de evento -->
    <div v-else-if="variant === 'detail'" class="skeleton-detail">
      <div class="sd sd--back" />
      <div class="sd sd--chips" />
      <div class="sd sd--title" />
      <div class="sd sd--title sd--title-short" />
      <div class="sd sd--image" />
      <div class="sd sd--meta" />
      <div class="sd sd--meta sd--meta-short" />
      <div class="sd sd--meta sd--meta-short" />
      <div class="sd sd--text" />
      <div class="sd sd--text" />
      <div class="sd sd--text sd--text-short" />
      <div class="sd sd--actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'event-card',
    validator: (v) => ['event-card', 'hero', 'list', 'carousel', 'detail'].includes(v),
  },
  count: { type: Number, default: 3 },
  carouselCount: { type: Number, default: 4 },
})
</script>

<style scoped>
@keyframes shimmer {
  0%   { background-position: -1000px 0; }
  100% { background-position:  1000px 0; }
}

.skeleton-image,
.skeleton-title,
.skeleton-text,
.skeleton-button,
.skeleton-hero-image,
.skeleton-hero-title,
.skeleton-carousel-title,
.sd {
  background: linear-gradient(90deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.04) 100%);
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
  border-radius: 8px;
}

.skeleton-event-card {
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  overflow: hidden;
  flex: 0 0 320px;
  width: 320px;
}

.skeleton-image { height: 200px; width: 100%; border-radius: 0; }
.skeleton-body { padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.skeleton-title { height: 24px; width: 80%; }
.skeleton-text { height: 16px; width: 100%; }
.skeleton-text--short { width: 60%; }

.skeleton-hero {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  height: 400px;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(255,255,255,0.04);
}

.skeleton-hero-image { height: 100%; }
.skeleton-hero-content { padding: 32px; display: flex; flex-direction: column; gap: 16px; justify-content: center; }
.skeleton-hero-title { height: 40px; width: 90%; }
.skeleton-button { height: 44px; width: 140px; }

.skeleton-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.skeleton-list .skeleton-event-card { width: 100%; flex: unset; }

.skeleton-carousel { margin-top: 32px; }
.skeleton-carousel-header { margin-bottom: 16px; }
.skeleton-carousel-title { height: 32px; width: 200px; }
.skeleton-carousel-items { display: flex; gap: 24px; overflow: hidden; }

/* ---- Detail skeleton ---- */
.skeleton-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
  padding-top: 8px;
}

.sd--back        { height: 32px; width: 120px; border-radius: 999px; }
.sd--chips       { height: 28px; width: 240px; }
.sd--title       { height: 52px; width: 88%; }
.sd--title-short { width: 55%; height: 52px; }
.sd--image       { height: 340px; border-radius: 16px; }
.sd--meta        { height: 20px; width: 65%; }
.sd--meta-short  { width: 42%; }
.sd--text        { height: 18px; width: 100%; }
.sd--text-short  { width: 72%; }
.sd--actions     { height: 44px; width: 360px; border-radius: 8px; margin-top: 8px; }

@media (max-width: 768px) {
  .skeleton-hero { grid-template-columns: 1fr; height: 480px; }
  .skeleton-list { grid-template-columns: 1fr; }
  .sd--actions   { width: 100%; }
}
</style>