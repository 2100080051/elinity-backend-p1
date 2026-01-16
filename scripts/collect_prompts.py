#!/usr/bin/env python3
"""Collect system_prompt.txt files from the workspace game-suite and copy into
python_elinity-main/prompts/<game-slug>/system_prompt.txt

Usage: run from anywhere; it will try to infer workspace root relative to this file.
"""
from pathlib import Path
import shutil
import sys


def find_workspace_root() -> Path:
    # This script lives in python_elinity-main/scripts; go up two levels to reach workspace root
    p = Path(__file__).resolve()
    # python_elinity-main/scripts -> python_elinity-main -> workspace_root
    return p.parents[2]


def collect_prompts():
    root = find_workspace_root()
    src_candidates = list(root.rglob('**/system_prompt.txt'))
    out_base = root / 'python_elinity-main' / 'prompts'
    out_base.mkdir(parents=True, exist_ok=True)

    copied = []
    for src in src_candidates:
        # ignore any prompts already inside backend prompts folder
        try:
            if 'python_elinity-main' in [p.name for p in src.parts]:
                continue
        except Exception:
            pass

        # try to detect game slug: look for parent 'public' then its parent
        parent = src.parent
        slug = None
        if parent.name.lower() == 'public' and parent.parent:
            slug = parent.parent.name
        else:
            # fallback: use immediate parent folder name
            slug = parent.name

        # sanitize slug for filesystem
        slug_safe = slug.replace(' ', '-').lower()
        dest_dir = out_base / slug_safe
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / 'system_prompt.txt'
        try:
            shutil.copy2(str(src), str(dest_file))
            copied.append((str(src), str(dest_file)))
        except Exception as e:
            print(f"Failed to copy {src} -> {dest_file}: {e}")

    # Summary
    print(f"Found {len(src_candidates)} candidate system_prompt.txt files in workspace")
    print(f"Copied {len(copied)} prompts into {out_base}")
    for s, d in copied:
        print(f" - {s} -> {d}")

    if len(copied) == 0:
        print("No prompts copied. Ensure the game-suite exists in the workspace and contains public/system_prompt.txt files.")


if __name__ == '__main__':
    collect_prompts()
