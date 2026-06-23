---
name: shoploop-video
description: Use when the user wants to generate, create, render, or download a Shoploop/Seedance video from text, one or more reference images, first/last frames, a reference video, or mixed media references; also use for prompt-to-video, image-to-video, video-reference motion, social short clips, product videos, and no-watermark mp4 delivery through a Shoploop API key.
---

# Shoploop Video

## Overview

Generate no-watermark videos through the Shoploop AI gateway. Treat Shoploop as the only user-facing provider: do not mention hidden upstream vendors, internal model names, account-pool internals, or supplier tokens.

## Quick Start

Use the bundled CLI from this skill:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "cinematic 9:16 product demo, soft morning light" --duration 5 --aspect-ratio 9:16 --resolution 1080p --download shoploop_outputs/demo.mp4
```

The CLI finds `.env.shoploop` by searching from the current directory upward to the project root. Run the script at its installed path (`.agents/skills/shoploop-video/scripts/shoploop.py` for a project install, or the matching path under your global skills dir). On Windows use `python` or `py -3` instead of `python3`. Required:

```bash
SHOPLOOP_KEY=sk-your-customer-key
```

## API Key — Check First

Before generating, confirm a usable key exists. Run:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py --check-key
```

- It prints `SHOPLOOP_KEY: configured` (exit 0) when a real key is set, or `not configured` (exit 3) when `.env.shoploop` is missing, the value is empty, or it is still the template placeholder `sk-your-customer-key`. It never prints the key itself.
- If not configured: **stop and ask the user for their Shoploop key** (format `sk-...`). When they give it, write it into `.env.shoploop` at the project root as `SHOPLOOP_KEY=<their key>` (create the file from `assets/env.shoploop.example` if it does not exist), then re-run `--check-key` to confirm before generating.
- If the user does not have a key, tell them to get one from their Shoploop provider. Never guess, invent, or reuse a key, and never echo the key back into chat, logs, or commits.
- Prefer `shoploop-setup` when the skill itself is not installed or you want the full scaffold (`.env.shoploop` + `.gitignore` + check) in one step.

## Workflow

1. Confirm the key is configured (see **API Key — Check First**). If it is not, ask the user for it and save it before doing anything else.
2. Understand the user's target video: subject, action, style, aspect ratio, duration, and deliverable path.
3. Preserve every user-provided image or video exactly. Do not crop, resize, enhance, extract frames, transcode, or split media unless the user explicitly asks.
4. Choose the smallest matching mode:
   - Text only: no references.
   - One image: `--mode image`.
   - Two or more images as visual, character, style, product, or scene references: `--mode multi-reference`.
   - First and last frame: `--mode first-last` and pass the first frame before the last frame.
   - Reference video for motion, rhythm, or camera movement: `--mode video-reference`.
5. Run `scripts/shoploop.py` with `--json` when another tool needs machine-readable output; otherwise return the mp4 URL and any downloaded file path.
6. If rendering fails, report the Shoploop-facing reason plainly and suggest a smaller, safer prompt only when moderation or prompt ambiguity is the likely cause.

## Command Patterns

Text to video:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "golden sunrise over the ocean, cinematic camera drift" --duration 5 --aspect-ratio 16:9 --resolution 1080p --download shoploop_outputs/ocean.mp4
```

Image to video:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "make this product image move naturally, slow push-in" --image-file /absolute/path/product.png --mode image --duration 5 --download shoploop_outputs/product.mp4
```

Multi-reference:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "use the character and room references to create a morning routine scene" --image-file /absolute/path/person.png --image-file /absolute/path/room.png --mode multi-reference --duration 8 --aspect-ratio 9:16 --resolution 1080p --download shoploop_outputs/morning.mp4
```

First/last frame:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "smooth transition from sitting at the desk to standing near the window" --image-file /absolute/path/first.png --image-file /absolute/path/last.png --mode first-last --duration 8 --aspect-ratio 9:16 --download shoploop_outputs/transition.mp4
```

Reference video:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "use the product photo as identity and follow the motion rhythm in the reference clip" --image-file /absolute/path/product.png --video-file /absolute/path/motion.mp4 --mode video-reference --duration 10 --aspect-ratio 9:16 --resolution 1080p --download shoploop_outputs/motion.mp4
```

## Defaults

- Default base URL: `https://seedance.shoploopai.com`.
- Default public model: `seedance2.0`.
- Default duration: 5 seconds.
- Supported duration range: 4-15 seconds.
- Prefer `9:16` for social/mobile requests unless the user asks for another canvas.
- Use `shoploop_outputs/` for downloaded files when the user does not specify a path.

## Common Mistakes

- Do not ask users to run commands themselves when you can run the CLI.
- Do not call the API before confirming a key is configured; if it is missing or still the placeholder, ask the user for their key and save it first.
- Do not guess, invent, or reuse an API key.
- Do not expose hidden provider names, internal model versions, or upstream account details.
- Do not print or store `SHOPLOOP_KEY`.
- Do not alter reference media unless explicitly requested.
- Do not assume an instant result; rendering can take several minutes.
