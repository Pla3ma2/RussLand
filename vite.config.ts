import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  base: "./",
  build: { target: "es2020" },
  define: { __BUILD__: JSON.stringify(new Date().toISOString().slice(0, 16).replace("T", " ")) },
  plugins: [
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "RussLand",
        short_name: "RussLand",
        description: "Apprendre le russe, pour les francophones",
        lang: "fr",
        start_url: "./",
        scope: "./",
        display: "standalone",
        background_color: "#f6f1e9",
        theme_color: "#3d5a80",
        icons: [
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // В установочный кэш — только само приложение (≈1 МБ), чтобы обновление ставилось быстро и надёжно.
        // Уроки (json) — «сначала сеть», озвучка — сохраняется по мере прослушивания.
        globPatterns: ["**/*.{js,css,html,svg,png,webmanifest}"],
        globIgnores: ["**/models/**", "**/vosk-*.js", "**/audio/**", "**/content/**"],
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true,
        runtimeCaching: [
          {
            urlPattern: ({ url }) => /\/content\/.*\.json$/.test(url.pathname),
            handler: "NetworkFirst",
            options: { cacheName: "content", networkTimeoutSeconds: 4, expiration: { maxEntries: 100 } },
          },
          {
            // озвучка 5000 слов (~5000 файлов) — сохраняется по мере прослушивания
            urlPattern: ({ url }) => /\/audio\/.*\.mp3$/.test(url.pathname),
            handler: "CacheFirst",
            options: { cacheName: "audio", expiration: { maxEntries: 12000 }, cacheableResponse: { statuses: [0, 200] } },
          },
          {
            // движок распознавания (5 МБ) кэшируем, только когда его включат
            urlPattern: ({ url }) => /\/assets\/vosk-.*\.js$/.test(url.pathname),
            handler: "CacheFirst",
            options: { cacheName: "vosk-engine", expiration: { maxEntries: 4 } },
          },
        ],
        maximumFileSizeToCacheInBytes: 8 * 1024 * 1024,
      },
    }),
  ],
});
