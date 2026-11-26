# PULSECHAIN GARDEN

**https://ihelpmaybe.github.io/pulsechain-garden/**

Local fork of [prompt-site](https://github.com/egoprry/prompt-site) (the engine behind groypergarden.com), rebranded for **Richard Heart / HEX / PulseChain** image & video prompts.

Static SPA. No framework. Drop folders in `content/`, run `npm run build`, serve.

## Quick start

```bash
npm install
npm run build
npm run serve
```

Opens at http://localhost:4173

## Add a post

```bash
npm run new
```

Or manually create `content/<slug>/` with `title.md`, `tags.md`, `content.md` (plus optional `date.md`, `hero.md`, images). Then `npm run build`.

## Layout

| Path | What |
|---|---|
| `content/` | Prompt posts + `links.json` + `prompt-of-day.json` |
| `styles/` | Reusable Midjourney sref/profile/mood entries |
| `data/` | Asset gallery images |
| `app.js` / `styles.css` | Site shell (wrap, don’t reinvent) |

## Brand

- Name: **PULSECHAIN GARDEN**
- Accent: Pulse teal (`#00e5a8`)
- Upstream groyper content removed — seed only RH/Pulse starters
