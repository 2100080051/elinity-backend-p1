# app.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from middleware.auth_middleware import AdminAuthMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
import importlib
import logging

# Defensive router imports: some routers initialize external clients at import-time
# (Firebase, AssemblyAI, Milvus, etc.). To make local/dev boots reliable we
# attempt to import each router individually and continue on failure. Set
# SKIP_HEAVY_IMPORTS=1 in the env to prefer skipping optional heavy routers.

_ROUTER_MODULES = [
    'auth',
    'users',
    'journal',
    'social_feed',
    'ai_modes',
    'events',
    'admin_panel',
    'chats',
    'groups',
    'members',
    'question_cards',
    'lumi',
    'skill_evaluation',
    'billing',
    'search',
    'tools',
    'recommendations',
    'notifications',
    'upload_file',
    'upload_file',
    'user_dashboard',
    'blogs',
    'connections',
    'lifebook',
    'multimodal',
    # Games
    'games_ai_adventure_dungeon',
    'games_ai_comic_creator',
    'games_ai_emoji_war',
    'games_ai_escape_room',
    'games_ai_fortune_teller',
    'games_ai_improv_theater',
    'games_ai_poetry_garden',
    'games_ai_puzzle_architect',
    'games_ai_puzzle_saga',
    'games_ai_rap_battle',
    'games_ai_roast_toast',
    'games_ai_role_swap',
    'games_ai_sandbox',
    'games_character_swap',
    'games_collaborative_canvas',
    'games_connection_sparks',
    'games_creative_duel_arena',
    'games_cultural_exchange',
    'games_dream_battles',
    'games_dream_builder',
    'games_emotion_charades',
    'games_emotion_labyrinth_node',
    'games_epic_poem_duel',
    'games_friendship_towers',
    'games_future_artifact_maker',
    'games_future_forecast',
    'games_gratitude_quest',
    'games_great_debate',
    'games_guess_the_fake',
    'games_hidden_truths',
    'games_inner_world_quest',
    'games_journey_journal',
    'games_journey_through_music',
    'games_legacy_builder',
    'games_life_goals_board_game',
    'games_life_swap_simulator',
    'games_meme_forge',
    'games_memory_match_maker',
    'games_micro_mysteries',
    'games_mind_meld',
    'games_mood_dj',
    'games_mood_journey',
    'games_mood_mosaic',
    'games_myth_builder',
    'games_mythic_beast_builder',
    'games_relationship_rpg',
    'games_serendipity_hunt',
    'games_shared_playlist_maker',
    'games_social_labyrinth',
    'games_story_relay',
    'games_symbol_quest',
    'games_the_ai_heist',
    'games_the_alignment_game',
    'games_the_hidden_question',
    'games_the_long_journey',
    'games_time_travelers',
    'games_truth_arcade',
    'games_truth_timeline',
    'games_value_compass',
    'games_the_story_weaver',
    'games_truth_and_layer',
    'games_world_builders',
    'games_memory_mosaic',
    'games_myth_maker_arena',
    'game_multiplayer',
    'games_the_compass_game',
    'games_echoes_and_expressions',
    'games_serendipity_strings',
    'games_the_long_quest',
]

_IMPORTED = {}
_IMPORT_ERRORS = {}
# Default to skipping heavy imports to make local/dev boots reliable unless
# explicitly disabled. Set SKIP_HEAVY_IMPORTS=0 to enable heavy modules.
SKIP_HEAVY = os.getenv('SKIP_HEAVY_IMPORTS', '0') not in ('0', 'false', 'no')
for mod_name in _ROUTER_MODULES:
    try:
        _IMPORTED[mod_name] = importlib.import_module(f"api.routers.{mod_name}")
    except Exception as e:
        error_msg = f"Optional router api.routers.{mod_name} failed to import: {e}"
        logging.getLogger(__name__).warning(error_msg)
        _IMPORT_ERRORS[mod_name] = str(e)
        _IMPORTED[mod_name] = None

# ... (Rest of file) ...

# ... removed from here ...

# Expose imported modules as variables (e.g. auth, users, ...) expected later in the file
globals().update(_IMPORTED)
dashboard_app = None
login = None
try:
    from dashboard.routers import app as dashboard_app, login
except Exception as e:
    logging.getLogger(__name__).warning(f"Dashboard routers failed to import: {e}")

websocket = None
onboarding = None
group_chat = None
# Emergency disable:
if not SKIP_HEAVY:
    try:
        from api.routers.websockets import websocket, onboarding, group_chat
    except Exception as e:
        logging.getLogger(__name__).warning(f"Websocket routers failed to import: {e}")

internal_users_router = None
try:
    from api.routers.internal_users import router as internal_users_router
except Exception as e:
    logging.getLogger(__name__).warning(f"Internal users router failed to import: {e}")
voice_onboarding = None
voice_onboarding_save = None
# Emergency disable:
try:
    from api.routers import voice_onboarding as _voice_onboarding, voice_onboarding_save as _voice_onboarding_save
    voice_onboarding = _voice_onboarding
    voice_onboarding_save = _voice_onboarding_save
except Exception:
    pass
#     except Exception:
#         # If optional dependencies (like speech_recognition) are missing or something else fails,
#         # don't prevent the app from starting. The endpoints will be unavailable until dependencies are installed.
#         import logging
#         logging.getLogger(__name__).warning("Voice onboarding routers not loaded (optional). Install audio dependencies to enable them.")
from fastapi.responses import HTMLResponse
from database.session import engine, Base
import time
from sqlalchemy.exc import OperationalError
from core.limiter import RateLimiter
# Ensure DB models that are not auto-imported get registered
try:
    import models.service_key  # registers ServiceKey on Base.metadata
except Exception:
    pass

limiter = RateLimiter(requests=5, window=60)

import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    # Try to create tables but tolerate transient DB connection/SSL failures.
    # This prevents the whole app from exiting when the DB provider temporarily
    # refuses connections (SSL handshake/allowlist issues). We retry a few times
    # with exponential backoff and log clear diagnostic messages.
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError as e:
            attempt += 1
            wait = min(30, 2 ** attempt)
            logging.getLogger(__name__).error(
                "Database initialization failed (attempt %d/%d): %s. Retrying in %ds",
                attempt, max_attempts, e, wait,
            )
            time.sleep(wait)
    else:
        logging.getLogger(__name__).error(
            "Database initialization failed after %d attempts; continuing without DB. "
            "Ensure DB is reachable, allowlisted, and SSL settings are correct.",
            max_attempts,
        )

    # --- EMERGENCY MIGRATION FOR P1 ---
    # Since we added a column to an existing table without Alembic, we must force it.
    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            # Check if column exists (Postgres specific simpler way: just try adding and ignore error)
            try:
                # Attempt to add the column. If it exists, this will fail safely.
                # Using 'JSON' type which is compatible.
                conn.execute(text("ALTER TABLE tenants ADD COLUMN connection_preferences JSON DEFAULT '{}'"))
                logging.getLogger(__name__).info("✅ Successfully added 'connection_preferences' column to tenants.")
            except Exception as e:
                # Allow failure if column exists
                logging.getLogger(__name__).info(f"Skipping migration (column likely exists): {e}")
    except Exception as e:
         logging.getLogger(__name__).error(f"Migration Check Failed: {e}")
    # ----------------------------------

    # Seed database with fake data if empty
    # subprocess.run(["python", "scripts/seed_db.py"], check=True)
    yield
    # Optional: drop tables on shutdown
    # Base.metadata.drop_all(bind=engine)


# Initialize the application with lifespan
# Include routers dynamically and only if the module imported successfully.
_INCLUDES = [
    ('/auth', 'auth'),
    ('/users', 'users'),
    ('/upload-file', 'upload_file'),
    ('/assets', 'assets'),
    ('/chats', 'chats'),
    ('/groups', 'groups'),
    ('/members', 'members'),
    ('/journal', 'journal'),
    ('/websocket', 'websocket'),
    ('/onboarding', 'voice_onboarding'),
    ('/multimodal', 'multimodal'),
    ('/room', 'group_chat'),
    ('/notifications', 'notifications'),
    ('/plans', 'plans'),
    ('/blogs', 'blogs'),
    ('/recommendations', 'recommendations'),
    ('/lumi', 'lumi'),
    ('/questions', 'question_cards'),
    ('/events', 'events'),
    ('/feed', 'social_feed'),
    ('/tools', 'tools'),
    ('/lifebook', 'lifebook'),
    ('/dashboard', 'user_dashboard'),
    ('/admin-panel', 'admin_panel'),
    ('/billing', 'billing'),
    ('/search', 'search'),
    ('/ai-mode', 'ai_modes'),
    ('/upload', 'upload_file'),
    ('/admin/blogs', 'blogs'),
    ('/games/multiplayer', 'game_multiplayer'),
    ('/games/value-compass', 'games_value_compass'),
    ('/games/mood-journey', 'games_mood_journey'),
    ('/games/truth-arcade', 'games_truth_arcade'),
    ('/games/time-travelers', 'games_time_travelers'),
    ('/games/the-long-journey', 'games_the_long_journey'),
    ('/games/story-relay', 'games_story_relay'),
    ('/games/the-alignment-game', 'games_the_alignment_game'),
    ('/games/shared-playlist-maker', 'games_shared_playlist_maker'),
    ('/games/serendipity-hunt', 'games_serendipity_hunt'),
    ('/games/relationship-rpg', 'games_relationship_rpg'),
    ('/games/mood-mosaic', 'games_mood_mosaic'),
    ('/games/mood-dj', 'games_mood_dj'),
    ('/games/memory-match-maker', 'games_memory_match_maker'),
    ('/games/micro-mysteries', 'games_micro_mysteries'),
    ('/games/mind-meld', 'games_mind_meld'),
    ('/games/myth-builder', 'games_myth_builder'),
    ('/games/ai-adventure-dungeon', 'games_ai_adventure_dungeon'),
    ('/games/ai-comic-creator', 'games_ai_comic_creator'),
    ('/games/ai-emoji-war', 'games_ai_emoji_war'),
    ('/games/ai-escape-room', 'games_ai_escape_room'),
    ('/games/ai-fortune-teller', 'games_ai_fortune_teller'),
    ('/games/ai-improv-theater', 'games_ai_improv_theater'),
    ('/games/ai-oracle', 'games_ai_oracle'),
    ('/games/ai-poetry-garden', 'games_ai_poetry_garden'),
    ('/games/ai-puzzle-architect', 'games_ai_puzzle_architect'),
    ('/games/ai-puzzle-saga', 'games_ai_puzzle_saga'),
    ('/games/ai-rap-battle', 'games_ai_rap_battle'),
    ('/games/ai-roast-toast', 'games_ai_roast_toast'),
    ('/games/ai-role-swap', 'games_ai_role_swap'),
    ('/games/character-swap', 'games_character_swap'),
    ('/games/collaborative-canvas', 'games_collaborative_canvas'),
    ('/games/connection-sparks', 'games_connection_sparks'),
    ('/games/creative-duel-arena', 'games_creative_duel_arena'),
    ('/games/cultural-exchange', 'games_cultural_exchange'),
    ('/games/dream-battles', 'games_dream_battles'),
    ('/games/dream-builder', 'games_dream_builder'),
    ('/games/emotion-charades', 'games_emotion_charades'),
    ('/games/emotion-labyrinth', 'games_emotion_labyrinth'),
    ('/games/epic-poem-duel', 'games_epic_poem_duel'),
    ('/games/friendship-towers', 'games_friendship_towers'),
    ('/games/future-artifact-maker', 'games_future_artifact_maker'),
    ('/games/future-forecast', 'games_future_forecast'),
    ('/games/gratitude-quest', 'games_gratitude_quest'),
    ('/games/great-debate', 'games_great_debate'),
    ('/games/guess-the-fake', 'games_guess_the_fake'),
    ('/games/hidden-truths', 'games_hidden_truths'),
    ('/games/inner-world-quest', 'games_inner_world_quest'),
    ('/games/journey-journal', 'games_journey_journal'),
    ('/games/journey-through-music', 'games_journey_through_music'),
    ('/games/legacy-builder', 'games_legacy_builder'),
    ('/games/life-goals-board-game', 'games_life_goals_board_game'),
    ('/games/life-swap-simulator', 'games_life_swap_simulator'),
    ('/games/meme-forge', 'games_meme_forge'),
    ('/games/social-labyrinth', 'games_social_labyrinth'),
    ('/games/symbol-quest', 'games_symbol_quest'),
    ('/games/the-ai-heist', 'games_the_ai_heist'),
    ('/games/ai-sandbox', 'games_ai_sandbox'),
    ('/games/the-great-debate', 'games_the_great_debate'),
    ('/games/the-hidden-question', 'games_the_hidden_question'),
    ('/games/truth-timeline', 'games_truth_timeline'),
    ('/games/mythic-beast-builder', 'games_mythic_beast_builder'),
    ('/games/the-story-weaver', 'games_the_story_weaver'),
    ('/games/truth-and-layer', 'games_truth_and_layer'),
    ('/games/world-builders', 'games_world_builders'),
    ('/games/memory-mosaic', 'games_memory_mosaic'),
    ('/games/myth-maker-arena', 'games_myth_maker_arena'),
    ('/games/the-compass-game', 'games_the_compass_game'),
    ('/games/echoes-and-expressions', 'games_echoes_and_expressions'),
    ('/games/serendipity-strings', 'games_serendipity_strings'),
    ('/games/the-long-quest', 'games_the_long_quest'),
    ('/p1', 'connections')
]

# Create the FastAPI app instance before including routers so `app` is always defined.
# Keep this lightweight so import-time doesn't trigger heavy subsystems.
app = FastAPI(lifespan=lifespan, title=os.getenv("APP_NAME", "elinity-backend"))

# Basic CORS middleware (override with CORS_ALLOW_ORIGINS env as comma-separated list)
cors_env = os.getenv("CORS_ALLOW_ORIGINS")
allow_origins = cors_env.split(",") if cors_env else ["*"]
# Force add the main frontend domain just in case
allow_origins.append("https://elinity-the-story-weaver-docker.azurewebsites.net")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware with fallback secret
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-secret"))

# Mount static files if present
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

for prefix, varname in _INCLUDES:
    mod = globals().get(varname)
    if mod and hasattr(mod, 'router'):
        try:
            app.include_router(prefix=prefix, router=mod.router)
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to include router {varname} at {prefix}: {e}")

if voice_onboarding and hasattr(voice_onboarding, 'router'):
    app.include_router(router=voice_onboarding.router)
if voice_onboarding_save and hasattr(voice_onboarding_save, 'router'):
    app.include_router(prefix='/voice', router=voice_onboarding_save.router)

# The remaining game routers are included dynamically above in the
# _INCLUDES loop; avoid re-including them here to prevent NameError when
# optional routers failed to import.

# Include dashboard router with /admin prefix
# Include dashboard router with /admin prefix
if dashboard_app:
    app.include_router(
        dashboard_app.router,
        prefix="/admin",
        tags=["dashboard"]
    )

# Include login routes with /admin/auth prefix
if login:
    app.include_router(
        login.router,
        prefix="/admin/auth",
        tags=["auth"]
    )

# Internal endpoints for service integrations
if internal_users_router:
    app.include_router(internal_users_router)


@app.get("/debug/imports")
async def debug_imports():
    """Debug endpoint to list loaded modules and import errors."""
    return {
        "loaded": [k for k, v in _IMPORTED.items() if v is not None],
        "errors": _IMPORT_ERRORS,
        "routes": [route.path for route in app.routes]
    }

@app.get("/", response_class=HTMLResponse)
async def root(rate_limited: bool = Depends(limiter)):
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    """Simple health endpoint used by probes."""
    return {"status": "ok"}

from api.routers import relationship_skills
app.include_router(relationship_skills.router, prefix="/relationship-skills", tags=["relationship-skills"])
from api.routers import self_growth_skills
app.include_router(self_growth_skills.router, prefix="/self-growth", tags=["self-growth"])
from api.routers import social_skills
app.include_router(social_skills.router, prefix="/social", tags=["social-growth"])
from api.routers import skill_evaluation
app.include_router(skill_evaluation.router, prefix="/evaluate", tags=["evaluation"])
