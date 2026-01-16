import os
import re
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path("c:/Users/nabhi/Downloads/python_elinity-main2")
GAMES_ROOT = WORKSPACE_ROOT / "elinity game suite"
BACKEND_ROOT = WORKSPACE_ROOT / "python_elinity-main"
ROUTERS_DIR = BACKEND_ROOT / "api/routers"

# Templates
BACKEND_TEMPLATE = """from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class StartReq(BaseModel):
    user_id: Optional[str] = "anon"
    theme: Optional[str] = "DEFAULT"

class JoinReq(BaseModel):
    session_id: str
    user_id: str
    role: Optional[str] = "Player"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

class ChatReq(BaseModel):
    session_id: str
    user_id: str
    message: str

@router.post('/start')
async def start(req: StartReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    slug = '{{GAME_SLUG}}' 
    system = load_system_prompt(slug)
    
    prompt = f'Generate an opening scene for {req.theme} in 2-3 sentences.'
    fallback = 'The game begins.'
    opening_text = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=200, fallback=fallback)
    
    initial_state = {
        "scene": opening_text, 
        "theme": req.theme,
        "turn": 1,
        "status": "active",
        "chat_messages": []
    }
    
    session = gm.create_session(game_slug=slug, host_id=req.user_id, initial_state=initial_state)
    gm.join_session(session.session_id, req.user_id, {"role": "Host", "joined_at": "now"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state, 'players': session.players}

@router.post('/join')
async def join(req: JoinReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.join_session(req.session_id, req.user_id, {"role": req.role})
    return {'ok': True, 'players': session.players, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.get_session(req.session_id)
    
    slug = '{{GAME_SLUG}}'
    system = load_system_prompt(slug)
    
    current_scene = session.state.get("scene", "")
    prompt = f"Current Scene: {current_scene}\\nPlayer ({req.user_id}) Action: {req.action}\\nNarrate outcome."
    fallback = f"You {req.action}."
    new_scene = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=300, fallback=fallback)
    
    new_state = {
        "scene": new_scene,
        "last_action": req.action,
        "turn": session.state.get("turn", 0) + 1
    }
    
    updated_session = gm.update_state(
        req.session_id, 
        new_state, 
        history_entry={"role": "user", "content": req.action, "user_id": req.user_id, "response": new_scene}
    )
    
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.post('/chat')
async def chat(req: ChatReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.get_session(req.session_id)
    
    messages = list(session.state.get("chat_messages", []))
    new_msg = {
        "user_id": req.user_id,
        "message": req.message,
        "timestamp": "now"
    }
    messages.append(new_msg)
    
    if len(messages) > 50: messages = messages[-50:]
    
    updated_session = gm.update_state(req.session_id, {"chat_messages": messages})
    return {'ok': True, 'chat_messages': updated_session.state.get("chat_messages")}

@router.get('/status/{session_id}')
async def status(session_id: str, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.get_session(session_id)
    return {'ok': True, 'state': session.state, 'players': session.players, 'history': session.history}
"""

FRONTEND_TEMPLATE = """import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Send, MessageSquare, Users, Home, Share2, ChevronRight } from 'lucide-react';

const THEME = {{THEME_JSON}}; 
const BG_PROMPT = "{{BG_PROMPT}}";
const GAME_TITLE = "{{GAME_TITLE}}";

const API_BASE = process.env.NEXT_PUBLIC_P1_BACKEND_URL ? `${process.env.NEXT_PUBLIC_P1_BACKEND_URL}/games/{{GAME_SLUG}}` : "http://localhost:8000/games/{{GAME_SLUG}}"; 

export default function Game() {
  const router = useRouter();
  const [story, setStory] = useState([]);
  const [players, setPlayers] = useState({});
  const [chatMessages, setChatMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [input, setInput] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userId, setUserId] = useState(`Player_${Math.floor(Math.random() * 1000)}`);
  const scrollRef = useRef(null);
  const chatScrollRef = useRef(null);

  const scrollToBottom = () => scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  const scrollChatToBottom = () => chatScrollRef.current?.scrollIntoView({ behavior: "smooth" });

  useEffect(scrollToBottom, [story]);
  useEffect(scrollChatToBottom, [chatMessages]);

  useEffect(() => {
    if (router.isReady) {
      const { session_id } = router.query;
      if (session_id) {
        setSessionId(session_id);
        joinSession(session_id);
      }
    }
  }, [router.isReady, router.query]);

  useEffect(() => {
    if (!sessionId) return;
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/status/${sessionId}`);
        if (res.data.ok) {
           setPlayers(res.data.players || {});
           setChatMessages(res.data.state.chat_messages || []);
           
           if (res.data.history && res.data.history.length > 0) {
              const newStory = [];
              res.data.history.forEach(h => {
                  newStory.push({role: h.role, content: h.content || h.response, user_id: h.user_id});
                  if (h.response && h.response !== h.content) {
                      newStory.push({role: 'ai', content: h.response});
                  }
              });
              setStory(newStory);
           } else if (res.data.state.scene && story.length === 0) {
               setStory([{role: 'ai', content: res.data.state.scene}]);
           }
        }
      } catch (e) {}
    }, 3000); 
    return () => clearInterval(interval);
  }, [sessionId, story.length]);

  const joinSession = async (sid) => {
      setLoading(true);
      try {
          const res = await axios.post(`${API_BASE}/join`, { session_id: sid, user_id: userId });
          if (res.data.ok) {
             setPlayers(res.data.players);
             setChatMessages(res.data.state.chat_messages || []);
          }
      } catch (e) {}
      setLoading(false);
  };

  const createGame = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/start`, { user_id: userId });
      if (res.data.ok) {
          const sid = res.data.session_id;
          setSessionId(sid);
          setPlayers(res.data.players);
          setStory([{ role: 'ai', content: res.data.state.scene }]);
          router.push(`/?session_id=${sid}`, undefined, { shallow: true });
      }
    } catch (e) {}
    setLoading(false);
  };

  const send = async (e) => {
    e.preventDefault();
    if (!input || !sessionId) return;
    const userMsg = input;
    setInput('');
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/action`, { 
        session_id: sessionId,
        user_id: userId,
        action: userMsg 
      });
    } catch (e) {}
    setLoading(false);
  };

  const sendChat = async (e) => {
    e.preventDefault();
    if (!chatInput || !sessionId) return;
    const msg = chatInput;
    setChatInput('');
    try {
        await axios.post(`${API_BASE}/chat`, {
            session_id: sessionId,
            user_id: userId,
            message: msg
        });
    } catch (e) {}
  };

  const copyLink = () => {
      navigator.clipboard.writeText(window.location.href);
      alert("Link copied!");
  };

  return (
    <div className={`min-h-screen text-white font-sans selection:bg-white/30 overflow-hidden ${THEME.bg}`}>
       <div className="fixed inset-0 opacity-30 pointer-events-none" style={{
          backgroundImage: `url(https://image.pollinations.ai/prompt/${BG_PROMPT}?nologo=true)`, 
          backgroundSize: 'cover', backgroundPosition: 'center'
      }}></div>
      <div className="fixed inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/80 pointer-events-none" />

      <div className="max-w-6xl mx-auto p-4 md:p-8 relative z-10 flex flex-col h-screen">
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-6">
            <button onClick={() => window.location.href = "/"} className="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all">
                <Home size={20} className="text-gray-400 hover:text-white" />
            </button>
            <div>
                <h1 className={`text-2xl md:text-4xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r ${THEME.gradient}`}>
                {GAME_TITLE}
                </h1>
                <p className="text-[10px] opacity-40 tracking-[0.3em] uppercase mt-1 px-1">
                    {sessionId ? `Live Session: ${sessionId.substring(0,8)}` : "AI Adventure Series"}
                </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
             {sessionId && (
                <>
                <div className="hidden md:flex items-center mr-4 -space-x-2">
                    {Object.values(players).map((p, i) => (
                        <div key={i} title={p.name || p.user_id} className="w-8 h-8 rounded-full border-2 border-black bg-white/10 flex items-center justify-center text-[10px] font-bold">
                            {(p.name || 'P')[0].toUpperCase()}
                        </div>
                    ))}
                </div>
                <button onClick={copyLink} className="bg-white/5 hover:bg-white/10 p-3 rounded-xl border border-white/10 transition-all text-gray-400">
                    <Share2 size={18} />
                </button>
                <button 
                  onClick={() => setShowChat(!showChat)} 
                  className={`p-3 rounded-xl border transition-all ${showChat ? 'bg-white text-black border-white' : 'bg-white/5 border-white/10 text-gray-400'}`}>
                    <MessageSquare size={18} />
                </button>
                </>
             )}
          </div>
        </header>

        <div className="flex-1 flex gap-6 overflow-hidden">
            <main className="flex-1 glass-card border flex flex-col overflow-hidden rounded-[2.5rem] shadow-2xl backdrop-blur-3xl bg-black/40 border-white/10 relative">
                {!sessionId ? (
                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-8">
                    <motion.div 
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="p-8 rounded-full bg-white/5 border border-white/10"
                    >
                        <Sparkles size={64} className="text-gold" />
                    </motion.div>
                    <div className="space-y-4">
                        <h2 className="text-4xl font-black tracking-tight">Step into the Void</h2>
                        <p className="text-gray-400 max-w-sm mx-auto">Collaborate with AI and friends to shape a unique destiny in this immersive realm.</p>
                    </div>
                    <div className="flex flex-col gap-4 w-full max-w-sm">
                        <input 
                            className="bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-center text-lg outline-none focus:border-white/30 transition-all font-medium"
                            placeholder="Enter your handle..."
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                        />
                        <button onClick={createGame} className="w-full py-5 rounded-2xl font-bold text-xl bg-white text-black hover:scale-[1.02] active:scale-[0.98] transition-all shadow-xl shadow-white/5">
                            Wake the AI
                        </button>
                    </div>
                </div>
                ) : (
                <>
                <div className="flex-1 overflow-y-auto p-8 md:p-12 space-y-12 custom-scrollbar">
                    {story.map((msg, i) => (
                        <motion.div 
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          key={i} 
                          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[85%] ${
                            msg.role === 'user' 
                            ? 'bg-white/10 rounded-2xl p-6 border border-white/10' 
                            : 'text-2xl md:text-3xl font-light leading-relaxed'
                        }`}>
                            {msg.role === 'user' && <div className="text-[10px] uppercase tracking-widest text-gray-500 mb-2">{msg.user_id}</div>}
                            <div className="whitespace-pre-wrap">{msg.content}</div>
                        </div>
                        </motion.div>
                    ))}
                    {loading && (
                        <div className="flex gap-2 p-6 bg-white/5 rounded-2xl w-fit animate-pulse">
                            <div className="w-2 h-2 rounded-full bg-white/20" />
                            <div className="w-2 h-2 rounded-full bg-white/20" />
                            <div className="w-2 h-2 rounded-full bg-white/20" />
                        </div>
                    )}
                    <div ref={scrollRef}></div>
                </div>

                <div className="p-6 md:p-8 bg-black/40 backdrop-blur-xl border-t border-white/5">
                    <form onSubmit={send} className="relative group">
                        <input 
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="What is your next move?"
                        disabled={loading}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl pl-8 pr-20 py-6 outline-none focus:bg-white/10 focus:border-white/30 transition-all text-xl font-light placeholder:text-gray-600"
                        />
                        <button 
                          type="submit" 
                          disabled={!input || loading} 
                          className="absolute right-4 top-1/2 -translate-y-1/2 p-4 rounded-xl font-bold bg-white text-black disabled:opacity-20 hover:scale-110 active:scale-95 transition-all shadow-lg"
                        >
                        <ChevronRight size={24} />
                        </button>
                    </form>
                </div>
                </>
                )}
            </main>

            <AnimatePresence>
                {showChat && (
                    <motion.aside 
                        initial={{ x: 300, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 300, opacity: 0 }}
                        className="w-80 bg-black/40 backdrop-blur-3xl border border-white/10 rounded-[2.5rem] flex flex-col overflow-hidden"
                    >
                        <div className="p-6 border-b border-white/10 flex items-center justify-between">
                            <h3 className="font-bold uppercase tracking-widest text-xs">Guild Chat</h3>
                            <button onClick={() => setShowChat(false)} className="text-gray-500 hover:text-white">&times;</button>
                        </div>
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                            {chatMessages.map((m, i) => (
                                <div key={i} className="space-y-1">
                                    <div className="text-[10px] text-gray-500 font-bold uppercase truncate">{m.user_id}</div>
                                    <div className="bg-white/5 rounded-xl p-3 text-sm border border-white/5">{m.message}</div>
                                </div>
                            ))}
                            <div ref={chatScrollRef} />
                        </div>
                        <form onSubmit={sendChat} className="p-4 border-t border-white/10">
                            <input 
                                value={chatInput}
                                onChange={e => setChatInput(e.target.value)}
                                placeholder="Group message..."
                                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-white/20"
                            />
                        </form>
                    </motion.aside>
                )}
            </AnimatePresence>
        </div>
      </div>

      <style jsx global>{`
        .glass-card {
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        }
        .custom-scrollbar::-webkit-scrollbar {
            width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
      `}</style>
    </div>
  );
}
"""

def migrate():
    print("Starting migration...")
    games = [d for d in os.listdir(GAMES_ROOT) if (GAMES_ROOT / d).is_dir() and d.startswith("elinity")]
    
    for game_folder in games:
        if game_folder == "elinity-ai-adventure-dungeon": continue 
        
        print(f"Migrating {game_folder}...")
        
        clean_name = game_folder.replace("elinity-", "", 1).replace("-", "_")
        router_name = f"games_{clean_name}"
        router_path = ROUTERS_DIR / f"{router_name}.py"
        
        wrong_name = f"games_{game_folder.replace('-', '_')}"
        wrong_path = ROUTERS_DIR / f"{wrong_name}.py"
        if wrong_path.exists() and wrong_path != router_path:
            wrong_path.unlink()
        
        frontend_index = GAMES_ROOT / game_folder / "pages" / "index.js"
        theme_json = '{"bg":"bg-stone-950","gradient":"from-blue-400 to-purple-500"}'
        bg_prompt = "Abstract AI Art"
        game_title = game_folder.replace("-", " ").title()
        
        if frontend_index.exists():
            content = frontend_index.read_text(encoding='utf-8')
            theme_match = re.search(r'const THEME = ({.*?});', content)
            if theme_match: theme_json = theme_match.group(1)
            bg_match = re.search(r'const BG_PROMPT = "(.*?)";', content)
            if bg_match: bg_prompt = bg_match.group(1)
            title_match = re.search(r'const GAME_TITLE = "(.*?)";', content)
            if title_match: game_title = title_match.group(1)
        
        router_content = BACKEND_TEMPLATE.replace("{{GAME_SLUG}}", game_folder)
        router_path.write_text(router_content, encoding='utf-8')
        
        if frontend_index.exists():
            url_slug = clean_name.replace("_", "-")
            frontend_content = FRONTEND_TEMPLATE.replace("{{GAME_SLUG}}", url_slug)
            frontend_content = frontend_content.replace("{{THEME_JSON}}", theme_json)
            frontend_content = frontend_content.replace("{{BG_PROMPT}}", bg_prompt)
            frontend_content = frontend_content.replace("{{GAME_TITLE}}", game_title)
            
            frontend_index.write_text(frontend_content, encoding='utf-8')
        
        local_api = GAMES_ROOT / game_folder / "pages" / "api" / "game.js"
        if local_api.exists():
            local_api.unlink()

        pkg_json_path = GAMES_ROOT / game_folder / "package.json"
        if pkg_json_path.exists():
            pkg_content = pkg_json_path.read_text(encoding='utf-8')
            if '"start": "next start -p 8080"' in pkg_content:
                fixed_pkg = pkg_content.replace('"start": "next start -p 8080"', '"start": "next start"')
                pkg_json_path.write_text(fixed_pkg, encoding='utf-8')

    print("Migration Complete.")
    
if __name__ == "__main__":
    migrate()
