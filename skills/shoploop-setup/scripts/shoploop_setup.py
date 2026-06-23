#!/usr/bin/env python3
"""Install and check the Shoploop Codex skill set."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_SKILLS = ("shoploop-video", "shoploop-setup")
OPTIONAL_SKILLS = ("shoploop-reseller",)
SHOPLOOP_GITIGNORE_BLOCK = ("# Shoploop", ".env.shoploop", "shoploop_outputs/")


def _skill_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _source_parent() -> Path:
    return _skill_root_from_script().parent


def _copy_skill(src: Path, dst: Path) -> bool:
    if not src.exists():
        raise SystemExit(f"missing source skill: {src}")
    if src.resolve() == dst.resolve():
        print(f"[shoploop-setup] {src.name} already installed at {dst}")
        return False

    def ignore(_dir, names):
        return {n for n in names if n in {"__pycache__", ".DS_Store"} or n.endswith(".pyc")}

    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)
    return True


def install(target_parent: Path) -> None:
    target_parent.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_SKILLS + OPTIONAL_SKILLS:
        src = _source_parent() / name
        if not src.exists() and name in OPTIONAL_SKILLS:
            print(f"[shoploop-setup] optional skill {name}: not included")
            continue
        if _copy_skill(src, target_parent / name):
            print(f"[shoploop-setup] installed {name} -> {target_parent / name}")


def _load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def ensure_env(project: Path) -> Path:
    path = project / ".env.shoploop"
    if not path.exists():
        template = _source_parent() / "shoploop-video" / "assets" / "env.shoploop.example"
        path.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[shoploop-setup] created template {path}")
    else:
        print(f"[shoploop-setup] found {path}")
    return path


def ensure_gitignore(project: Path) -> None:
    """Idempotently append a small Shoploop block to the project .gitignore.

    Never overwrites the customer's existing .gitignore; only adds the lines
    that are missing, and never the broad media globs that v1 shipped.
    """
    path = project / ".gitignore"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    existing = {line.strip() for line in text.splitlines()}
    to_add = [line for line in SHOPLOOP_GITIGNORE_BLOCK if line not in existing]
    if "# Shoploop" in existing:
        to_add = [line for line in to_add if line != "# Shoploop"]
    if not to_add:
        print("[shoploop-setup] .gitignore already has Shoploop entries")
        return
    sep = "" if (not text or text.endswith("\n")) else "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(sep + "\n".join(to_add) + "\n")
    print(f"[shoploop-setup] updated {path}")


def check(project: Path, skill_parent: Path | None = None) -> int:
    skill_parent = skill_parent or project / ".agents" / "skills"
    ok = True
    print(f"[shoploop-setup] Python: {sys.version.split()[0]}")
    for name in REQUIRED_SKILLS:
        exists = (skill_parent / name / "SKILL.md").exists()
        print(f"[shoploop-setup] skill {name}: {'ok' if exists else 'missing'}")
        ok = ok and exists
    for name in OPTIONAL_SKILLS:
        exists = (skill_parent / name / "SKILL.md").exists()
        print(f"[shoploop-setup] optional skill {name}: {'present' if exists else 'not included'}")

    cli = skill_parent / "shoploop-video" / "scripts" / "shoploop.py"

    # Resolve "configured" exactly the way the video CLI does so setup and the
    # actual generate path can never disagree (e.g. an empty/whitespace
    # SHOPLOOP_KEY exported in the shell must not look "set" here while the CLI
    # refuses to render). Prefer the CLI itself as the single source of truth;
    # fall back to an equivalent inline check (non-empty env wins, else file).
    if cli.exists():
        kr = subprocess.run(
            [sys.executable, str(cli), "--check-key"],
            cwd=str(project),
            text=True,
            capture_output=True,
            timeout=30,
        )
        key_set = kr.returncode == 0
    else:
        env_values = _load_env(project / ".env.shoploop")
        env_var = (os.environ.get("SHOPLOOP_KEY") or "").strip()
        key = env_var or env_values.get("SHOPLOOP_KEY", "").strip()
        key_set = bool(key and key != "sk-your-customer-key")
    print(f"[shoploop-setup] SHOPLOOP_KEY: {'set' if key_set else 'unset'}")
    if not key_set:
        ok = False

    if cli.exists():
        result = subprocess.run(
            [sys.executable, str(cli), "setup dry run", "--dry-run"],
            cwd=str(project),
            text=True,
            capture_output=True,
            timeout=30,
        )
        print(f"[shoploop-setup] video CLI dry-run: {'ok' if result.returncode == 0 else 'failed'}")
        if result.returncode != 0:
            print((result.stderr or result.stdout).strip())
            ok = False
    else:
        print(f"[shoploop-setup] video CLI: not found at {cli}")
        ok = False
    return 0 if ok else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Install/check Shoploop Codex skills.")
    parser.add_argument("--project", default=None, help="project directory for .agents/skills and .env.shoploop")
    parser.add_argument("--global", dest="global_install", action="store_true", help="install to ~/.agents/skills")
    parser.add_argument("--target", default=None, help="custom target skills directory")
    parser.add_argument("--check", action="store_true", help="run setup checks after installing")
    parser.add_argument("--env", action="store_true", help="create .env.shoploop template in the project")
    args = parser.parse_args()

    project = Path(args.project or os.getcwd()).resolve()
    if args.target:
        installed_parent = Path(args.target).expanduser().resolve()
    elif args.global_install:
        installed_parent = Path.home() / ".agents" / "skills"  # official user scope; ~/.codex/skills also works
    else:
        installed_parent = project / ".agents" / "skills"
    install(installed_parent)

    if args.env or args.check:
        ensure_env(project)
        ensure_gitignore(project)
    if args.check:
        raise SystemExit(check(project, installed_parent))


if __name__ == "__main__":
    main()
