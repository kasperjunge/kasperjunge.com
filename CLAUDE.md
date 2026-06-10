# kasperjunge.com

Personal website and blog for Kasper Junge.

## Publishing a blog post

1. Create a markdown file in `posts/<slug>.md` with frontmatter:
   ```
   ---
   title: "Post title"
   slug: post-slug
   date: YYYY-MM-DD
   description: "1-3 sentence summary for SEO and social sharing."
   ---
   ```
2. Run `just build` to generate the static site (output lands in `blog/<slug>/`).
3. Use `just serve` for local preview with watch.

Note: the `README.md` describes an older hand-written HTML workflow. The real workflow is markdown posts in `posts/` built via `build.py` / the `justfile`.

## Writing rules

These are firm. Follow them in any prose written for this site.

- Do not write in clipped, staccato sentence fragments for emphasis. Avoid things like "No problem statement. No user. No why." or "Great. Wonderful." or "Yes. A thousand times yes." Write in full, flowing sentences.
- Do not use bold (`**...**`) in prose.
- Never use em-dashes ("—"). Use a hyphen ("-") or restructure with a comma instead.
