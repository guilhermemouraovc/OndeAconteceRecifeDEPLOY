<template>
  <q-layout view="lHh Lpr lFf" class="oa-layout">
    <a href="#main-content" class="skip-link">Pular para o conteúdo</a>

    <q-header class="oa-header">
      <div class="frevo-stripe" aria-hidden="true" />

      <q-toolbar class="oa-toolbar">
        <router-link to="/" class="brand" aria-label="Onde Acontece Recife — início">
          <span class="brand-mark" aria-hidden="true" />
          <span class="brand-text">
            <span class="brand-title font-display">Onde Acontece</span>
            <span class="brand-sub">Recife</span>
          </span>
        </router-link>

        <q-space />

        <!-- Barra de busca inline na toolbar -->
        <div
          v-if="showSearch && !$route.path.startsWith('/evento') && !$q.screen.lt.md"
          class="toolbar-search"
        >
          <q-input
            v-model="store.searchQuery"
            dense
            borderless
            clearable
            dark
            placeholder="Buscar shows, peças..."
            class="toolbar-search__input"
            @keyup.enter="goProgramacao"
          >
            <template #prepend>
              <q-icon name="search" color="grey-5" size="18px" />
            </template>
          </q-input>
        </div>

        <nav v-if="!$q.screen.lt.md" class="nav-desktop" aria-label="Principal">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            :to="{ name: item.name }"
            class="nav-link"
            :class="{ 'nav-link--active': $route.name === item.name }"
          >
            {{ item.label }}
            <q-badge v-if="item.name === 'favoritos' && favCount" class="nav-badge" rounded>
              {{ favCount }}
            </q-badge>
          </router-link>

          <!-- Dropdown Produtores -->
          <div class="nav-dropdown">
            <button
              class="nav-link nav-link--btn"
              :class="{ 'nav-link--active': produtoresAtivo }"
              type="button"
            >
              Produtores
              <q-icon name="expand_more" size="16px" class="nav-dropdown__arrow" />
            </button>
            <div class="nav-dropdown__menu">
              <router-link
                v-for="item in produtoresItems"
                :key="item.name"
                :to="{ name: item.name }"
                class="nav-dropdown__item"
                :class="{ 'nav-dropdown__item--active': route.name === item.name }"
              >
                <q-icon :name="item.icon" size="16px" />
                {{ item.label }}
              </router-link>
            </div>
          </div>
        </nav>

        <q-btn
          v-if="showSearch"
          flat
          round
          dense
          icon="tune"
          aria-label="Abrir filtros"
          class="header-icon-btn q-ml-sm"
          :class="{ 'header-icon-btn--active': store.hasActiveFilters }"
          @click="filterDrawer = true"
        />

        <q-btn
          v-if="$q.screen.lt.md"
          flat
          round
          dense
          icon="menu"
          aria-label="Menu"
          class="header-icon-btn q-ml-sm"
          @click="mobileMenu = true"
        />
      </q-toolbar>

    </q-header>

    <!-- Drawer de filtros -->
    <q-drawer v-model="filterDrawer" side="right" overlay bordered class="oa-filter-drawer">
      <q-scroll-area class="fit">
        <div class="fd-inner">

          <!-- Cabeçalho do drawer -->
          <div class="fd-header">
            <div class="fd-header__left">
              <q-icon name="tune" size="20px" class="fd-header__icon" />
              <span class="fd-header__title font-display">Filtros</span>
            </div>
            <button class="fd-close" aria-label="Fechar filtros" @click="filterDrawer = false">
              <q-icon name="close" size="20px" />
            </button>
          </div>

          <!-- Indicador de filtros ativos -->
          <div v-if="store.hasActiveFilters" class="fd-active-badge">
            <q-icon name="filter_alt" size="14px" />
            Filtros ativos
            <button class="fd-active-badge__clear" @click="store.clearFilters()">Limpar</button>
          </div>

          <!-- Categoria -->
          <div class="fd-section">
            <span class="fd-label">Categoria</span>
            <CategoryFilter v-model="store.filterCategoria" />
          </div>

          <!-- Preço -->
          <div class="fd-section">
            <span class="fd-label">Preço</span>
            <div class="fd-chips">
              <button
                v-for="opt in precoOptions"
                :key="opt.value"
                class="fd-chip"
                :class="{ 'fd-chip--active': store.filterPreco === opt.value }"
                type="button"
                @click="store.filterPreco = store.filterPreco === opt.value ? '' : opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- Bairro -->
          <div class="fd-section">
            <span class="fd-label">Bairro</span>
            <q-select
              v-model="store.filterBairro"
              :options="store.bairrosDisponiveis"
              clearable
              dense
              outlined
              dark
              label="Todos os bairros"
              class="fd-select"
            />
          </div>

          <!-- Data -->
          <div class="fd-section">
            <span class="fd-label">Data</span>
            <div class="fd-chips">
              <button
                v-for="opt in dataOptions"
                :key="opt.value"
                class="fd-chip"
                :class="{ 'fd-chip--active': store.filterData === opt.value }"
                type="button"
                @click="store.filterData = store.filterData === opt.value ? '' : opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- Toggle Agora -->
          <div class="fd-section fd-agora">
            <button
              class="fd-agora-btn"
              :class="{ 'fd-agora-btn--active': store.filterAgora }"
              type="button"
              @click="store.filterAgora = !store.filterAgora"
            >
              <span class="fd-agora-dot" />
              <q-icon name="bolt" size="16px" />
              O que tá rolando agora
            </button>
            <span class="fd-agora-hint">Eventos nas próximas 3 horas</span>
          </div>

          <!-- Botão aplicar -->
          <div class="fd-footer">
            <q-btn
              color="primary"
              label="Ver resultados"
              no-caps
              unelevated
              class="full-width"
              @click="aplicarFiltros"
            />
          </div>

        </div>
      </q-scroll-area>
    </q-drawer>

    <q-drawer v-model="mobileMenu" side="left" overlay bordered class="mobile-drawer">
      <q-list dark padding>
        <q-item
          v-for="item in [...navItems, ...produtoresItems]"
          :key="item.name"
          clickable
          v-ripple
          :to="{ name: item.name }"
          @click="mobileMenu = false"
        >
          <q-item-section avatar><q-icon :name="item.icon" /></q-item-section>
          <q-item-section>{{ item.label }}</q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view id="main-content" />
    </q-page-container>

    <ChatbotPanel v-if="$route.name !== 'moderacao'" />

    <q-footer class="oa-footer">
      <div class="frevo-stripe" aria-hidden="true" />
      <div class="footer-inner">
        <div class="brand" aria-label="Onde Acontece Recife">
          <span class="brand-mark" aria-hidden="true" />
          <span class="brand-text">
            <span class="brand-title font-display">Onde Acontece</span>
            <span class="brand-sub">Recife</span>
          </span>
        </div>
        <span class="footer-divider" aria-hidden="true" />
        <p class="footer-tagline">
          A agenda cultural da cidade, reunindo eventos da Prefeitura, produtores independentes e
          plataformas de ingressos num só lugar.
        </p>
      </div>
    </q-footer>
  </q-layout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventsStore } from 'src/stores/events'
import CategoryFilter from 'components/CategoryFilter.vue'
import ChatbotPanel from 'components/ChatbotPanel.vue'

const store = useEventsStore()
const route = useRoute()
const router = useRouter()

const filterDrawer = ref(false)
const mobileMenu = ref(false)

const favCount = computed(() => store.favoritos.length)
const showSearch = computed(() => !['event-detail', 'scraper', 'moderacao'].includes(route.name))

const navItems = [
  { name: 'home', label: 'Agenda', icon: 'home' },
  { name: 'programacao', label: 'Programação', icon: 'event' },
  { name: 'mapa', label: 'Mapa', icon: 'map' },
  { name: 'favoritos', label: 'Salvos', icon: 'favorite' },
]

const produtoresItems = [
  { name: 'cadastro', label: 'Cadastrar evento', icon: 'add_circle' },
  { name: 'moderacao', label: 'Moderação', icon: 'task_alt' },
  { name: 'scraper', label: 'Coleta de dados', icon: 'sync' },
]

const produtoresAtivo = computed(() =>
  produtoresItems.some((i) => route.name === i.name)
)

const precoOptions = [
  { label: 'Gratuito', value: 'gratuito' },
  { label: 'Até R$ 50', value: 'ate50' },
  { label: 'R$ 50–100', value: '50a100' },
  { label: 'Acima de R$ 100', value: 'acima100' },
]

const dataOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: 'Amanhã', value: 'amanha' },
  { label: 'Fim de semana', value: 'fds' },
  { label: 'Esta semana', value: 'semana' },
]

function aplicarFiltros() {
  filterDrawer.value = false
  if (route.name !== 'programacao') {
    router.push({ name: 'programacao' })
  }
}

function goProgramacao() {
  router.push({ name: 'programacao', query: store.searchQuery ? { q: store.searchQuery } : {} })
}

onMounted(() => store.fetchEvents())
</script>

<style scoped lang="scss">
.oa-layout {
  min-height: 100vh;
}

.oa-header {
  background: rgba(6, 22, 38, 0.85) !important;
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: none;
}

.oa-toolbar {
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  padding: 10px 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: inherit;
}

.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: conic-gradient(
    from 210deg,
    var(--frevo-2),
    var(--frevo-4),
    var(--frevo-1),
    var(--frevo-3),
    var(--frevo-2)
  );
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.brand-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #fff;
}

.brand-sub {
  font-size: 0.68rem;
  color: var(--oa-accent);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  font-weight: 600;
}

.nav-desktop {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 0.92rem;
  font-weight: 600;
  color: rgba(248, 250, 252, 0.72);
  text-decoration: none;
  border-radius: 8px;
  transition: color 0.2s ease;

  &::after {
    content: '';
    position: absolute;
    left: 14px;
    right: 14px;
    bottom: 2px;
    height: 2px;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--frevo-2), var(--frevo-4));
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.25s ease;
  }

  &:hover {
    color: #fff;
  }

  &--active {
    color: #fff;

    &::after {
      transform: scaleX(1);
    }
  }
}

.nav-badge {
  background: var(--oa-coral);
  font-size: 0.65rem;
}

.header-icon-btn {
  color: rgba(248, 250, 252, 0.8);

  &--active {
    color: var(--oa-accent) !important;
  }
}

.toolbar-search {
  width: 360px;
  margin: 0 16px;
  flex-shrink: 1;
}

.toolbar-search__input {
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 0 14px;
  transition: border-color 0.2s ease;
  font-size: 0.88rem;

  &:focus-within {
    border-color: rgba(94, 234, 212, 0.5);
    background: rgba(255, 255, 255, 0.1);
  }
}

/* ---- Footer ---- */
.oa-footer {
  background: #04101d !important;
  color: var(--oa-muted);
}

.footer-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer-divider {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.12);
  flex-shrink: 0;
}

.footer-tagline {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--oa-muted);
  flex: 1;
}

@media (max-width: 600px) {
  .footer-inner {
    flex-wrap: wrap;
  }

  .footer-divider {
    display: none;
  }
}
/* ---- Dropdown Produtores ---- */
.nav-dropdown {
  position: relative;

  &:hover .nav-dropdown__menu,
  &:focus-within .nav-dropdown__menu {
    opacity: 1;
    pointer-events: all;
    transform: translateY(0);
  }
}

.nav-link--btn {
  font-family: inherit;
  background: none;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.nav-dropdown__arrow {
  transition: transform 0.2s ease;
}

.nav-dropdown:hover .nav-dropdown__arrow {
  transform: rotate(180deg);
}

.nav-dropdown__menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 200px;
  background: #04101d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
  opacity: 0;
  pointer-events: none;
  transform: translateY(-6px);
  transition: opacity 0.18s ease, transform 0.18s ease;
  z-index: 200;
}

.nav-dropdown__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(248, 250, 252, 0.72);
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.07);
    color: #fff;
  }

  &--active {
    color: var(--oa-accent);
    background: rgba(94, 234, 212, 0.08);
  }
}

</style>

<!-- CSS global para os drawers: sem scoped para alcançar elementos do Quasar -->
<style lang="scss">
.oa-filter-drawer,
.mobile-drawer {
  background: #04101d !important;
  color: #f8fafc !important;

  // força o scroll area a herdar o fundo
  .q-scrollarea,
  .q-scrollarea__container,
  .q-scrollarea__content {
    background: transparent !important;
  }
}

/* ---- Internos do drawer de filtros ---- */
.fd-inner {
  padding: 0 0 32px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.fd-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  margin-bottom: 4px;
}

.fd-header__left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.fd-header__icon {
  color: var(--oa-accent);
}

.fd-header__title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
}

.fd-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--oa-muted);
  transition: background 0.2s, color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }
}

.fd-active-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 8px 20px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(94, 234, 212, 0.08);
  border: 1px solid rgba(94, 234, 212, 0.2);
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--oa-accent);
}

.fd-active-badge__clear {
  margin-left: auto;
  font-family: inherit;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--oa-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: #fff;
  }
}

.fd-section {
  padding: 16px 20px 0;
}

.fd-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--oa-muted);
  margin-bottom: 10px;
}

/* chips de preço e data */
.fd-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.fd-chip {
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--oa-muted);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
  transition: all 0.18s ease;

  &:hover {
    border-color: rgba(255, 255, 255, 0.25);
    color: #fff;
  }

  &--active {
    color: #fff;
    background: rgba(94, 234, 212, 0.12);
    border-color: var(--oa-accent);
  }
}

/* select de bairro dentro do drawer */
.fd-select {
  .q-field__control {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
  }

  .q-field__native,
  .q-field__label {
    color: #f8fafc !important;
  }
}

/* toggle agora */
.fd-agora {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  margin-top: 8px;
  padding-top: 20px;
}

.fd-agora-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--oa-muted);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 8px 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  justify-content: center;

  &:hover {
    border-color: rgba(94, 234, 212, 0.35);
    color: #fff;
  }

  &--active {
    color: #fff;
    background: rgba(94, 234, 212, 0.12);
    border-color: var(--oa-accent);

    .fd-agora-dot {
      background: #4ade80;
      box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.25);
      animation: fd-pulse 1.8s ease-in-out infinite;
    }
  }
}

.fd-agora-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--oa-muted);
  flex-shrink: 0;
  transition: background 0.2s;
}

.fd-agora-hint {
  display: block;
  font-size: 0.75rem;
  color: var(--oa-muted);
  margin-top: 6px;
  text-align: center;
}

@keyframes fd-pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.25); }
  50%       { box-shadow: 0 0 0 6px rgba(74, 222, 128, 0.06); }
}

.fd-footer {
  padding: 24px 20px 0;
}
</style>