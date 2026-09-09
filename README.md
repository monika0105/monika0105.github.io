# Monika Santra — Portfolio Site

Personal academic portfolio for **Monika Santra**, PhD Candidate in Computer Science & Engineering at Penn State (The SOS Group).

---

## How to update the site

All content lives in JSON files inside `data/`. Edit a file, run one command, and push.

```
data/
├── profile.json       ← name, title, tagline, photo, email, links, analytics
├── publications.json  ← papers (title, authors, venue, year, tags, arxiv URL, citations)
├── experience.json    ← jobs / research positions (org, role, period, location, one-line description)
├── education.json     ← degrees
├── awards.json        ← honors and awards
└── projects.json      ← project name + a couple lines of description
```

The site is intentionally minimal: a profile photo, Experience, Education, Honors & Awards, Projects, and Publications. No skills grid, photo gallery, service list, or hobbies section.

### Everyday workflow

```bash
# 1. Edit the relevant data file, e.g.:
nano data/profile.json

# 2. Rebuild index.html
python3 build.py

# 3. Preview locally (recommended — PDF and image links need HTTP)
python3 -m http.server
# then open http://localhost:8000 in a browser

# 4. Push to GitHub (site updates in ~30 seconds)
git add .
git commit -m "Update position to [new place]"
git push
```

---

## Common updates

### Change your position / university

Edit `data/profile.json`:

```json
{
  "title":   "Postdoc · MIT CSAIL",
  "tagline": "Short one-line description of what you work on."
}
```

Then `python3 build.py` → `git push`.

### Add a new publication

Append an object to `data/publications.json`:

```json
{
  "year": 2026,
  "title": "My New Paper",
  "authors": "M. Santra, A. Collaborator",
  "venue": "IEEE S&P 2026",
  "tags": ["IEEE S&P", "arXiv:2601.99999"],
  "arxiv": "https://arxiv.org/abs/2601.99999",
  "citations": 0
}
```

- `tags` controls the coloured badges. Values starting with `arXiv:` become clickable links automatically.
- `"under review"` → amber badge; venue names → teal badge; `"N citations"` → grey badge.
- `"M. Santra"` in `authors` is automatically bolded as the self-author.

### Add a new job

Append to `data/experience.json`:

```json
{
  "org":         "MIT CSAIL",
  "period":      "2026 – present",
  "role":        "Postdoctoral Researcher",
  "location":    "Cambridge, MA, USA",
  "description": "One line describing what you work on there."
}
```

### Add a new project

Append to `data/projects.json`:

```json
{
  "name": "Project Alpha",
  "description": "A couple of lines describing what it is and why it matters."
}
```

### Update the CV

Replace the file at `cv/Monika_CV_new.pdf`:

```bash
cp ~/Downloads/CV_updated.pdf cv/Monika_CV_new.pdf
git add cv/Monika_CV_new.pdf
git commit -m "Update CV"
git push
```

The CV link in the header points to `cv/Monika_CV_new.pdf` — no rebuild needed as long as the filename stays the same.

### Change the profile photo

Replace `images/profile.jpg` with a new square-ish image (it's cropped into a circle). `profile.json`'s `"photo"` field points at it, so no rebuild is needed as long as the filename stays the same.

```bash
cp ~/Downloads/my_photo.jpg images/profile.jpg
git add images/profile.jpg
git commit -m "Update profile photo"
git push
```

---

## Analytics (GoatCounter)

[GoatCounter](https://www.goatcounter.com/) is a free, privacy-friendly analytics tool that shows page views, visitor countries, and cities — no cookies, GDPR-compliant.

### Setup

1. Go to [goatcounter.com](https://www.goatcounter.com/) → **Sign up for free**.
2. Choose a site code, e.g. `monikasantra` → your dashboard will be at `https://monikasantra.goatcounter.com`.
3. Edit `data/profile.json` and set `goatcounter_site`:

```json
"analytics": {
  "goatcounter_site": "monikasantra"
}
```

4. Rebuild and push:

```bash
python3 build.py
git add .
git commit -m "Enable analytics"
git push
```

Your dashboard will show real-time stats after the next visitor hits the page.

> To disable analytics entirely, set `"goatcounter_site": ""` and rebuild.

---

## Publishing as a GitHub Personal Website

### Step 1 — Create the repository

1. Go to [github.com/new](https://github.com/new).
2. Set the name to **`<your-username>.github.io`** (e.g. `monikas.github.io`).
3. Set visibility to **Public**.
4. Leave "Initialize with README" **unchecked**.
5. Click **Create repository**.

### Step 2 — Push this folder

```bash
git init
git add .
git commit -m "Initial portfolio site"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-username>.github.io.git
git push -u origin main
```

### Step 3 — Enable GitHub Pages

1. Repository → **Settings → Pages**.
2. Source: **Deploy from a branch** → `main` → `/ (root)`.
3. Click **Save**.

Your site will be live at `https://<your-username>.github.io` within ~60 seconds.

---

## Custom domain (optional)

To use `monikasantra.com` instead of `<username>.github.io`:

1. Buy the domain from any registrar.
2. Add a DNS **CNAME record**: `www` → `<your-username>.github.io`.
3. Create a file named `CNAME` in the repo root:
   ```
   www.monikasantra.com
   ```
4. **Settings → Pages → Custom domain** → enter your domain → **Save**.
5. Check **Enforce HTTPS** once the certificate is issued (~5 minutes).

---

## Local preview

```bash
# Recommended (PDF and image links work correctly over HTTP)
python3 -m http.server
# open http://localhost:8000

# Quick check (no server needed, but PDF links won't open inline)
open index.html
```

---

## File structure

```
portfolio-site/
├── build.py            # ← Run this after editing any data/ file
├── build.js            # Node.js alternative to build.py
├── index.html          # ← Generated output; do not edit directly
├── publications.json   # Legacy copy (data/publications.json is the source)
├── data/
│   ├── profile.json
│   ├── publications.json
│   ├── experience.json
│   ├── education.json
│   ├── awards.json
│   └── projects.json
├── cv/
│   └── Monika_CV_new.pdf
├── images/
│   └── profile.jpg     # Profile photo shown in the header
└── README.md
```

> **Rule of thumb:** Only edit files in `data/`. After any edit, run `python3 build.py` and push.
> Never edit `index.html` directly — your changes will be overwritten on the next build.
