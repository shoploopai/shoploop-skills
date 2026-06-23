---
name: shoploop-setup
description: Use when setting up a new computer, new Codex project, reseller workstation, or customer workspace for Shoploop video generation; use to install Shoploop skills, create or verify .env.shoploop, check API key configuration, validate the bundled video CLI, and explain how Codex discovers .agents/skills or ~/.agents/skills.
---

# Shoploop Setup

## Overview

Prepare a computer so Codex can generate Shoploop videos out of the box. This skill installs the Shoploop skill set, creates the expected key template, and verifies the local CLI without exposing hidden provider details.

## Install Modes

Use one of these installation targets:

- Project install: copy skills into `<project>/.agents/skills`. Best for customer project folders and portable zip handoff.
- Global install: copy skills into `~/.agents/skills` (the official Codex user scope; `~/.codex/skills` also works). Best for a reseller or creator machine that should have Shoploop available everywhere.
- Both: project install first, then global install if the user asks for system-wide availability.

## Standard Workflow

1. Locate the Shoploop skill source. In this repository it is `.agents/skills`. On Windows use `python` or `py -3` instead of `python3` in every command below.
2. Run the setup helper:

```bash
python3 .agents/skills/shoploop-setup/scripts/shoploop_setup.py --project .
```

3. If the user wants global install:

```bash
python3 .agents/skills/shoploop-setup/scripts/shoploop_setup.py --global
```

4. Create or update `.env.shoploop`. The helper seeds it from the template with the placeholder `SHOPLOOP_KEY=sk-your-customer-key`. **Ask the user for their Shoploop key** (format `sk-...`) and replace the placeholder with it. If the user does not have a key, tell them to get one from their Shoploop provider — never guess or invent a key, and never echo it back into chat, logs, or commits.

```bash
SHOPLOOP_KEY=sk-customer-key
SHOPLOOP_BASE=https://seedance.shoploopai.com
SHOPLOOP_MODEL=seedance2.0
```

5. Validate without rendering:

```bash
python3 .agents/skills/shoploop-setup/scripts/shoploop_setup.py --project . --check
```

## What To Check

- `shoploop-video` and `shoploop-setup` exist in the selected skill directory.
- `shoploop-reseller` is optional and should only be present in reseller/operator packages.
- `SHOPLOOP_KEY` is set through `.env.shoploop` or the shell environment, and is not the placeholder `sk-your-customer-key`. The check reports `unset` for an empty value or the placeholder. Report only set/unset; never print the key. If unset, ask the user for their key and save it before finishing.
- You can also run the video CLI's own check: `python3 .agents/skills/shoploop-video/scripts/shoploop.py --check-key` (exit 0 = configured, exit 3 = not configured).
- `shoploop-video/scripts/shoploop.py --dry-run` can build a request body.
- The user knows that a new Codex session may be needed for newly installed skills to appear in the skill list.

## Handoff For Customers

For a customer machine, give them:

- The `.agents/skills/shoploop-*` folders.
- A `.env.shoploop` file containing only their Shoploop API key and public endpoint.
- A starter prompt such as: `帮我生成一个 9:16 的产品展示视频，5 秒，电影感，下载到 shoploop_outputs/demo.mp4`.

## Common Mistakes

- Do not put real keys into git, Markdown docs, screenshots, or final replies.
- Do not tell users to configure hidden provider tokens.
- Do not edit the user's shell profile unless they explicitly ask for a global environment variable.
- Do not treat installation as complete until the dry-run check passes.
