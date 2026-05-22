# GitHub Repository Strategy

The SOE project lives at: **https://github.com/ChefLee5/SOE-Orginal-Repository-**

## Repository Structure (886 files, ~919 MB)

```
SOE-Orginal-Repository/
├── .github/workflows/deploy.yml        ← GitHub Actions deployment
├── .gitignore                          ← Excludes large media (see below)
├── README.md                           ← Project overview
│
├── ebook/                              ← 📖 Picture Dictionary (EPUB pipeline)
│   ├── content/                        ← 15 Markdown source files (583 KB)
│   ├── OEBPS/
│   │   ├── pages/                      ← 160 generated XHTML pages
│   │   ├── images/                     ← 157 compressed scene illustrations
│   │   ├── styles/dictionary.css       ← Design system
│   │   └── fonts/                      ← 4 WOFF2 fonts (Fredoka, Nunito)
│   ├── META-INF/container.xml
│   ├── content.opf                     ← EPUB manifest
│   ├── scripts/                        ← 16 build/audit scripts
│   ├── posters/flashcards/             ← Printable flashcard assets
│   ├── staging/characters/             ← Character staging images
│   ├── generate_pages.py               ← Full MD → XHTML generator
│   ├── build_epub.py                   ← Extended EPUB builder
│   ├── BUILD_GUIDE.md                  ← Build pipeline reference
│   └── CONTENT_MAP.md                  ← Complete scene inventory
│
├── web/                                ← 🌐 Companion Website (React + Vite)
│   ├── src/
│   │   ├── pages/                      ← 8 pages: Home, Heroes, Universe, etc.
│   │   ├── components/                 ← Navbar, Footer, SplashScreen, etc.
│   │   ├── data/                       ← heroes.json, gallery.json
│   │   ├── i18n/locales/               ← EN, ES, FR translations
│   │   └── remotion/                   ← Video generation (HeroTeaser, Trailer)
│   ├── public/assets/                  ← Optimized web images
│   ├── vercel.json                     ← Vercel deployment config
│   └── robots.txt, sitemap.xml         ← SEO
│
└── UDL Downloads/Visual assets/        ← 🎨 Source Image Assets (473 MB)
    ├── Character reference/            ← 15 full-body character PNGs
    ├── Characters & Duo_s Completed/   ← Character PNGs + reference JPEGs + duo scenes
    ├── le_cheval/                       ← Le Cheval music video shots (11 images)
    └── new_soe_book/                   ← Full book page renders (1-14 + cover + alternates)
```

## .gitignore Strategy

The repo excludes large/regeneratable media to keep push sizes manageable:

```
# Large media directories
Prototypes/
Book Illustrations/
The Sound of Essentials_ The Rhythm Quest/updated reference photos/

# Heavy binary formats
*.mp4, *.mov, *.mp3, *.wav, *.psd, *.ai

# Build artifacts
dist/, build/, *.epub
```

## Last Commit (as of May 2026)

```
feat: replace all character .jpg/.webp with full-res .png assets
- Delete 31 old compressed jpg and webp character images
- Add 14 full-body character PNGs from source asset folder
- Add 14 _crop.png variants plus SERIPHIA_celestia.png
- Update heroes.json, MediaRoom.jsx, dictionaryData.js to use .png
- Add robots.txt and sitemap.xml for SEO
- Update vercel.json with cache and security headers
- Sync i18n es.json and fr.json translation keys
- Update README with current stack and deploy docs
```

## Deployment

- **Website:** Deployed via Vercel (vercel.json configured with cache headers)
- **EPUB:** Direct download or platform distribution (KDP, Apple Books, Kobo, Google Play)
- **CI/CD:** GitHub Actions workflow at `.github/workflows/deploy.yml`
