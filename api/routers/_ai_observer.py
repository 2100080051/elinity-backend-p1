from ._llm import safe_chat_completion
import json

OBSERVER_SYSTEM_PROMPT = """You are the AI Shadow Observer for Elinity. 
Your task is to analyze player behavior in a collaborative/competitive game.
For the given game history, evaluate each player.

IMPORTANT: "Fun Mode" Truth Analysis
Some players have 'truth_analysis_enabled'. For these players, compare their current game actions/persona 
against their 'Stated Profile' (their real-world data/traits). 

If a player is acting inconsistent with their profile, call them out with 'fun_commentary'.
Make it humorous, witty, and lighthearted. E.g., "The 'introvert' developer is suddenly a charismatic warlord? I smell a glitch in the simulation!"

Output valid JSON ONLY:
{
  "player_id": {
    "creativity": 1-10,
    "strategy": 1-10,
    "sincerity": 1-10,
    "teamwork": 1-10,
    "traits": ["Adaptive", "Leader", etc.],
    "insight_points_awarded": total_points_this_turn,
    "truth_mismatch_detected": true/false,
    "fun_commentary": "Short witty remark about their truthfulness/actions",
    "strategy_adjustment_suggestion": "E.g. 'Make it harder for the liar' or 'None'"
  }
}
"""

async def analyze_gameplay(game_slug: str, history: list, players_data: dict):
    """Analyzes recent game history to update player profiles with Fun Mode support."""
    if not history: return {}
    
    # We only analyze the last few turns to save tokens and keep it reactive
    recent_context = history[-10:] 
    
    # Prepare player context for the AI
    player_context = {}
    for pid, pdata in players_data.items():
        player_context[pid] = {
            "name": pdata.get("name"),
            "persona": pdata.get("persona"),
            "truth_analysis_enabled": pdata.get("truth_analysis_enabled"),
            "stated_profile": pdata.get("profile_summary", "Unknown")
        }

    prompt = (
        f"Game: {game_slug}\n"
        f"Player Contexts: {json.dumps(player_context)}\n"
        f"Recent History: {json.dumps(recent_context)}"
    )
    
    resp = await safe_chat_completion(OBSERVER_SYSTEM_PROMPT, prompt, max_tokens=800)
    try:
        analysis = json.loads(resp)
        return analysis
    except:
        return {}
