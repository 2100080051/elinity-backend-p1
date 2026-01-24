import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Drama,
    Theater,
    Sparkles,
    Users,
    Zap,
    Package,
    Ghost,
    MessageSquare,
    ChevronRight,
    Lightbulb,
    Music,
    Wind
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const ImprovTheaterView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        energy = 50,
        applause = 0,
        mask = 'Neutral',
        props = [],
        available_actions = [],
        status = 'active'
    } = gameState;

    const handleAction = async (action: string) => {
        if (!action.trim() || !sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', action);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("Enactor communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#110505] text-[#e5e5e5] font-serif p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Curtain Background Effect */}
            <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-red-950/40 to-transparent pointer-events-none" />
            <div className="absolute inset-y-0 left-0 w-20 bg-gradient-to-r from-red-950/20 to-transparent pointer-events-none" />
            <div className="absolute inset-y-0 right-0 w-20 bg-gradient-to-l from-red-950/20 to-transparent pointer-events-none" />

            {/* Header - Theater Status */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-red-600/10 rounded-full border border-red-600/20 shadow-[0_0_20px_rgba(220,38,38,0.1)]">
                        <Theater className="w-6 h-6 text-red-500" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black tracking-[0.1em] text-white uppercase italic">The Enactor's Stage</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-red-500/70 italic">Scene No. {gameState.turn || 1} // {mask} Mask</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-bold text-white/30 tracking-widest mb-1">Scene Energy</p>
                        <div className="flex items-center gap-3">
                            <div className="h-2 w-32 bg-white/5 rounded-full overflow-hidden border border-white/10">
                                <motion.div
                                    animate={{ width: `${energy}%` }}
                                    className="h-full bg-gradient-to-r from-red-600 to-yellow-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]"
                                />
                            </div>
                            <span className="text-xl font-black italic tracking-tighter text-white">{energy}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Center: Stage Narrative */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-[#1a0a0a] border border-white/10 rounded-[2.5rem] p-12 overflow-y-auto backdrop-blur-3xl relative group custom-scrollbar shadow-2xl"
                    >
                        <div className="absolute top-6 left-6 flex items-center gap-2">
                            <Lightbulb className="w-4 h-4 text-yellow-500" />
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-yellow-500/50 italic">Stage_Lights // Full_Beam</span>
                        </div>

                        <div className="prose prose-invert max-w-none">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className={`text-xl leading-relaxed italic border-l-2 border-red-500/10 pl-6 mb-6 last:mb-0 ${line.startsWith('ENACTOR:') ? 'text-white font-bold' : 'text-white/60'}`}>
                                    {line}
                                </p>
                            ))}
                        </div>
                    </motion.div>

                    {/* Dramatic Input */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2 justify-center">
                            {available_actions.map((cue: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(cue)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-white/5 border border-white/10 rounded-full hover:bg-gold-500/10 hover:border-gold-500/40 transition-all text-[10px] font-black uppercase tracking-widest text-[#d4af37] flex items-center gap-2 group italic"
                                >
                                    <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all" />
                                    {cue}
                                </button>
                            ))}
                        </div>

                        <div className="relative group">
                            <div className="absolute -inset-1 bg-gradient-to-r from-red-600 to-gold-600 rounded-full blur opacity-10 group-focus-within:opacity-30 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Yes, and..."
                                className="relative w-full bg-black/60 border border-white/10 rounded-full py-5 px-10 focus:outline-none focus:border-red-500/30 transition-all text-white placeholder:text-white/10 text-xl font-bold italic tracking-tight"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-red-600 rounded-full flex items-center justify-center text-white hover:bg-red-500 transition-all shadow-xl shadow-red-950/20"
                            >
                                <Drama className="w-6 h-6" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Stage Meta Info */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    {/* Active Props */}
                    <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 backdrop-blur-md">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 border-b border-white/5 pb-4 mb-6 flex items-center gap-2">
                            <Package className="w-4 h-4 text-red-500" /> Prop Table
                        </h3>

                        <div className="flex flex-wrap gap-3">
                            {props.length > 0 ? props.map((p: string, i: number) => (
                                <div key={i} className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs font-bold text-white/60 flex items-center gap-2 group hover:text-white transition-colors">
                                    <Sparkles className="w-3 h-3 text-gold-500" />
                                    {p}
                                </div>
                            )) : (
                                <p className="text-[10px] uppercase font-bold text-white/10 tracking-widest italic">The table is empty...</p>
                            )}
                        </div>
                    </div>

                    {/* Applause Meter */}
                    <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 mb-6 flex items-center gap-2">
                            <Music className="w-4 h-4 text-red-500" /> Crowd Reaction
                        </h3>
                        <div className="flex flex-col gap-2">
                            <div className="flex justify-between items-end">
                                <span className="text-[10px] uppercase font-black text-white/30 tracking-widest italic">Applause Meter</span>
                                <span className="text-xl font-black italic tracking-tighter text-white">{applause}%</span>
                            </div>
                            <div className="h-6 w-full bg-black/40 rounded-lg p-1 border border-white/5 flex gap-1">
                                {[...Array(20)].map((_, i) => (
                                    <div key={i} className={`flex-grow rounded-sm ${i < (applause / 5) ? 'bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.3)]' : 'bg-white/5'}`} />
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Meta Card */}
                    <div className="bg-red-600/5 border border-red-600/10 rounded-3xl p-8">
                        <Users className="w-8 h-8 text-red-500/30 mb-4" />
                        <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-red-500/50 italic">
                            REMEMBER: BLOCKING THE ENACTOR'S CUES WILL DRAIN SCENE ENERGY. ALWAYS SAY YES AND...
                        </p>
                    </div>
                </div>
            </div>

            {status === 'curtains' && (
                <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Ghost className="w-20 h-20 text-white/10 mx-auto mb-8" />
                        <h2 className="text-6xl font-black italic tracking-tighter text-white mb-4">Curtains Down</h2>
                        <p className="text-gray-400 mb-10 font-light leading-relaxed">The stage has gone dark. The Enactor awaits the next performance.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-12 py-4 bg-white/5 border border-white/10 rounded-full text-white font-bold uppercase tracking-widest hover:bg-white/10 transition-all shadow-2xl"
                        >
                            Encore
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};
