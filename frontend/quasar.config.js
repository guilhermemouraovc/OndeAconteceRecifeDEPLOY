import { defineConfig } from '#q-app/wrappers'

export default defineConfig(() => {
  return {
    boot: ['pinia'],

    css: ['app.scss'],

    extras: ['mdi-v7', 'material-icons'],

    build: {
      target: {
        browser: ['es2022', 'firefox115', 'chrome115', 'safari14'],
        node: 'node20',
      },
      vueRouterMode: 'history',
      extendViteConf(viteConf) {
        viteConf.build.chunkSizeWarningLimit = 1000
        viteConf.build.cssCodeSplit = true
        viteConf.build.sourcemap = false
      },
    },

    devServer: {
      open: true,
      port: 9200,
    },

    framework: {
      config: {
        brand: {
          primary: '#0f766e',
          secondary: '#071a2f',
          accent: '#eab308',
          dark: '#071a2f',
          positive: '#22c55e',
          negative: '#dc2626',
          info: '#5eead4',
          warning: '#f59e0b',
        },
      },
      plugins: ['Notify', 'Dialog'],
    },

    animations: [],

    pwa: {
      workboxMode: 'GenerateSW',
      manifest: {
        name: 'Onde Acontece Recife',
        short_name: 'OARecife',
        description: 'Agenda cultural de Recife',
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#071a2f',
        theme_color: '#0f766e',
        icons: [
          { src: 'icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512x512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    },
  }
})
