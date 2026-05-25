<template>
  <section class="brand-hero" aria-labelledby="brand-title">
    <div class="brand-art" aria-label="Project logo">
      <img
        class="logo-image"
        src="/brand/our_logo.png"
        alt="Knowledge Explorer logo with a llama, connected knowledge graph nodes, and a growth chart"
      />
    </div>

    <div class="hero-copy">
      <p class="eyebrow">SUPER_BANK · GRAPH INTELLIGENCE</p>
      <h1 id="brand-title">Knowledge Explorer <span>&amp; Transparency</span></h1>
      <p class="slogan">Turning banking complexity into connected insights.</p>
      <p class="description">
        Trace systems, teams, controls, ownership and operational impact through
        evidence-backed graph intelligence with grounded AI explanations.
      </p>

      <div class="hero-actions">
        <button type="button" class="primary" @click="$emit('explore')">Ask a question</button>
        <button type="button" class="secondary" @click="$emit('kpis')">Explore KPIs</button>
      </div>

      <div class="trust-strip" aria-label="Solution capabilities">
        <span><i /> Neo4j evidence</span>
        <span><i /> Explainable impact paths</span>
        <span><i /> Local AI enrichment</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineEmits<{ explore: []; kpis: [] }>()
</script>

<style scoped>
.brand-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(260px, .72fr) minmax(430px, 1.28fr);
  gap: clamp(26px, 4vw, 64px);
  align-items: center;
  overflow: hidden;
  margin-bottom: 18px;
  padding: clamp(24px, 4vw, 42px);
  border: 1px solid #16314d;
  border-radius: 25px;
  background:
    radial-gradient(circle at 15% 45%, rgba(45, 212, 191, .12), transparent 33%),
    radial-gradient(circle at 84% 6%, rgba(56, 189, 248, .13), transparent 28%),
    linear-gradient(118deg, #061221 0%, #08182b 54%, #061120 100%);
  box-shadow: 0 24px 70px rgba(1, 6, 18, .38);
}
.brand-hero::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: radial-gradient(circle, rgba(56,189,248,.18) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to left, rgba(0,0,0,.24), transparent 44%);
}
.brand-art {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 260px;
}
.logo-image {
  width: min(100%, 320px);
  height: auto;
  display: block;
  filter: drop-shadow(0 16px 28px rgba(0, 0, 0, .22));
}
.hero-copy { position: relative; z-index: 1; }
.eyebrow {
  margin: 0 0 11px;
  color: #38bdf8;
  font-size: .7rem;
  letter-spacing: .2em;
  font-weight: 760;
}
h1 {
  margin: 0 0 12px;
  max-width: 700px;
  color: #f3f7fd;
  font-size: clamp(2.05rem, 3.3vw, 3rem);
  line-height: 1.05;
  letter-spacing: -.055em;
}
h1 span { color: #81e6e0; }
.slogan {
  margin: 0 0 12px;
  color: #d6e6f6;
  font-size: clamp(1.04rem, 1.4vw, 1.18rem);
  font-weight: 540;
}
.description {
  margin: 0;
  max-width: 620px;
  color: #8ea7c1;
  font-size: .93rem;
  line-height: 1.62;
}
.hero-actions { display: flex; gap: 11px; margin-top: 25px; }
.hero-actions button {
  border-radius: 11px;
  padding: 12px 18px;
  font-weight: 720;
  cursor: pointer;
  transition: transform .16s ease, border-color .16s ease, background .16s ease;
}
.hero-actions button:hover { transform: translateY(-1px); }
.primary { border: 1px solid #38bdf8; background: #38bdf8; color: #04111f; }
.secondary { border: 1px solid #24425f; background: #0b1d32; color: #daebfa; }
.secondary:hover { border-color: #38bdf8; }
.trust-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 17px;
  margin-top: 27px;
  color: #8099b5;
  font-size: .75rem;
}
.trust-strip span { display: flex; align-items: center; gap: 7px; }
.trust-strip i {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #2dd4bf;
  box-shadow: 0 0 10px rgba(45, 212, 191, .6);
}
@media (max-width: 980px) {
  .brand-hero { grid-template-columns: 1fr; }
  .brand-art { min-height: 220px; }
  .logo-image { width: min(100%, 260px); }
}
@media (max-width: 570px) {
  .hero-actions { flex-direction: column; }
}
</style>
