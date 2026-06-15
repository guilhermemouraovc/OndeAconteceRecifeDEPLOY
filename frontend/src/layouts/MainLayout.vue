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
        </nav>

        <q-btn
          v-if="showSearch"
          flat
          round
          dense
          icon="tune"
          aria-label="Abrir filtros"
          class="header-icon-btn q-ml-sm"
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

      <div v-if="showSearch && !$route.path.startsWith('/evento')" class="search-bar">
        <q-input
          v-model="store.searchQuery"
          dense
          borderless
          clearable
          dark
          placeholder="Buscar shows, peças, exposições..."
          class="search-input"
          @keyup.enter="goProgramacao"
        >
          <template #prepend>
            <q-icon name="search" color="grey-5" />
          </template>
        </q-input>
      </div>
    </q-header>

    <q-drawer v-model="filterDrawer" side="right" overlay bordered class="filter-drawer">
      <q-scroll-area class="fit">
        <div class="filter-drawer__inner">
          <div class="filter-drawer__title font-display">Filtros</div>

          <CategoryFilter v-model="store.filterCategoria" />

          <div class="filter-group">
            <label class="filter-label">Preço</label>
            <q-select
              v-model="store.filterPreco"
              :options="precoOptions"
              emit-value
              map-options
              clearable
              dense
              outlined
              dark
              label="Todos"
            />
          </div>

          <div class="filter-group">
            <label class="filter-label">Bairro</label>
            <q-select
              v-model="store.filterBairro"
              :options="store.bairrosDisponiveis"
              clearable
              dense
              outlined
              dark
              label="Todos"
            />
          </div>

          <div class="filter-group">
            <label class="filter-label">Data</label>
            <q-select
              v-model="store.filterData"
              :options="dataOptions"
              emit-value
              map-options
              clearable
              dense
              outlined
              dark
              label="Qualquer"
            />
          </div>

          <q-toggle
            v-model="store.filterAgora"
            label="O que tá rolando agora? (3h)"
            color="accent"
            dark
            class="q-mt-md"
          />

          <div class="filter-actions q-mt-lg">
            <q-btn
              color="primary"
              label="Aplicar"
              no-caps
              unelevated
              class="full-width"
              @click="filterDrawer = false"
            />
            <q-btn
              v-if="store.hasActiveFilters"
              flat
              label="Limpar filtros"
              no-caps
              color="grey-5"
              class="full-width q-mt-sm"
              @click="store.clearFilters()"
            />
          </div>
        </div>
      </q-scroll-area>
    </q-drawer>

    <q-drawer v-model="mobileMenu" side="left" overlay bordered class="mobile-drawer">
      <q-list dark padding>
        <q-item
          v-for="item in [...navItems, { name: 'scraper', label: 'Coleta', icon: 'sync' }]"
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
        <div class="footer-col footer-col--brand">
          <div class="brand">
            <span class="brand-mark" aria-hidden="true" />
            <span class="brand-text">
              <span class="brand-title font-display">Onde Acontece</span>
              <span class="brand-sub">Recife</span>
            </span>
          </div>
          <p class="footer-tagline">
            A agenda cultural da cidade, reunindo eventos da Prefeitura, produtores independentes e
            plataformas de ingressos num só lugar.
          </p>
        </div>

        <div class="footer-col">
          <div class="footer-heading">Explorar</div>
          <router-link :to="{ name: 'programacao' }" class="footer-link">Programação</router-link>
          <router-link :to="{ name: 'mapa' }" class="footer-link">Mapa de eventos</router-link>
          <router-link :to="{ name: 'favoritos' }" class="footer-link">Salvos</router-link>
        </div>

        <div class="footer-col">
          <div class="footer-heading">Produtores</div>
          <router-link :to="{ name: 'cadastro' }" class="footer-link">Cadastrar evento</router-link>
          <router-link :to="{ name: 'moderacao' }" class="footer-link">Moderação</router-link>
          <router-link :to="{ name: 'scraper' }" class="footer-link">Coleta de dados</router-link>
        </div>
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
  { name: 'cadastro', label: 'Cadastrar', icon: 'add_circle' },
  { name: 'moderacao', label: 'Moderação', icon: 'task_alt' },
]

const precoOptions = [
  { label: 'Gratuito', value: 'gratuito' },
  { label: 'Até R$ 50', value: 'ate50' },
  { label: 'R$ 50 a R$ 100', value: '50a100' },
  { label: 'Acima de R$ 100', value: 'acima100' },
]

const dataOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: 'Amanhã', value: 'amanha' },
  { label: 'Fim de semana', value: 'fds' },
  { label: 'Esta semana', value: 'semana' },
]

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
}

.search-bar {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px 14px;
  width: 100%;
}

.search-input {
  max-width: 460px;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 0 18px;
  transition: border-color 0.2s ease;

  &:focus-within {
    border-color: rgba(94, 234, 212, 0.5);
  }
}

.filter-drawer,
.mobile-drawer {
  background: var(--oa-deep) !important;
  color: white;
}

.filter-drawer__inner {
  padding: 24px 20px;
}

.filter-drawer__title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.filter-group {
  margin-top: 16px;
}

.filter-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--oa-muted);
  margin-bottom: 6px;
}

.oa-footer {
  background: #04101d !important;
  color: var(--oa-muted);
}

.footer-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 16px 24px;
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  gap: 32px;
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-tagline {
  margin: 12px 0 0;
  font-size: 0.9rem;
  line-height: 1.65;
  max-width: 360px;
}

.footer-heading {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(248, 250, 252, 0.85);
  margin-bottom: 4px;
}

.footer-link {
  color: var(--oa-muted);
  text-decoration: none;
  font-size: 0.92rem;
  transition: color 0.2s ease;

  &:hover {
    color: var(--oa-accent);
  }
}


@media (max-width: 768px) {
  .footer-inner {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>