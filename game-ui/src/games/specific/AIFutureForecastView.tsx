import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Database,
    Cpu,
    Zap,
    Activity,
    Globe,
    Layers,
    ChevronRight,
    TrendingUp,
    AlertTriangle,
    Radio,
    BarChart3,
    Dna
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const AIFutureForecastView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        probability = 50,
        stability = 100,
        era = 'Unknown',
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
        <div className="min-h-screen bg-[#000505] text-[#00f2ff] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Holographic scanning effect */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-full bg-[linear-gradient(transparent_0%,rgba(0,242,255,0.05)_50%,transparent_100%)] bg-[size:100%_4px] animate-scan" style={{ animationDuration: '4s' }} />
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(0,242,255,0.05),transparent)]" />
            </div>

            {/* Header - Chronos HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-[#00f2ff]/20 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-cyan-500/10 rounded-lg border border-cyan-500/30 shadow-[0_0_15px_rgba(0,242,255,0.2)]">
                        <Cpu className="w-6 h-6 text-cyan-400" />
                    </div>
                    <div>
                        <h1 className="text-xl font-black tracking-[0.3em] text-white uppercase italic">Timeline Simulation // <span className="text-cyan-400 font-bold">{era}</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.5em] text-cyan-500/50 italic">CHRONOS_OS ACTIVE // CAUSALITY_SCAN: PASS</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8 bg-black/80 px-8 py-3 rounded-lg border border-[#00f2ff]/10 backdrop-blur-xl">
                    <DataStat icon={<TrendingUp className="w-4 h-4 text-cyan-400" />} label="Causality" value={`${probability}%`} sub="Convergence" />
                    <div className="w-px h-8 bg-white/5" />
                    <DataStat icon={<Activity className="w-4 h-4 text-amber-400" />} label="Stability" value={`${stability}%`} sub="Cohesion" />
                    <div className="w-px h-8 bg-white/5" />
                    <DataStat icon={<Globe className="w-4 h-4 text-emerald-400" />} label="Bio-Sphere" value="99.2%" sub="Viability" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Simulation Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-[#001a1a]/40 border border-[#00f2ff]/10 rounded-xl p-10 relative overflow-hidden backdrop-blur-md flex flex-col"
                    >
                        <div className="absolute top-0 left-0 w-2 h-full bg-cyan-500/20" />

                        <div className="relative z-10">
                            <div className="flex items-center gap-2 mb-8 text-[10px] font-black text-cyan-500/40 uppercase tracking-[0.8em]">
                                <Database className="w-4 h-4" /> Timeline_Event_Stream
                            </div>

                            <p className="text-xl md:text-2xl font-light leading-relaxed text-cyan-50/80 uppercase selection:bg-cyan-500/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-6 last:mb-0 border-l-2 border-cyan-500/10 pl-10 hover:border-cyan-500 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>

                        {/* Probability graph visual placeholder */}
                        <div className="mt-auto h-24 flex items-end gap-1 opacity-20">
                            {[...Array(40)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    animate={{ height: `${30 + (Math.random() * 70)}%` }}
                                    transition={{ repeat: Infinity, duration: 2, delay: i * 0.05 }}
                                    className="flex-1 bg-cyan-500 rounded-t-sm"
                                />
                            ))}
                        </div>
                    </motion.div>

                    {/* Simulation Controls */}
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-wrap gap-2 justify-center">
                            {available_actions.map((sim: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(sim)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-black border border-cyan-500/10 rounded-lg hover:bg-cyan-500/10 hover:border-cyan-400 transition-all text-[10px] font-black uppercase tracking-widest text-cyan-500/60 hover:text-white flex items-center gap-3 group"
                                >
                                    <Layers className="w-3 h-3 opacity-30 group-hover:opacity-100 transition-all" />
                                    {sim}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-cyan-500 rounded-lg blur opacity-5 group-focus-within:opacity-20 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Adjust timeline parameters..."
                                className="relative w-full bg-black/80 border border-cyan-500/20 rounded-xl py-6 px-10 focus:outline-none focus:border-cyan-400 transition-all text-white placeholder:text-cyan-950 font-mono text-lg uppercase"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-14 h-14 bg-cyan-500 text-black rounded-lg flex items-center justify-center hover:bg-cyan-400 transition-all shadow-[0_0_20px_rgba(0,242,255,0.3)]"
                            >
                                <Zap className={`w-7 h-7 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Analytical Data */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-black/60 border border-cyan-500/10 rounded-xl p-8 backdrop-blur-md">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-cyan-500/30 mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                            <BarChart3 className="w-4 h-4" /> Simulation_Telemetry
                        </h3>

                        <div className="space-y-8">
                            <TimelineMetric label="蝴蝶效应 (Butterfly Effect)" value={15} color="bg-cyan-500" />
                            <TimelineMetric label="线性收敛 (Linear Convergence)" value={82} color="bg-emerald-500" />
                            <TimelineMetric label="量子纠缠 (Quantum Entanglement)" value={44} color="bg-purple-500" />
                        </div>

                        <div className="mt-12 p-6 bg-cyan-500/5 border border-cyan-500/10 rounded-lg flex items-start gap-4">
                            <Radio className="w-5 h-5 text-cyan-400 opacity-20 mt-1" />
                            <p className="text-[9px] uppercase font-bold tracking-widest leading-loose text-cyan-500/40">
                                Warning: Major events are fixed in the simulation. Peripheral adjustments will yield minimal systemic shift unless resonance hits 100%.
                            </p>
                        </div>
                    </div>

                    <div className="bg-[#001a1a]/10 border border-cyan-500/5 rounded-xl p-8 flex flex-col items-center justify-center gap-4 text-cyan-500/10">
                        <Dna className="w-12 h-12 opacity-10 animate-pulse" />
                        <span className="text-[10px] font-black uppercase tracking-[0.5em] text-center">Genetic Baseline Found</span>
                    </div>
                </div>
            </div>

            {status === 'collapsed' && (
                <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-2xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center border-2 border-red-500/20 p-12 rounded-2xl bg-black"
                    >
                        <AlertTriangle className="w-20 h-20 text-red-500 mx-auto mb-8 animate-pulse shadow-[0_0_50px_rgba(239,68,68,0.5)]" />
                        <h2 className="text-5xl font-black italic tracking-tighter text-white mb-4 uppercase">Timeline Null</h2>
                        <p className="text-red-500/60 mb-12 font-bold leading-relaxed tracking-widest uppercase text-sm">Causality has reached zero. The simulation has been terminated to prevent local memory corruption.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-16 py-5 bg-red-600 rounded text-white font-black uppercase tracking-[0.4em] hover:bg-red-500 transition-all"
                        >
                            Reset OS
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const DataStat = ({ icon, label, value, sub }: { icon: React.ReactNode, label: string, value: string, sub: string }) => (
    <div className="text-center">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest">{label}</span>
        </div>
        <p className="text-xl font-black italic text-white tracking-tighter">{value}</p>
        <p className="text-[7px] uppercase font-bold text-cyan-500/30 tracking-widest">{sub}</p>
    </div>
);

const TimelineMetric = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-3">
        <div className="flex justify-between items-center text-[9px] font-black uppercase tracking-[0.2em] text-cyan-500/40">
            <span>{label}</span>
            <span>{value}%</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_10px_rgba(0,242,255,0.2)]`}
            />
        </div>
    </div>
);
