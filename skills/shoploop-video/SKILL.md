---
name: shoploop-video
description: Use when the user wants to generate, create, render, or download a Shoploop/Seedance video from text, one or more reference images, first/last frames, a reference video, a reference audio, or any mix of those in one render (multi-source); also use for prompt-to-video, image-to-video, video-reference motion, multi-reference product/model showcase, controllable duration (4-15s) / resolution (720p/1080p) / aspect ratio (9:16/16:9/1:1/4:3/3:4), social short clips, product videos, and no-watermark mp4 delivery through a Shoploop API key.
---

# Shoploop Video

## Overview

Generate no-watermark videos through the Shoploop AI gateway. Treat Shoploop as the only user-facing provider: do not mention hidden upstream vendors, internal model names, account-pool internals, or supplier tokens.

## Quick Start

Use the bundled CLI from this skill:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "cinematic 9:16 product demo, soft morning light" --duration 5 --aspect-ratio 9:16 --resolution 1080p --download shoploop_outputs/demo.mp4
```

The `--duration 5`, `--aspect-ratio 9:16`, and `--resolution 1080p` here are just sample values — confirm the real ones with the user first (see **Confirm Output Settings**).

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

## Confirm Output Settings (ask the user first)

The numbers in every example below (5s, 1080p, 9:16) are **illustrative samples, not defaults to apply blindly**. Before you generate, confirm these three output settings with the user and wait for their answer (二次确认) — this is required even if the request seems clear:

1. **Duration / 时长** — how many seconds? Supported values **4 / 5 / 8 / 10 / 15s**. (If they have no preference, suggest 5s.)
2. **Resolution / 画质** — **720p** or **1080p**. (Suggest 1080p; 720p renders a bit faster/cheaper.)
3. **Aspect ratio / 比例** — one of **9:16** (vertical/social), **16:9** (landscape), **1:1** (square), **4:3**, **3:4**. These are the only supported ratios — **21:9 / ultra-wide and other ratios are not available** (the gateway will reject them with a clear message). (Suggest 9:16 for social/mobile.)

All three knobs are independent and fully controllable — any duration × any resolution × any ratio is a valid combination, including multi-reference renders. Pass them via `--duration` / `--resolution` / `--aspect-ratio`.

How to confirm: restate the full set with your suggested values and ask the user to confirm or adjust, e.g. "我按 **5 秒 / 1080p / 9:16** 来生成,可以吗?要改时长、画质或比例直接说。" Even if the user already specified one or two of them, still echo back all three and get an explicit go-ahead. Do not run the CLI until the user has confirmed. Then pass exactly the confirmed values via `--duration` / `--resolution` / `--aspect-ratio`.

## Workflow

1. Confirm the key is configured (see **API Key — Check First**). If it is not, ask the user for it and save it before doing anything else.
2. Understand the user's target video: subject, action, style, and deliverable path.
3. **Confirm the output settings — duration, resolution, and aspect ratio — with the user (see Confirm Output Settings). Do NOT generate until the user has confirmed all three.**
4. Preserve every user-provided image or video exactly. Do not crop, resize, enhance, extract frames, transcode, or split media unless the user explicitly asks.
5. Choose the smallest matching mode:
   - Text only: no references.
   - One image: `--mode image`.
   - Two or more images as visual, character, style, product, or scene references: `--mode multi-reference`.
   - First and last frame: `--mode first-last` and pass the first frame before the last frame.
   - Reference video for motion, rhythm, or camera movement: `--mode video-reference`.
   - **Mixed multi-source** — combine any of: image(s) (character/product/scene), a reference video (motion/camera), and a reference audio (soundtrack / lip-sync voice) in one render. Just attach them all; the gateway routes a mixed set to the multi-reference engine automatically. Up to 3 videos and 3 audios; total reference length ≤ 15s.
6. Run `scripts/shoploop.py` with the user's **confirmed** duration / resolution / aspect ratio. Add `--json` when another tool needs machine-readable output; otherwise return the mp4 URL and any downloaded file path.
7. If rendering fails, report the Shoploop-facing reason plainly and suggest a smaller, safer prompt only when moderation or prompt ambiguity is the likely cause.

## Long renders — the CLI waits for you (do NOT re-run)

A 10–15s video takes several minutes to render. The CLI handles the whole wait for you: it submits, then polls in the background until the finished mp4 URL is ready — all inside the single command you run. So:

- Run the command **once** and let it finish, even if it takes a few minutes. The `still rendering...` progress lines are normal.
- **Never** re-run the command (or start another generation) while one is still rendering. Each run starts a brand-new, separately-billed render — re-running is exactly what creates duplicate videos.
- If the CLI ever exits saying it timed out while the video is still rendering (it prints a `job` id), just run the **same** command once more to fetch it — do not change the prompt or start a different render.

## Command Patterns

In every command below, treat `--duration`, `--resolution`, and `--aspect-ratio` as placeholders — substitute the values you confirmed with the user (see **Confirm Output Settings**); do not copy the sample numbers verbatim.

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

Mixed multi-source (model + products + reference video, e.g. an e-commerce showcase). Combine images, a video, and optionally an audio in one render; every size/length knob is free:

```bash
python3 .agents/skills/shoploop-video/scripts/shoploop.py "fashion model showcasing the products, natural turn and smile following the reference video's motion, soft studio light" \
  --image-file /absolute/path/model.jpg \
  --image-file /absolute/path/product1.png \
  --image-file /absolute/path/product2.png \
  --video-file /absolute/path/reference.mp4 \
  --duration 15 --resolution 1080p --aspect-ratio 9:16 \
  --download shoploop_outputs/showcase.mp4
```

Add `--audio-file /absolute/path/voice.mp3` (or `--audio-url`) to drive a soundtrack / lip-sync voice.

## Defaults

- Default base URL: `https://seedance.shoploopai.com`.
- Default public model: `seedance2.0`.
- Output settings (duration / resolution / aspect ratio) are **suggestions to offer the user, not values to auto-apply** — always confirm them first (see **Confirm Output Settings**). Suggested starting point: 5s / 1080p / 9:16.
- Supported duration: 4 / 5 / 8 / 10 / 15 seconds. Supported resolution: 720p / 1080p. Supported ratios: 9:16 / 16:9 / 1:1 / 4:3 / 3:4. Any combination is valid (the knobs are independent).
- References can be combined: image(s) + reference video + reference audio in one render (multi-source). Up to 3 videos and 3 audios; total reference length ≤ 15s.
- Use `shoploop_outputs/` for downloaded files when the user does not specify a path.

## Common Mistakes

- Do not generate with assumed duration, resolution, or aspect ratio — confirm all three with the user first (二次确认), even when the examples show specific values.
- Do not treat the sample numbers in the example commands as defaults to copy verbatim.
- Do not ask users to run commands themselves when you can run the CLI.
- Do not call the API before confirming a key is configured; if it is missing or still the placeholder, ask the user for their key and save it first.
- Do not guess, invent, or reuse an API key.
- Do not expose hidden provider names, internal model versions, or upstream account details.
- Do not print or store `SHOPLOOP_KEY`.
- Do not alter reference media unless explicitly requested.
- Do not assume an instant result; rendering can take several minutes.
- **Do not re-run the command while a render is in progress.** The CLI polls internally until the mp4 is ready; re-running starts a new, duplicate, billable render. Wait for the single command to finish.
