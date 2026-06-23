#!/usr/bin/env python3
"""Shoploop video CLI.

Generate no-watermark videos through the Shoploop AI gateway using an
OpenAI-compatible chat endpoint. The user-facing provider is Shoploop/Seedance.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request


MIN_DURATION = 4
MAX_DURATION = 15
URL_RE = re.compile(r"https?://[^\s\"'<>)]+" )
PLACEHOLDER_KEY = "sk-your-customer-key"
NO_KEY_MESSAGE = (
    "No Shoploop API key is configured. Ask the user for their Shoploop key "
    "(format sk-...), save it as SHOPLOOP_KEY in .env.shoploop at the project "
    "root, then retry. Never guess or invent a key. (Or run shoploop-setup.)"
)


def _find_env_file() -> str | None:
    """Locate .env.shoploop by walking up from the current working directory.

    Stops at the filesystem root, at $HOME, or at the first project marker
    (.git / .agents) so we never escape into an unrelated parent project or
    grab a stray ~/.env.shoploop. Only walks cwd (not the script dir): a global
    install lives under ~/.agents/skills, and walking that up would reach $HOME.
    """
    home = os.path.realpath(os.path.expanduser("~"))
    cur = os.path.realpath(os.getcwd())
    while True:
        candidate = os.path.join(cur, ".env.shoploop")
        if os.path.isfile(candidate):
            return candidate
        if os.path.isdir(os.path.join(cur, ".git")) or os.path.isdir(os.path.join(cur, ".agents")):
            break
        parent = os.path.dirname(cur)
        if parent == cur or os.path.realpath(parent) == home:
            break
        cur = parent
    return None


def _load_env_file() -> str | None:
    path = _find_env_file()
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            # A non-empty shell env var wins; otherwise take the file value.
            # Plain setdefault would let an empty or whitespace-only exported var
            # shadow a real key in .env.shoploop, so generation would refuse even
            # though the file holds a valid key.
            if not os.environ.get(key, "").strip():
                os.environ[key] = value.strip().strip("\"'")
    return path


_load_env_file()

BASE = os.environ.get("SHOPLOOP_BASE", "https://seedance.shoploopai.com").rstrip("/")
KEY = os.environ.get("SHOPLOOP_KEY", "").strip()
MODEL = os.environ.get("SHOPLOOP_MODEL", "seedance2.0").strip() or "seedance2.0"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _key_is_configured() -> bool:
    """True only when a real customer key is present.

    Treats both an empty value and the template placeholder as "not configured",
    so a freshly scaffolded .env.shoploop counts as missing and the caller can
    ask the user for their real key instead of sending a doomed request.
    """
    return bool(KEY) and KEY != PLACEHOLDER_KEY


def _die(message: str) -> None:
    print(f"[shoploop] {message}", file=sys.stderr)
    raise SystemExit(1)


def _warn(message: str) -> None:
    print(f"[shoploop] warning: {message}", file=sys.stderr)


class AppendReference(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        refs = getattr(namespace, self.dest, None) or []
        kind = {
            "--image": "image-url",
            "--image-file": "image-file",
            "--video-url": "video-url",
            "--video-file": "video-file",
        }.get(option_string, "image-url")
        refs.append((kind, values))
        setattr(namespace, self.dest, refs)


def _file_data_url(path: str, fallback_mime: str) -> str:
    if not os.path.exists(path):
        _die(f"file does not exist: {path}")
    mime = mimetypes.guess_type(path)[0] or fallback_mime
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _normalize_aspect_ratio(value: str | None) -> str | None:
    if not value:
        return None
    raw = value.strip()
    normalized = raw.lower().replace("：", ":").replace("×", "x").replace("*", "x")
    normalized = re.sub(r"\s+", "", normalized)
    separator = "x" if "x" in normalized else ":"
    match = re.fullmatch(r"(\d+(?:\.\d+)?)[:x](\d+(?:\.\d+)?)", normalized)
    if not match:
        return raw
    w_raw, h_raw = match.group(1), match.group(2)
    w, h = float(w_raw), float(h_raw)
    if w <= 0 or h <= 0:
        _die("aspect ratio values must be positive")
    if w_raw.isdigit() and h_raw.isdigit():
        wi, hi = int(w_raw), int(h_raw)
        if separator == ":" and wi < 100 and hi < 100:
            return f"{wi}:{hi}"
        divisor = math.gcd(wi, hi)
        return f"{wi // divisor}:{hi // divisor}"
    return f"{w_raw}:{h_raw}"


def _detect_mode(prompt: str, requested: str, image_count: int, video_count: int) -> str:
    if requested != "auto":
        return requested
    text = prompt.lower()
    if any(k in text for k in ("首尾帧", "首帧尾帧", "first-last", "first frame", "last frame")):
        return "first-last"
    if any(k in text for k in ("视频参考", "参考视频", "动作参考", "motion reference", "video reference")):
        return "video-reference"
    if any(k in text for k in ("多参考", "多图参考", "多张参考", "multi-reference", "multi reference")):
        return "multi-reference"
    if any(k in text for k in ("图生", "图生视频", "image-to-video", "image to video")):
        return "image"
    if video_count:
        return "video-reference"
    if image_count >= 2:
        return "multi-reference"
    if image_count == 1:
        return "image"
    return "text"


def _mode_prefix(mode: str, image_count: int, video_count: int) -> str:
    if mode == "image":
        if image_count < 1:
            _warn("image mode usually needs one image reference")
        return "Mode: image-to-video. Use the attached image as the source or starting visual frame. "
    if mode == "multi-reference":
        if image_count < 1:
            _warn("multi-reference mode usually needs one or more images")
        return "Mode: multi-reference. Use all attached images as visual, character, product, style, or scene references. "
    if mode == "first-last":
        if image_count < 2:
            _warn("first-last mode usually needs two images")
        return "Mode: first-last-frame. Treat the first attached image as the first frame and the second as the final frame. "
    if mode == "video-reference":
        if video_count < 1:
            _warn("video-reference mode usually needs one reference video")
        return "Mode: video reference. Use the attached video for motion, rhythm, posture changes, and camera movement. "
    return ""


def _redact_body(body: dict) -> dict:
    safe = json.loads(json.dumps(body))
    for message in safe.get("messages", []):
        content = message.get("content", [])
        if not isinstance(content, list):
            continue
        for part in content:
            for media_key in ("image_url", "video_url"):
                media = part.get(media_key) if isinstance(part, dict) else None
                if isinstance(media, dict):
                    url = media.get("url", "")
                    if isinstance(url, str) and url.startswith("data:"):
                        media["url"] = f"<data-url {len(url)} chars>"
    return safe


def _download(url: str, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "shoploop-cli/3.0"})
    with OPENER.open(request, timeout=300) as response, open(path, "wb") as f:
        f.write(response.read())


def _finish(url: str, args, elapsed: int) -> None:
    result = {"url": url, "elapsed": elapsed}
    if args.download:
        try:
            _download(url, args.download)
            result["download"] = args.download
            print(f"[shoploop] saved -> {args.download}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            _die(f"download failed: {exc}")
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(url)


def _stream_response(body: dict, args) -> None:
    if not _key_is_configured():
        _die(NO_KEY_MESSAGE)
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        BASE + "/v1/chat/completions",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KEY}",
            "User-Agent": "shoploop-cli/3.0",
            "Accept": "text/event-stream",
        },
    )
    started = time.time()
    text = ""
    try:
        with OPENER.open(request, timeout=1200) as response:
            raw_body = b""
            for raw in response:
                line = raw.decode("utf-8", "replace").strip()
                raw_body += raw
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and obj.get("error"):
                    _die(f"gateway error: {obj['error']}")
                for choice in obj.get("choices") or []:
                    delta = choice.get("delta") or {}
                    piece = delta.get("content") or ""
                    if piece:
                        text += piece
                        print(f"[shoploop]   [{int(time.time() - started)}s] rendering...", file=sys.stderr)
            if not text and raw_body:
                try:
                    obj = json.loads(raw_body.decode("utf-8", "replace"))
                    text = json.dumps(obj, ensure_ascii=False)
                except json.JSONDecodeError:
                    pass
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:500].decode("utf-8", "replace")
        if exc.code == 401:
            _die("HTTP 401 - the Shoploop API key is missing or invalid. " + NO_KEY_MESSAGE)
        if exc.code in (402, 403):
            _die(f"HTTP {exc.code} - Shoploop account permission or balance problem: {detail}")
        if exc.code == 429:
            _die("HTTP 429 - too many requests. Wait briefly and retry.")
        _die(f"HTTP {exc.code}: {detail}")
    except Exception as exc:  # noqa: BLE001
        _die(f"request failed: {exc}")

    match = URL_RE.search(text)
    if not match:
        _die(f"no video URL in response: {text[:240]!r}")
    _finish(match.group(0), args, round(time.time() - started))


def main() -> None:
    parser = argparse.ArgumentParser(prog="shoploop", description="Generate a video through Shoploop AI.")
    parser.add_argument("prompt", nargs="?", help="text prompt describing the video")
    parser.add_argument("--image", action=AppendReference, dest="refs", metavar="URL", help="reference image URL; repeatable")
    parser.add_argument("--image-file", action=AppendReference, dest="refs", metavar="PATH", help="local reference image file; repeatable")
    parser.add_argument("--video-url", action=AppendReference, dest="refs", metavar="URL", help="reference video URL")
    parser.add_argument("--video-file", action=AppendReference, dest="refs", metavar="PATH", help="local reference video file")
    parser.add_argument("--duration", type=int, default=5, metavar="SECONDS", help="video duration, 4-15 seconds")
    parser.add_argument("--mode", choices=("auto", "text", "image", "multi-reference", "video-reference", "first-last"), default="auto")
    parser.add_argument("--aspect-ratio", default=None, metavar="RATIO", help="canvas ratio, e.g. 9:16, 16:9, 1080x1920")
    parser.add_argument("--resolution", default=None, metavar="VALUE", help="output resolution, e.g. 1080p")
    parser.add_argument("--model", default=None, metavar="MODEL", help="public Shoploop model name; default seedance2.0")
    parser.add_argument("--download", default=None, metavar="PATH", help="also save the mp4 to this local path")
    parser.add_argument("--json", action="store_true", help="print JSON {url, elapsed, download?}")
    parser.add_argument("--dry-run", action="store_true", help="print the request body with local media redacted")
    parser.add_argument("--check-key", action="store_true", help="report whether SHOPLOOP_KEY is configured (never prints the key) and exit")
    args = parser.parse_args()

    if args.check_key:
        if _key_is_configured():
            print("[shoploop] SHOPLOOP_KEY: configured")
            return
        print(f"[shoploop] SHOPLOOP_KEY: not configured. {NO_KEY_MESSAGE}", file=sys.stderr)
        raise SystemExit(3)

    if not args.prompt:
        parser.error("prompt is required (or pass --check-key to only verify the key)")

    if args.duration is not None and not (MIN_DURATION <= args.duration <= MAX_DURATION):
        _die(f"duration must be between {MIN_DURATION}s and {MAX_DURATION}s")

    content = [{"type": "text", "text": args.prompt}]
    image_count = 0
    video_count = 0
    for kind, value in args.refs or []:
        if kind == "image-url":
            content.append({"type": "image_url", "image_url": {"url": value}})
            image_count += 1
        elif kind == "image-file":
            content.append({"type": "image_url", "image_url": {"url": _file_data_url(value, "image/jpeg")}})
            image_count += 1
        elif kind == "video-url":
            content.append({"type": "video_url", "video_url": {"url": value}})
            video_count += 1
        elif kind == "video-file":
            content.append({"type": "video_url", "video_url": {"url": _file_data_url(value, "video/mp4")}})
            video_count += 1

    mode = _detect_mode(args.prompt, args.mode, image_count, video_count)
    prefix = _mode_prefix(mode, image_count, video_count)
    if prefix:
        content[0]["text"] = prefix + content[0]["text"]

    body = {
        "model": args.model or MODEL,
        "stream": True,
        "messages": [{"role": "user", "content": content}],
        "duration": args.duration,
    }
    ratio = _normalize_aspect_ratio(args.aspect_ratio)
    if ratio:
        body["aspect_ratio"] = ratio
    if args.resolution:
        body["resolution"] = args.resolution

    if args.dry_run:
        print(json.dumps(_redact_body(body), ensure_ascii=False, indent=2))
        return

    if not _key_is_configured():
        _die(NO_KEY_MESSAGE)

    print(f"[shoploop] submitting ({mode}) to {BASE} - rendering, usually a few minutes...", file=sys.stderr)
    _stream_response(body, args)


if __name__ == "__main__":
    main()
