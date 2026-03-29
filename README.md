# jerchenxin.github.io

## Blog Workflow

1. Write posts in `posts/<slug>/index.md`
2. Build generated pages and index:

```bash
python3 scripts/build_blog.py
```

## Local Preview

Start a local HTTP server from the repository root:

```bash
python3 -m http.server 8000
```

Then open these URLs in a browser:

- Home: `http://localhost:8000`
- Blog index: `http://localhost:8000/blog.html`
- Example post: `http://localhost:8000/generated/2026-03-28-autoresearch-agent.html`

Press `Ctrl+C` in the terminal to stop the server.

## Comments Setup

The blog is wired for `giscus`, but GitHub-side setup is still required before comments go live:

1. Enable Discussions for `jerchenxin/jerchenxin.github.io`.
2. Install the `giscus` GitHub App for that repository.
3. In the `giscus` configuration page, choose the `General` discussion category.
4. Copy the generated `category_id` into `GISCUS_CONFIG` in `scripts/build_blog.py`.
5. Rebuild the site with `python3 scripts/build_blog.py`.
