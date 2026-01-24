import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumText } from '../../components/shared/PremiumComponents';
import { Scale, Target, Hexagon, Activity, Cpu, Crosshair, AlertTriangle, ShieldAlert } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const AlignmentGameView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    // AXES: order (0-100), light (0-100)
    const order = gameState.order ?? 50;
    const light = gameState.light ?? 50;
    const integrity = gameState.vessel_integrity ?? 100;
    const dissonance = gameState.dissonance ?? 0;
    const scenario = gameState.scenario || "The aperture is closed. Waiting for the Zenith.";
    const verdict = gameState.verdict || "Soul Analysis in progress...";
    const archetype = gameState.archetype || "The Unawakened";
    const options = gameState.options || [];

    const handleChoice = async (choice: string) => {
        if (!sessionId || !gameSlug) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'choice', choice);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error("Neural interruption:", e); }
        setLoading(false);
    };

    return (
        <PremiumGameLayout
            title="Morphological Alignment"
            subtitle={`integrity: ${integrity}%`}
            icon={Target}
            backgroundVar="fractal"
            guideText="Resolve the apertures. The Fractal Zenith calculates your soul's geometry. beware of dissonance—it de-syncs your vessel integrity."
        >
            <div className="flex flex-col h-full gap-8 relative p-6 md:p-10 overflow-hidden">

                {/* --- TOP HUD --- */}
                <div className="flex justify-between items-start z-30">
                    <div className="flex flex-col gap-2">
                        <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl backdrop-blur-xl flex items-center gap-3">
                            <Cpu className={`w-4 h-4 ${integrity > 50 ? 'text-cyan-400' : 'text-red-500 animate-pulse'}`} />
                            <div className="flex flex-col">
                                <span className="text-[8px] text-white/30 uppercase tracking-[0.3em] font-black">Vessel Integrity</span>
                                <div className="h-1 w-32 bg-white/10 rounded-full mt-1 overflow-hidden">
                                    <motion.div animate={{ width: `${integrity}%` }} className={`h-full ${integrity > 50 ? 'bg-cyan-500' : 'bg-red-600'} shadow-[0_0_10px_rgba(6,182,212,0.5)]`} />
                                </div>
                            </div>
                        </div>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="px-6 py-3 bg-black/60 border-2 border-white/5 rounded-2xl backdrop-blur-3xl flex flex-col items-center"
                    >
                        <span className="text-[9px] text-orange-500/80 uppercase tracking-[0.5em] font-black mb-1">Current Archetype</span>
                        <span className="text-xl font-black text-white tracking-tight">{archetype}</span>
                    </motion.div>
                </div>

                {/* --- MAIN GEOMETRY INTERFACE --- */}
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch min-h-0">

                    {/* LEFT: Moral Compass Graph (4 cols) */}
                    <div className="lg:col-span-4 flex flex-col gap-6">
                        <div className="flex-1 bg-white/5 border border-white/10 rounded-[2.5rem] p-8 backdrop-blur-xl flex flex-col relative overflow-hidden group">
                            <div className="text-center mb-6">
                                <Hexagon className="w-6 h-6 text-white/20 mx-auto mb-2" />
                                <h3 className="text-[10px] uppercase tracking-[0.4em] text-white/40 font-black">Alignment Geometry</h3>
                            </div>

                            {/* The 2D Graph */}
                            <div className="flex-1 relative border border-white/10 rounded-xl bg-black/20 m-4">
                                {/* Grid Lines */}
                                <div className="absolute inset-0 grid grid-cols-2 grid-rows-2">
                                    <div className="border border-white/5" />
                                    <div className="border border-white/5" />
                                    <div className="border border-white/5" />
                                    <div className="border border-white/5" />
                                </div>
                                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                    <div className="w-full h-[1px] bg-white/10" />
                                    <div className="h-full w-[1px] bg-white/10" />
                                </div>

                                {/* Axis Labels */}
                                <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[8px] uppercase tracking-widest text-cyan-400 font-black">Light (Altruism)</span>
                                <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[8px] uppercase tracking-widest text-red-500 font-black">Dark (Ego)</span>
                                <span className="absolute top-1/2 -left-8 -translate-y-1/2 -rotate-90 text-[8px] uppercase tracking-widest text-white/40 font-black">Chaos</span>
                                <span className="absolute top-1/2 -right-10 -translate-y-1/2 rotate-90 text-[8px] uppercase tracking-widest text-white/40 font-black">Order</span>

                                {/* The Point */}
                                <motion.div
                                    animate={{ left: `${order}%`, bottom: `${light}%` }}
                                    className="absolute w-4 h-4 -ml-2 -mb-2 bg-white rounded-full shadow-[0_0_20px_#fff] z-20"
                                >
                                    <div className="absolute inset-0 rounded-full bg-white animate-ping opacity-20" />
                                </motion.div>
                            </div>

                            <div className="mt-8 space-y-2 px-4 text-center">
                                <div className="flex justify-between items-center text-[9px] uppercase tracking-widest text-white/40 font-bold">
                                    <span>Dissonance Level</span>
                                    <span className={dissonance > 50 ? 'text-red-500 animate-pulse' : ''}>{dissonance}%</span>
                                </div>
                                <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                    <motion.div animate={{ width: `${dissonance}%` }} className={`h-full ${dissonance > 50 ? 'bg-red-500' : 'bg-white/40'}`} />
                                </div>
                            </div>
                        </div>

                        {/* Verdict Panel */}
                        <div className="bg-black/40 border border-white/5 p-6 rounded-3xl backdrop-blur-md">
                            <div className="flex items-center gap-2 mb-3">
                                <Activity className="w-3 h-3 text-cyan-500" />
                                <span className="text-[10px] uppercase font-black tracking-widest text-white/40">Zenith Verdict</span>
                            </div>
                            <p className="text-sm font-serif italic text-white/60 leading-relaxed">"{verdict}"</p>
                        </div>
                    </div>

                    {/* RIGHT: The Trial Aperture (8 cols) */}
                    <div className="lg:col-span-8 flex flex-col gap-6">
                        <div className="flex-1 relative flex flex-col">
                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={scenario}
                                    initial={{ opacity: 0, x: 20, filter: 'blur(10px)' }}
                                    animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                                    exit={{ opacity: 0, x: -20, filter: 'blur(10px)' }}
                                    className="flex-1 bg-gradient-to-br from-white/[0.03] to-transparent border border-white/10 rounded-[3rem] p-12 overflow-y-auto"
                                >
                                    <div className="flex items-center gap-4 mb-8">
                                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-2xl">
                                            <AlertTriangle className="w-6 h-6 text-red-500" />
                                        </div>
                                        <span className="text-xs font-black uppercase tracking-[0.4em] text-red-500/80">Incoming Aperture</span>
                                    </div>
                                    <h2 className="text-2xl md:text-4xl text-white font-serif leading-snug lg:leading-normal">
                                        <PremiumText text={scenario} />
                                    </h2>
                                </motion.div>
                            </AnimatePresence>
                        </div>

                        {/* Options Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-48">
                            {options.map((opt: any, i: number) => (
                                <motion.button
                                    key={i}
                                    whileHover={{ scale: 1.02, y: -4 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => handleChoice(opt.label)}
                                    disabled={loading}
                                    className="group relative h-full bg-white/5 hover:bg-white/10 border border-white/10 rounded-3xl p-6 text-left transition-all overflow-hidden flex flex-col justify-between"
                                >
                                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-100 group-hover:rotate-12 transition-all">
                                        <Crosshair className="w-12 h-12 text-white" />
                                    </div>
                                    <span className="text-[9px] uppercase font-black tracking-[0.3em] text-white/30 group-hover:text-cyan-400">Resolution {i + 1}</span>
                                    <div>
                                        <h4 className="text-sm font-black text-white uppercase tracking-tight mb-1">{opt.label}</h4>
                                        <p className="text-[10px] text-white/40 font-serif line-clamp-2 leading-relaxed">{opt.description}</p>
                                    </div>
                                </motion.button>
                            ))}
                            {options.length === 0 && (
                                <div className="col-span-3 flex items-center justify-center bg-white/5 rounded-3xl animate-pulse">
                                    <span className="text-[10px] uppercase tracking-widest font-black text-white/20">Waiting for Moral Reconfiguration...</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* --- WARNING OVERLAYS --- */}
                <AnimatePresence>
                    {dissonance > 80 && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 pointer-events-none border-[12px] border-red-500/20 z-50 animate-pulse"
                        >
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 p-4 bg-red-600/90 text-white flex items-center gap-3 rounded-2xl backdrop-blur-3xl shadow-[0_0_50px_rgba(220,38,38,0.5)]">
                                <ShieldAlert size={24} />
                                <span className="text-xs font-black uppercase tracking-tighter">Critical Moral Dissonance Detected</span>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

            </div>
        </PremiumGameLayout>
    );
};
