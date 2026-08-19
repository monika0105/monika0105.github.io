#!/usr/bin/env python3
"""
build.py — Portfolio site builder

Reads all JSON files from data/ and writes a fully-rendered index.html.

Usage:
    python3 build.py

To update anything (position, publications, awards, etc.):
  1. Edit the relevant file in data/
  2. Run:  python3 build.py
  3. Open index.html in a browser to verify
  4. git add . && git commit -m "..." && git push

Analytics (GoatCounter):
  Set "goatcounter_site" in data/profile.json to your GoatCounter site code
  (e.g. "monikasantra" if your dashboard is at https://monikasantra.goatcounter.com).
  Leave it as "" to disable analytics entirely.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

profile      = load("profile.json")
publications = load("publications.json")
experience   = load("experience.json")
education    = load("education.json")
awards       = load("awards.json")
skills       = load("skills.json")
service      = load("service.json")
hobbies      = load("hobbies.json")

# ── Helpers ──────────────────────────────────────────────────────────────────

def tag_html(tag, arxiv_urls):
    if tag.startswith("arXiv:"):
        aid = tag[6:]
        url = arxiv_urls.get(aid, f"https://arxiv.org/abs/{aid}")
        return f'<a href="{url}" target="_blank" rel="noopener" class="pub-tag tag-arxiv">{tag}</a>'
    if tag == "under review":
        return f'<span class="pub-tag tag-review">under review</span>'
    if re.match(r"^\d+ citation", tag):
        return f'<span class="pub-tag tag-cite">{tag}</span>'
    return f'<span class="pub-tag tag-venue">{tag}</span>'

def highlight_self(authors):
    parts = [a.strip() for a in authors.split(",")]
    out = []
    for a in parts:
        if a == "M. Santra":
            out.append(f'<span class="author-self">{a}</span>')
        else:
            out.append(a)
    return ", ".join(out)

# ── Renderers ────────────────────────────────────────────────────────────────

def render_publications(pubs):
    arxiv_urls = {}
    for p in pubs:
        if p.get("arxiv"):
            m = re.search(r"abs/([^\s]+)$", p["arxiv"])
            if m:
                arxiv_urls[m.group(1)] = p["arxiv"]

    rows = []
    for p in pubs:
        tags_html = "\n            ".join(tag_html(t, arxiv_urls) for t in (p.get("tags") or []))
        if p.get("citations"):
            n = p["citations"]
            tags_html += f'\n            <span class="pub-tag tag-cite">{n} citation{"s" if n != 1 else ""}</span>'
        rows.append(f"""
      <div class="pub-item">
        <div class="pub-year">{p['year']}</div>
        <div>
          <div class="pub-title">{p['title']}</div>
          <div class="pub-authors">{highlight_self(p['authors'])}</div>
          <div class="pub-venue">{p['venue']}</div>
          <div class="pub-tags">
            {tags_html}
          </div>
        </div>
      </div>""")
    return "\n".join(rows)


def render_experience(exp):
    rows = []
    for e in exp:
        projects = []
        for pr in e["projects"]:
            bullets = "\n              ".join(f"<li>{b}</li>" for b in pr["bullets"])
            name_html = f'<div class="exp-project-name">{pr["name"]}</div>' if pr.get("name") else ""
            projects.append(f"""
          <div class="exp-project">
            {name_html}
            <ul class="exp-bullets">
              {bullets}
            </ul>
          </div>""")
        rows.append(f"""
      <div class="exp-item">
        <div class="exp-header">
          <div class="exp-org">{e['org']}</div>
          <div class="exp-period">{e['period']}</div>
        </div>
        <div class="exp-role">{e['role']}</div>
        <div class="exp-location">{e['location']}</div>
        <div class="exp-projects">{"".join(projects)}
        </div>
      </div>""")
    return "\n".join(rows)


def render_education(edu):
    rows = []
    for e in edu:
        thesis = f'<div class="edu-thesis">{e["thesis"]}</div>' if e.get("thesis") else ""
        rows.append(f"""
      <div class="edu-item">
        <div class="edu-school">{e['school']}</div>
        <div class="edu-period">{e['period']}</div>
        <div class="edu-degree">{e['degree']}</div>
        <div class="edu-location">{e['location']}</div>
        {thesis}
      </div>""")
    return "\n".join(rows)


def render_awards(aws):
    rows = []
    for a in aws:
        detail = f" — {a['detail']}" if a.get("detail") else ""
        rows.append(f"""
      <div class="award-item">
        <div class="award-icon">◆</div>
        <div class="award-text"><strong>{a['title']}</strong>{detail}</div>
        <div class="award-year">{a['year']}</div>
      </div>""")
    return "\n".join(rows)


def render_skills(sk):
    rows = []
    for g in sk:
        items = "\n          ".join(f'<span class="skill-tag">{i}</span>' for i in g["items"])
        rows.append(f"""
      <div class="skill-group">
        <div class="skill-label">{g['label']}</div>
        <div class="skill-items">
          {items}
        </div>
      </div>""")
    return "\n".join(rows)


def render_service(svc):
    rows = []
    for s in svc:
        rows.append(f"""
      <div class="service-item">
        <div class="service-role">{s['role']}</div>
        <div class="service-where">{s['where']}</div>
        <div class="service-year">{s['year']}</div>
      </div>""")
    return "\n".join(rows)


def render_hobbies(hb):
    rows = []
    for h in hb:
        rows.append(f"""
      <a href="{h['link']}" target="_blank" rel="noopener" class="hobby-card">
        <div class="hobby-card-icon">{h['icon']}</div>
        <div class="hobby-card-title">{h['title']}</div>
        <div class="hobby-card-desc">{h['desc']}</div>
        <div class="hobby-card-link">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          {h['link_label']}
        </div>
      </a>""")
    return "\n".join(rows)


def render_about(paras):
    return "\n      ".join(f"<p>{para}</p>" for para in paras)


def render_interests(interests):
    return "\n      ".join(f'<span class="chip">{i}</span>' for i in interests)


def analytics_snippet(site_code):
    if not site_code:
        return "<!-- analytics: set goatcounter_site in data/profile.json to enable -->"
    return f"""<!-- GoatCounter analytics (privacy-friendly — shows page views + visitor country/city) -->
<script data-goatcounter="https://{site_code}.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script>"""

# ── Build ────────────────────────────────────────────────────────────────────

def build():
    p  = profile
    lk = p["links"]
    st = p["scholar_stats"]
    gc = analytics_snippet((p.get("analytics") or {}).get("goatcounter_site", ""))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{p['name']} — PhD Candidate, Computer Security</title>
<!-- Generated by build.py — edit data/*.json then run: python3 build.py -->
<style>
/* ─── TOKENS ─────────────────────────────────────────────────────────── */
:root {{
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
  --badge:       var(--amber);

  --font-display: 'Palatino Linotype', 'Book Antiqua', Palatino, Georgia, serif;
  --font-body:    system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Courier New', monospace;

  --radius: 6px;
  --nav-w: 220px;
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:          var(--navy);
    --bg-card:     var(--navy-card);
    --bg-card2:    #0F2035;
    --border:      var(--navy-border);
    --text:        var(--off-white);
    --text-muted:  var(--silver);
    --text-faint:  var(--muted);
    --accent:      var(--teal);
    --accent-glow: var(--teal);
  }}
}}

:root[data-theme="dark"] {{
  --bg:          var(--navy);
  --bg-card:     var(--navy-card);
  --bg-card2:    #0F2035;
  --border:      var(--navy-border);
  --text:        var(--off-white);
  --text-muted:  var(--silver);
  --text-faint:  var(--muted);
  --accent:      var(--teal);
  --accent-glow: var(--teal);
}}

/* ─── RESET ──────────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; font-size: 16px; }}
body {{
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  line-height: 1.65;
  transition: background 0.2s, color 0.2s;
  min-height: 100vh;
}}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }}

/* ─── LAYOUT ─────────────────────────────────────────────────────────── */
.site-wrap {{ display: flex; min-height: 100vh; }}

/* ─── SIDEBAR NAV ────────────────────────────────────────────────────── */
.sidebar {{
  position: fixed; top: 0; left: 0;
  width: var(--nav-w); height: 100vh;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  padding: 2.5rem 1.5rem;
  z-index: 100; overflow-y: auto;
}}
.sidebar-name {{
  font-family: var(--font-display); font-size: 1.1rem;
  font-weight: normal; color: var(--text); line-height: 1.3; margin-bottom: 0.25rem;
}}
.sidebar-title {{
  font-size: 0.7rem; color: var(--text-faint);
  letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 2rem;
}}
.sidebar-accent-line {{
  width: 28px; height: 2px; background: var(--accent);
  margin-bottom: 2rem; animation: drawLine 0.6s ease-out 0.3s both;
}}
nav ul {{ list-style: none; display: flex; flex-direction: column; gap: 0.15rem; }}
nav a {{
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.8rem; color: var(--text-muted); letter-spacing: 0.04em;
  padding: 0.4rem 0.5rem; border-radius: var(--radius);
  transition: color 0.15s, background 0.15s; text-decoration: none;
}}
nav a .nav-glyph {{
  font-family: var(--font-mono); font-size: 0.65rem;
  color: var(--accent); opacity: 0.5; transition: opacity 0.15s;
}}
nav a:hover, nav a.active {{ color: var(--text); background: var(--bg-card2); text-decoration: none; }}
nav a:hover .nav-glyph, nav a.active .nav-glyph {{ opacity: 1; }}
.sidebar-footer {{
  margin-top: auto; padding-top: 2rem;
  font-size: 0.7rem; color: var(--text-faint);
}}
.sidebar-links {{ display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.75rem; }}
.sidebar-links a {{
  font-size: 0.75rem; color: var(--text-muted);
  display: flex; align-items: center; gap: 0.4rem; text-decoration: none;
}}
.sidebar-links a:hover {{ color: var(--accent); text-decoration: none; }}
.theme-toggle {{
  display: flex; align-items: center; gap: 0.4rem;
  background: none; border: 1px solid var(--border); border-radius: 4px;
  padding: 0.3rem 0.6rem; cursor: pointer; font-size: 0.7rem;
  color: var(--text-muted); margin-top: 1rem;
  font-family: var(--font-mono); width: 100%;
}}
.theme-toggle:hover {{ color: var(--text); border-color: var(--accent); }}

/* ─── MAIN CONTENT ───────────────────────────────────────────────────── */
.main {{ margin-left: var(--nav-w); flex: 1; max-width: 900px; padding: 4rem 3.5rem; }}

/* ─── HERO ───────────────────────────────────────────────────────────── */
.hero {{ padding-bottom: 5rem; border-bottom: 1px solid var(--border); margin-bottom: 5rem; }}
.hero-eyebrow {{
  font-family: var(--font-mono); font-size: 0.72rem; color: var(--accent);
  letter-spacing: 0.1em; margin-bottom: 1.5rem; animation: fadeUp 0.5s ease-out 0.1s both;
}}
.hero-name {{
  font-family: var(--font-display); font-size: clamp(2.4rem, 5vw, 3.8rem);
  font-weight: normal; color: var(--text); line-height: 1.1; letter-spacing: -0.01em;
  margin-bottom: 1.25rem; text-wrap: balance; animation: fadeUp 0.5s ease-out 0.2s both;
}}
.hero-tagline {{
  font-size: 1.05rem; color: var(--text-muted); max-width: 52ch;
  line-height: 1.6; margin-bottom: 2rem; animation: fadeUp 0.5s ease-out 0.3s both;
}}
.hero-tagline strong {{ color: var(--text); font-weight: 500; }}
.hero-meta {{
  display: flex; flex-wrap: wrap; gap: 1rem 2rem;
  font-size: 0.8rem; color: var(--text-faint); animation: fadeUp 0.5s ease-out 0.4s both;
}}
.hero-meta span {{ display: flex; align-items: center; gap: 0.4rem; }}
.hero-cta {{
  display: flex; flex-wrap: wrap; gap: 0.75rem;
  margin-top: 2rem; animation: fadeUp 0.5s ease-out 0.5s both;
}}
.btn {{
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.55rem 1.1rem; border-radius: var(--radius);
  font-size: 0.8rem; font-family: var(--font-body); font-weight: 500;
  cursor: pointer; text-decoration: none; transition: all 0.15s; border: 1px solid transparent;
}}
.btn-primary {{ background: var(--accent); color: var(--navy); border-color: var(--accent); }}
.btn-primary:hover {{ background: var(--accent-glow); text-decoration: none; color: var(--navy); }}
.btn-secondary {{ background: transparent; color: var(--text-muted); border-color: var(--border); }}
.btn-secondary:hover {{ border-color: var(--accent); color: var(--text); text-decoration: none; }}

/* ─── SECTION ANATOMY ────────────────────────────────────────────────── */
section {{ margin-bottom: 5rem; }}
.section-head {{ display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 2.25rem; }}
.section-glyph {{
  font-family: var(--font-mono); font-size: 0.7rem; color: var(--accent);
  letter-spacing: 0.05em; opacity: 0.7; flex-shrink: 0;
}}
.section-title {{
  font-family: var(--font-display); font-size: 1.5rem;
  font-weight: normal; color: var(--text); letter-spacing: -0.01em; text-wrap: balance;
}}
.section-rule {{ flex: 1; height: 1px; background: var(--border); margin-left: 0.5rem; }}

/* ─── ABOUT ──────────────────────────────────────────────────────────── */
.about-body {{ font-size: 0.95rem; color: var(--text-muted); line-height: 1.75; max-width: 68ch; }}
.about-body p + p {{ margin-top: 1rem; }}
.about-body strong {{ color: var(--text); font-weight: 500; }}
.interests-chips {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1.5rem; }}
.chip {{
  font-size: 0.73rem; font-family: var(--font-mono);
  padding: 0.3rem 0.7rem; border: 1px solid var(--border);
  border-radius: 3px; color: var(--text-muted); letter-spacing: 0.02em; background: var(--bg-card2);
}}

/* ─── PUBLICATIONS ───────────────────────────────────────────────────── */
.pub-list {{ display: flex; flex-direction: column; gap: 0; }}
.pub-item {{
  padding: 1.4rem 0; border-bottom: 1px solid var(--border);
  display: grid; grid-template-columns: auto 1fr; gap: 0 1.25rem;
}}
.pub-item:first-child {{ border-top: 1px solid var(--border); }}
.pub-year {{
  font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-faint);
  padding-top: 0.2rem; min-width: 40px; font-variant-numeric: tabular-nums;
}}
.pub-title {{ font-size: 0.92rem; font-weight: 600; color: var(--text); line-height: 1.45; margin-bottom: 0.25rem; }}
.pub-authors {{ font-size: 0.8rem; color: var(--text-faint); margin-bottom: 0.35rem; line-height: 1.4; }}
.pub-authors .author-self {{ color: var(--text-muted); font-weight: 500; }}
.pub-venue {{ font-size: 0.78rem; font-style: italic; color: var(--text-muted); }}
.pub-tags {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.5rem; }}
.pub-tag {{
  font-size: 0.65rem; font-family: var(--font-mono);
  padding: 0.15rem 0.5rem; border-radius: 2px; font-variant-numeric: tabular-nums;
}}
.tag-venue {{
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent); border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
}}
.tag-preprint {{
  background: color-mix(in srgb, var(--text-faint) 10%, transparent);
  color: var(--text-faint); border: 1px solid var(--border);
}}
.tag-review {{
  background: color-mix(in srgb, var(--amber) 12%, transparent);
  color: var(--amber); border: 1px solid color-mix(in srgb, var(--amber) 30%, transparent);
}}
.tag-cite {{ background: transparent; color: var(--text-faint); border: 1px solid var(--border); }}
.tag-arxiv {{
  background: color-mix(in srgb, #e07b39 12%, transparent);
  color: #c96a20; border: 1px solid color-mix(in srgb, #e07b39 30%, transparent); text-decoration: none;
}}
:root[data-theme="dark"] .tag-arxiv {{ color: #f0a060; }}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) .tag-arxiv {{ color: #f0a060; }}
}}
a.pub-tag:hover {{ opacity: 0.8; text-decoration: none; }}

/* ─── EXPERIENCE ─────────────────────────────────────────────────────── */
.exp-list {{ display: flex; flex-direction: column; gap: 2.5rem; }}
.exp-header {{
  display: flex; justify-content: space-between; align-items: flex-start;
  flex-wrap: wrap; gap: 0.25rem; margin-bottom: 0.35rem;
}}
.exp-org {{ font-size: 0.95rem; font-weight: 600; color: var(--text); }}
.exp-period {{ font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-faint); font-variant-numeric: tabular-nums; }}
.exp-role {{ font-size: 0.8rem; color: var(--accent); font-style: italic; margin-bottom: 0.6rem; }}
.exp-location {{ font-size: 0.75rem; color: var(--text-faint); margin-bottom: 0.75rem; }}
.exp-projects {{ display: flex; flex-direction: column; gap: 0.9rem; }}
.exp-project-name {{ font-size: 0.82rem; font-weight: 600; color: var(--text); margin-bottom: 0.2rem; }}
.exp-bullets {{ list-style: none; display: flex; flex-direction: column; gap: 0.3rem; }}
.exp-bullets li {{
  font-size: 0.83rem; color: var(--text-muted); padding-left: 1.1rem;
  position: relative; line-height: 1.55;
}}
.exp-bullets li::before {{ content: '–'; position: absolute; left: 0; color: var(--text-faint); }}

/* ─── EDUCATION ──────────────────────────────────────────────────────── */
.edu-list {{ display: flex; flex-direction: column; gap: 0; }}
.edu-item {{
  padding: 1.4rem 0; border-bottom: 1px solid var(--border);
  display: grid; grid-template-columns: 1fr auto; gap: 0.25rem 1rem;
}}
.edu-item:first-child {{ border-top: 1px solid var(--border); }}
.edu-school {{ font-size: 0.92rem; font-weight: 600; color: var(--text); grid-column: 1; }}
.edu-period {{
  font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-faint);
  font-variant-numeric: tabular-nums; grid-column: 2; grid-row: 1;
  white-space: nowrap; padding-top: 0.15rem;
}}
.edu-degree {{ font-size: 0.82rem; color: var(--text-muted); grid-column: 1; }}
.edu-location {{ font-size: 0.75rem; color: var(--text-faint); grid-column: 1 / -1; margin-top: 0.1rem; }}
.edu-thesis {{
  font-size: 0.78rem; color: var(--text-faint); font-style: italic;
  grid-column: 1 / -1; margin-top: 0.4rem; line-height: 1.45;
}}

/* ─── AWARDS ─────────────────────────────────────────────────────────── */
.award-list {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.award-item {{
  display: flex; align-items: flex-start; gap: 0.85rem;
  padding: 1rem 1.25rem; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); border-left: 3px solid var(--amber);
}}
.award-icon {{ font-size: 0.85rem; flex-shrink: 0; padding-top: 0.1rem; }}
.award-text {{ font-size: 0.83rem; color: var(--text-muted); line-height: 1.5; }}
.award-text strong {{ color: var(--text); font-weight: 500; }}
.award-year {{
  font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-faint);
  margin-left: auto; padding-left: 1rem; flex-shrink: 0; font-variant-numeric: tabular-nums;
}}

/* ─── SKILLS ─────────────────────────────────────────────────────────── */
.skills-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1.25rem; }}
.skill-label {{
  font-family: var(--font-mono); font-size: 0.68rem; color: var(--accent);
  letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem;
}}
.skill-items {{ display: flex; flex-wrap: wrap; gap: 0.35rem; }}
.skill-tag {{
  font-size: 0.73rem; padding: 0.25rem 0.6rem;
  background: var(--bg-card2); border: 1px solid var(--border);
  border-radius: 3px; color: var(--text-muted);
}}

/* ─── SERVICE ────────────────────────────────────────────────────────── */
.service-list {{ display: flex; flex-direction: column; gap: 0.6rem; }}
.service-item {{ display: flex; gap: 1rem; font-size: 0.84rem; align-items: baseline; }}
.service-role {{ color: var(--text-muted); flex: 1; }}
.service-where {{ color: var(--text-faint); font-style: italic; }}
.service-year {{
  font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-faint);
  font-variant-numeric: tabular-nums; flex-shrink: 0;
}}

/* ─── PHOTOS ─────────────────────────────────────────────────────────── */
.photo-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.75rem; }}
.photo-item {{
  position: relative; border-radius: var(--radius); overflow: hidden;
  aspect-ratio: 4 / 3; background: var(--bg-card2); border: 1px solid var(--border);
}}
.photo-item img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s ease; }}
.photo-item:hover img {{ transform: scale(1.04); }}
.photo-caption {{
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 0.4rem 0.6rem;
  background: linear-gradient(transparent, rgba(0,0,0,0.55));
  font-size: 0.7rem; color: #fff; opacity: 0; transition: opacity 0.2s;
}}
.photo-item:hover .photo-caption {{ opacity: 1; }}
.photo-placeholder {{
  width: 100%; height: 100%; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 0.5rem;
  background: var(--bg-card2); color: var(--text-faint);
}}
.photo-placeholder svg {{ opacity: 0.35; }}
.photo-placeholder span {{ font-size: 0.68rem; font-family: var(--font-mono); opacity: 0.5; }}

/* ─── HOBBIES ────────────────────────────────────────────────────────── */
.hobby-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; }}
.hobby-card {{
  display: flex; flex-direction: column; gap: 0.6rem;
  padding: 1.25rem 1.25rem 1rem; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: var(--radius);
  text-decoration: none; color: inherit; transition: border-color 0.15s, transform 0.15s;
}}
.hobby-card:hover {{ border-color: var(--accent); transform: translateY(-2px); text-decoration: none; color: inherit; }}
.hobby-card-icon {{ font-size: 1.6rem; line-height: 1; }}
.hobby-card-title {{ font-size: 0.9rem; font-weight: 600; color: var(--text); }}
.hobby-card-desc {{ font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; }}
.hobby-card-link {{
  margin-top: auto; font-size: 0.75rem; font-family: var(--font-mono);
  color: var(--accent); display: flex; align-items: center; gap: 0.3rem;
}}

/* ─── CONTACT ────────────────────────────────────────────────────────── */
.contact-grid {{ display: flex; flex-wrap: wrap; gap: 1rem; }}
.contact-card {{
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.9rem 1.25rem; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: var(--radius);
  font-size: 0.82rem; color: var(--text-muted); text-decoration: none; transition: border-color 0.15s, color 0.15s;
}}
.contact-card:hover {{ border-color: var(--accent); color: var(--text); text-decoration: none; }}
.contact-card-icon {{ font-size: 1rem; color: var(--accent); }}

/* ─── FOOTER ─────────────────────────────────────────────────────────── */
.site-footer {{
  margin-left: var(--nav-w); padding: 1.5rem 3.5rem;
  border-top: 1px solid var(--border); font-size: 0.72rem; color: var(--text-faint);
  display: flex; gap: 1rem; flex-wrap: wrap; justify-content: space-between; align-items: center;
}}
.site-footer a {{ color: var(--text-faint); }}
.site-footer a:hover {{ color: var(--accent); text-decoration: none; }}

/* ─── MOBILE ─────────────────────────────────────────────────────────── */
@media (max-width: 768px) {{
  .sidebar {{
    position: static; width: 100%; height: auto;
    border-right: none; border-bottom: 1px solid var(--border);
    padding: 1.5rem; flex-direction: row; flex-wrap: wrap; align-items: center; gap: 1rem;
  }}
  .sidebar nav {{ display: none; }}
  .sidebar-footer {{ display: none; }}
  .sidebar-accent-line {{ display: none; }}
  .sidebar-title {{ display: none; }}
  .site-wrap {{ flex-direction: column; }}
  .main {{ margin-left: 0; padding: 2.5rem 1.5rem; max-width: 100%; }}
  .pub-item {{ grid-template-columns: 1fr; gap: 0.4rem; }}
  .edu-item {{ grid-template-columns: 1fr; }}
  .edu-period {{ grid-column: 1; grid-row: auto; }}
  .award-item {{ flex-wrap: wrap; }}
  .award-year {{ margin-left: 0; }}
  .site-footer {{ margin-left: 0; padding: 1.25rem 1.5rem; }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ transition: none !important; animation: none !important; }}
}}

/* ─── ANIMATIONS ─────────────────────────────────────────────────────── */
@keyframes drawLine {{ from {{ width: 0; }} to {{ width: 28px; }} }}
@keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body>
<div class="site-wrap">

<!-- ─── SIDEBAR ──────────────────────────────────────────────────────── -->
<aside class="sidebar">
  <div>
    <div class="sidebar-name">{p['name']}</div>
    <div class="sidebar-title">{p['title']}</div>
    <div class="sidebar-accent-line"></div>
    <nav aria-label="Page navigation">
      <ul>
        <li><a href="#about"><span class="nav-glyph">&gt;_</span> About</a></li>
        <li><a href="#publications"><span class="nav-glyph">&gt;_</span> Publications</a></li>
        <li><a href="#experience"><span class="nav-glyph">&gt;_</span> Experience</a></li>
        <li><a href="#education"><span class="nav-glyph">&gt;_</span> Education</a></li>
        <li><a href="#awards"><span class="nav-glyph">&gt;_</span> Awards</a></li>
        <li><a href="#skills"><span class="nav-glyph">&gt;_</span> Skills</a></li>
        <li><a href="#photos"><span class="nav-glyph">&gt;_</span> Photos</a></li>
        <li><a href="#service"><span class="nav-glyph">&gt;_</span> Service</a></li>
        <li><a href="#hobbies"><span class="nav-glyph">&gt;_</span> Hobbies</a></li>
        <li><a href="#contact"><span class="nav-glyph">&gt;_</span> Contact</a></li>
      </ul>
    </nav>
  </div>
  <div class="sidebar-footer">
    <div>{p['group']}</div>
    <div style="margin-top:0.2rem;">{p['university']}</div>
    <div class="sidebar-links">
      <a href="mailto:{p['email']}" aria-label="Email">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/></svg>
        {p['email']}
      </a>
      <a href="{lk['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>
        LinkedIn
      </a>
      <a href="{lk['scholar']}" target="_blank" rel="noopener" aria-label="Google Scholar">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
        Google Scholar
      </a>
      <a href="{lk['cv']}" target="_blank" rel="noopener" aria-label="CV">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        CV / R&eacute;sum&eacute;
      </a>
    </div>
    <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
      toggle theme
    </button>
  </div>
</aside>

<!-- ─── MAIN ──────────────────────────────────────────────────────────── -->
<main class="main">

  <!-- HERO -->
  <header class="hero" id="top">
    <div class="hero-eyebrow">{p['email']} &middot; {p['group']}</div>
    <h1 class="hero-name">{p['name']}</h1>
    <p class="hero-tagline">{p['tagline']}</p>
    <div class="hero-meta">
      <span>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
        {p['university']}
      </span>
      <span>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
        {p['period']}
      </span>
      <span>Advisor: {p['advisor']}</span>
    </div>
    <div class="hero-cta">
      <a href="{lk['scholar']}" target="_blank" rel="noopener" class="btn btn-primary">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
        Google Scholar
      </a>
      <a href="{lk['linkedin']}" target="_blank" rel="noopener" class="btn btn-secondary">LinkedIn</a>
      <a href="{lk['google_sites']}" target="_blank" rel="noopener" class="btn btn-secondary">Google Sites</a>
      <a href="{lk['cv']}" target="_blank" rel="noopener" class="btn btn-secondary">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        CV / R&eacute;sum&eacute;
      </a>
    </div>
  </header>

  <!-- ABOUT -->
  <section id="about">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">About</h2>
      <div class="section-rule"></div>
    </div>
    <div class="about-body">
      {render_about(p['about'])}
    </div>
    <div class="interests-chips">
      {render_interests(p['interests'])}
    </div>
  </section>

  <!-- PUBLICATIONS -->
  <section id="publications">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Publications</h2>
      <div class="section-rule"></div>
    </div>
    <div class="pub-list">
      {render_publications(publications)}
    </div>
    <p style="margin-top:1.25rem; font-size:0.78rem; color:var(--text-faint);">
      Full list on
      <a href="{lk['scholar']}" target="_blank" rel="noopener">Google Scholar</a>
      &middot; <a href="{lk['arxiv']}" target="_blank" rel="noopener">arXiv</a>
      &middot; h-index: {st['hindex']} &middot; {st['total_citations']} total citations
    </p>
  </section>

  <!-- EXPERIENCE -->
  <section id="experience">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Experience</h2>
      <div class="section-rule"></div>
    </div>
    <div class="exp-list">
      {render_experience(experience)}
    </div>
  </section>

  <!-- EDUCATION -->
  <section id="education">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Education</h2>
      <div class="section-rule"></div>
    </div>
    <div class="edu-list">
      {render_education(education)}
    </div>
  </section>

  <!-- PHOTOS -->
  <section id="photos">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Photos</h2>
      <div class="section-rule"></div>
    </div>
    <div class="photo-grid" id="photoGrid">
      <div class="photo-item"><div class="photo-placeholder"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg><span>profile.jpg</span></div></div>
      <div class="photo-item"><div class="photo-placeholder"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg><span>research.jpg</span></div></div>
      <div class="photo-item"><div class="photo-placeholder"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 10H3M21 6H3M21 14H3M17 18H3"/></svg><span>talk.jpg</span></div></div>
      <div class="photo-item"><div class="photo-placeholder"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg><span>lab.jpg</span></div></div>
      <div class="photo-item"><div class="photo-placeholder"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg><span>hobby.jpg</span></div></div>
    </div>
    <p style="margin-top:0.75rem; font-size:0.75rem; color:var(--text-faint); font-family:var(--font-mono);">
      // Drop <code style="font-family:inherit;">images/profile.jpg</code>, <code style="font-family:inherit;">research.jpg</code>, <code style="font-family:inherit;">talk.jpg</code>, <code style="font-family:inherit;">lab.jpg</code>, <code style="font-family:inherit;">hobby.jpg</code> to replace placeholders
    </p>
  </section>

  <!-- AWARDS -->
  <section id="awards">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Honors &amp; Awards</h2>
      <div class="section-rule"></div>
    </div>
    <div class="award-list">
      {render_awards(awards)}
    </div>
  </section>

  <!-- SKILLS -->
  <section id="skills">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Skills</h2>
      <div class="section-rule"></div>
    </div>
    <div class="skills-grid">
      {render_skills(skills)}
    </div>
  </section>

  <!-- SERVICE -->
  <section id="service">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Service</h2>
      <div class="section-rule"></div>
    </div>
    <div class="service-list">
      {render_service(service)}
    </div>
  </section>

  <!-- HOBBIES -->
  <section id="hobbies">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Hobbies</h2>
      <div class="section-rule"></div>
    </div>
    <div class="hobby-grid">
      {render_hobbies(hobbies)}
    </div>
  </section>

  <!-- CONTACT -->
  <section id="contact">
    <div class="section-head">
      <span class="section-glyph">&gt;_</span>
      <h2 class="section-title">Contact</h2>
      <div class="section-rule"></div>
    </div>
    <div class="contact-grid">
      <a href="mailto:{p['email']}" class="contact-card">
        <span class="contact-card-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/></svg></span>
        {p['email']}
      </a>
      <a href="{lk['scholar']}" target="_blank" rel="noopener" class="contact-card">
        <span class="contact-card-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg></span>
        Google Scholar
      </a>
      <a href="{lk['linkedin']}" target="_blank" rel="noopener" class="contact-card">
        <span class="contact-card-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg></span>
        LinkedIn
      </a>
      <a href="{lk['google_sites']}" target="_blank" rel="noopener" class="contact-card">
        <span class="contact-card-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg></span>
        Google Sites
      </a>
      <a href="{lk['arxiv']}" target="_blank" rel="noopener" class="contact-card">
        <span class="contact-card-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg></span>
        arXiv
      </a>
    </div>
    <p style="margin-top:1.5rem; font-size:0.8rem; color:var(--text-faint); max-width:48ch;">
      {p['contact_note']}
    </p>
  </section>

</main>
</div>

<footer class="site-footer">
  <span>{p['name']} &middot; PhD Candidate, Penn State CSE &middot; {p['group']}</span>
  <span>
    <a href="mailto:{p['email']}">{p['email']}</a>
    &nbsp;&middot;&nbsp;
    <a href="{lk['scholar']}" target="_blank" rel="noopener">Scholar</a>
    &nbsp;&middot;&nbsp;
    <a href="{lk['linkedin']}" target="_blank" rel="noopener">LinkedIn</a>
  </span>
</footer>

{gc}

<script>
// ── Theme: persist preference in localStorage ──────────────────────────────
(function initTheme() {{
  const saved = localStorage.getItem('theme');
  if (saved === 'dark' || saved === 'light') {{
    document.documentElement.setAttribute('data-theme', saved);
  }}
}})();

const toggle = document.getElementById('themeToggle');
const root   = document.documentElement;

toggle.addEventListener('click', () => {{
  const current = root.getAttribute('data-theme');
  if (current === 'dark') {{
    root.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');
  }} else if (current === 'light') {{
    root.removeAttribute('data-theme');
    localStorage.removeItem('theme');
  }} else {{
    root.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  }}
}});

// ── Photo grid: replace placeholder tiles when real images exist ────────────
const PHOTOS = [
  {{ file: 'profile.jpg',  caption: 'Profile' }},
  {{ file: 'research.jpg', caption: 'Research' }},
  {{ file: 'talk.jpg',     caption: 'Talk' }},
  {{ file: 'lab.jpg',      caption: 'Lab' }},
  {{ file: 'hobby.jpg',    caption: 'Hobby' }},
];

(function loadPhotos() {{
  const grid = document.getElementById('photoGrid');
  if (!grid) return;
  const placeholders = Array.from(grid.querySelectorAll('.photo-item'));
  PHOTOS.forEach(({{ file, caption }}, i) => {{
    const img = new Image();
    img.onload = () => {{
      const tile = placeholders[i];
      if (tile) {{
        tile.innerHTML = `<img src="images/${{file}}" alt="${{caption}}" loading="lazy">
          <div class="photo-caption">${{caption}}</div>`;
      }}
    }};
    img.src = `images/${{file}}`;
  }});
}})();

// ── Active nav link: rootMargin works for tall sections ────────────────────
const sections = document.querySelectorAll('section[id], header[id]');
const navLinks  = document.querySelectorAll('nav a');
const observer  = new IntersectionObserver((entries) => {{
  entries.forEach(entry => {{
    if (entry.isIntersecting) {{
      navLinks.forEach(a => a.classList.remove('active'));
      const active = document.querySelector(`nav a[href="#${{entry.target.id}}"]`);
      if (active) active.classList.add('active');
    }}
  }});
}}, {{ rootMargin: '-20% 0px -70% 0px' }});
sections.forEach(s => observer.observe(s));
</script>
</body>
</html>"""
    return html


html = build()
out_path = os.path.join(ROOT, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

lines = html.count("\n") + 1
kb    = len(html.encode("utf-8")) / 1024
print(f"✓  index.html written  ({lines} lines | {kb:.1f} KB)")
