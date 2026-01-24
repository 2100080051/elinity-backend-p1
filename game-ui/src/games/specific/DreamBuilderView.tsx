import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Cloud,
    Wind,
    Zap,
    Eye,
    Moon,
    Sparkles,
    ChevronRight,
    Infinity as InfinityIcon,
    Ghost,
    Compass,
    Tent,
    Palette
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const DreamBuilderView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        lucidity = 30,
        stability = 100,
        surrealism = 'Low',
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
            console.error("Weaver communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#020617] text-[#cbd5e1] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Moving cloud particles */}
            <div className="absolute inset-0 pointer-events-none">
                <motion.div
                    animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
                    transition={{ repeat: Infinity, duration: 20 }}
                    className="absolute top-20 left-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-[100px]"
                />
                <motion.div
                    animate={{ x: [0, -40, 0], y: [0, 50, 0] }}
                    transition={{ repeat: Infinity, duration: 15 }}
                    className="absolute bottom-20 right-10 w-80 h-80 bg-purple-500/10 rounded-full blur-[100px]"
                />
            </div>

            {/* Header - Weaver HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-indigo-900/40 rounded-full border border-indigo-500/20 shadow-[0_0_20px_rgba(99,102,241,0.2)]">
                        <Moon className="w-6 h-6 text-indigo-300" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-light tracking-[0.2em] text-white uppercase italic">Dream Construct // <span className="text-indigo-400 font-bold">{surrealism}</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-500/40 italic">Subconscious Link: Active</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8 bg-black/50 px-8 py-4 rounded-[2rem] border border-white/10 backdrop-blur-xl">
                    <DreamStat icon={<Eye className="w-4 h-4 text-indigo-400" />} label="Lucidity" value={`${lucidity}%`} />
                    <div className="w-px h-8 bg-white/5" />
                    <DreamStat icon={<InfinityIcon className="w-4 h-4 text-purple-400" />} label="Stability" value={`${stability}%`} />
                    <div className="w-px h-8 bg-white/5" />
                    <DreamStat icon={<Ghost className="w-4 h-4 text-pink-400" />} label="Drift" value="Normal" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Manifestation Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 0.99 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-[#0f172a]/40 border border-white/5 rounded-[3rem] p-12 backdrop-blur-md relative overflow-hidden flex flex-col justify-center"
                    >
                        <div className="absolute top-6 right-10 opacity-5">
                            <Sparkles className="w-24 h-24" />
                        </div>

                        <div className="relative z-10">
                            <div className="flex items-center gap-2 mb-8 text-[11px] font-bold text-white/10 uppercase tracking-[0.5em]">
                                <Compass className="w-4 h-4" /> Manifestation_Log
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-slate-200 italic selection:bg-indigo-500/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-6 last:mb-0 border-l-2 border-indigo-500/20 pl-10 hover:border-indigo-500/50 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Dream Actions */}
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-wrap gap-2 justify-center">
                            {available_actions.map((manifest: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(manifest)}
                                    disabled={loading}
                                    className="px-6 py-2.5 bg-white/5 border border-white/10 rounded-full hover:bg-indigo-500/20 hover:border-indigo-500 transition-all text-[11px] font-bold tracking-widest text-white/40 hover:text-white flex items-center gap-2 group shadow-lg"
                                >
                                    <Cloud className="w-3 h-3 text-indigo-400 group-hover:scale-110 transition-transform" />
                                    {manifest}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Think it into existence..."
                                className="w-full bg-black/60 border border-white/5 rounded-3xl py-6 px-10 focus:outline-none focus:border-indigo-500/40 transition-all text-white placeholder:text-white/10 text-xl font-light italic"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-14 h-14 bg-indigo-600/80 text-white rounded-2xl flex items-center justify-center hover:bg-indigo-500 transition-all shadow-xl"
                            >
                                <Zap className={`w-6 h-6 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Subconscious Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#0f172a]/20 border border-white/5 rounded-[2rem] p-8 backdrop-blur-md">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/20 mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                            <Palette className="w-4 h-4" /> Dream Layers
                        </h3>

                        <div className="space-y-6">
                            <MetricRow label="Surrealism" value={surrealism} />
                            <MetricRow label="Subconscious Depth" value="400m" />
                            <MetricRow label="Identity Cohesion" value={`${lucidity}%`} />
                        </div>

                        <div className="mt-12 p-6 bg-indigo-500/5 border border-indigo-500/10 rounded-[2rem] flex items-start gap-4">
                            <Wind className="w-5 h-5 text-indigo-400 opacity-30 mt-1" />
                            <p className="text-[10px] uppercase font-bold tracking-[0.1em] leading-loose text-indigo-200/30 italic">
                                Walls are merely suggestions here. If you can conceive of the key, the door will create itself.
                            </p>
                        </div>
                    </div>

                    <div className="bg-indigo-900/5 border border-indigo-500/10 rounded-[2rem] p-8 flex flex-col items-center justify-center gap-4 text-indigo-500/20">
                        <Tent className="w-12 h-12 opacity-20 animate-bounce" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-center">Dream Rooted In Void</span>
                    </div>
                </div>
            </div>

            {status === 'awakened' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Eye className="w-20 h-20 text-white mx-auto mb-8 shadow-[0_0_40px_rgba(255,255,255,0.2)]" />
                        <h2 className="text-6xl font-light italic tracking-tighter text-white mb-4 uppercase">Waking Up</h2>
                        <p className="text-white/30 mb-12 font-bold leading-relaxed tracking-widest uppercase text-sm">The constructs have dissolved into the morning light. The Weaver awaits your return to the fog.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-16 py-5 bg-white rounded-full text-black font-black uppercase tracking-[0.2em] hover:bg-indigo-400 transition-all shadow-2xl"
                        >
                            Return to Fog
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const DreamStat = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="text-center">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest">{label}</span>
        </div>
        <p className="text-2xl font-light italic text-white tracking-tighter">{value}</p>
    </div>
);

const MetricRow = ({ label, value }: { label: string, value: string }) => (
    <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase font-bold tracking-widest text-white/20">{label}</span>
        <span className="text-xs font-bold text-indigo-300 italic tracking-tight uppercase">{value}</span>
    </div>
);
