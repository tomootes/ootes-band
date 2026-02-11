# OOTES>BAND Website

Jekyll static site for a band. Dutch-language content.

## Tech Stack

- Jekyll (GitHub Pages) with Liquid templating
- Tailwind CSS v4 (via browser script) for utility classes
- Custom SCSS in `_scss/` compiled through `assets/css/styles.scss`
- Prettier for formatting

## Styling
- Keywords for the aestethic: 90s, bandcamp, DIY

### Approach: Tailwind-first, SCSS for components

- Use **SCSS with BEM naming** (`block__element--modifier`) only for reusable components (see `_scss/_newsletter-form.scss` for example).
- CSS custom properties are defined in `_scss/_css-variables.scss`.

### Color Palette (solarpunk / green nature theme)

- Brand green: `#00AA58` (`--green-brand`)
- Dark greens for text: `--green-text` (#2d5540), `--green-text-dark` (#1a3326)
- Peach accent: `--peach-brand` (#f6d1be)
- Light backgrounds: `--bg-cream`, `--bg-mint`, `--bg-fresh`
- Use Tailwind's `green-*` scale for quick utility styling.

### Typography

- Body: Arial / Helvetica (system sans-serif)
- Headings (h1-h5): "Fira Mono" (monospace)
- Secondary: "Fira Sans" (Google Fonts, weights 100-900)

### Responsive Design

- Mobile-first using Tailwind's `md:` breakpoint (768px+).
- Templates must be responsive (see DEFINITION_OF_DONE.md).
- Sidebar is hidden on mobile (`hidden md:flex`).

## Project Structure

- `_layouts/` — Page layouts (`default.html`, `song.html`)
- `_includes/` — Reusable partials (nav, footer, sidebar, etc.)
- `_scss/` — SCSS source files, imported via `_scss/main.scss`
- `_songs/`, `_gigs/`, `_photo_series/`, `_videos/` — Jekyll collections

## Dev

- Run locally: `npm run jekyll` (or `bundle exec jekyll serve --livereload`)
