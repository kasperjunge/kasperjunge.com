default:
    @just --list

build:
    uv run python build.py

serve:
    uv run python build.py --serve --watch

new-post:
    #!/usr/bin/env bash
    set -euo pipefail
    date=$(date +%Y-%m-%d)
    slug="untitled-$(date +%s)"
    file="posts/${slug}.md"
    cat > "$file" <<EOF
    ---
    title: "Untitled"
    slug: ${slug}
    date: ${date}
    description: ""
    ---

    Write your post here.
    EOF
    echo "Created $file"
    ${EDITOR:-open} "$file"
