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

## Writing blog posts

When writing a blog post (or any prose) for this site, first read `docs/tone-of-voice.md` and write as Kasper. That document captures his writing voice, with verbatim examples to imitate, and the hard formatting rules (no staccato fragments, no bold, no em-dashes).
