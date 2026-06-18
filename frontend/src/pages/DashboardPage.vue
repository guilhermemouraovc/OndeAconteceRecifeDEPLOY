<template>
  <q-page class="bg-landing dashboard-page">
    <div class="main-container dashboard-shell">
      <section class="dashboard-hero">
        <div class="dashboard-hero__copy">
          <span class="section-eyebrow">OndeAconteceRecife · Painel analítico</span>
          <h1 class="dashboard-hero__title font-display">
            Dashboard interativo
            <em>com leitura visual</em> da agenda cultural
          </h1>
          <p class="dashboard-hero__subtitle">
            Visualização consolidada com análise exploratória, regressão, classificação simples e
            agrupamentos. Os gráficos são alimentados pelos CSVs do projeto para refletir a base de
            dados real do trabalho.
          </p>
        </div>

        <q-card class="hero-summary">
          <div class="hero-summary__label">Base carregada</div>
          <div class="hero-summary__value">
            {{ formatCount(filteredEvents.length) }}
            <span>eventos</span>
          </div>
          <div class="hero-summary__meta">
            <span>{{ uniqueCategories.length }} categorias</span>
            <span>{{ uniqueNeighborhoods.length }} bairros</span>
            <span>{{ uniqueSources.length }} fontes</span>
          </div>
        </q-card>
      </section>

      <q-card class="filters-panel glass-card">
        <div class="filters-panel__title">Filtros do dashboard</div>
        <div class="filters-grid">
          <q-select v-model="filters.category" :options="categoryOptions" label="Categoria" dense outlined clearable emit-value map-options dark />
          <q-select v-model="filters.neighborhood" :options="neighborhoodOptions" label="Bairro" dense outlined clearable emit-value map-options dark />
          <q-select v-model="filters.source" :options="sourceOptions" label="Fonte" dense outlined clearable emit-value map-options dark />
          <q-select v-model="filters.dayMode" :options="dayModeOptions" label="Recorte temporal" dense outlined emit-value map-options dark />
          <q-input v-model="filters.minPrice" type="number" label="Preço mínimo" dense outlined dark />
          <q-input v-model="filters.maxPrice" type="number" label="Preço máximo" dense outlined dark />
        </div>
        <div class="filters-panel__footer">
          <q-toggle v-model="filters.freeOnly" color="teal" label="Somente gratuitos" />
          <q-btn flat no-caps color="grey-4" label="Limpar filtros" @click="resetFilters" />
        </div>
      </q-card>

      <div class="kpi-grid">
        <q-card v-for="item in kpis" :key="item.label" class="kpi-card glass-card">
          <div class="kpi-card__label">{{ item.label }}</div>
          <div class="kpi-card__value">{{ item.value }}</div>
          <div class="kpi-card__hint">{{ item.hint }}</div>
        </q-card>
      </div>

      <q-tabs
        v-model="tab"
        dense
        align="left"
        class="dashboard-tabs"
        active-color="white"
        indicator-color="accent"
        narrow-indicator
      >
        <q-tab name="overview" label="Exploração" />
        <q-tab name="regression" label="Regressão" />
        <q-tab name="classification" label="Classificação" />
        <q-tab name="clusters" label="Agrupamentos" />
      </q-tabs>

      <q-tab-panels v-model="tab" animated class="dashboard-panels">
        <q-tab-panel name="overview" class="panel-content">
          <div class="panel-grid panel-grid--two">
            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Distribuição</div>
                  <h2 class="panel-card__title">Categorias em destaque</h2>
                </div>
              </div>
              <div class="stack-list">
                <div v-for="item in topCategories" :key="item.label" class="stack-row">
                  <div class="stack-row__top">
                    <span>{{ item.label }}</span>
                    <strong>{{ formatCount(item.count) }}</strong>
                  </div>
                  <q-linear-progress size="10px" rounded color="teal" :value="item.share" />
                </div>
              </div>
            </q-card>

            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Agrupamento</div>
                  <h2 class="panel-card__title">Bairros mais frequentes</h2>
                </div>
              </div>
              <div class="stack-list">
                <div v-for="item in topNeighborhoods" :key="item.label" class="stack-row">
                  <div class="stack-row__top">
                    <span>{{ item.label }}</span>
                    <strong>{{ formatCount(item.count) }}</strong>
                  </div>
                  <q-linear-progress size="10px" rounded color="amber" :value="item.share" />
                </div>
              </div>
            </q-card>

            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Distribuição</div>
                  <h2 class="panel-card__title">Preço dos eventos</h2>
                </div>
              </div>
              <div class="stack-list">
                <div v-for="bucket in priceHistogram" :key="bucket.label" class="stack-row">
                  <div class="stack-row__top">
                    <span>{{ bucket.label }}</span>
                    <strong>{{ bucket.count }}</strong>
                  </div>
                  <q-linear-progress size="10px" rounded color="deep-orange" :value="bucket.share" />
                </div>
              </div>
            </q-card>

            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Correlação</div>
                  <h2 class="panel-card__title">Leitura multivariada</h2>
                </div>
              </div>
              <div class="corr-table">
                <div class="corr-table__head">
                  <span />
                  <span v-for="label in correlationLabels" :key="label">{{ label }}</span>
                </div>
                <div v-for="row in correlationMatrix" :key="row.label" class="corr-table__row">
                  <span class="corr-table__label">{{ row.label }}</span>
                  <span
                    v-for="cell in row.values"
                    :key="cell.label"
                    class="corr-table__cell"
                    :style="{ '--cell-color': cellColor(cell.value) }"
                  >
                    {{ formatDecimal(cell.value, 2) }}
                  </span>
                </div>
              </div>
            </q-card>
          </div>

          <q-card class="panel-card glass-card q-mt-lg">
            <div class="panel-card__head">
              <div>
                <div class="panel-card__eyebrow">Insights iniciais</div>
                <h2 class="panel-card__title">Leitura textual da base filtrada</h2>
              </div>
            </div>
            <div class="insight-grid">
              <div v-for="item in overviewInsights" :key="item.title" class="insight-card">
                <div class="insight-card__title">{{ item.title }}</div>
                <p class="insight-card__text">{{ item.text }}</p>
              </div>
            </div>
          </q-card>
        </q-tab-panel>

        <q-tab-panel name="regression" class="panel-content">
          <div class="panel-grid panel-grid--two">
            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Dispersão</div>
                  <h2 class="panel-card__title">Movimentação x hora</h2>
                </div>
                <div class="metric-pill" v-if="regression">
                  R² {{ formatDecimal(regression.r2, 2) }}
                </div>
              </div>

              <div v-if="regression" class="svg-wrap">
                <svg viewBox="0 0 1000 520" role="img" aria-label="Dispersão e linha de tendência">
                  <line
                    v-for="line in regression.gridLines"
                    :key="line"
                    :x1="regression.padding.left"
                    :x2="1000 - regression.padding.right"
                    :y1="line"
                    :y2="line"
                    class="svg-grid"
                  />
                  <line
                    :x1="regression.line.x1"
                    :y1="regression.line.y1"
                    :x2="regression.line.x2"
                    :y2="regression.line.y2"
                    class="svg-trend"
                  />
                  <circle
                    v-for="point in regression.points"
                    :key="point.key"
                    :cx="point.cx"
                    :cy="point.cy"
                    :r="point.r"
                    :fill="point.fill"
                    class="svg-point"
                  />
                </svg>
              </div>
            </q-card>

            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Resíduos</div>
                  <h2 class="panel-card__title">Desvio do modelo linear</h2>
                </div>
              </div>

              <div v-if="regression" class="svg-wrap svg-wrap--small">
                <svg viewBox="0 0 1000 360" role="img" aria-label="Resíduos da regressão">
                  <line
                    v-for="line in regression.residualGrid"
                    :key="line"
                    :x1="regression.padding.left"
                    :x2="1000 - regression.padding.right"
                    :y1="line"
                    :y2="line"
                    class="svg-grid"
                  />
                  <line
                    :x1="regression.padding.left"
                    :x2="1000 - regression.padding.right"
                    :y1="regression.zeroY"
                    :y2="regression.zeroY"
                    class="svg-baseline"
                  />
                  <circle
                    v-for="point in regression.residualPoints"
                    :key="point.key"
                    :cx="point.cx"
                    :cy="point.cy"
                    :r="point.r"
                    :fill="point.fill"
                    class="svg-point"
                  />
                </svg>
              </div>

              <div v-if="regressionResidualHistogram.length" class="stack-list stack-list--compact">
                <div v-for="bucket in regressionResidualHistogram" :key="bucket.label" class="stack-row">
                  <div class="stack-row__top">
                    <span>{{ bucket.label }}</span>
                    <strong>{{ bucket.count }}</strong>
                  </div>
                  <q-linear-progress size="10px" rounded color="deep-orange" :value="bucket.share" />
                </div>
              </div>
            </q-card>
          </div>

          <q-card class="panel-card glass-card q-mt-lg">
            <div class="panel-card__head">
              <div>
                <div class="panel-card__eyebrow">Interpretação</div>
                <h2 class="panel-card__title">O que a regressão está sugerindo</h2>
              </div>
            </div>
            <div class="insight-grid">
              <div class="insight-card">
                <div class="insight-card__title">Tendência</div>
                <p class="insight-card__text">{{ regressionSummary.trend }}</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Ajuste</div>
                <p class="insight-card__text">{{ regressionSummary.fit }}</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Resíduos</div>
                <p class="insight-card__text">{{ regressionSummary.residuals }}</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Leitura prática</div>
                <p class="insight-card__text">{{ regressionSummary.practical }}</p>
              </div>
            </div>
          </q-card>
        </q-tab-panel>

        <q-tab-panel name="classification" class="panel-content">
          <div class="metric-grid metric-grid--four">
            <q-card v-for="metric in classificationKpis" :key="metric.label" class="kpi-card glass-card">
              <div class="kpi-card__label">{{ metric.label }}</div>
              <div class="kpi-card__value">{{ metric.value }}</div>
              <div class="kpi-card__hint">{{ metric.hint }}</div>
            </q-card>
          </div>

          <div class="panel-grid panel-grid--two q-mt-lg">
            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Matriz de confusão</div>
                  <h2 class="panel-card__title">Classificador simples</h2>
                </div>
              </div>
              <div v-if="classification" class="confusion-wrap">
                <div class="confusion-wrap__axis-top">Previsto</div>
                <div class="confusion-wrap__labels">
                  <span />
                  <span>Pago</span>
                  <span>Gratuito</span>
                </div>
                <div class="confusion-wrap__body">
                  <div class="confusion-wrap__axis-side">Real</div>
                  <div class="confusion-wrap__rows">
                    <div class="confusion-wrap__row">
                      <span class="confusion-wrap__row-label">Pago</span>
                      <span class="confusion-wrap__cell" :style="{ '--cell-alpha': confusionIntensity(classification.counts.tp) }"><strong>{{ classification.counts.tp }}</strong><small>TP</small></span>
                      <span class="confusion-wrap__cell" :style="{ '--cell-alpha': confusionIntensity(classification.counts.fp) }"><strong>{{ classification.counts.fp }}</strong><small>FP</small></span>
                    </div>
                    <div class="confusion-wrap__row">
                      <span class="confusion-wrap__row-label">Gratuito</span>
                      <span class="confusion-wrap__cell" :style="{ '--cell-alpha': confusionIntensity(classification.counts.fn) }"><strong>{{ classification.counts.fn }}</strong><small>FN</small></span>
                      <span class="confusion-wrap__cell" :style="{ '--cell-alpha': confusionIntensity(classification.counts.tn) }"><strong>{{ classification.counts.tn }}</strong><small>TN</small></span>
                    </div>
                  </div>
                </div>
              </div>
            </q-card>

            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">ROC e PR</div>
                  <h2 class="panel-card__title">Capacidade de separação</h2>
                </div>
                <div class="metric-pill" v-if="classification">
                  {{ activeModel }}
                </div>
              </div>

              <div class="q-mb-md">
                <q-btn-toggle
                  v-model="activeModel"
                  :options="modelOptions"
                  no-caps
                  unelevated
                  toggle-color="teal"
                  text-color="grey-2"
                  class="model-toggle"
                />
              </div>

              <div v-if="classification" class="svg-stack">
                <div class="svg-wrap svg-wrap--small">
                  <svg viewBox="0 0 1000 360" role="img" aria-label="Curva ROC">
                    <line
                      v-for="line in classificationModel.rocGrid"
                      :key="line"
                      :x1="classificationModel.padding.left"
                      :x2="1000 - classificationModel.padding.right"
                      :y1="line"
                      :y2="line"
                      class="svg-grid"
                    />
                    <line x1="64" y1="296" x2="936" y2="64" class="svg-baseline" />
                    <polyline :points="classificationModel.rocPolyline" class="svg-curve svg-curve--gold" />
                  </svg>
                </div>

                <div class="svg-wrap svg-wrap--small">
                  <svg viewBox="0 0 1000 360" role="img" aria-label="Curva Precision Recall">
                    <line
                      v-for="line in classificationModel.prGrid"
                      :key="line"
                      :x1="classificationModel.padding.left"
                      :x2="1000 - classificationModel.padding.right"
                      :y1="line"
                      :y2="line"
                      class="svg-grid"
                    />
                    <line :x1="classificationModel.padding.left" :x2="1000 - classificationModel.padding.right" :y1="classificationModel.prBaselineY" :y2="classificationModel.prBaselineY" class="svg-baseline" />
                    <polyline :points="classificationModel.prPolyline" class="svg-curve svg-curve--teal" />
                  </svg>
                </div>
              </div>
            </q-card>
          </div>

          <q-card class="panel-card glass-card q-mt-lg">
            <div class="panel-card__head">
              <div>
                <div class="panel-card__eyebrow">Narrativa</div>
                <h2 class="panel-card__title">Leitura textual das métricas</h2>
              </div>
            </div>
            <div class="insight-grid">
              <div class="insight-card">
                <div class="insight-card__title">Acurácia</div>
                <p class="insight-card__text">{{ classificationSummary.accuracy }}</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Precisão e recall</div>
                <p class="insight-card__text">{{ classificationSummary.balance }}</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">ROC e PR</div>
                <p class="insight-card__text">{{ classificationSummary.curves }}</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Implicação prática</div>
                <p class="insight-card__text">{{ classificationSummary.practical }}</p>
              </div>
            </div>
          </q-card>
        </q-tab-panel>

        <q-tab-panel name="clusters" class="panel-content">
          <div class="panel-grid panel-grid--two">
            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Agrupamentos</div>
                  <h2 class="panel-card__title">Clusters simples por hora e preço</h2>
                </div>
              </div>
              <div v-if="cluster" class="svg-wrap">
                <svg viewBox="0 0 1000 520" role="img" aria-label="Clusters por hora e preço">
                  <line
                    v-for="line in cluster.gridLines"
                    :key="line"
                    :x1="cluster.padding.left"
                    :x2="1000 - cluster.padding.right"
                    :y1="line"
                    :y2="line"
                    class="svg-grid"
                  />
                  <circle
                    v-for="point in cluster.points"
                    :key="point.key"
                    :cx="point.cx"
                    :cy="point.cy"
                    :r="point.r"
                    :fill="point.fill"
                    class="svg-point"
                  />
                </svg>
              </div>
            </q-card>

            <q-card class="panel-card glass-card">
              <div class="panel-card__head">
                <div>
                  <div class="panel-card__eyebrow">Resumo dos grupos</div>
                  <h2 class="panel-card__title">Leitura rápida dos agrupamentos</h2>
                </div>
              </div>

              <div class="cluster-list">
                <div v-for="item in clusterSummary" :key="item.label" class="cluster-item">
                  <div class="cluster-item__top">
                    <span>{{ item.label }}</span>
                    <strong>{{ formatCount(item.count) }}</strong>
                  </div>
                  <div class="cluster-item__meta">{{ item.meta }}</div>
                </div>
              </div>
            </q-card>
          </div>

          <q-card class="panel-card glass-card q-mt-lg">
            <div class="panel-card__head">
              <div>
                <div class="panel-card__eyebrow">Movimentação por bairro e hora</div>
                <h2 class="panel-card__title">Mapa de calor da base de horários</h2>
              </div>
            </div>

            <div class="q-mb-md">
              <q-select v-model="movementDay" :options="movementDays" label="Dia da semana" dense outlined emit-value map-options dark style="max-width: 260px" />
            </div>

            <div v-if="movementHeatmap.length" class="heatmap">
              <div class="heatmap__head">
                <span />
                <span v-for="hour in movementHours" :key="hour">{{ hour }}</span>
              </div>
              <div v-for="row in movementHeatmap" :key="row.label" class="heatmap__row">
                <span class="heatmap__label">{{ row.label }}</span>
                <span
                  v-for="cell in row.values"
                  :key="cell.hour"
                  class="heatmap__cell"
                  :style="{ '--heat-color': heatColor(cell.value) }"
                >
                  {{ formatDecimal(cell.value, 0) }}
                </span>
              </div>
            </div>
          </q-card>

          <q-card class="panel-card glass-card q-mt-lg">
            <div class="panel-card__head">
              <div>
                <div class="panel-card__eyebrow">Documentação breve</div>
                <h2 class="panel-card__title">Decisões visuais e uso web</h2>
              </div>
            </div>
            <div class="insight-grid">
              <div class="insight-card">
                <div class="insight-card__title">Clareza</div>
                <p class="insight-card__text">Os gráficos foram organizados por objetivo analítico e mantêm a linguagem visual do OndeAconteceRecife.</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Usabilidade</div>
                <p class="insight-card__text">Os filtros ficam no topo e cada aba responde ao recorte sem exigir sair da aplicação principal.</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Publicação</div>
                <p class="insight-card__text">A visualização fica acessível diretamente no frontend do projeto, sem dashboard paralelo.</p>
              </div>
              <div class="insight-card">
                <div class="insight-card__title">Melhorias</div>
                <p class="insight-card__text">Os CSVs agora alimentam a análise, então a entrega passa a refletir a base enviada para o trabalho.</p>
              </div>
            </div>
          </q-card>
        </q-tab-panel>
      </q-tab-panels>
    </div>
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useApi } from 'src/composables/useApi'
import { formatCount, formatCurrency, formatDecimal, scaleLinear } from 'src/utils/dashboardAnalytics'

const { getJson } = useApi()

const tab = ref('overview')
const activeModel = ref('Random Forest')
const movementDay = ref('Segunda')
const dashboardData = ref(null)
const loading = ref(false)
const error = ref('')

const filters = reactive({
  category: '',
  neighborhood: '',
  source: '',
  dayMode: 'todos',
  minPrice: '',
  maxPrice: '',
  freeOnly: false,
})

const dayModeOptions = [
  { label: 'Todos', value: 'todos' },
  { label: 'Hoje', value: 'hoje' },
  { label: 'Fim de semana', value: 'fds' },
  { label: 'Semana', value: 'semana' },
]

const modelOptions = [
  { label: 'Random Forest', value: 'Random Forest' },
  { label: 'Regressão Logística', value: 'Regressao Logistica' },
]

const stats = computed(() => dashboardData.value?.stats || {})
const events = computed(() => dashboardData.value?.events || [])
const movement = computed(() => dashboardData.value?.movement || [])

const categoryOptions = computed(() => (stats.value.top_categories || []).map((item) => ({ label: item.label, value: item.label })))
const neighborhoodOptions = computed(() => (stats.value.top_neighborhoods || []).map((item) => ({ label: item.label, value: item.label })))
const sourceOptions = computed(() => [...new Set(events.value.map((event) => event.source).filter(Boolean))].sort().map((value) => ({ label: value, value })))
const uniqueCategories = computed(() => [...new Set(events.value.map((event) => event.categoria).filter(Boolean))])
const uniqueNeighborhoods = computed(() => [...new Set(events.value.map((event) => event.bairro).filter(Boolean))])
const uniqueSources = computed(() => [...new Set(events.value.map((event) => event.source).filter(Boolean))])

const kpis = computed(() => [
  {
    label: 'Eventos',
    value: formatCount(stats.value.total || filteredEvents.value.length),
    hint: 'base carregada dos CSVs do projeto',
  },
  {
    label: 'Gratuitos',
    value: formatCount(stats.value.free_count || filteredEvents.value.filter((event) => event.gratuito || numericPrice(event) === 0).length),
    hint: 'eventos sem cobrança de ingresso',
  },
  {
    label: 'Preço médio',
    value: stats.value.avg_price != null ? formatCurrency(stats.value.avg_price) : 'N/D',
    hint: 'média do recorte atual',
  },
  {
    label: 'Público médio',
    value: stats.value.avg_public != null ? formatCount(Math.round(stats.value.avg_public)) : 'N/D',
    hint: 'estimativa média de presença',
  },
])

const filteredEvents = computed(() => applyEventFilters(events.value, filters))

const topCategories = computed(() => countsAsShare(filteredEvents.value, (event) => event.categoria).slice(0, 6))
const topNeighborhoods = computed(() => countsAsShare(filteredEvents.value, (event) => event.bairro).slice(0, 6))
const priceHistogram = computed(() => histogram(filteredEvents.value.map((event) => numericPrice(event)), 8))
const regressionResidualHistogram = computed(() => histogram(dashboardData.value?.regression?.residuals || [], 8))

const correlationLabels = ['Preço', 'Público', 'Hora', 'Gratuito']
const correlationMatrix = computed(() => {
  const rows = filteredEvents.value
  const vectors = {
    price: rows.map((event) => numericPrice(event)),
    public: rows.map((event) => toNumber(event.publico_estimado)),
    hour: rows.map((event) => toNumber(event.hour)),
    free: rows.map((event) => (event.gratuito ? 1 : 0)),
  }
  return [
    correlationRow('Preço', 'price', ['price', 'public', 'hour', 'free'], vectors),
    correlationRow('Público', 'public', ['price', 'public', 'hour', 'free'], vectors),
    correlationRow('Hora', 'hour', ['price', 'public', 'hour', 'free'], vectors),
    correlationRow('Gratuito', 'free', ['price', 'public', 'hour', 'free'], vectors),
  ]
})

const regression = computed(() => {
  const data = dashboardData.value?.regression
  if (!data) return null
  const points = data.points || []
  const width = 1000
  const height = 520
  const padding = { top: 44, right: 48, bottom: 56, left: 64 }
  const xs = points.map((p) => p.hora)
  const ys = points.map((p) => p.movimentacao_pct)
  const xScale = scaleLinear(xs, padding.left, width - padding.right)
  const yScale = scaleLinear(ys, height - padding.bottom, padding.top)
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const line = {
    x1: xScale(minX),
    y1: yScale(data.slope * minX + data.intercept),
    x2: xScale(maxX),
    y2: yScale(data.slope * maxX + data.intercept),
  }
  return {
    padding,
    points: points.map((point, index) => ({
      key: `${index}-${point.hora}-${point.movimentacao_pct}`,
      cx: xScale(point.hora),
      cy: yScale(point.movimentacao_pct),
      r: 5,
      fill: '#e25549',
    })),
    line,
    gridLines: gridLines(height, padding.top, height - padding.bottom, 5),
    residualPoints: points.map((point, index) => ({
      key: `res-${index}-${point.hora}`,
      cx: xScale(point.pred),
      cy: yScale(point.residual),
      r: 4,
      fill: '#5eead4',
    })),
    residualGrid: gridLines(360, 36, 312, 4),
    zeroY: scaleLinear(ys, 312, 36)(0),
    r2: data.r2,
    mae: data.mae,
    rmse: data.rmse,
    slope: data.slope,
    intercept: data.intercept,
  }
})

const classification = computed(() => dashboardData.value?.classification?.models?.[activeModel.value] || null)

const classificationKpis = computed(() => {
  if (!classification.value) return emptyMetricSet()
  return [
    { label: 'Acurácia', value: `${formatDecimal(classification.value.accuracy * 100, 1)}%`, hint: `base de ${classification.value.support} amostras` },
    { label: 'Precisão', value: `${formatDecimal(classification.value.precision * 100, 1)}%`, hint: 'erros positivos sob controle' },
    { label: 'Recall', value: `${formatDecimal(classification.value.recall * 100, 1)}%`, hint: 'capacidade de encontrar os pagos' },
    { label: 'F1-score', value: `${formatDecimal(classification.value.f1 * 100, 1)}%`, hint: 'equilíbrio entre precisão e recall' },
  ]
})

const classificationModel = computed(() => {
  if (!classification.value) return null
  const roc = classification.value.roc.points || []
  const pr = classification.value.pr.points || []
  return {
    padding: { top: 36, right: 48, bottom: 42, left: 64 },
    rocPolyline: roc.map((point) => `${scaleLinear(roc.map((p) => p.fpr), 64, 952)(point.fpr)},${scaleLinear(roc.map((p) => p.tpr), 318, 36)(point.tpr)}`).join(' '),
    prPolyline: pr.map((point) => `${scaleLinear(pr.map((p) => p.recall), 64, 952)(point.recall)},${scaleLinear(pr.map((p) => p.precision), 318, 36)(point.precision)}`).join(' '),
    rocGrid: gridLines(360, 36, 318, 5),
    prGrid: gridLines(360, 36, 318, 5),
    prBaselineY: scaleLinear(pr.map((p) => p.precision), 318, 36)(classification.value.baseline_rate ?? baselineRate()),
    confusion: classification.value.confusion_matrix,
    featureImportance: classification.value.feature_importance || [],
    rocAuc: classification.value.roc.auc,
    prAuc: classification.value.pr.auc,
  }
})

const cluster = computed(() => {
  const data = dashboardData.value?.clusters
  if (!data) return null
  const points = data.points || []
  const width = 1000
  const height = 520
  const padding = { top: 44, right: 48, bottom: 48, left: 64 }
  const xs = points.map((point) => point.hour)
  const ys = points.map((point) => point.preco)
  const xScale = scaleLinear(xs, padding.left, width - padding.right)
  const yScale = scaleLinear(ys, height - padding.bottom, padding.top)
  const palette = ['#5eead4', '#f5a623', '#e25549']
  return {
    padding,
    points: points.map((point, index) => ({
      key: `${index}-${point.hour}-${point.preco}`,
      cx: xScale(point.hour),
      cy: yScale(point.preco),
      r: 6,
      fill: palette[point.cluster % palette.length],
    })),
    gridLines: gridLines(height, padding.top, height - padding.bottom, 5),
    centroids: data.centroids || [],
  }
})

const clusterSummary = computed(() => {
  if (!dashboardData.value?.clusters?.centroids) return []
  return dashboardData.value.clusters.centroids.map((centroid, index) => {
    const count = dashboardData.value.clusters.points.filter((point) => point.cluster === index).length
    return {
      label: `Grupo ${index + 1}`,
      count,
      meta: `Hora média em ${formatDecimal(centroid.hour, 1)}h · preço médio de ${formatCurrency(centroid.preco)}`,
    }
  })
})

const movementDays = computed(() => [...new Set(movement.value.map((item) => item.dia_semana).filter(Boolean))].sort())
const movementHours = computed(() => [...new Set(movement.value.filter((item) => item.dia_semana === movementDay.value).map((item) => item.horario_label))].slice(0, 12))
const movementHeatmap = computed(() => buildHeatmap(movement.value, movementDay.value))

const regressionSummary = computed(() => {
  if (!regression.value) {
    return {
      trend: 'Ainda não há pontos suficientes para desenhar uma tendência confiável.',
      fit: 'Sem ajuste estatístico no recorte atual.',
      residuals: 'Sem resíduos porque o modelo não foi montado.',
      practical: 'Amplie o recorte de dados para liberar a leitura de tendência.',
    }
  }
  return {
    trend: regression.value.slope >= 0
      ? 'A inclinação está positiva, indicando que horários maiores tendem a estar associados a maior movimentação.'
      : 'A inclinação está negativa, indicando que horários maiores tendem a estar associados a menor movimentação.',
    fit: `O modelo linear explica ${formatDecimal(regression.value.r2 * 100, 1)}% da variação observada, com RMSE de ${formatDecimal(regression.value.rmse, 2)}.`,
    residuals: `Os resíduos têm MAE de ${formatDecimal(regression.value.mae, 2)}, mostrando o quanto a tendência se afasta dos pontos reais.`,
    practical: 'A linha de tendência ajuda a comunicar a direção da relação, mas ela ainda não substitui uma análise mais rica com mais variáveis.',
  }
})

const classificationSummary = computed(() => {
  if (!classification.value) {
    return {
      accuracy: 'Sem previsões suficientes para calcular acurácia.',
      balance: 'Sem valores de precisão e recall no recorte atual.',
      curves: 'ROC e precision-recall exigem probabilidades para desenhar a curva.',
      practical: 'Amplie o recorte para medir o classificador simples.',
    }
  }
  return {
    accuracy: `Acurácia de ${formatDecimal(classification.value.accuracy * 100, 1)}% sobre ${classification.value.support} eventos avaliados.`,
    balance: `Precisão de ${formatDecimal(classification.value.precision * 100, 1)}% e recall de ${formatDecimal(classification.value.recall * 100, 1)}% mostram o equilíbrio entre falsos positivos e falsos negativos.`,
    curves: `A área sob a ROC é ${formatDecimal(classification.value.roc.auc, 3)} e a área sob precision-recall é ${formatDecimal(classification.value.pr.auc, 3)}.`,
    practical: 'Quando o recall cai, o sistema deixa de reconhecer eventos pagos; quando a precisão cai, ele sinaliza pagos onde não deveria.',
  }
})

const overviewInsights = computed(() => {
  const topCategory = topCategories.value[0]
  const topNeighborhood = topNeighborhoods.value[0]
  const strongest = strongestCorrelationValue.value
  return [
    {
      title: 'Categoria dominante',
      text: topCategory
        ? `${topCategory.label} lidera o recorte com ${formatCount(topCategory.count)} eventos, mostrando concentração temática na agenda.`
        : 'Ainda não há eventos suficientes para destacar uma categoria dominante.',
    },
    {
      title: 'Bairro mais frequente',
      text: topNeighborhood
        ? `${topNeighborhood.label} aparece com maior volume e tende a concentrar a oferta cultural no conjunto filtrado.`
        : 'Ainda não há eventos suficientes para apontar um bairro predominante.',
    },
    {
      title: 'Correlação mais visível',
      text: strongest
        ? `${strongest.labelA} e ${strongest.labelB} apresentam correlação de ${formatDecimal(strongest.value, 2)}.`
        : 'Não foi possível estimar correlação com o recorte atual.',
    },
    {
      title: 'Leitura geral',
      text: 'O painel combina distribuição, relação linear, métricas de classificação e agrupamento simples para dar uma visão multivariada inicial da base.',
    },
  ]
})

const strongestCorrelationValue = computed(() => {
  let strongest = null
  for (const row of correlationMatrix.value) {
    for (const cell of row.values) {
      if (!strongest || Math.abs(cell.value) > strongest.value) {
        strongest = { labelA: row.label, labelB: cell.label, value: Math.abs(cell.value) }
      }
    }
  }
  return strongest
})

onMounted(loadDashboard)

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    dashboardData.value = await getJson('/dashboard/data')
    movementDay.value = movementDays.value[0] || 'Segunda'
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Falha ao carregar dashboard.'
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.category = ''
  filters.neighborhood = ''
  filters.source = ''
  filters.dayMode = 'todos'
  filters.minPrice = ''
  filters.maxPrice = ''
  filters.freeOnly = false
}

function applyEventFilters(list, active) {
  return list.filter((event) => {
    if (active.category && !normalize(event.categoria).includes(normalize(active.category))) return false
    if (active.neighborhood && !normalize(event.bairro).includes(normalize(active.neighborhood))) return false
    if (active.source && !normalize(event.source).includes(normalize(active.source))) return false
    const price = numericPrice(event)
    if (active.freeOnly && price !== 0) return false
    if (active.minPrice !== '' && price != null && price < Number(active.minPrice)) return false
    if (active.maxPrice !== '' && price != null && price > Number(active.maxPrice)) return false
    if (active.dayMode !== 'todos') {
      const weekday = normalize(event.weekday)
      if (active.dayMode === 'hoje') {
        if (!weekday.includes(normalize(currentWeekday()))) return false
      } else if (active.dayMode === 'fds' && !['sábado', 'domingo'].includes(weekday)) {
        return false
      } else if (active.dayMode === 'semana' && ['sábado', 'domingo'].includes(weekday)) {
        return false
      }
    }
    return true
  })
}

function countsAsShare(list, getter) {
  const map = new Map()
  for (const item of list) {
    const key = getter(item) || 'Sem informação'
    map.set(key, (map.get(key) || 0) + 1)
  }
  const total = [...map.values()].reduce((acc, value) => acc + value, 0) || 1
  return [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([label, count]) => ({ label, count, share: count / total }))
}

function histogram(values, bins = 8) {
  const clean = values.filter((value) => Number.isFinite(value))
  if (!clean.length) return []
  const min = Math.min(...clean)
  const max = Math.max(...clean)
  if (min === max) return [{ label: `${round(min)} - ${round(max)}`, count: clean.length, share: 1 }]
  const size = (max - min) / bins
  const buckets = Array.from({ length: bins }, (_, index) => ({
    start: min + index * size,
    end: min + (index + 1) * size,
    count: 0,
  }))
  for (const value of clean) {
    const index = Math.min(bins - 1, Math.max(0, Math.floor((value - min) / size)))
    buckets[index].count += 1
  }
  const total = buckets.reduce((acc, bucket) => acc + bucket.count, 0) || 1
  return buckets.map((bucket) => ({
    label: `${round(bucket.start)} - ${round(bucket.end)}`,
    count: bucket.count,
    share: bucket.count / total,
  }))
}

function correlationRow(labelA, baseKey, keys, vectors) {
  return {
    label: labelA,
    values: keys.map((key) => ({
      label: key,
      value: pearson(vectors[baseKey], vectors[key]),
    })),
  }
}

function pearson(xs, ys) {
  const pairs = xs
    .map((x, index) => [x, ys[index]])
    .filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y))
  if (pairs.length < 2) return 0
  const xMean = mean(pairs.map(([x]) => x))
  const yMean = mean(pairs.map(([, y]) => y))
  let num = 0
  let xDen = 0
  let yDen = 0
  for (const [x, y] of pairs) {
    const dx = x - xMean
    const dy = y - yMean
    num += dx * dy
    xDen += dx * dx
    yDen += dy * dy
  }
  return xDen && yDen ? num / Math.sqrt(xDen * yDen) : 0
}

function buildHeatmap(list, day) {
  const rows = list.filter((item) => item.dia_semana === day)
  const hours = [...new Set(rows.map((item) => item.horario_label))].sort((a, b) => {
    const [ah] = a.split(':').map(Number)
    const [bh] = b.split(':').map(Number)
    return ah - bh
  })
  const byBairro = [...new Set(rows.map((item) => item.bairro))].sort()
  return byBairro.map((bairro) => ({
    label: bairro,
    values: hours.map((hour) => {
      const cell = rows.filter((item) => item.bairro === bairro && item.horario_label === hour)
      const value = cell.length ? mean(cell.map((item) => Number(item.movimentacao_pct))) : 0
      return { hour, value }
    }),
  }))
}

function heatColor(value) {
  const v = Math.min(1, Math.max(0, value / 100))
  const hue = 205 - v * 150
  return `hsla(${hue}, 72%, 50%, ${0.18 + v * 0.45})`
}

function cellColor(value) {
  if (!Number.isFinite(value)) return 'rgba(255, 255, 255, 0.04)'
  const normalized = Math.max(-1, Math.min(1, value))
  const magnitude = Math.abs(normalized)
  const alpha = 0.08 + magnitude * 0.34
  const hue = normalized >= 0 ? 165 : 12
  return `hsla(${hue}, 72%, 50%, ${alpha})`
}

function confusionIntensity(value) {
  const counts = classification.value?.confusion_matrix || [[1]]
  const flat = counts.flat()
  const max = Math.max(...flat, 1)
  return Math.max(0.18, value / max)
}

function mean(values) {
  const clean = values.filter((value) => Number.isFinite(value))
  return clean.length ? clean.reduce((acc, value) => acc + value, 0) / clean.length : 0
}

function normalize(value) {
  return String(value || '').trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
}

function numericPrice(event) {
  if (event.gratuito || Number(event.preco) === 0) return 0
  const value = Number(event.preco)
  return Number.isFinite(value) ? value : null
}

function toNumber(value) {
  const n = Number(value)
  return Number.isFinite(n) ? n : null
}

function currentWeekday() {
  return ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'][new Date().getDay()]
}

function baselineRate() {
  const model = classification.value
  if (!model) return 0
  return model.recall
}

function round(value) {
  return Math.round(value)
}

function emptyMetricSet() {
  return [
    { label: 'Acurácia', value: 'N/D', hint: 'sem previsão disponível' },
    { label: 'Precisão', value: 'N/D', hint: 'sem previsão disponível' },
    { label: 'Recall', value: 'N/D', hint: 'sem previsão disponível' },
    { label: 'F1-score', value: 'N/D', hint: 'sem previsão disponível' },
  ]
}

function buildGridLines(height, top, bottom, count) {
  const step = (bottom - top) / Math.max(1, count - 1)
  return Array.from({ length: count }, (_, index) => top + index * step)
}

function gridLines(height, top, bottom, count) {
  return buildGridLines(height, top, bottom, count)
}

</script>

<style scoped lang="scss">
.dashboard-page {
  padding-top: 28px;
  padding-bottom: 60px;
}

.dashboard-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.dashboard-hero {
  display: grid;
  grid-template-columns: 1.25fr 0.75fr;
  gap: 20px;
  align-items: stretch;
}

.dashboard-hero__title {
  font-size: clamp(2.2rem, 5vw, 4rem);
  line-height: 1.04;
  color: #fff;
  margin: 16px 0 0;
}

.dashboard-hero__title em {
  color: var(--oa-gold);
  font-style: italic;
}

.dashboard-hero__subtitle {
  max-width: 68ch;
  margin: 18px 0 0;
  color: var(--oa-muted);
  line-height: 1.7;
  font-size: 1.05rem;
}

.hero-summary {
  padding: 22px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.03));
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-summary__label {
  color: var(--oa-accent);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.75rem;
  font-weight: 700;
}

.hero-summary__value {
  color: #fff;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 700;
  margin-top: 8px;
}

.hero-summary__value span {
  font-size: 0.95rem;
  color: var(--oa-muted);
  margin-left: 8px;
}

.hero-summary__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  margin-top: 12px;
  color: var(--oa-muted);
  font-size: 0.9rem;
}

.glass-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.035));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
  border-radius: 22px;
  backdrop-filter: blur(14px);
}

.filters-panel {
  padding: 20px;
}

.filters-panel__title {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 14px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.filters-panel__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.kpi-grid,
.metric-grid {
  display: grid;
  gap: 14px;
}

.kpi-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.metric-grid--four {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.kpi-card {
  padding: 18px;
}

.kpi-card__label {
  color: var(--oa-muted);
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.kpi-card__value {
  color: #fff;
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  font-weight: 700;
  margin-top: 10px;
}

.kpi-card__hint {
  margin-top: 6px;
  color: var(--oa-muted);
  line-height: 1.5;
}

.dashboard-tabs {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  padding: 6px;
  width: fit-content;
}

.dashboard-panels {
  background: transparent;
}

.panel-content {
  padding: 20px 0 0;
}

.panel-grid {
  display: grid;
  gap: 18px;
}

.panel-grid--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.panel-card {
  padding: 20px;
}

.panel-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.panel-card__eyebrow {
  color: var(--oa-accent);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.74rem;
  font-weight: 700;
}

.panel-card__title {
  color: #fff;
  font-size: 1.3rem;
  margin: 6px 0 0;
}

.metric-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(94, 234, 212, 0.12);
  border: 1px solid rgba(94, 234, 212, 0.24);
  color: var(--oa-accent);
  font-weight: 700;
  white-space: nowrap;
}

.stack-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.stack-list--compact {
  margin-top: 18px;
}

.stack-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stack-row__top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #fff;
  font-size: 0.92rem;
}

.stack-row__top strong {
  color: var(--oa-gold);
}

.corr-table {
  display: grid;
  gap: 8px;
}

.corr-table__head,
.corr-table__row {
  display: grid;
  grid-template-columns: 110px repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.corr-table__head {
  color: var(--oa-muted);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding-bottom: 4px;
}

.corr-table__label,
.corr-table__cell {
  padding: 12px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.corr-table__label {
  color: #fff;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.03);
}

.corr-table__cell {
  background: var(--cell-color);
  color: #fff;
  text-align: center;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}

.insight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.insight-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.insight-card__title {
  color: var(--oa-gold);
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.insight-card__text {
  color: var(--oa-text);
  line-height: 1.7;
  margin: 10px 0 0;
}

.svg-wrap {
  width: 100%;
}

.svg-wrap--small {
  margin-top: 8px;
}

.svg-wrap svg {
  width: 100%;
  height: auto;
  display: block;
}

.svg-grid {
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 1;
}

.svg-trend {
  stroke: var(--oa-gold);
  stroke-width: 4;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.svg-curve {
  fill: none;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.svg-curve--gold {
  stroke: var(--oa-gold);
}

.svg-curve--teal {
  stroke: var(--oa-accent);
}

.svg-baseline {
  stroke: rgba(255, 255, 255, 0.28);
  stroke-width: 2.5;
  stroke-dasharray: 8 8;
}

.svg-point {
  stroke: rgba(6, 22, 38, 0.4);
  stroke-width: 2;
}

.confusion-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.confusion-wrap__axis-top {
  color: var(--oa-muted);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.78rem;
  font-weight: 700;
  text-align: center;
}

.confusion-wrap__labels {
  display: grid;
  grid-template-columns: 96px repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.confusion-wrap__labels span {
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  color: var(--oa-gold);
  font-size: 0.84rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  text-align: center;
}

.confusion-wrap__body {
  display: flex;
  gap: 10px;
}

.confusion-wrap__axis-side {
  width: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--oa-muted);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.78rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  min-height: 240px;
}

.confusion-wrap__rows {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.confusion-wrap__row {
  display: grid;
  grid-template-columns: 96px repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.confusion-wrap__row-label,
.confusion-wrap__cell {
  border-radius: 16px;
  min-height: 112px;
}

.confusion-wrap__row-label {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: rgba(255, 255, 255, 0.04);
  font-weight: 700;
}

.confusion-wrap__cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, var(--cell-alpha));
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #fff;
}

.confusion-wrap__cell strong {
  font-size: 1.6rem;
  font-weight: 800;
}

.confusion-wrap__cell small {
  color: var(--oa-muted);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.model-toggle {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 999px;
}

.cluster-list {
  display: grid;
  gap: 12px;
}

.cluster-item {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.cluster-item__top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #fff;
  font-weight: 700;
}

.cluster-item__top strong {
  color: var(--oa-accent);
}

.cluster-item__meta {
  margin-top: 8px;
  color: var(--oa-muted);
  line-height: 1.6;
}

.heatmap {
  display: grid;
  gap: 8px;
  overflow-x: auto;
}

.heatmap__head,
.heatmap__row {
  display: grid;
  grid-template-columns: 160px repeat(auto-fit, minmax(60px, 1fr));
  gap: 8px;
}

.heatmap__head {
  color: var(--oa-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.heatmap__label,
.heatmap__cell {
  padding: 12px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.heatmap__label {
  background: rgba(255, 255, 255, 0.03);
  color: #fff;
  font-weight: 700;
}

.heatmap__cell {
  background: var(--heat-color);
  color: #fff;
  text-align: center;
}

.section-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--oa-accent);
}

.section-eyebrow::before {
  content: '';
  width: 28px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--frevo-2), var(--frevo-4));
}

@media (max-width: 1100px) {
  .dashboard-hero,
  .panel-grid--two,
  .kpi-grid,
  .metric-grid--four,
  .insight-grid,
  .filters-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filters-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 780px) {
  .dashboard-hero,
  .panel-grid--two,
  .kpi-grid,
  .metric-grid--four,
  .insight-grid,
  .filters-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-tabs {
    width: 100%;
  }

  .corr-table__head,
  .corr-table__row {
    grid-template-columns: 90px repeat(4, minmax(0, 1fr));
  }
}
</style>
