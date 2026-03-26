#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
GENERATED_DIR = ROOT / "generated"

ABSOLUTE_URL_RE = re.compile(r"^(?:https?://|/|#|mailto:)", re.IGNORECASE)


@dataclass
class Post:
    slug: str
    title: str
    date: str
    order: int
    summary: str
    tags: list[str]
    display_date: str
    body_html: str


def parse_front_matter(raw: str, source: Path) -> tuple[dict[str, str], str]:
    if not raw.startswith("---\n"):
        raise ValueError(f"{source}: missing front matter start '---'")

    end_index = raw.find("\n---\n", 4)
    if end_index == -1:
        raise ValueError(f"{source}: missing front matter end '---'")

    front_matter_text = raw[4:end_index]
    body = raw[end_index + 5 :].lstrip("\n")
    data: dict[str, str] = {}

    for line in front_matter_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(f"{source}: invalid front matter line: {line}")
        key, value = stripped.split(":", 1)
        data[key.strip().lower()] = value.strip()

    return data, body


def normalize_relative_url(url: str, slug: str) -> str:
    if ABSOLUTE_URL_RE.match(url):
        return url
    normalized = url[2:] if url.startswith("./") else url
    return f"../posts/{slug}/{normalized}"


def render_inline(text: str, slug: str) -> str:
    placeholders: dict[str, str] = {}

    def replace_code(match: re.Match[str]) -> str:
        key = f"@@CODE{len(placeholders)}@@"
        placeholders[key] = f"<code>{html.escape(match.group(1))}</code>"
        return key

    text = re.sub(r"`([^`]+)`", replace_code, text)
    text = html.escape(text)

    def replace_image(match: re.Match[str]) -> str:
        alt_text = match.group(1)
        url = normalize_relative_url(html.unescape(match.group(2)), slug)
        return (
            f'<img src="{html.escape(url, quote=True)}" '
            f'alt="{alt_text}" loading="lazy" decoding="async" />'
        )

    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = normalize_relative_url(html.unescape(match.group(2)), slug)
        return f'<a href="{html.escape(url, quote=True)}">{label}</a>'

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)

    for key, value in placeholders.items():
        text = text.replace(key, value)

    return text


def markdown_to_html(markdown_text: str, slug: str) -> str:
    lines = markdown_text.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    in_ul = False
    in_ol = False
    in_code = False
    code_lang = ""
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph if part.strip())
        if text:
            output.append(f"<p>{render_inline(text, slug)}</p>")
        paragraph = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            output.append("</ul>")
            in_ul = False
        if in_ol:
            output.append("</ol>")
            in_ol = False

    for line in lines:
        stripped = line.rstrip()

        if in_code:
            if stripped.startswith("```"):
                escaped_code = html.escape("\n".join(code_lines))
                class_attr = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
                output.append(f"<pre><code{class_attr}>{escaped_code}</code></pre>")
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                code_lines.append(line)
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            close_lists()
            in_code = True
            code_lang = stripped[3:].strip()
            code_lines = []
            continue

        if not stripped.strip():
            flush_paragraph()
            close_lists()
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            close_lists()
            level = len(heading_match.group(1))
            heading_text = render_inline(heading_match.group(2).strip(), slug)
            output.append(f"<h{level}>{heading_text}</h{level}>")
            continue

        ul_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if ul_match:
            flush_paragraph()
            if in_ol:
                output.append("</ol>")
                in_ol = False
            if not in_ul:
                output.append("<ul>")
                in_ul = True
            output.append(f"<li>{render_inline(ul_match.group(1).strip(), slug)}</li>")
            continue

        ol_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ol_match:
            flush_paragraph()
            if in_ul:
                output.append("</ul>")
                in_ul = False
            if not in_ol:
                output.append("<ol>")
                in_ol = True
            output.append(f"<li>{render_inline(ol_match.group(1).strip(), slug)}</li>")
            continue

        paragraph.append(stripped)

    if in_code:
        escaped_code = html.escape("\n".join(code_lines))
        class_attr = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
        output.append(f"<pre><code{class_attr}>{escaped_code}</code></pre>")

    flush_paragraph()
    close_lists()
    return "\n".join(output)


def format_date(raw_date: str) -> str:
    parsed = dt.date.fromisoformat(raw_date)
    return parsed.strftime("%B %d, %Y")


def load_post(post_dir: Path) -> Post:
    slug = post_dir.name
    markdown_path = post_dir / "index.md"
    raw = markdown_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw, markdown_path)

    title = meta.get("title", "").strip()
    date = meta.get("date", "").strip()
    order_raw = meta.get("order", "0").strip()
    summary = meta.get("summary", "").strip()
    tags_raw = meta.get("tags", "")

    if not title:
        raise ValueError(f"{markdown_path}: missing title")
    if not date:
        raise ValueError(f"{markdown_path}: missing date")
    if not summary:
        raise ValueError(f"{markdown_path}: missing summary")
    try:
        order = int(order_raw)
    except ValueError as exc:
        raise ValueError(f"{markdown_path}: order must be an integer, got: {order_raw}") from exc

    tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

    return Post(
        slug=slug,
        title=title,
        date=date,
        order=order,
        summary=summary,
        tags=tags,
        display_date=format_date(date),
        body_html=markdown_to_html(body, slug),
    )


def render_post_html(post: Post) -> str:
    tags_html = ""
    if post.tags:
        tags_line = "".join(
            f'<span class="mini-tag">{html.escape(tag)}</span>' for tag in post.tags
        )
        tags_html = f'<div class="post-tags-inline" aria-label="Post tags">{tags_line}</div>'

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(post.title)} | CHEN Xin</title>
  <meta name=\"description\" content={json.dumps(post.summary)} />
  <link rel=\"stylesheet\" href=\"../jemdoc.css\" type=\"text/css\" />
</head>
<body>
  <div class=\"page\">
    <header class=\"site-header\">
      <div>
        <h1>{html.escape(post.title)}</h1>
        <p class=\"subtitle\">{post.display_date}</p>
      </div>
      <nav class=\"top-nav\" aria-label=\"Main navigation\">
        <a href=\"../index.html\">Home</a>
        <a href=\"../blog.html\">Blog</a>
      </nav>
    </header>

    <main class=\"content-grid blog-grid\">
      <article class=\"card full post-content\">
        <p class=\"post-summary\">{html.escape(post.summary)}</p>
        {tags_html}
        {post.body_html}
      </article>
    </main>

    <footer class=\"site-footer\">
      <p><a href=\"../blog.html\">Back to blog list</a></p>
    </footer>
  </div>
</body>
</html>
"""


def build() -> None:
    if not POSTS_DIR.exists():
        raise FileNotFoundError(f"missing posts directory: {POSTS_DIR}")

    post_dirs = sorted(
        [path for path in POSTS_DIR.iterdir() if path.is_dir() and (path / "index.md").exists()],
        key=lambda item: item.name,
    )

    posts = [load_post(path) for path in post_dirs]
    posts.sort(key=lambda item: item.slug)
    posts.sort(key=lambda item: item.order)
    posts.sort(key=lambda item: item.date, reverse=True)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    expected_post_files = {f"{post.slug}.html" for post in posts}

    # Remove stale generated post pages that no longer have a markdown source.
    for existing_file in GENERATED_DIR.glob("*.html"):
        if existing_file.name not in expected_post_files:
            existing_file.unlink()

    for post in posts:
        html_content = render_post_html(post)
        (GENERATED_DIR / f"{post.slug}.html").write_text(html_content, encoding="utf-8")

    index_payload = [
        {
            "slug": post.slug,
            "title": post.title,
            "date": post.date,
            "order": post.order,
            "display_date": post.display_date,
            "summary": post.summary,
            "tags": post.tags,
            "url": f"generated/{post.slug}.html",
        }
        for post in posts
    ]
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    posts_json = json.dumps(index_payload, ensure_ascii=False, indent=2)
    (GENERATED_DIR / "posts.json").write_text(
        posts_json + "\n",
        encoding="utf-8",
    )
    (GENERATED_DIR / "posts.js").write_text(
        "window.__BLOG_POSTS__ = " + posts_json + ";\n",
        encoding="utf-8",
    )

    print(f"Built {len(posts)} post(s) into {GENERATED_DIR}")


if __name__ == "__main__":
    build()
