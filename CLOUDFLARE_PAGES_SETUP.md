# Cloudflare Pages Setup

Use the free Cloudflare Pages subdomain:

```text
https://aitoolpilot.pages.dev
```

## One-Time Setup

1. Open Cloudflare Dashboard.
2. Go to Workers & Pages.
3. Choose Pages, then Connect to Git.
4. Connect GitHub and select `merelyer/aitoolpilot`.
5. Set project name to `aitoolpilot`.
6. Set build command to empty or None.
7. Set build output directory to `site`.
8. Save and deploy.

After the first deploy, Cloudflare should serve:

```text
https://aitoolpilot.pages.dev
```

## Repository Settings Already Updated

- `config/settings.json` uses `https://aitoolpilot.pages.dev`.
- generated sitemap and robots point to `https://aitoolpilot.pages.dev`.
- internal links use root paths such as `/privacy/`, not the old GitHub Pages `/aitoolpilot/` subpath.

## If Cloudflare Says The Name Is Taken

Use the closest available project name, then update:

- `config/settings.json` `site.url`
- `config/settings.json` `site.domain`
- static files under `site/`
