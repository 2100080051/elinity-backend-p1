import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Music,
    Wind,
    Zap,
    Disc,
    Mic2,
    Radio,
    ChevronRight,
    TrendingUp,
    Award,
    Calendar,
    Waves,
    Heart
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const MusicJourneyView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        flow = 50,
        tempo = 'Andante',
        instrument = 'Violin',
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
            console.error("Maestro communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#1c1917] text-[#e7e5e4] font-serif p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Sheet music backdrop */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/cream-paper.png')]" />
            <div className="absolute top-1/2 left-0 w-full h-px bg-white/5 shadow-[0_0_10px_rgba(255,255,255,0.1)]" />
            <div className="absolute top-[55%] left-0 w-full h-px bg-white/5 shadow-[0_0_10px_rgba(255,255,255,0.1)]" />

            {/* Header - Maestro HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-stone-800 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-4 bg-stone-900 rounded-2xl border border-stone-700 shadow-xl">
                        <Music className="w-8 h-8 text-amber-500" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tight text-white uppercase italic">The Maestro's Symphony</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-stone-500 italic">Era: {instrument} Era // Active Rhythm</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10 bg-stone-900/80 px-10 py-4 rounded-[2.5rem] border border-stone-800 backdrop-blur-md">
                    <MaestroStat label="Flow" value={`${flow}%`} sub="Harmony" color="text-amber-400" />
                    <div className="w-px h-10 bg-stone-800" />
                    <MaestroStat label="Tempo" value={tempo} sub="Pace" color="text-white" />
                    <div className="w-px h-10 bg-stone-800" />
                    <MaestroStat label="Mood" value="Elegant" sub="Aura" color="text-stone-400" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Orchestral Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-stone-900/40 border border-stone-800 rounded-[3rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl"
                    >
                        <div className="absolute top-10 left-10 opacity-5">
                            <Calendar className="w-32 h-32" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto text-center">
                            <div className="flex items-center justify-center gap-2 mb-10 text-[11px] font-bold text-stone-600 uppercase tracking-[0.6em]">
                                <Waves className="w-4 h-4" /> Orchestral_Response
                            </div>

                            <p className="text-3xl md:text-4xl font-light leading-relaxed text-stone-200 italic selection:bg-amber-500/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Conductor Actions */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((score: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(score)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-stone-900 border border-stone-700 rounded-xl hover:bg-stone-800 hover:border-amber-500 transition-all text-[11px] font-black uppercase tracking-[0.2em] text-stone-500 hover:text-amber-500 flex items-center gap-3 group shadow-xl"
                                >
                                    <Award className="w-3 h-3 text-amber-500 opacity-0 group-hover:opacity-100 transition-all" />
                                    {score}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-amber-500/10 rounded-2xl blur opacity-0 group-focus-within:opacity-20 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your command to the orchestra..."
                                className="w-full bg-stone-950 border border-stone-800 rounded-2xl py-8 px-12 focus:outline-none focus:border-amber-500/40 transition-all text-white placeholder:text-stone-800 text-2xl font-light italic text-center"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-amber-600 text-white rounded-xl flex items-center justify-center hover:bg-amber-500 transition-all shadow-2xl"
                            >
                                <Zap className={`w-8 h-8 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Symphony Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-stone-900 border border-stone-800 rounded-[2.5rem] p-10 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-stone-600 mb-10 flex items-center gap-2 border-b border-stone-800 pb-5">
                            <TrendingUp className="w-4 h-4" /> Symphony_Diagnostics
                        </h3>

                        <div className="space-y-12">
                            <SymphonyMeter label="Harmony Resonance" value={flow} color="bg-amber-500" />
                            <SymphonyMeter label="Acoustic Integrity" value={92} color="bg-stone-500" />
                            <SymphonyMeter label="Emotional Impact" value={flow + 10} color="bg-red-500" />
                        </div>

                        <div className="mt-14 p-8 bg-amber-500/5 border border-amber-500/10 rounded-3xl flex items-start gap-5">
                            <Heart className="w-6 h-6 text-amber-500 opacity-20 mt-1" />
                            <p className="text-[10px] uppercase font-bold tracking-[0.1em] leading-loose text-stone-500 italic text-center w-full">
                                "The stage is set. The history of mankind is merely a melody waiting to be mastered."
                            </p>
                        </div>
                    </div>

                    <div className="bg-stone-900/20 border border-stone-800 rounded-[2.5rem] p-8 flex flex-col items-center justify-center gap-4 text-stone-700">
                        <Radio className="w-10 h-10 opacity-10 animate-pulse" />
                        <span className="text-[8px] font-black uppercase tracking-[0.6em] text-center">Transmission Locked</span>
                    </div>
                </div>
            </div>

            {status === 'harmonized' && (
                <div className="fixed inset-0 z-[100] bg-[#1c1917]/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Music className="w-24 h-24 text-amber-500 mx-auto mb-10 shadow-[0_0_60px_rgba(245,158,11,0.3)]" />
                        <h2 className="text-6xl font-black italic tracking-tighter text-white mb-6 uppercase">Masterpiece</h2>
                        <p className="text-stone-500 mb-14 font-bold leading-relaxed tracking-widest uppercase text-sm px-4">Your arrangement has echoed through the halls of time. The Maestro bows in respect to your vision.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-5 bg-amber-600 rounded-xl text-white font-black uppercase tracking-[0.3em] hover:bg-amber-500 transition-all shadow-2xl"
                        >
                            Reset Concert
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const MaestroStat = ({ label, value, sub, color }: { label: string, value: string, sub: string, color: string }) => (
    <div className="text-center">
        <p className="text-[9px] uppercase font-black text-stone-600 tracking-widest mb-1">{label}</p>
        <p className={`text-2xl font-black italic tracking-tighter ${color}`}>{value}</p>
        <p className="text-[8px] uppercase font-bold text-stone-700 tracking-tight">{sub}</p>
    </div>
);

const SymphonyMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.3em] text-stone-500">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-0.5 bg-stone-800 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_15px_rgba(0,0,0,0.5)]`}
            />
        </div>
    </div>
);
