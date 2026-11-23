import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  base: "./",
  build: { target: "es2020" },
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
        // уроки и озвучка — в офлайн-кэш сразу; модель Vosk (45 МБ) сама сохраняется в IndexedDB, когда её включат
        globPatterns: ["**/*.{js,css,html,svg,png,json,mp3}"],
        globIgnores: ["**/models/**", "**/vosk-*.js"],
        runtimeCaching: [
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
