export default defineNuxtConfig({
  devtools: { enabled: false },
  css: ["~/assets/main.css"],
  runtimeConfig: {
    // Override at container runtime using NUXT_API_TARGET.
    apiTarget: "http://backend:8000/api",
  },
})
