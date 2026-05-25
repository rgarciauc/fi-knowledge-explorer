export default defineNuxtConfig({
  devtools: { enabled: false },
  css: ["~/assets/main.css"],
  runtimeConfig: {
    // Server-side API proxy target.
    apiTarget: "http://backend:8000/api",
    public: {
      // Keep "/api" for same-origin operation. For a local demo, this can be set
      // to "http://localhost:8000/api" to bypass any intermediary buffering.
      streamingApiBase: "/api",
    },
  },
})
