export const API_CONFIG = {
  timeout: 15000,
  pageSize: 100,
  carouselItemsPerPage: 4,
}

export const DEFAULT_IMAGES = {
  eventPlaceholder:
    'data:image/svg+xml,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="225" viewBox="0 0 400 225"><rect fill="#0f3d5c" width="400" height="225"/><text x="200" y="118" text-anchor="middle" fill="#5eead4" font-family="sans-serif" font-size="18">Onde Acontece</text></svg>',
    ),
}

export const CATEGORIES = [
  { id: 'musica', name: 'Música', tags: ['música', 'música ao vivo', 'show'], icon: 'music_note', color: 'teal' },
  { id: 'teatro', name: 'Teatro', tags: ['teatro', 'peça', 'espetáculo'], icon: 'theater_comedy', color: 'pink' },
  { id: 'danca', name: 'Dança', tags: ['dança', 'dance'], icon: 'accessibility_new', color: 'purple' },
  { id: 'cinema', name: 'Cinema', tags: ['cinema', 'filme'], icon: 'movie', color: 'blue' },
  { id: 'exposicao', name: 'Exposição', tags: ['exposição', 'arte', 'museu'], icon: 'palette', color: 'amber' },
  { id: 'literatura', name: 'Literatura', tags: ['literatura', 'livro', 'poesia'], icon: 'menu_book', color: 'green' },
  { id: 'oficina', name: 'Oficina', tags: ['oficina', 'workshop'], icon: 'build', color: 'orange' },
  { id: 'festival', name: 'Festival', tags: ['festival', 'festa'], icon: 'celebration', color: 'deep-orange' },
  { id: 'outros', name: 'Outros', tags: ['outros', 'cultura'], icon: 'category', color: 'grey' },
]

export const FORMAT_CONFIG = {
  locale: 'pt-BR',
}

export const PRODUCER_CATEGORIES = [
  'Música ao vivo',
  'Teatro',
  'Dança',
  'Cinema',
  'Exposição',
  'Literatura',
  'Oficina',
  'Festival',
  'Feira cultural',
  'Patrimônio e memória',
  'Infantil',
  'Outros',
]
