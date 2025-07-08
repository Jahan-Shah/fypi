// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  // devtools: { enabled: true },
  vite: {
    plugins:
      [tailwindcss(),],
    server: {
      proxy: {
        '/api2': {
          target: 'http://localhost:5000/',
          changeOrigin: true,
          rewrite: path => path.replace(/^\/api2/, '/api'),
          ws: true,
        }
      },
      // optional if you're working with ngrok:
      allowedHosts: ['.ngrok-free.app'],
    },
  },
  css: ['~/assets/css/main.css'],
  modules: [
    '@nuxt/eslint',
    '@nuxt/icon',
    '@nuxt/fonts',
    '@nuxt/image',
    'nuxt-mongoose',
    'shadcn-nuxt',
  ],
  shadcn: {
    /**
     * Prefix for all the imported component
     */
    prefix: '',
    /**
     * Directory that the component lives in.
     * @default "./components/ui"
     */
    componentDir: './components/ui'
  }
})