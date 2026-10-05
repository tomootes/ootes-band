# OOTES>BAND

Website for OOTES>BAND, live at [ootes.band](https://ootes.band).

## Prerequisites

- Ruby 3.3.6 (see `.ruby-version`) and Bundler:

  ```sh
  sudo apt install ruby-full ruby-bundler
  ```

- Node 24 (see `.nvmrc`), only needed for Prettier and the npm script.

## Install

```sh
bundle install
npm install
```

## Development

```sh
npm run jekyll
# or: bundle exec jekyll serve --livereload
```

The site is served at http://localhost:4000. Changes to `_config.yml` require a server restart.

## Project structure

| Path                 | Contents                                                     |
| -------------------- | ------------------------------------------------------------ |
| `*.html` (root)      | Pages (`index`, `gigs`, `releases`, `videos`, `fotos`, ...)  |
| `_layouts/`          | Page layouts (`default`, `default-no-footer`, `song`)        |
| `_includes/`         | Partials (nav, footer, sidebar, audio player, newsletter...) |
| `_scss/`             | SCSS partials, imported via `_scss/main.scss`                |
| `assets/`            | Static assets; `assets/css/styles.scss` is the CSS entry     |
| `_gigs/`             | Gigs collection                                              |
| `_songs/`            | Songs with lyrics and chords                                 |
| `_photo_series/`     | Photo series (images by UUID)                                |
| `_videos/`           | Videos (YouTube links)                                       |

## Adding content

Add a file to the matching collection folder with front matter:

```yaml
# _gigs/<name>.md
---
title: "Eau Mont Jardin 2025"
date: 2025-08-10
location: "Jardin Les Etang, Omont"
---
```

```yaml
# _videos/<name>.html
---
title: "Black Boys on Mopeds"
date: 2026-05-18
video_url: "https://www.youtube.com/watch?v=..."
---
```

```yaml
# _songs/<name>.md
---
layout: song
title: "Song title"
original_song: "Artist ~ Original"
key: "C majeur"
spotify_url: ""
youtube_url: ""
---
```

```yaml
# _photo_series/<name>.md
---
title: "Eau Mont Jardin 2024"
date: 2024-08-11
location: "Jardin Les Etang, Omont"
photographer: "Name"
photos: [{ "uuid": "<image-uuid>", "cols": 4 }]
---
```

## Styling

Custom SCSS with BEM naming (`block__element--modifier`). Colours and other CSS custom properties live in `_scss/_css-variables.scss`. Format code with Prettier (config in `.prettierrc`).

## Deployment

Pushing to `main` deploys the site through GitHub Pages (custom domain in `CNAME`).
