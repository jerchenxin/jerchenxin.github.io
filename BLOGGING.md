# Blog Writing Guide

## Directory Layout

Each post uses one directory under `posts/`:

```text
posts/
  2026-03-27-llm-serving-notes/
    index.md
    fig-01.webp
    appendix.pdf
```

- `index.md` is the source.
- Other files in the same folder are attachments (images, PDFs, etc.).

## Markdown Format

Use front matter at the top of `index.md`:

```md
---
title: LLM Serving Notes: Throughput vs Latency
date: 2026-03-27
order: 1
summary: A practical checklist for balancing latency SLOs and serving cost in production.
tags: LLM, Serving, Infra
---

Post content here.
```

Required fields: `title`, `date`, `summary`.
Optional field: `order` (integer, default `0`). For posts on the same date, smaller `order` appears first.

## Attachment References

Inside markdown, use relative paths:

```md
![Serving pipeline](fig-01.webp)
[Appendix PDF](appendix.pdf)
```

During build, these links are rewritten for generated HTML pages.

## Build Command

Run:

```bash
python3 scripts/build_blog.py
```

Outputs:

- `generated/posts.json` (blog index data)
- `generated/posts.js` (browser-friendly index data for local preview)
- `generated/<slug>.html` (rendered post pages)

`blog.html` reads `generated/posts.json` and renders the post list automatically.
