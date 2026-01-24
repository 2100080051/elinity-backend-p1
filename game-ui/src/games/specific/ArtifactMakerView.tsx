import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Hammer,
    Box,
    Zap,
    Shield,
    Sparkles,
    Database,
    ChevronRight,
    TrendingUp,
    History,
    GalleryVertical,
    Layers,
    Archive
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const ArtifactMakerView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        integrity = 100,
        value = 0,
        stage = 'Raw Material',
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
            console.error("Curator communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#fafafa] text-[#171717] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Gallery spotlight effect */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(0,0,0,0.03),transparent)] pointer-events-none" />
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1px] h-full bg-black/[0.02]" />

            {/* Header - Curator HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-black/5 pb-8">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-white rounded-full shadow-2xl border border-black/5">
                        <Archive className="w-8 h-8 text-black" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-light tracking-tight text-black">Eternal <span className="font-black italic">Legacy</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-black animate-pulse" />
                            <span className="text-[10px] uppercase font-black tracking-widest text-black/30 italic">Vault Status: Accessioning // {stage}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-12">
                    <ArtifactStat label="Integrity" value={`${integrity}%`} sub="Core Strength" color="text-black" />
                    <div className="w-px h-12 bg-black/5" />
                    <ArtifactStat label="Historical Value" value={value.toString()} sub="Legacy Points" color="text-amber-600" />
                    <div className="w-px h-12 bg-black/5" />
                    <div className="flex flex-col items-center">
                        <span className="text-[9px] uppercase font-black tracking-widest text-black/20 mb-2">Stage</span>
                        <span className="px-5 py-1.5 bg-black text-white rounded-full text-[10px] font-black uppercase tracking-tighter shadow-lg">{stage}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Crafting Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-white border border-black/5 rounded-[3rem] p-16 relative overflow-hidden flex flex-col justify-center shadow-xl shadow-black/[0.02]"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.02]">
                            <GalleryVertical className="w-48 h-48" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto text-center">
                            <div className="flex items-center justify-center gap-2 mb-12 text-[11px] font-black text-black/10 uppercase tracking-[0.8em]">
                                <History className="w-4 h-4" /> Provenance_Establishment
                            </div>

                            <p className="text-3xl md:text-4xl font-light leading-relaxed text-neutral-800 italic selection:bg-black/5">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Craftsman Inputs */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((action: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(action)}
                                    disabled={loading}
                                    className="px-8 py-3.5 bg-white border border-black/10 rounded-2xl hover:bg-black hover:text-white transition-all text-[11px] font-black uppercase tracking-widest text-black/40 flex items-center gap-3 group shadow-lg"
                                >
                                    <Sparkles className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all scale-0 group-hover:scale-100" />
                                    {action}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-2 bg-black/5 rounded-[2.5rem] blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Refine the design with your intent..."
                                className="relative w-full bg-white border border-black/10 rounded-[2rem] py-8 px-12 focus:outline-none focus:border-black transition-all text-black placeholder:text-black/5 text-2xl font-light italic text-center shadow-2xl"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-black text-white rounded-2xl flex items-center justify-center hover:bg-neutral-800 transition-all shadow-xl"
                            >
                                <Hammer className={`w-8 h-8 ${loading ? 'animate-bounce' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Technical Diagnostics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white border border-black/5 rounded-[3rem] p-10 shadow-2xl shadow-black/[0.01]">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-black/10 mb-10 flex items-center gap-2 border-b border-black/5 pb-5">
                            <Layers className="w-4 h-4" /> Technical_Specification
                        </h3>

                        <div className="space-y-12">
                            <SpecMeter label="Structural Cohesion" value={integrity} color="bg-black" />
                            <SpecMeter label="Symbolic Depth" value={Math.min(100, (value / 5000) * 100)} color="bg-amber-600" />
                            <SpecMeter label="Aesthetic Finish" value={85} color="bg-zinc-400" />
                        </div>

                        <div className="mt-14 p-8 bg-black/[0.02] border border-black/5 rounded-[2rem] flex items-start gap-5">
                            <Box className="w-6 h-6 text-black opacity-10 mt-1" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-black/20 italic text-center w-full">
                                "The Curator observes every stroke. Perfection is the only path to the eternal display."
                            </p>
                        </div>
                    </div>

                    <div className="bg-black/[0.01] border border-black/5 rounded-[3rem] p-8 flex flex-col items-center justify-center gap-4 text-black/5">
                        <GalleryVertical className="w-12 h-12 opacity-10 animate-pulse" />
                        <span className="text-[8px] font-black uppercase tracking-[0.5em] text-center">Collection Sync Active</span>
                    </div>
                </div>
            </div>

            {status === 'archived' && (
                <div className="fixed inset-0 z-[100] bg-white/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Archive className="w-24 h-24 text-black mx-auto mb-10 shadow-2xl" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-black mb-6 uppercase">Preserved</h2>
                        <p className="text-black/40 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">Your creation has been deemed worthy of the Eternal Vault. It shall outlast empires and stars.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-black rounded-2xl text-white font-black uppercase tracking-[0.3em] hover:bg-neutral-800 transition-all shadow-2xl"
                        >
                            Return to Crafting
                        </button>
                    </motion.div>
                </div>
            )}

            {status === 'destroyed' && (
                <div className="fixed inset-0 z-[100] bg-black flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <TrendingUp className="w-24 h-24 text-red-600 mx-auto mb-10 rotate-180" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-6 uppercase">Failed</h2>
                        <p className="text-white/20 mb-14 font-black leading-relaxed tracking-[0.3em] uppercase text-sm">The material could not withstand your vision. The fragments have been recycled.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-white rounded-2xl text-black font-black uppercase tracking-[0.4em] hover:bg-neutral-200 transition-all shadow-2xl"
                        >
                            Start Over
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const ArtifactStat = ({ label, value, sub, color }: { label: string, value: string, sub: string, color: string }) => (
    <div className="text-center">
        <p className="text-[9px] uppercase font-black text-black/10 tracking-widest mb-1">{label}</p>
        <p className={`text-3xl font-black italic tracking-tighter ${color}`}>{value}</p>
        <p className="text-[8px] uppercase font-bold text-black/20 tracking-tight">{sub}</p>
    </div>
);

const SpecMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-black/20">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-black/[0.03] rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-lg`}
            />
        </div>
    </div>
);
