<template>
  <section class="brand-hero" aria-labelledby="brand-title">
    <div class="brand-art" aria-label="Financial Institution Knowledge Explorer logo">
      <div class="logo-mark">
        <svg viewBox="0 0 188 188" role="img" aria-labelledby="logo-title">
          <title id="logo-title">Peruvian llama knowledge graph mark</title>
          <defs>
            <linearGradient id="llamaBody" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#32d3c5" />
              <stop offset="1" stop-color="#1f9eb0" />
            </linearGradient>
            <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
              <stop stop-color="#fbbf24" />
              <stop offset="1" stop-color="#f59e0b" />
            </linearGradient>
          </defs>
          <circle cx="94" cy="94" r="86" fill="#061425" stroke="#17334c" stroke-width="2" />
          <path d="M20 120C47 99 66 103 91 81c23-20 45-21 77-18" fill="none" stroke="#163551" stroke-width="2"/>
          <path d="M24 73C47 59 69 55 93 63c20 7 38 21 68 21" fill="none" stroke="#102b47" stroke-width="2"/>
          <circle cx="25" cy="119" r="5" fill="#38bdf8" />
          <circle cx="54" cy="59" r="5" fill="#fbbf24" />
          <circle cx="160" cy="63" r="6" fill="#38bdf8" />
          <circle cx="164" cy="113" r="5" fill="#2dd4bf" />
          <path d="M66 126c-7-20-5-45 4-58 4-6 9-9 18-10l1-22c0-6 4-10 9-10 5 0 8 4 9 10l2 16c4-3 8-4 12-4 16 0 27 14 27 31v32h-18V86c0-7-4-13-11-13-7 0-10 6-10 15v38H66Z" fill="url(#llamaBody)" />
          <path d="M88 59c8 0 16 5 19 13l-12 4c-3-3-7-4-12-3l5-14Z" fill="#071624" opacity=".4"/>
          <circle cx="100" cy="46" r="3.5" fill="#061425" />
          <path d="M81 105h49M78 113h52" stroke="#f1f5f9" stroke-width="3" opacity=".84" />
          <path d="M87 96 100 87l13 9 13-9" fill="none" stroke="url(#gold)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
          <circle cx="87" cy="96" r="3" fill="#fbbf24" />
          <circle cx="100" cy="87" r="3" fill="#fbbf24" />
          <circle cx="113" cy="96" r="3" fill="#fbbf24" />
          <circle cx="126" cy="87" r="3" fill="#fbbf24" />
        </svg>
      </div>
      <div class="wordmark">
        <p>FINANCIAL INSTITUTION</p>
        <strong>KNOWLEDGE<br />EXPLORER</strong>
        <span>Evidence · Accountability · Insight</span>
      </div>
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
  grid-template-columns: minmax(280px, .72fr) minmax(430px, 1.28fr);
  gap: clamp(30px, 5vw, 72px);
  align-items: center;
  overflow: hidden;
  margin-bottom: 18px;
  padding: clamp(27px, 4vw, 46px);
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
  background-image:
    radial-gradient(circle, rgba(56,189,248,.22) 1px, transparent 1px);
  background-size: 42px 42px;
  mask-image: linear-gradient(to left, rgba(0,0,0,.33), transparent 44%);
}
.brand-art {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 19px;
  min-height: 205px;
}
.logo-mark {
  flex: 0 0 min(188px, 48%);
  filter: drop-shadow(0 14px 26px rgba(17, 170, 180, .16));
}
.logo-mark svg { display: block; width: 100%; height: auto; }
.wordmark p {
  margin: 0 0 7px;
  color: #67d6ec;
  font-size: .61rem;
  font-weight: 760;
  letter-spacing: .2em;
}
.wordmark strong {
  display: block;
  color: #eef6ff;
  font-size: clamp(1.04rem, 1.45vw, 1.26rem);
  letter-spacing: .08em;
  line-height: 1.32;
}
.wordmark span {
  display: block;
  margin-top: 13px;
  max-width: 145px;
  color: #7290ad;
  font-size: .66rem;
  line-height: 1.55;
  letter-spacing: .06em;
  text-transform: uppercase;
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
  width: 7px; height: 7px; border-radius: 50%;
  background: #2dd4bf; box-shadow: 0 0 10px rgba(45, 212, 191, .6);
}
@media (max-width: 980px) {
  .brand-hero { grid-template-columns: 1fr; }
  .brand-art { justify-content: center; min-height: auto; }
}
@media (max-width: 570px) {
  .brand-art { gap: 9px; }
  .hero-actions { flex-direction: column; }
}
</style>
