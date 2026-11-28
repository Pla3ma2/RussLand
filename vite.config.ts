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
      // Офлайн-режим убран: этот service worker при установке удаляет себя и все старые кэши.
      selfDestroying: true,
    }),
  ],
});
