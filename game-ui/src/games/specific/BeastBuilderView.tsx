import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Flame,
    Wind,
    Zap,
    Activity,
    Shield,
    Dna,
    ChevronRight,
    TrendingUp,
    Skull,
    Star,
    Skull as SkullIcon,
    Crown,
    Waves,
    Grape,
    Sparkles
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const BeastBuilderView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        vitality = 10,
        resonance = 10,
        form = 'The Egg',
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
            console.error("Binder communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#050a05] text-[#bef264] font-mono p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Primal Aether overlay */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_30%,#14532d_0%,transparent_100%)] opacity-40 blur-[120px]" />
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/dark-matter.png')] opacity-20" />
            </div>

            {/* Header - Binder HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-8 bg-black/40 backdrop-blur-2xl p-8 rounded-[2rem]">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-lime-900 rounded-3xl border border-lime-500/20 shadow-[0_0_40px_rgba(163,230,53,0.1)]">
                        <Dna className="w-8 h-8 text-lime-400 animate-spin-slow" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">Aetheric <span className="text-lime-500">Menagerie</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-lime-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-lime-500/30 italic">Incubation Level: {form.toUpperCase()} // Stabilizers: ON</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <BeastStat label="Vitality" value={`${vitality}%`} icon={<Flame className="w-4 h-4 text-orange-500" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <BeastStat label="Resonance" value={`${resonance}%`} icon={<Zap className="w-4 h-4 text-cyan-400" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <BeastStat label="Form" value={form} icon={<Waves className="w-4 h-4 text-lime-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Evolution Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, filter: 'blur(10px)' }}
                        animate={{ opacity: 1, filter: 'blur(0px)' }}
                        className="flex-grow bg-[#061406]/60 border border-lime-500/10 rounded-[2.5rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.05]">
                            <Grape className="w-32 h-32 text-lime-500" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-lime-900 uppercase tracking-[0.8em]">
                                <Activity className="w-4 h-4" /> Genetic_Sequence_Alpha
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-lime-50 italic selection:bg-lime-500/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0 border-l-2 border-lime-500/20 pl-10 hover:border-lime-500 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Essence Actions */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((essence: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(essence)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-[#0a1f0a] border border-lime-500/20 rounded-xl hover:bg-lime-900 hover:border-lime-500 transition-all text-[11px] font-black uppercase tracking-[0.2em] text-lime-500 hover:text-white flex items-center gap-3 group shadow-xl"
                                >
                                    <Sparkles className="w-3 h-3 text-lime-400 opacity-0 group-hover:opacity-100 transition-all" />
                                    {essence}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-lime-500/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Weave your intent into the genetic code..."
                                className="w-full bg-black border border-lime-500/10 rounded-2xl py-8 px-12 focus:outline-none focus:border-lime-500 transition-all text-lime-400 placeholder:text-lime-900 text-2xl font-light italic text-center shadow-inner shadow-lime-900/40"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-lime-600 text-black rounded-xl flex items-center justify-center hover:bg-lime-400 transition-all shadow-2xl"
                            >
                                <Zap className={`w-8 h-8 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Synthesis Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#061406] border border-lime-500/10 rounded-[2.5rem] p-10 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-lime-900 mb-10 flex items-center gap-2 border-b border-lime-500/5 pb-5">
                            <TrendingUp className="w-4 h-4" /> Synthesis_Diagnostics
                        </h3>

                        <div className="space-y-12">
                            <SynthesisMeter label="Biological Integrity" value={vitality} color="bg-lime-500" />
                            <SynthesisMeter label="Soul Convergence" value={resonance} color="bg-cyan-500" />
                            <SynthesisMeter label="Mutation Stability" value={85} color="bg-orange-500" />
                        </div>

                        <div className="mt-14 p-8 bg-lime-900/20 border border-lime-500/10 rounded-3xl flex items-start gap-5">
                            <Shield className="w-6 h-6 text-lime-500 opacity-20 mt-1" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-lime-900 italic text-center w-full">
                                "The Binder does not create; they merely suggest the path. The beast chooses the form."
                            </p>
                        </div>
                    </div>

                    <div className="bg-lime-900/5 border border-lime-500/5 rounded-[2.5rem] p-8 flex flex-col items-center justify-center gap-4 text-lime-900">
                        <Dna className="w-10 h-10 opacity-10 animate-spin-slow" />
                        <span className="text-[8px] font-black uppercase tracking-[0.6em] text-center">Transmission Scrambled</span>
                    </div>
                </div>
            </div>

            {status === 'ascended' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Crown className="w-24 h-24 text-lime-400 mx-auto mb-10 shadow-[0_0_60px_rgba(163,230,53,0.3)] animate-bounce" />
                        <h2 className="text-6xl font-black italic tracking-tighter text-white mb-6 uppercase leading-none">Aetheric <br /><span className="text-lime-500">Ascension</span></h2>
                        <p className="text-lime-900 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">The creature has broken the bonds of mortality. It has become a constellation in the cosmic menagerie.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-lime-600 text-black font-black uppercase tracking-[0.4em] hover:bg-white transition-all shadow-2xl rounded-2xl"
                        >
                            Reset Hatchery
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const BeastStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group cursor-help">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest text-[#bef264]">{label}</span>
        </div>
        <p className="text-2xl font-black italic text-white tracking-tighter group-hover:text-lime-400 transition-colors uppercase">{value}</p>
    </div>
);

const SynthesisMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-lime-900">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-lg`}
            />
        </div>
    </div>
);
