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
const skills       = JSON.parse(fs.readFileSync(path.join(d, 'skills.json'),       'utf8'));
const hobbies      = JSON.parse(fs.readFileSync(path.join(d, 'hobbies.json'),      'utf8'));

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

    const tagsHtml = (p.tags || []).map(t => tagHtml(t, arxivUrls)).join('\n            ');

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

function renderResearch(paras) {
  return paras.map(p => `<p>${p}</p>`).join('\n      ');
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
  return prs.map(pr => {
    const skillsHtml = pr.skills ? `<p class="project-skills"><strong>Skills:</strong> ${pr.skills.join(', ')}</p>` : '';
    return `
      <div class="project-item">
        <div class="project-name">${pr.name}</div>
        <p class="project-desc">${pr.description}</p>
        ${skillsHtml}
      </div>`;
  }).join('\n');
}

function renderSkills(sk) {
  return sk.map(g => {
    const items = g.items.map(i => `<span class="skill-tag">${i}</span>`).join('\n          ');
    return `
      <div class="skill-group">
        <div class="skill-label">${g.label}</div>
        <div class="skill-items">
          ${items}
        </div>
      </div>`;
  }).join('\n');
}

function renderHobbies(hb) {
  return hb.map(h => `
      <a href="${h.link}" target="_blank" rel="noopener" class="hobby-item">
        <div class="hobby-title">${h.title}</div>
        <p class="hobby-desc">${h.desc}</p>
        <div class="hobby-link">${h.link_label} &rarr;</div>
      </a>`).join('\n');
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
  --nav-w: 190px;
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
.page { margin-left: var(--nav-w); }
.page-inner { max-width: clamp(680px, 68vw, 880px); margin: 0 auto; padding: 4rem 3.5rem 5rem; }

/* ─── SIDE NAV ───────────────────────────────────────────────────────── */
.side-nav {
  position: fixed; top: 0; left: 0; width: var(--nav-w); height: 100vh;
  overflow-y: auto; padding: 2.5rem 1.25rem;
  background: var(--bg-card); border-right: 1px solid var(--border);
}
.side-nav ul { list-style: none; display: flex; flex-direction: column; gap: 0.15rem; }
.side-nav a {
  display: block; font-size: 0.8rem; color: var(--text-muted); letter-spacing: 0.02em;
  padding: 0.45rem 0.6rem; border-radius: var(--radius); text-decoration: none;
  transition: color 0.15s, background 0.15s;
}
.side-nav a:hover, .side-nav a.active { color: var(--text); background: var(--bg-card2); text-decoration: none; }

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

/* ─── RESEARCH ───────────────────────────────────────────────────────── */
.research-body { font-size: 0.9rem; color: var(--text-muted); line-height: 1.75; }
.research-body p + p { margin-top: 1rem; }

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
.project-list { display: flex; flex-direction: column; gap: 1.5rem; }
.project-name { font-size: 0.9rem; font-weight: 600; color: var(--text); margin-bottom: 0.25rem; }
.project-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; }
.project-skills { font-size: 0.76rem; color: var(--text-faint); margin-top: 0.35rem; line-height: 1.5; }
.project-skills strong { color: var(--text-muted); font-weight: 500; }

/* ─── SKILLS ─────────────────────────────────────────────────────────── */
.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1.25rem; }
.skill-label {
  font-family: var(--font-mono); font-size: 0.68rem; color: var(--accent);
  letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem;
}
.skill-items { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.skill-tag {
  font-size: 0.73rem; padding: 0.25rem 0.6rem;
  background: var(--bg-card2); border: 1px solid var(--border);
  border-radius: 3px; color: var(--text-muted);
}

/* ─── HOBBIES ────────────────────────────────────────────────────────── */
.hobby-list { display: flex; flex-direction: column; gap: 0.75rem; }
.hobby-item {
  display: block; padding: 1rem 1.25rem; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: var(--radius);
  text-decoration: none; color: inherit; transition: border-color 0.15s;
}
.hobby-item:hover { border-color: var(--accent); text-decoration: none; }
.hobby-title { font-size: 0.9rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem; }
.hobby-desc { font-size: 0.83rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 0.5rem; }
.hobby-link { font-size: 0.75rem; font-family: var(--font-mono); color: var(--accent); }

/* ─── FOOTER ─────────────────────────────────────────────────────────── */
.site-footer {
  margin-left: var(--nav-w);
  border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-faint);
}
.footer-inner {
  max-width: clamp(680px, 68vw, 880px); margin: 0 auto; padding: 2rem 3.5rem 3rem;
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
@media (max-width: 768px) {
  .side-nav { display: none; }
  .page { margin-left: 0; }
  .site-footer { margin-left: 0; }
}
@media (max-width: 640px) {
  .page-inner { padding: 2.5rem 1.25rem 3.5rem; }
  .pub-item { grid-template-columns: 1fr; gap: 0.4rem; }
  .edu-item { grid-template-columns: 1fr; }
  .edu-period { grid-column: 1; grid-row: auto; }
  .award-item { flex-wrap: wrap; }
  .award-year { margin-left: 0; }
  .footer-inner { flex-direction: column; align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
}
</style>
</head>
<body>
<nav class="side-nav" aria-label="Page navigation">
  <ul>
    <li><a href="#research">Research</a></li>
    <li><a href="#experience">Experience</a></li>
    <li><a href="#projects">Projects</a></li>
    <li><a href="#skills">Skills</a></li>
    <li><a href="#education">Education</a></li>
    <li><a href="#honors">Honors</a></li>
    <li><a href="#publications">Publications</a></li>
    <li><a href="#hobbies">Hobbies</a></li>
  </ul>
</nav>
<div class="page">
<div class="page-inner">

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

  <!-- RESEARCH -->
  <section id="research">
    <h2 class="section-title">${p.research_title}</h2>
    <div class="research-body">
      ${renderResearch(p.research_intro)}
    </div>
  </section>

  <!-- EXPERIENCE -->
  <section id="experience">
    <h2 class="section-title">Experience</h2>
    <div class="exp-list">
      ${renderExperience(experience)}
    </div>
  </section>

  <!-- PROJECTS -->
  <section id="projects">
    <h2 class="section-title">Projects</h2>
    <div class="project-list">
      ${renderProjects(projects)}
    </div>
  </section>

  <!-- SKILLS SUMMARY -->
  <section id="skills">
    <h2 class="section-title">Skills Summary</h2>
    <div class="skills-grid">
      ${renderSkills(skills)}
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

  <!-- HOBBIES -->
  <section id="hobbies">
    <h2 class="section-title">Hobbies</h2>
    <div class="hobby-list">
      ${renderHobbies(hobbies)}
    </div>
  </section>

</div>
</div>

<footer class="site-footer">
  <div class="footer-inner">
    <span>${p.name} &middot; ${p.title}</span>
    <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">toggle theme</button>
  </div>
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

// ── Active nav link: rootMargin works for tall sections ────────────────────
const sections = document.querySelectorAll('section[id]');
const navLinks  = document.querySelectorAll('.side-nav a');
const observer  = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(a => a.classList.remove('active'));
      const active = document.querySelector(`.side-nav a[href="#${entry.target.id}"]`);
      if (active) active.classList.add('active');
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });
sections.forEach(s => observer.observe(s));
</script>
</body>
</html>`;
}

// ── Write output ─────────────────────────────────────────────────────────────
const html = buildHtml();
fs.writeFileSync(path.join(__dirname, 'index.html'), html, 'utf8');
console.log('✓  index.html written successfully');
console.log(`   ${html.split('\n').length} lines | ${(Buffer.byteLength(html) / 1024).toFixed(1)} KB`);
