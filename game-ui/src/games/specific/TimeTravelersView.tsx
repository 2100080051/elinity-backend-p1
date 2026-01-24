import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Clock,
    RotateCcw,
    Zap,
    Activity,
    ShieldAlert,
    History,
    ChevronRight,
    TrendingUp,
    Cpu,
    Layers,
    Sparkles,
    Search,
    Timer,
    Compass,
    Hourglass
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const TimeTravelersView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        stability = 100,
        era = 'Unknown',
        points = 0,
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
            console.error("Chronos communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#1c1917] text-[#e7e5e4] font-mono p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Temporal distortion grids */}
            <div className="absolute inset-0 pointer-events-none opacity-10">
                <div className="absolute inset-0 bg-[linear-gradient(rgba(231,229,228,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(231,229,228,0.1)_1px,transparent_1px)] bg-[size:40px_40px] transform scale-150 rotate-12" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(139,92,246,0.1),transparent_70%)]" />
            </div>

            {/* Header - Chronos HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/10 pb-8 bg-black/20 backdrop-blur-xl p-8 rounded-[2rem] shadow-2xl">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-black rounded-full border border-violet-500/30 shadow-[0_0_40px_rgba(139,92,246,0.2)]">
                        <Clock className="w-8 h-8 text-violet-400 animate-spin-slow" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">Temporal <span className="text-violet-500">Weave</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-violet-500/40 italic">Sync Rate: Stable // Epoch: {era.toUpperCase()}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <ChronosStat label="Stability" value={`${stability}%`} icon={<ShieldAlert className={`w-4 h-4 ${stability < 50 ? 'text-red-500' : 'text-violet-400'}`} />} />
                    <div className="w-px h-10 bg-white/10" />
                    <ChronosStat label="Butterfly Pts" value={points.toString()} icon={<TrendingUp className="text-amber-500 w-4 h-4" />} />
                    <div className="w-px h-10 bg-white/10" />
                    <ChronosStat label="Timeline" value="Primary" icon={<Compass className="w-4 h-4 text-cyan-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Fragment Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-[#0c0a09]/80 border border-white/5 rounded-[3rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.03] animate-pulse">
                            <Timer className="w-48 h-48" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-white/10 uppercase tracking-[0.8em]">
                                <History className="w-4 h-4" /> Epoch_Data_Log
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-stone-200 italic selection:bg-violet-900/40">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0 border-l-2 border-violet-500/10 pl-10 hover:border-violet-500 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Traveler Disruption */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((jump: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(jump)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-white/5 border border-white/10 rounded-xl hover:bg-violet-900/20 hover:border-violet-500 transition-all text-[11px] font-black uppercase tracking-widest text-stone-500 hover:text-white flex items-center gap-3 group shadow-xl"
                                >
                                    <Sparkles className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all" />
                                    {jump}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-violet-500/10 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Execute temporal shift directive..."
                                className="w-full bg-[#050505] border border-white/10 rounded-2xl py-8 px-12 focus:outline-none focus:border-violet-500 transition-all text-stone-200 placeholder:text-stone-800 text-2xl font-light italic text-center shadow-inner"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-violet-600 text-white rounded-xl flex items-center justify-center hover:bg-white hover:text-black transition-all shadow-2xl"
                            >
                                <RotateCcw className={`w-8 h-8 ${loading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Chronometric Analysis */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#0c0a09] border border-white/5 rounded-[3rem] p-10 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-white/10 mb-10 flex items-center gap-2 border-b border-white/5 pb-5">
                            <TrendingUp className="w-4 h-4" /> Temporal_Stability_Matrix
                        </h3>

                        <div className="space-y-12">
                            <StabilityMeter label="Causality Cohesion" value={stability} color="bg-violet-500" />
                            <StabilityMeter label="Butterfly Accumulation" value={Math.min(100, (points / 2000) * 100)} color="bg-amber-600" />
                            <StabilityMeter label="Dimensional Friction" value={20} color="bg-indigo-500" />
                        </div>

                        <div className="mt-14 p-8 bg-violet-900/5 border border-violet-900/10 rounded-3xl flex items-start gap-5">
                            <Hourglass className="w-6 h-6 text-violet-500 opacity-20 mt-1" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-stone-500 italic text-center w-full">
                                "History is not a line, but a labyrinth. Be careful not to lose your way in the shadows of what was."
                            </p>
                        </div>
                    </div>

                    <div className="bg-violet-900/5 border border-violet-900/10 rounded-[3rem] p-8 flex flex-col items-center justify-center gap-4 text-violet-950">
                        <Cpu className="w-12 h-12 opacity-20 animate-pulse" />
                        <span className="text-[9px] font-black uppercase tracking-[0.6em] text-center">Neural Link Established</span>
                    </div>
                </div>
            </div>

            {status === 'collapsed' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <RotateCcw className="w-24 h-24 text-red-600 mx-auto mb-10 animate-spin-reverse" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-6 uppercase">Stability <br /><span className="text-red-600">Lost</span></h2>
                        <p className="text-stone-500 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">The timeline has shattered into infinite fragments. You are adrift in the non-exist.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-red-600 text-white font-black uppercase tracking-[0.4em] hover:bg-white hover:text-black transition-all shadow-2xl rounded-2xl"
                        >
                            Reset Timeline
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const ChronosStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group cursor-wait">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest text-stone-400">{label}</span>
        </div>
        <p className="text-2xl font-black italic text-stone-100 tracking-tighter group-hover:text-violet-400 transition-colors uppercase">{value}</p>
    </div>
);

const StabilityMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-stone-600">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_20px_rgba(139,92,246,0.3)]`}
            />
        </div>
    </div>
);
