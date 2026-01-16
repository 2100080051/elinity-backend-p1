import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumText } from '../../components/shared/PremiumComponents';
import { Globe, ChevronRight, Sparkles, Send, Map, Users, History, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const WorldBuildersView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const round = gameState.round || "Geography";
    const codex = gameState.world_codex || [];
    const narrative = gameState.last_ai_response?.narrative || "The world is unformed. What lands shall we shape?";
    const nextPrompt = gameState.last_ai_response?.next_prompt || "Specify the next element of this world.";

    const categoryIcons: { [key: string]: any } = {
        'Geography': Map,
        'Culture': Users,
        'History': History,
        'Character': User
    };

    const handleSubmit = async (action: string, content: string) => {
        if (!sessionId || !gameSlug) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, action, content);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error(e); }
        setLoading(false);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="World Builders"
            subtitle={`Epoch: ${round}`}
            icon={Globe}
            backgroundVar="starfield"
            guideText="1. Shape the world together by defining Geography, Culture, and History.\n2. In each epoch, describe a new element.\n3. Vote or collaborate to build the most vivid realm!\n4. Use 'Skip Age' to progress through time."
        >
            <div className="flex flex-col h-full gap-6">
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-0">

                    {/* Left/Middle: Lore & Narrative (3/4) */}
                    <div className="lg:col-span-3 flex flex-col gap-6 overflow-hidden">
                        <div className="flex-1 bg-black/40 rounded-3xl border border-white/10 relative overflow-hidden flex flex-col shadow-2xl">
                            {/* Ambient World Glow */}
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500/0 via-gold/50 to-blue-500/0 opacity-50" />

                            <div className="relative z-10 flex-1 flex flex-col p-8 md:p-14 overflow-y-auto custom-scrollbar">
                                <motion.div
                                    key={round}
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="mb-6"
                                >
                                    <span className="px-3 py-1 rounded-full bg-gold/10 border border-gold/20 text-[10px] text-gold font-bold uppercase tracking-[0.2em] mb-4 inline-block">
                                        Current Epoch: {round}
                                    </span>
                                </motion.div>

                                <div className="flex-1 flex flex-col justify-center">
                                    <AnimatePresence mode="wait">
                                        <motion.div
                                            key={narrative.substring(0, 30)}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: -10 }}
                                            transition={{ duration: 0.6 }}
                                            className="text-2xl md:text-4xl font-light text-white leading-[1.4] font-serif italic"
                                        >
                                            <PremiumText text={narrative} />
                                        </motion.div>
                                    </AnimatePresence>

                                    <motion.p
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 0.6 }}
                                        className="mt-12 text-lg text-gold/80 font-medium tracking-wide"
                                    >
                                        <ChevronRight size={18} className="inline mr-2" />
                                        {nextPrompt}
                                    </motion.p>
                                </div>
                            </div>
                        </div>

                        {/* Input System */}
                        <div className="bg-[#12101b] p-2 rounded-2xl border border-white/10 shadow-xl flex items-center gap-3">
                            <div className="flex-1 relative">
                                <input
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && handleSubmit('create', input)}
                                    placeholder={`Describe a new ${round.toLowerCase()} element...`}
                                    disabled={loading}
                                    className="w-full bg-transparent border-none text-white placeholder-white/20 py-5 px-6 focus:outline-none text-lg font-serif"
                                />
                                {loading && (
                                    <div className="absolute right-4 top-1/2 -translate-y-1/2">
                                        <Sparkles className="animate-spin text-gold/50" size={20} />
                                    </div>
                                )}
                            </div>
                            <PremiumButton
                                onClick={() => handleSubmit('create', input)}
                                disabled={loading || !input}
                                className="h-[60px] px-8 rounded-xl"
                            >
                                <Send size={20} />
                            </PremiumButton>
                            <button
                                onClick={() => handleSubmit('advance_round', 'skip')}
                                className="h-[60px] px-4 rounded-xl text-white/40 hover:text-white hover:bg-white/5 transition-all text-xs font-bold uppercase tracking-widest flex items-center gap-2 group"
                            >
                                Skip Age <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                            </button>
                        </div>
                    </div>

                    {/* Right: The Codex (1/4) */}
                    <div className="lg:col-span-1 bg-black/50 rounded-3xl border border-white/10 flex flex-col overflow-hidden shadow-2xl">
                        <div className="p-6 bg-white/5 border-b border-white/10 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Globe size={18} className="text-gold" />
                                <h3 className="font-premium font-bold uppercase tracking-[0.2em] text-xs text-white">World Codex</h3>
                            </div>
                            <span className="text-[10px] text-gray-500 font-mono">{codex.length} ENTRIES</span>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                            <AnimatePresence>
                                {codex.length === 0 ? (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="text-center py-20 opacity-20"
                                    >
                                        <Map size={48} className="mx-auto mb-4" />
                                        <p className="text-sm italic">The history of this world starts with you.</p>
                                    </motion.div>
                                ) : (
                                    codex.map((entry: any, i: number) => {
                                        const Icon = categoryIcons[entry.type] || Map;
                                        return (
                                            <motion.div
                                                key={i}
                                                initial={{ opacity: 0, x: 20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                className="group bg-white/5 border border-white/5 rounded-2xl p-5 hover:border-gold/30 hover:bg-gold/5 transition-all duration-300 cursor-default"
                                            >
                                                <div className="flex items-center gap-3 mb-3">
                                                    <div className="p-2 rounded-lg bg-black/40 text-gold/60 group-hover:text-gold transition-colors">
                                                        <Icon size={14} />
                                                    </div>
                                                    <h4 className="text-sm font-bold text-white/90 group-hover:text-white">{entry.title}</h4>
                                                </div>
                                                <p className="text-xs text-gray-400 group-hover:text-gray-300 leading-relaxed font-serif">
                                                    {entry.description}
                                                </p>
                                            </motion.div>
                                        );
                                    })
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>
        </PremiumGameLayout>
    );
};

