---
title: "Skills Are Replacing Commands, Rules, and Subagents"
slug: skills-replacing-commands-rules-subagents
date: 2026-01-23
description: "OpenAI deprecated custom prompts. Cursor built a migration tool. The evidence is clear: skills are replacing commands, rules, and subagents."
---

This might be obvious to some, but it just clicked for me while building [agent-resources](https://github.com/kasperjunge/agent-resources).

When Anthropic released the [Agent Skills open standard](https://agentskills.io/) on December 18, 2025, [GitHub announced support the same day](https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills/). [OpenAI Codex](https://developers.openai.com/codex/skills/) followed shortly after. The consolidation is happening fast.

## The evidence

- **Commands:** [OpenAI Codex has deprecated custom prompts](https://developers.openai.com/codex/custom-prompts/) in favor of skills. Claude Code's [/slash-commands documentation now redirects to the skills page](https://docs.claude.com/en/docs/claude-code/skills) — skills are invoked as slash commands with `/skill-name`.
- **Rules:** [Cursor includes a built-in /migrate-to-skills](https://cursor.com/docs/context/skills) command that converts dynamic rules and slash commands into skills.
- **Subagents:** There's an [open proposal to add context: fork](https://github.com/anthropics/claude-code/issues/14661) to skills, allowing them to run in isolated context. Cursor's subagents docs recommend: "If you find yourself creating a subagent for a simple, single-purpose task... consider using a skill instead."

## What skills don't replace

Instruction files. Skills are task-specific capabilities. Instruction files (`CLAUDE.md`, [AGENTS.md](https://agents.md/)) are persistent environment context — project structure, conventions, workflows. You need both.

## Why I pivoted agent-resources

[agent-resources](https://github.com/kasperjunge/agent-resources) originally supported skills, commands, rules, and subagents. I've now removed everything except skills. The other primitives are being absorbed — no point maintaining them.

Next up: instruction file templates. That's the gap that remains.
