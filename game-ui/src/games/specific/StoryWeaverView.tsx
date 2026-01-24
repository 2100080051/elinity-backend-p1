import { useState, useEffect } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton } from '../../components/shared/PremiumComponents';
import {
    Book, Star, Sparkles, Wand2, Shield,
    Skull, Flame, Wind, MessageSquare,
    ArrowRight, History, Layers
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const StoryWeaverView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug, players } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [showHistory, setShowHistory] = useState(false);

    const narrative = gameState.last_ai_response?.narrative || (gameState.story_text && gameState.story_text.length > 0 ? gameState.story_text[gameState.story_text.length - 1] : "The ink wait for the first drop of fate.");
    const phase = gameState.phase || "Prologue";
    const karma = gameState.karma ?? 50;
    const arc = gameState.character_arc || "The Wanderer";
    const chapter = gameState.chapter || 1;
    const atmosphere = gameState.atmosphere || "Mysterious";
    const conditions = gameState.world_conditions || [];
    const fatePaths = gameState.fate_paths || [];

    const handleAction = async (content: string, type: string = 'contribute') => {
        if (!content.trim() || !sessionId || !gameSlug) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, type, content);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("Fate was interrupted:", e);
        }
        setLoading(false);
        setInput("");
    };

    const playerOrder = gameState.player_order || [];
    const turnIndex = gameState.turn_index || 0;
    const currentTurnUserId = playerOrder.length > 0 ? playerOrder[turnIndex % playerOrder.length] : null;
    const isMyTurn = !currentTurnUserId || currentTurnUserId === userId;

    const currentTurnParams = players[currentTurnUserId] || {};
    const currentTurnName = currentTurnParams.name || (currentTurnUserId === userId ? "You" : "The Silent Weaver");

    // Dynamic styles based on Karma
    const isGrim = karma < 40;
    const isRadiant = karma > 60;

    return (
        <PremiumGameLayout
            title="The Story Weaver"
            subtitle={`Chapter ${chapter}: ${atmosphere}`}
            icon={Book}
            backgroundVar={isGrim ? "abyss" : isRadiant ? "aurora" : "starfield"}
            guideText="Shape a legendary character arc. Your words flow through the Chronicler of Fate. select fate paths or weave your own path."
        >
            <div className="flex flex-col h-full relative overflow-hidden">

                {/* --- HEADER STATS --- */}
                <div className="absolute top-4 inset-x-4 flex justify-between items-center z-50 pointer-events-none">
                    <motion.div
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        className="flex gap-2"
                    >
                        {conditions.map((cond: string, i: number) => (
                            <div key={i} className="px-3 py-1 bg-white/5 border border-white/10 rounded-full backdrop-blur-md flex items-center gap-2">
                                <Wind className="w-3 h-3 text-cyan-400" />
                                <span className="text-[9px] uppercase tracking-widest font-bold text-cyan-100">{cond}</span>
                            </div>
                        ))}
                    </motion.div>

                    <div className="flex gap-3 pointer-events-auto">
                        <div className="group relative">
                            <div className={`absolute -inset-1 bg-gradient-to-r ${isRadiant ? 'from-yellow-500 to-orange-500' : 'from-purple-500 to-blue-500'} rounded-2xl blur-md opacity-20 group-hover:opacity-100 transition duration-500`} />
                            <div className="relative px-4 py-2 bg-black/40 border border-white/10 rounded-2xl backdrop-blur-xl flex items-center gap-3">
                                {isGrim ? <Skull className="w-4 h-4 text-red-500" /> : isRadiant ? <Sparkles className="w-4 h-4 text-yellow-400" /> : <Shield className="w-4 h-4 text-blue-400" />}
                                <div className="flex flex-col">
                                    <span className="text-[8px] text-white/40 font-bold uppercase tracking-widest">Character Arc</span>
                                    <span className="text-sm font-serif font-black text-white">{arc}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* --- MAIN NARRATIVE AREA --- */}
                <div className="relative flex-1 flex flex-col items-center justify-center p-6 md:p-12 overflow-hidden">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={narrative}
                            initial={{ opacity: 0, scale: 0.98, filter: 'blur(10px)' }}
                            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                            exit={{ opacity: 0, scale: 1.02, filter: 'blur(10px)' }}
                            transition={{ duration: 0.8, ease: "circOut" }}
                            className="relative w-full max-w-2xl bg-gradient-to-b from-white/[0.03] to-transparent p-10 rounded-[3rem] border border-white/5 shadow-2xl overflow-y-auto max-h-full custom-scrollbar"
                        >
                            {/* Large Decorative Initial Letter logic could go here */}
                            <p className="font-serif text-2xl md:text-3xl text-white/90 leading-[1.8] italic tracking-tight drop-shadow-2xl selection:bg-orange-500/30">
                                {narrative}
                            </p>

                            {/* Fate Paths Selection */}
                            <AnimatePresence>
                                {isMyTurn && fatePaths.length > 0 && (
                                    <motion.div
                                        initial={{ y: 20, opacity: 0 }}
                                        animate={{ y: 0, opacity: 1 }}
                                        className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4"
                                    >
                                        {fatePaths.map((path: string, i: number) => (
                                            <button
                                                key={i}
                                                onClick={() => handleAction(path, 'fate_selection')}
                                                disabled={loading}
                                                className="group relative p-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-left transition-all duration-300 transform hover:-translate-y-1"
                                            >
                                                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <Wand2 className="w-3 h-3 text-orange-400" />
                                                </div>
                                                <span className="text-xs text-white/40 block mb-1 font-bold tracking-widest uppercase">Fate Path {i + 1}</span>
                                                <p className="text-sm text-white/80 font-serif line-clamp-2">{path}</p>
                                            </button>
                                        ))}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* --- INTERACTIVE FOOTER --- */}
                <div className="p-6 md:p-10 bg-gradient-to-t from-black via-black/80 to-transparent flex flex-col gap-6 items-center">

                    {/* Progress Bar (Karma) */}
                    <div className="w-full max-w-xl flex flex-col gap-2">
                        <div className="flex justify-between items-end px-2">
                            <span className="text-[10px] font-black tracking-[0.2em] text-white/20 uppercase">Grim</span>
                            <span className="text-[14px] font-serif italic text-white/60 tracking-widest">{atmosphere}</span>
                            <span className="text-[10px] font-black tracking-[0.2em] text-white/20 uppercase">Radiant</span>
                        </div>
                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden relative">
                            <motion.div
                                initial={{ width: '50%' }}
                                animate={{ width: `${karma}%` }}
                                className={`h-full bg-gradient-to-r ${isGrim ? 'from-red-900 to-purple-600' : isRadiant ? 'from-orange-500 to-yellow-300' : 'from-purple-600 to-orange-500'} shadow-[0_0_15px_rgba(255,165,0,0.3)]`}
                            />
                        </div>
                    </div>

                    <div className="w-full max-w-4xl flex gap-4 items-end">
                        <div className="flex-1 relative">
                            {/* Character Interaction State */}
                            <div className="absolute -top-12 left-4 flex items-center gap-3">
                                <div className={`w-2 h-2 rounded-full ${isMyTurn ? 'bg-orange-500 animate-ping' : 'bg-white/20'}`} />
                                <span className={`text-[10px] font-black tracking-widest uppercase ${isMyTurn ? 'text-orange-400' : 'text-white/20'}`}>
                                    {isMyTurn ? "Your Turn to Weave Destiny" : `The Chronicles await ${currentTurnName}`}
                                </span>
                            </div>

                            <textarea
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleAction(input))}
                                placeholder={isMyTurn ? "Speak your truth or defy fate..." : "Waiting for the chronicle to turn..."}
                                className={`w-full bg-white/5 border-2 rounded-[2rem] px-8 py-5 min-h-[100px] max-h-[200px] text-xl font-serif text-white placeholder:text-white/10 focus:outline-none transition-all duration-500 ${isMyTurn ? 'border-white/10 focus:border-orange-500/40 shadow-2xl focus:bg-white/[0.08]' : 'border-transparent opacity-30 cursor-not-allowed'}`}
                                disabled={loading || !isMyTurn}
                            />
                        </div>

                        <PremiumButton
                            onClick={() => handleAction(input)}
                            disabled={loading || !input || !isMyTurn}
                            className={`h-[100px] w-[100px] rounded-[2rem] flex flex-col items-center justify-center gap-1 group shadow-2xl transition-all duration-500 ${isMyTurn ? 'bg-orange-500 hover:bg-orange-400 scale-100 hover:scale-105 active:scale-95' : 'bg-white/5 opacity-20'}`}
                        >
                            {loading ? (
                                <motion.div animate={{ rotate: 360, scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1.5 }}>
                                    <Flame className="w-8 h-8 text-white" />
                                </motion.div>
                            ) : (
                                <>
                                    <ArrowRight className="w-8 h-8 text-white group-hover:translate-x-1 transition-transform" />
                                    <span className="text-[10px] font-black tracking-tighter uppercase">Weave</span>
                                </>
                            )}
                        </PremiumButton>
                    </div>

                    {/* History Toggler */}
                    <button
                        onClick={() => setShowHistory(!showHistory)}
                        className="flex items-center gap-2 text-[10px] font-black text-white/20 hover:text-white/60 transition-colors uppercase tracking-[0.2em]"
                    >
                        <History size={12} />
                        View Past Chronicles
                    </button>
                </div>

                {/* --- HISTORY SIDEBAR OVERLAY --- */}
                <AnimatePresence>
                    {showHistory && (
                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            className="absolute inset-y-0 right-0 w-full max-w-md bg-black/90 backdrop-blur-3xl border-l border-white/10 z-[100] p-10 flex flex-col gap-6"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-serif font-black flex items-center gap-3">
                                    <Layers className="text-orange-500" /> Past Chronicles
                                </h3>
                                <button onClick={() => setShowHistory(false)} className="text-white/40 hover:text-white">&times; Close</button>
                            </div>
                            <div className="flex-1 overflow-y-auto custom-scrollbar space-y-8 pr-4">
                                {gameState.story_text?.map((text: string, i: number) => (
                                    <motion.div
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: i * 0.1 }}
                                        key={i}
                                        className="relative pl-6 border-l-2 border-white/5"
                                    >
                                        <div className="absolute -left-1.5 top-0 w-3 h-3 rounded-full bg-white/10" />
                                        <p className="text-sm font-serif italic text-white/50 leading-relaxed">{text}</p>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

            </div>
        </PremiumGameLayout>
    );
};
