---
title: My Claude Code Workflow - February 2026
slug: my-claude-code-workflow
date: 2026-02-01
description: How I use Claude Code for daily development — my setup, habits, and what works.
---

I love reading blog posts on people's vibe coding workflows, for example Peter Steinberger's, creator of Clawdbot/Moltbot, [Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed), so I thought I would make my own. Let's get straight to it.

First, I would like to send shoutouts to Dexter Horthy from HumanLayer, who inspired my current personal development workflow. In [this blog post](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) Dexter describes his framework Research-Plan-Implement. Reading that blog post was really an eye opener to me. I [teach vibe coding to development teams](https://vibe-coding.dk/) and have taught around 150 software developers so far in Research-Plan-Implement and every time my partner [Christian](https://www.linkedin.com/in/cbechn/) and I host a workshop, we tell developers to pick real tasks from their backlog and most of them are able to get what is estimated for around 20 hours done in an hour or so using Research-Plan-Implement. It is really true magic, and I've seen senior architects at first sceptical about vibe coding sitting just speechless staring at their computer while the RPI framework does their work for them in a fraction of the time they could have done it.

Just to say, I've seen this work across many devs and teams. It is pure magic and a really great fundamental theory for thinking about agentic coding.

Okay now, let's actually get in to it!

## Setup

As mentioned, I use Claude Code. I used to use a mix of slash commands, subagents, rules and scripts they could execute to develop processes for my AI agents. However, I recently noticed some patterns while developing [agent-resources](https://github.com/kasperjunge/agent-resources): 

1. [Claude Code supports that you can invoke skills using /skillname , which basically provides behavior identical to slash commands.](https://code.claude.com/docs/en/skills)
2. [Codex has deprecated prompts (their version of slash commands) and recommends using skills which can be invoked with /skillname](https://developers.openai.com/codex/custom-prompts/)
3. [Claude Code lets you set "context: fork" in skills, which makes it run in a forked subagent context - which enable skills to behave similarly to subagents](https://code.claude.com/docs/en/skills#frontmatter-reference)
4. A skill with only name, description and body text is identical to rules, which are supported in Cursor and Claude Code.
5. [Cursor recommends considering using skills when making a subagent.](https://cursor.com/docs/context/subagents#when-to-use-subagents)

Skills can replace many of the other agentic primitives and the agent coding tools seems to slowly deprecate commands/prompts, rules and subagents, which all indicates that [agent skills seems to be replacing commands, subagents and rules](https://kasperjunge.com/blog/skills-replacing-commands-rules-subagents/).

So, I try to only use skills.



## Daily Workflow

<!-- How you typically use Claude Code throughout the day -->

## What Works Well

<!-- Patterns and practices that have been effective -->

## What I'm Still Figuring Out

<!-- Areas you're experimenting with or improving -->


