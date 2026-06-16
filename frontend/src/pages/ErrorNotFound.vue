<template>
  <q-page class="bg-landing not-found-page">
    <div class="not-found-inner">
      <div class="not-found-art" aria-hidden="true">
        <div class="not-found-blob not-found-blob--1" />
        <div class="not-found-blob not-found-blob--2" />
        <span class="not-found-code font-display">404</span>
      </div>

      <h1 class="not-found-title font-display">
        Essa página sumiu<br />
        <em class="not-found-em">do mapa</em>
      </h1>

      <p class="not-found-text">
        O endereço que você tentou acessar não existe ou foi removido.<br />
        Mas tem coisa boa rolando em Recife — vem ver!
      </p>

      <div class="not-found-actions">
        <q-btn
          color="primary"
          label="Ver agenda"
          icon="event"
          no-caps
          unelevated
          :to="{ name: 'home' }"
        />
        <q-btn
          flat
          label="Ver no mapa"
          icon="map"
          no-caps
          class="not-found-ghost"
          :to="{ name: 'mapa' }"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>
// sem imports necessários
</script>

<style scoped lang="scss">
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.not-found-inner {
  text-align: center;
  padding: 40px 24px;
  max-width: 520px;
}

/* Arte com o número 404 */
.not-found-art {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

.not-found-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(55px);
  pointer-events: none;
}

.not-found-blob--1 {
  width: 220px;
  height: 220px;
  background: var(--frevo-4);
  opacity: 0.2;
  top: -40px;
  left: -60px;
}

.not-found-blob--2 {
  width: 180px;
  height: 180px;
  background: var(--frevo-2);
  opacity: 0.15;
  bottom: -30px;
  right: -40px;
}

.not-found-code {
  font-size: clamp(5rem, 20vw, 9rem);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, var(--oa-accent) 0%, var(--frevo-2) 60%, var(--frevo-1) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 1;
}

.not-found-title {
  font-size: clamp(1.6rem, 4vw, 2.4rem);
  font-weight: 600;
  color: #fff;
  line-height: 1.2;
  margin: 0 0 16px;
}

.not-found-em {
  font-style: italic;
  color: var(--oa-gold);
}

.not-found-text {
  color: var(--oa-muted);
  font-size: 1rem;
  line-height: 1.7;
  margin: 0 0 32px;
}

.not-found-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.not-found-ghost {
  color: rgba(248, 250, 252, 0.8);
}
</style>