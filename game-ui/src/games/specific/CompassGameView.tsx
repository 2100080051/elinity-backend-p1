import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Compass,
    GitBranch,
    Navigation,
    Anchor,
    Wind,
    Moon,
    Zap,
    Activity,
    Sparkles,
    ChevronRight,
    Database,
    Star,
    Sunrise,
    Waves,
    Cpu,
    Heart
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const CompassGameView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        location = 'The Great Unknown',
        north_south = 50,
        east_west = 50,
        status = 'active',
        last_ai_response = {}
    } = gameState;

    const narrative = last_ai_response?.narrative || "The stars are silent. Where do we sail?";
    const insight = last_ai_response?.compass_insight;
    const choices = last_ai_response?.choices || [];

    const handleChoice = async (c: string) => {
        if (!sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'choose_path', c);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("The Master Voyager communication error:", e);
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-[#020617] text-[#f8fafc] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Celestial Sea Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_40%,#1e3a8a_0%,transparent_100%)] opacity-20" />
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-10" />
            </div>

            {/* Header - Master Voyager HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-8 bg-black/40 backdrop-blur-3xl p-8 rounded-[2.5rem] shadow-2xl">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-blue-600 rounded-2xl shadow-[0_0_40px_rgba(37,99,235,0.3)]">
                        <Compass className="w-8 h-8 text-white animate-spin-slow" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">The Great <span className="text-blue-500">Compass</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.4em] text-blue-500/40 italic">Latitude: QUANTUM // Bearings: STABLE</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <NavigatorStat label="Location" value={location} icon={<Anchor className="w-4 h-4 text-blue-400" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <NavigatorStat label="Drift" value="Minimal" icon={<Wind className="text-sky-400 w-4 h-4" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <NavigatorStat label="Celestial Sync" value="High" icon={<Star className="w-4 h-4 text-amber-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 z-10 flex-grow pt-4 overflow-hidden">
                {/* Visual Compass Display */}
                <div className="lg:col-span-5 flex flex-col items-center justify-center p-8 relative shrink-0">
                    <div className="relative w-full max-w-[450px] aspect-square rounded-full border border-white/5 flex items-center justify-center shadow-2xl bg-white/[0.01] backdrop-blur-sm">
                        {/* Rotating Rings */}
                        <div className="absolute inset-4 border border-white/5 rounded-full animate-[spin_60s_linear_infinite]" />
                        <div className="absolute inset-10 border border-white/10 rounded-full animate-[spin_45s_linear_infinite_reverse]" />
                        <div className="absolute inset-20 border border-white/5 rounded-full animate-[spin_90s_linear_infinite]" />

                        {/* Axes Labels */}
                        <div className="absolute top-6 flex flex-col items-center opacity-40 group hover:opacity-100 transition-opacity">
                            <Cpu className="text-blue-400 w-5 h-5 mb-1" />
                            <span className="text-[10px] font-black tracking-[0.3em] text-blue-400 uppercase">Logic</span>
                        </div>
                        <div className="absolute bottom-6 flex flex-col items-center opacity-40 group hover:opacity-100 transition-opacity">
                            <Heart className="text-rose-500 w-5 h-5 mb-1" />
                            <span className="text-[10px] font-black tracking-[0.3em] text-rose-500 uppercase">Emotion</span>
                        </div>
                        <div className="absolute left-6 flex flex-col items-center opacity-40 group hover:opacity-100 transition-opacity">
                            <Zap className="text-amber-500 w-5 h-5 mb-1" />
                            <span className="text-[10px] font-black tracking-[0.3em] text-amber-500 uppercase">Self</span>
                        </div>
                        <div className="absolute right-6 flex flex-col items-center opacity-40 group hover:opacity-100 transition-opacity">
                            <Users className="text-emerald-500 w-5 h-5 mb-1" />
                            <span className="text-[10px] font-black tracking-[0.3em] text-emerald-500 uppercase">Others</span>
                        </div>

                        {/* The Indicator */}
                        <motion.div
                            animate={{
                                x: (east_west - 50) * 3,
                                y: (north_south - 50) * -3
                            }}
                            className="relative z-20 w-8 h-8 flex items-center justify-center"
                        >
                            <div className="absolute inset-0 bg-white rounded-full blur-md opacity-20 animate-pulse" />
                            <div className="w-3 h-3 bg-white rounded-full shadow-[0_0_20px_white] ring-4 ring-white/20" />

                            {/* Trace Lines */}
                            <div className="absolute h-64 w-[1px] bg-gradient-to-t from-transparent via-white/10 to-transparent pointer-events-none" />
                            <div className="absolute w-64 h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent pointer-events-none" />
                        </motion.div>

                        <Compass className="absolute inset-0 text-white/[0.02] p-24 pointer-events-none" />
                    </div>

                    <div className="mt-12 flex items-center gap-6">
                        <div className="px-6 py-2 bg-white/5 border border-white/10 rounded-full text-[10px] font-black tracking-widest text-white/40">
                            TRAJECTORY: {(north_south > 50 ? 'NORTH' : 'SOUTH')} / {(east_west > 50 ? 'EAST' : 'WEST')}
                        </div>
                    </div>
                </div>

                {/* Narrative & Decision Feed */}
                <div className="lg:col-span-7 flex flex-col gap-6 overflow-hidden">
                    <motion.div
                        key={narrative}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-grow bg-white/[0.02] border border-white/5 rounded-[3.5rem] p-16 relative overflow-hidden flex flex-col justify-center shadow-2xl backdrop-blur-md"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.03]">
                            <Sunrise className="w-64 h-64 text-blue-500" />
                        </div>

                        <div className="relative z-10 max-w-4xl">
                            <div className="flex items-center gap-3 mb-10 text-[11px] font-black text-blue-900 uppercase tracking-[0.8em]">
                                <Navigation className="w-4 h-4" /> Master_Voyager_Cartography
                            </div>

                            <p className="text-2xl md:text-5xl font-light leading-snug text-slate-100 italic selection:bg-blue-500/30 mb-12">
                                {narrative}
                            </p>

                            <AnimatePresence mode="wait">
                                {insight && (
                                    <motion.div
                                        key={insight}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="p-8 bg-blue-600/5 border border-blue-600/10 rounded-[2rem] text-blue-300 font-serif italic text-lg shadow-inner relative"
                                    >
                                        <div className="absolute top-0 left-0 w-full h-[1px] bg-blue-500/20" />
                                        "{insight}"
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </motion.div>

                    {/* Choice Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 h-48 shrink-0">
                        {choices.map((c: string, i: number) => (
                            <motion.button
                                key={i}
                                whileHover={{ scale: 1.02, y: -4 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => handleChoice(c)}
                                disabled={loading}
                                className="group relative bg-[#0f172a] hover:bg-blue-900/10 border border-blue-900/20 rounded-[2rem] p-8 text-left transition-all overflow-hidden flex flex-col justify-between shadow-xl"
                            >
                                <div className="absolute top-0 right-0 p-6 opacity-[0.05] group-hover:opacity-100 transition-all">
                                    <Waves className="w-12 h-12 text-blue-600" />
                                </div>
                                <div>
                                    <span className="text-[9px] uppercase font-black tracking-[0.4em] text-blue-700/60 mb-2 block">Fork {i + 1}</span>
                                    <h4 className="text-2xl font-serif font-black text-blue-100 group-hover:text-white transition-colors">{c}</h4>
                                </div>
                                <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-blue-900 group-hover:text-blue-500 transition-colors">
                                    <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                                    Sail Towards
                                </div>
                            </motion.button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

const NavigatorStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-slate-400">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-blue-500 transition-colors uppercase whitespace-nowrap">{value}</p>
    </div>
);
