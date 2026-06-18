const WEEKDAYS = ['domingo', 'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado']

export function parseDateTime(value) {
  if (!value) return null
  const raw = String(value).trim()
  const withTime = raw.includes('T') ? raw : `${raw}T00:00:00`
  const date = new Date(withTime)
  return Number.isNaN(date.getTime()) ? null : date
}

export function eventHour(event) {
  const date = parseDateTime(event?.inicio_iso)
  return date ? date.getHours() + date.getMinutes() / 60 : null
}

export function weekdayIndex(event) {
  const date = parseDateTime(event?.inicio_iso)
  return date ? date.getDay() : null
}

export function numericPrice(event) {
  if (event?.gratuito || event?.preco === 0) return 0
  const value = Number(event?.preco)
  return Number.isFinite(value) ? value : null
}

export function isPaidEvent(event) {
  return !event?.gratuito && numericPrice(event) !== 0
}

export function applyDashboardFilters(events, filters) {
  return events.filter((event) => {
    if (filters.category && !normalize(event.categoria).includes(normalize(filters.category))) return false
    if (filters.neighborhood && !normalize(event.bairro).includes(normalize(filters.neighborhood))) return false
    if (filters.source && normalize(event.source) !== normalize(filters.source)) return false

    const price = numericPrice(event)
    if (filters.freeOnly && price !== 0) return false
    if (filters.minPrice !== '' && price != null && price < Number(filters.minPrice)) return false
    if (filters.maxPrice !== '' && price != null && price > Number(filters.maxPrice)) return false

    if (filters.dayMode && filters.dayMode !== 'todos') {
      const day = weekdayIndex(event)
      if (day == null) return false
      if (filters.dayMode === 'hoje') {
        const today = new Date().getDay()
        if (day !== today) return false
      } else if (filters.dayMode === 'fds' && ![5, 6].includes(day)) {
        return false
      } else if (filters.dayMode === 'semana' && ![1, 2, 3, 4, 5].includes(day)) {
        return false
      }
    }

    return true
  })
}

export function countBy(items, getter) {
  const map = new Map()
  for (const item of items) {
    const key = getter(item) || 'Sem informação'
    map.set(key, (map.get(key) || 0) + 1)
  }
  return [...map.entries()].sort((a, b) => b[1] - a[1])
}

export function histogram(values, bins = 8) {
  const clean = values.filter((value) => Number.isFinite(value))
  if (!clean.length) return []
  const min = Math.min(...clean)
  const max = Math.max(...clean)
  if (min === max) {
    return [{ label: formatRange(min, max), count: clean.length, start: min, end: max }]
  }
  const size = (max - min) / bins
  const buckets = Array.from({ length: bins }, (_, index) => ({
    start: min + index * size,
    end: min + (index + 1) * size,
    count: 0,
  }))
  for (const value of clean) {
    const rawIndex = Math.floor((value - min) / size)
    const index = Math.min(bins - 1, Math.max(0, rawIndex))
    buckets[index].count += 1
  }
  return buckets.map((bucket) => ({
    ...bucket,
    label: formatRange(bucket.start, bucket.end),
  }))
}

export function pearsonCorrelation(xs, ys) {
  const pairs = xs
    .map((x, index) => [x, ys[index]])
    .filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y))

  if (pairs.length < 2) return 0

  const xVals = pairs.map(([x]) => x)
  const yVals = pairs.map(([, y]) => y)
  const xMean = mean(xVals)
  const yMean = mean(yVals)
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

  if (!xDen || !yDen) return 0
  return num / Math.sqrt(xDen * yDen)
}

export function linearRegression(points) {
  const clean = points.filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y))
  if (clean.length < 2) {
    return null
  }

  const xs = clean.map(([x]) => x)
  const ys = clean.map(([, y]) => y)
  const xMean = mean(xs)
  const yMean = mean(ys)

  let numerator = 0
  let denominator = 0
  for (const [x, y] of clean) {
    numerator += (x - xMean) * (y - yMean)
    denominator += (x - xMean) ** 2
  }

  const slope = denominator ? numerator / denominator : 0
  const intercept = yMean - slope * xMean
  const predictions = xs.map((x) => slope * x + intercept)
  const residuals = ys.map((y, index) => y - predictions[index])
  const total = ys.reduce((acc, y) => acc + (y - yMean) ** 2, 0)
  const residualSum = residuals.reduce((acc, r) => acc + r ** 2, 0)
  const r2 = total ? 1 - residualSum / total : 0
  const mae = mean(residuals.map((value) => Math.abs(value)))
  const rmse = Math.sqrt(mean(residuals.map((value) => value ** 2)))

  return {
    slope,
    intercept,
    predictions,
    residuals,
    r2,
    mae,
    rmse,
    points: clean,
  }
}

export function classificationMetrics(events, threshold = 0.5) {
  const rows = events
    .map((event) => {
      const actual = isPaidEvent(event) ? 1 : 0
      const prediction = predictedProbability(event)
      return prediction == null ? null : { actual, score: prediction }
    })
    .filter(Boolean)

  if (!rows.length) return null

  let tp = 0
  let tn = 0
  let fp = 0
  let fn = 0

  for (const row of rows) {
    const predicted = row.score >= threshold ? 1 : 0
    if (row.actual === 1 && predicted === 1) tp += 1
    else if (row.actual === 0 && predicted === 0) tn += 1
    else if (row.actual === 0 && predicted === 1) fp += 1
    else if (row.actual === 1 && predicted === 0) fn += 1
  }

  const accuracy = (tp + tn) / rows.length
  const precision = tp + fp ? tp / (tp + fp) : 0
  const recall = tp + fn ? tp / (tp + fn) : 0
  const f1 = precision + recall ? (2 * precision * recall) / (precision + recall) : 0
  const roc = rocCurve(rows)
  const pr = precisionRecallCurve(rows)

  return {
    counts: { tp, tn, fp, fn },
    accuracy,
    precision,
    recall,
    f1,
    roc,
    pr,
    support: rows.length,
  }
}

export function rocCurve(rows) {
  const scores = uniqueScores(rows)
  const points = scores.map((threshold) => {
    let tp = 0
    let fp = 0
    let tn = 0
    let fn = 0
    for (const row of rows) {
      const predicted = row.score >= threshold ? 1 : 0
      if (row.actual === 1 && predicted === 1) tp += 1
      else if (row.actual === 0 && predicted === 0) tn += 1
      else if (row.actual === 0 && predicted === 1) fp += 1
      else if (row.actual === 1 && predicted === 0) fn += 1
    }
    return {
      threshold,
      fpr: fp + tn ? fp / (fp + tn) : 0,
      tpr: tp + fn ? tp / (tp + fn) : 0,
    }
  })

  points.unshift({ threshold: 1.01, fpr: 0, tpr: 0 })
  points.push({ threshold: -0.01, fpr: 1, tpr: 1 })
  points.sort((a, b) => a.fpr - b.fpr || a.tpr - b.tpr)
  return { points, auc: areaUnderCurve(points.map((point) => [point.fpr, point.tpr])) }
}

export function precisionRecallCurve(rows) {
  const scores = uniqueScores(rows)
  const points = scores.map((threshold) => {
    let tp = 0
    let fp = 0
    let fn = 0
    for (const row of rows) {
      const predicted = row.score >= threshold ? 1 : 0
      if (row.actual === 1 && predicted === 1) tp += 1
      else if (row.actual === 0 && predicted === 1) fp += 1
      else if (row.actual === 1 && predicted === 0) fn += 1
    }
    const precision = tp + fp ? tp / (tp + fp) : 1
    const recall = tp + fn ? tp / (tp + fn) : 0
    return { threshold, precision, recall }
  })

  points.unshift({ threshold: 1.01, precision: 1, recall: 0 })
  points.push({ threshold: -0.01, precision: mean(rows.map((row) => row.actual)), recall: 1 })
  points.sort((a, b) => a.recall - b.recall || b.precision - a.precision)
  return { points, auc: areaUnderCurve(points.map((point) => [point.recall, point.precision])) }
}

export function kMeans(points, k = 3, iterations = 12) {
  const clean = points.filter((point) => point.every((value) => Number.isFinite(value)))
  if (!clean.length) return { labels: [], centroids: [] }

  const actualK = Math.max(1, Math.min(k, clean.length))
  let centroids = clean.slice(0, actualK).map((point) => [...point])
  let labels = new Array(clean.length).fill(0)

  for (let iteration = 0; iteration < iterations; iteration += 1) {
    labels = clean.map((point) => nearestCentroid(point, centroids))
    const nextCentroids = Array.from({ length: actualK }, (_, cluster) => {
      const members = clean.filter((_, index) => labels[index] === cluster)
      if (!members.length) return centroids[cluster]
      return members[0].map((_, dimension) => mean(members.map((member) => member[dimension])))
    })

    const stable = nextCentroids.every((centroid, index) =>
      centroid.every((value, dimension) => Math.abs(value - centroids[index][dimension]) < 1e-6),
    )
    centroids = nextCentroids
    if (stable) break
  }

  return { labels, centroids, points: clean }
}

export function scaleLinear(values, minOutput = 0, maxOutput = 1) {
  const clean = values.filter((value) => Number.isFinite(value))
  const min = Math.min(...clean)
  const max = Math.max(...clean)
  if (!clean.length) return () => minOutput
  if (min === max) return () => (minOutput + maxOutput) / 2
  return (value) => minOutput + ((value - min) / (max - min)) * (maxOutput - minOutput)
}

export function normalize(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

export function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatDecimal(value, digits = 2) {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value)
}

export function formatCount(value) {
  return new Intl.NumberFormat('pt-BR').format(value)
}

export function getWeekdayLabel(index) {
  return WEEKDAYS[index] || 'sem data'
}

function uniqueScores(rows) {
  const scores = [...new Set(rows.map((row) => row.score).filter((value) => Number.isFinite(value)))]
  return scores.sort((a, b) => b - a)
}

function predictedProbability(event) {
  const clf = event?.classificacao_texto || {}
  const probability = clf.probabilidade_pago
  if (Number.isFinite(probability)) return probability
  if (typeof clf.pago === 'number') return clf.pago
  if (typeof clf.gratuito === 'number') return 1 - clf.gratuito
  return null
}

function mean(values) {
  const clean = values.filter((value) => Number.isFinite(value))
  if (!clean.length) return 0
  return clean.reduce((acc, value) => acc + value, 0) / clean.length
}

function nearestCentroid(point, centroids) {
  let best = 0
  let bestDistance = Infinity
  centroids.forEach((centroid, index) => {
    const distance = centroid.reduce((sum, value, dimension) => sum + (value - point[dimension]) ** 2, 0)
    if (distance < bestDistance) {
      bestDistance = distance
      best = index
    }
  })
  return best
}

function areaUnderCurve(points) {
  if (points.length < 2) return 0
  let area = 0
  for (let i = 1; i < points.length; i += 1) {
    const [x1, y1] = points[i - 1]
    const [x2, y2] = points[i]
    area += ((y1 + y2) / 2) * (x2 - x1)
  }
  return Math.abs(area)
}

function formatRange(start, end) {
  return `${Math.round(start)} - ${Math.round(end)}`
}
