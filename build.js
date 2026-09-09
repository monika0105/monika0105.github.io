#!/usr/bin/env node
/**
 * build.js — Portfolio site builder
 *
 * Reads all JSON files from data/ and writes a fully-rendered index.html.
 *
 * Usage:
 *   node build.js
 *
 * To update anything (position, publications, awards, etc.):
 *   1. Edit the relevant file in data/
 *   2. Run: node build.js
 *   3. Open index.html in a browser to check
 *   4. git add . && git commit -m "..." && git push
 *
 * Analytics (GoatCounter):
 *   Set "goatcounter_site" in data/profile.json to your GoatCounter site code,
 *   e.g. "monikasantra" if your dashboard is at https://monikasantra.goatcounter.com
 *   Leave it as "" to disable analytics.
 */

'use strict';
const fs   = require('fs');
const path = require('path');

// ── Load all data files ──────────────────────────────────────────────────────
const d = path.join(__dirname, 'data');
const profile      = JSON.parse(fs.readFileSync(path.join(d, 'profile.json'),      'utf8'));
const publications = JSON.parse(fs.readFileSync(path.join(d, 'publications.json'), 'utf8'));
const experience   = JSON.parse(fs.readFileSync(path.join(d, 'experience.json'),   'utf8'));
const education    = JSON.parse(fs.readFileSync(path.join(d, 'education.json'),    'utf8'));
const awards       = JSON.parse(fs.readFileSync(path.join(d, 'awards.json'),       'utf8'));
const projects     = JSON.parse(fs.readFileSync(path.join(d, 'projects.json'),     'utf8'));

// ── Helper: resolve tag class ────────────────────────────────────────────────
function tagHtml(tag, arxivLinks) {
  if (tag.startsWith('arXiv:')) {
    const id  = tag.slice(6);
    const url = (arxivLinks && arxivLinks[id]) || `https://arxiv.org/abs/${id}`;
    return `<a href="${url}" target="_blank" rel="noopener" class="pub-tag tag-arxiv">${tag}</a>`;
  }
  if (tag === 'under review') return `<span class="pub-tag tag-review">under review</span>`;
  if (/^\d+ citation/.test(tag)) return `<span class="pub-tag tag-cite">${tag}</span>`;
  return `<span class="pub-tag tag-venue">${tag}</span>`;
}

// ── Renderers ────────────────────────────────────────────────────────────────

function renderPublications(pubs) {
  // Build a map of arXiv id → url from the arxiv field on each pub
  const arxivUrls = {};
  pubs.forEach(p => {
    if (p.arxiv) {
      const match = p.arxiv.match(/abs\/([^\s]+)$/);
      if (match) arxivUrls[match[1]] = p.arxiv;
    }
  });

  return pubs.map(p => {
    const authorsHtml = p.authors
      .split(', ')
      .map(a => a.trim() === 'M. Santra' ? `<span class="author-self">${a}</span>` : a)
      .join(', ');

    const citTag = p.citations ? `<span class="pub-tag tag-cite">${p.citations} citation${p.citations !== 1 ? 's' : ''}</span>` : '';
    const tagsHtml = (p.tags || []).map(t => tagHtml(t, arxivUrls)).join('\n            ') + citTag;

    return `
      <div class="pub-item">
        <div class="pub-year">${p.year}</div>
        <div>
          <div class="pub-title">${p.title}</div>
          <div class="pub-authors">${authorsHtml}</div>
          <div class="pub-venue">${p.venue}</div>
          <div class="pub-tags">
            ${tagsHtml}
          </div>
        </div>
      </div>`;
  }).join('\n');
}

function renderExperience(exp) {
  return exp.map(e => `
      <div class="exp-item">
        <div class="exp-header">
          <div class="exp-org">${e.org}</div>
          <div class="exp-period">${e.period}</div>
        </div>
        <div class="exp-role">${e.role} &middot; ${e.location}</div>
        <p class="exp-desc">${e.description}</p>
      </div>`).join('\n');
}

function renderEducation(edu) {
  return edu.map(e => {
    const thesis = e.thesis ? `<div class="edu-thesis">${e.thesis}</div>` : '';
    return `
      <div class="edu-item">
        <div class="edu-school">${e.school}</div>
        <div class="edu-period">${e.period}</div>
        <div class="edu-degree">${e.degree}</div>
        <div class="edu-location">${e.location}</div>
        ${thesis}
      </div>`;
  }).join('\n');
}

function renderAwards(aws) {
  return aws.map(a => {
    const detail = a.detail ? ` — ${a.detail}` : '';
    return `
      <div class="award-item">
        <div class="award-icon">◆</div>
        <div class="award-text"><strong>${a.title}</strong>${detail}</div>
        <div class="award-year">${a.year}</div>
      </div>`;
  }).join('\n');
}

function renderProjects(prs) {
  return prs.map(pr => `
      <div class="project-item">
        <div class="project-name">${pr.name}</div>
        <p class="project-desc">${pr.description}</p>
      </div>`).join('\n');
}

// ── GoatCounter snippet ──────────────────────────────────────────────────────
function analyticsSnippet(siteCode) {
  if (!siteCode) return '<!-- analytics: set goatcounter_site in data/profile.json to enable -->';
  return `<!-- GoatCounter analytics (privacy-friendly, shows views + visitor location) -->
<script data-goatcounter="https://${siteCode}.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script>`;
}

// ── Full HTML template ───────────────────────────────────────────────────────
function buildHtml() {
  const p  = profile;
  const lk = p.links;
  const st = p.scholar_stats;
  const gc = analyticsSnippet((p.analytics && p.analytics.goatcounter_site) || '');

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${p.name} — PhD Candidate, Computer Security</title>
<!-- Generated by build.js — edit data/*.json then run: node build.js -->
<style>
/* ─── TOKENS ─────────────────────────────────────────────────────────── */
:root {
  --navy:        #0D1B2A;
  --navy-card:   #152338;
  --navy-border: #1E3250;
  --teal:        #2BBFA8;
  --teal-dim:    #1E8A78;
  --amber:       #E8A12B;
  --off-white:   #F0F4F8;
  --silver:      #C8D4E0;
  --muted:       #7A92A8;

  --bg:          var(--off-white);
  --bg-card:     #FFFFFF;
  --bg-card2:    #F5F8FB;
  --border:      #D4DDE7;
  --text:        #0D1B2A;
  --text-muted:  #5A7080;
  --text-faint:  #8AA0B0;
  --accent:      var(--teal-dim);
  --accent-glow: #2BBFA8;

  --font-display: 'Palatino Linotype', 'Book Antiqua', Palatino, Georgia, serif;
  --font-body:    system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Courier New', monospace;

  --radius: 6px;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg:          var(--navy);
    --bg-card:     var(--navy-card);
    --bg-card2:    #0F2035;
    --border:      var(--navy-border);
    --text:        var(--off-white);
    --text-muted:  var(--silver);
    --text-faint:  var(--muted);
    --accent:      var(--teal);
    --accent-glow: var(--teal);
  }
}

:root[data-theme="dark"] {
  --bg:          var(--navy);
  --bg-card:     var(--navy-card);
  --bg-card2:    #0F2035;
  --border:      var(--navy-border);
  --text:        var(--off-white);
  --text-muted:  var(--silver);
  --text-faint:  var(--muted);
  --accent:      var(--teal);
  --accent-glow: var(--teal);
}

/* ─── RESET ──────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; font-size: 16px; }
body {
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  transition: background 0.2s, color 0.2s;
  min-height: 100vh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }

/* ─── LAYOUT ─────────────────────────────────────────────────────────── */
.page { max-width: 680px; margin: 0 auto; padding: 4rem 1.5rem 5rem; }

/* ─── HERO ───────────────────────────────────────────────────────────── */
.hero { text-align: center; padding-bottom: 3rem; margin-bottom: 3rem; border-bottom: 1px solid var(--border); }
.avatar {
  width: 128px; height: 128px; border-radius: 50%; object-fit: cover;
  margin: 0 auto 1.5rem; display: block; border: 3px solid var(--bg-card);
  box-shadow: 0 0 0 1px var(--border);
}
.hero-name {
  font-family: var(--font-display); font-size: clamp(1.9rem, 5vw, 2.6rem);
  font-weight: normal; color: var(--text); letter-spacing: -0.01em; margin-bottom: 0.5rem;
}
.hero-title { font-size: 0.95rem; color: var(--text-muted); margin-bottom: 0.6rem; }
.hero-tagline { font-size: 0.88rem; color: var(--text-faint); max-width: 44ch; margin: 0 auto 1.5rem; line-height: 1.6; }
.hero-links { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem 1.25rem; font-size: 0.82rem; }
.hero-links a { color: var(--text-muted); }
.hero-links a:hover { color: var(--accent); }

/* ─── SECTION ANATOMY ────────────────────────────────────────────────── */
section { margin-bottom: 3.5rem; }
.section-title {
  font-family: var(--font-display); font-size: 1.25rem;
  font-weight: normal; color: var(--text); letter-spacing: -0.01em;
  margin-bottom: 1.5rem; padding-bottom: 0.6rem; border-bottom: 1px solid var(--border);
}

/* ─── PUBLICATIONS ───────────────────────────────────────────────────── */
.pub-list { display: flex; flex-direction: column; gap: 0; }
.pub-item {
  padding: 1.4rem 0; border-bottom: 1px solid var(--border);
  display: grid; grid-template-columns: auto 1fr; gap: 0 1.25rem;
}
.pub-item:first-child { padding-top: 0; }
.pub-year {
  font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-faint);
  padding-top: 0.2rem; min-width: 40px; font-variant-numeric: tabular-nums;
}
.pub-title { font-size: 0.92rem; font-weight: 600; color: var(--text); line-height: 1.45; margin-bottom: 0.25rem; }
.pub-authors { font-size: 0.8rem; color: var(--text-faint); margin-bottom: 0.35rem; line-height: 1.4; }
.pub-authors .author-self { color: var(--text-muted); font-weight: 500; }
.pub-venue { font-size: 0.78rem; font-style: italic; color: var(--text-muted); }
.pub-tags { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.5rem; }
.pub-tag {
  font-size: 0.65rem; font-family: var(--font-mono);
  padding: 0.15rem 0.5rem; border-radius: 2px; font-variant-numeric: tabular-nums;
}
.tag-venue {
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent); border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
}
.tag-review {
  background: color-mix(in srgb, var(--amber) 12%, transparent);
  color: var(--amber); border: 1px solid color-mix(in srgb, var(--amber) 30%, transparent);
}
.tag-cite { background: transparent; color: var(--text-faint); border: 1px solid var(--border); }
.tag-arxiv {
  background: color-mix(in srgb, #e07b39 12%, transparent);
  color: #c96a20; border: 1px solid color-mix(in srgb, #e07b39 30%, transparent); text-decoration: none;
}
:root[data-theme="dark"] .tag-arxiv { color: #f0a060; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) .tag-arxiv { color: #f0a060; }
}
a.pub-tag:hover { opacity: 0.8; text-decoration: none; }
.pub-note { margin-top: 1.25rem; font-size: 0.78rem; color: var(--text-faint); }

/* ─── EXPERIENCE ─────────────────────────────────────────────────────── */
.exp-list { display: flex; flex-direction: column; gap: 1.75rem; }
.exp-header {
  display: flex; justify-content: space-between; align-items: baseline;
  flex-wrap: wrap; gap: 0.25rem; margin-bottom: 0.2rem;
}
.exp-org { font-size: 0.95rem; font-weight: 600; color: var(--text); }
.exp-period { font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-faint); font-variant-numeric: tabular-nums; }
.exp-role { font-size: 0.8rem; color: var(--accent); margin-bottom: 0.4rem; }
.exp-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; }

/* ─── EDUCATION ──────────────────────────────────────────────────────── */
.edu-list { display: flex; flex-direction: column; gap: 0; }
.edu-item {
  padding: 1.2rem 0; border-bottom: 1px solid var(--border);
  display: grid; grid-template-columns: 1fr auto; gap: 0.25rem 1rem;
}
.edu-item:first-child { padding-top: 0; }
.edu-item:last-child { border-bottom: none; }
.edu-school { font-size: 0.92rem; font-weight: 600; color: var(--text); grid-column: 1; }
.edu-period {
  font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-faint);
  font-variant-numeric: tabular-nums; grid-column: 2; grid-row: 1;
  white-space: nowrap; padding-top: 0.15rem;
}
.edu-degree { font-size: 0.82rem; color: var(--text-muted); grid-column: 1; }
.edu-location { font-size: 0.75rem; color: var(--text-faint); grid-column: 1 / -1; margin-top: 0.1rem; }
.edu-thesis {
  font-size: 0.78rem; color: var(--text-faint); font-style: italic;
  grid-column: 1 / -1; margin-top: 0.4rem; line-height: 1.45;
}

/* ─── AWARDS ─────────────────────────────────────────────────────────── */
.award-list { display: flex; flex-direction: column; gap: 0.65rem; }
.award-item {
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 0.85rem 1rem; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); border-left: 3px solid var(--amber);
}
.award-icon { font-size: 0.8rem; flex-shrink: 0; padding-top: 0.1rem; }
.award-text { font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; }
.award-text strong { color: var(--text); font-weight: 500; }
.award-year {
  font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-faint);
  margin-left: auto; padding-left: 1rem; flex-shrink: 0; font-variant-numeric: tabular-nums;
}

/* ─── PROJECTS ───────────────────────────────────────────────────────── */
.project-list { display: flex; flex-direction: column; gap: 1.25rem; }
.project-name { font-size: 0.9rem; font-weight: 600; color: var(--text); margin-bottom: 0.25rem; }
.project-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; }

/* ─── FOOTER ─────────────────────────────────────────────────────────── */
.site-footer {
  max-width: 680px; margin: 0 auto; padding: 2rem 1.5rem 3rem;
  border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-faint);
  display: flex; gap: 1rem; flex-wrap: wrap; justify-content: space-between; align-items: center;
}
.site-footer a { color: var(--text-faint); }
.site-footer a:hover { color: var(--accent); text-decoration: none; }
.theme-toggle {
  display: inline-flex; align-items: center; gap: 0.35rem;
  background: none; border: 1px solid var(--border); border-radius: 4px;
  padding: 0.3rem 0.6rem; cursor: pointer; font-size: 0.7rem;
  color: var(--text-muted); font-family: var(--font-mono);
}
.theme-toggle:hover { color: var(--text); border-color: var(--accent); }

/* ─── MOBILE ─────────────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .page { padding: 2.5rem 1.25rem 3.5rem; }
  .pub-item { grid-template-columns: 1fr; gap: 0.4rem; }
  .edu-item { grid-template-columns: 1fr; }
  .edu-period { grid-column: 1; grid-row: auto; }
  .award-item { flex-wrap: wrap; }
  .award-year { margin-left: 0; }
  .site-footer { flex-direction: column; align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
}
</style>
</head>
<body>
<div class="page">

  <!-- HERO -->
  <header class="hero">
    <img class="avatar" src="${p.photo}" alt="${p.name}">
    <h1 class="hero-name">${p.name}</h1>
    <p class="hero-title">${p.title}</p>
    <p class="hero-tagline">${p.tagline}</p>
    <div class="hero-links">
      <a href="mailto:${p.email}">Email</a>
      <a href="${lk.linkedin}" target="_blank" rel="noopener">LinkedIn</a>
      <a href="${lk.scholar}" target="_blank" rel="noopener">Google Scholar</a>
      <a href="${lk.cv}" target="_blank" rel="noopener">CV / R&eacute;sum&eacute;</a>
    </div>
  </header>

  <!-- EXPERIENCE -->
  <section id="experience">
    <h2 class="section-title">Experience</h2>
    <div class="exp-list">
      ${renderExperience(experience)}
    </div>
  </section>

  <!-- EDUCATION -->
  <section id="education">
    <h2 class="section-title">Education</h2>
    <div class="edu-list">
      ${renderEducation(education)}
    </div>
  </section>

  <!-- HONORS -->
  <section id="honors">
    <h2 class="section-title">Honors &amp; Awards</h2>
    <div class="award-list">
      ${renderAwards(awards)}
    </div>
  </section>

  <!-- PROJECTS -->
  <section id="projects">
    <h2 class="section-title">Projects</h2>
    <div class="project-list">
      ${renderProjects(projects)}
    </div>
  </section>

  <!-- PUBLICATIONS -->
  <section id="publications">
    <h2 class="section-title">Publications</h2>
    <div class="pub-list">
      ${renderPublications(publications)}
    </div>
    <p class="pub-note">
      Full list on
      <a href="${lk.scholar}" target="_blank" rel="noopener">Google Scholar</a>
      &middot; <a href="${lk.arxiv}" target="_blank" rel="noopener">arXiv</a>
      &middot; h-index: ${st.hindex} &middot; ${st.total_citations} total citations
    </p>
  </section>

</div>

<footer class="site-footer">
  <span>${p.name} &middot; ${p.title}</span>
  <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">toggle theme</button>
</footer>

${gc}

<script>
// ── Theme: persist preference in localStorage ──────────────────────────────
(function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark' || saved === 'light') {
    document.documentElement.setAttribute('data-theme', saved);
  }
})();

const toggle = document.getElementById('themeToggle');
const root   = document.documentElement;

toggle.addEventListener('click', () => {
  const current = root.getAttribute('data-theme');
  if (current === 'dark') {
    root.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');
  } else if (current === 'light') {
    root.removeAttribute('data-theme');
    localStorage.removeItem('theme');
  } else {
    root.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  }
});
</script>
</body>
</html>`;
}

// ── Write output ─────────────────────────────────────────────────────────────
const html = buildHtml();
fs.writeFileSync(path.join(__dirname, 'index.html'), html, 'utf8');
console.log('✓  index.html written successfully');
console.log(`   ${html.split('\n').length} lines | ${(Buffer.byteLength(html) / 1024).toFixed(1)} KB`);
