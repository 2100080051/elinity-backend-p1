from pathlib import Path
from typing import Optional
import os
import re


def load_system_prompt(game_slug: str, default: Optional[str] = "") -> str:
    """Locate and return a game's system prompt.

    Search order:
    1. <workspace_root>/elinity game suite/elinity game suite/<game_slug>/public/system_prompt.txt
    2. <workspace_root>/elinity game suite/<game_slug>/public/system_prompt.txt
    3. <workspace_root>/public/system_prompt.txt
    4. cwd()/public/system_prompt.txt
    5. return the provided default

    The function is defensive and returns the default if nothing is found or readable.
    """
    try:
        # workspace root is up 3 levels from this file (api/routers -> python_elinity-main -> elinity-combined)
        workspace_root = Path(__file__).resolve().parents[3]
    except Exception:
        workspace_root = Path.cwd()

    # 1) environment override: SYSTEM_PROMPT_<SLUG>
    slug_key = re.sub(r"[^A-Za-z0-9]", "_", game_slug).upper()
    env_key = f"SYSTEM_PROMPT_{slug_key}"
    if os.getenv(env_key):
        return os.getenv(env_key)

    # 2) bundled backend prompts folder (python_elinity-main/prompts/<slug>/system_prompt.txt)
    try:
        backend_root = Path(__file__).resolve().parents[2]
        bundled = backend_root / 'prompts' / game_slug / 'system_prompt.txt'
        if bundled.exists():
            return bundled.read_text(encoding='utf-8')
    except Exception:
        pass

    candidates = [
        workspace_root / 'elinity game suite' / 'elinity game suite' / game_slug / 'public' / 'system_prompt.txt',
        workspace_root / 'elinity game suite' / game_slug / 'public' / 'system_prompt.txt',
        workspace_root / 'public' / 'system_prompt.txt',
        Path.cwd() / 'public' / 'system_prompt.txt',
    ]

    for p in candidates:
        try:
            if p.exists():
                return p.read_text(encoding='utf-8')
        except Exception:
            # ignore and continue to next candidate
            continue

    return default or ""
