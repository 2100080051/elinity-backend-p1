import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Box,
    Cpu,
    Activity,
    Layers,
    Maximize2,
    Zap,
    ChevronRight,
    GitMerge,
    Grid,
    Trophy,
    Hammer,
    Wind
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const PuzzleArchitectView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        logic_flow = 10,
        assembly = 0,
        complexity = 'Basic',
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
            console.error("Logician communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#f8fafc] text-[#334155] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Minimalist Grid Background */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none opacity-40" />

            {/* Header - Logic HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-indigo-100 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-200">
                        <Box className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight text-slate-800 uppercase italic">Architectural Core</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400">Logic Stream Active // {complexity} Mode</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8 bg-white px-8 py-4 rounded-3xl border border-slate-100 shadow-sm backdrop-blur-md">
                    <StatItem icon={<Cpu className="w-4 h-4 text-indigo-500" />} label="Logic Flow" value={`${logic_flow}%`} />
                    <div className="w-px h-8 bg-slate-100" />
                    <StatItem icon={<Layers className="w-4 h-4 text-cyan-500" />} label="Assembly" value={`${assembly}%`} />
                    <div className="w-px h-8 bg-slate-100" />
                    <StatItem icon={<Activity className="w-4 h-4 text-emerald-500" />} label="Integrity" value="Stable" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Construction Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-white border border-slate-200 rounded-[2.5rem] p-12 relative overflow-hidden shadow-xl shadow-slate-200/50 flex flex-col"
                    >
                        <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50 rounded-bl-[100%] opacity-50" />

                        <div className="flex items-center gap-2 mb-8 text-[11px] font-bold text-indigo-400 uppercase tracking-[0.3em]">
                            <Maximize2 className="w-4 h-4" /> Structural_Diagnostic
                        </div>

                        <div className="prose prose-slate max-w-none text-slate-600 text-xl leading-relaxed font-light italic">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className="mb-6 last:mb-0 first-letter:text-4xl first-letter:font-bold first-letter:text-indigo-600 first-letter:mr-2 first-letter:float-left">
                                    {line}
                                </p>
                            ))}
                        </div>

                        {status === 'constructed' && (
                            <motion.div
                                initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
                                className="mt-auto p-6 bg-emerald-50 border border-emerald-100 rounded-3xl flex items-center gap-4 text-emerald-700 shadow-inner"
                            >
                                <Trophy className="w-8 h-8 text-emerald-500" />
                                <div>
                                    <h4 className="font-bold text-sm uppercase tracking-widest">Construction Verified</h4>
                                    <p className="text-xs opacity-70 italic">The structural integrity has reached maximum resonance.</p>
                                </div>
                            </motion.div>
                        )}
                    </motion.div>

                    {/* Architectural Inputs */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((node: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(node)}
                                    disabled={loading}
                                    className="px-6 py-2.5 bg-white border border-slate-200 rounded-2xl hover:bg-slate-50 hover:border-indigo-300 transition-all text-[11px] font-bold tracking-widest text-slate-500 hover:text-indigo-600 flex items-center gap-2 shadow-sm group"
                                >
                                    <GitMerge className="w-3 h-3 text-indigo-400 group-hover:rotate-90 transition-transform" />
                                    {node}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your logic to the matrix..."
                                className="w-full bg-white/80 border border-slate-200 rounded-3xl py-6 px-10 focus:outline-none focus:border-indigo-400 transition-all text-slate-700 placeholder:text-slate-300 text-lg font-light italic shadow-lg"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 p-4 bg-indigo-600 text-white rounded-2xl hover:bg-indigo-700 transition-all shadow-xl shadow-indigo-100"
                            >
                                <Hammer className={`w-5 h-5 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Construction Map */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm">
                        <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-8 border-b border-slate-50 pb-4">
                            Blueprints & Metrics
                        </h3>

                        <div className="space-y-6">
                            <MetricRow label="Symmetry" value={`${logic_flow + 10}%`} />
                            <MetricRow label="Resonance" value={`${assembly + 15}%`} />
                            <MetricRow label="Node Stability" value="Optimal" />
                        </div>

                        <div className="mt-10 p-6 bg-slate-50 rounded-3xl border border-slate-100 flex items-start gap-4">
                            <Wind className="w-5 h-5 text-indigo-300 mt-1" />
                            <p className="text-[10px] uppercase font-bold tracking-widest leading-loose text-slate-400 italic">
                                Logic is not a line, but a loop. Observe the patterns before committing the node.
                            </p>
                        </div>
                    </div>

                    <div className="bg-indigo-600/5 border-2 border-dashed border-indigo-200 rounded-3xl flex flex-col items-center justify-center p-8 gap-4 text-indigo-300">
                        <Grid className="w-12 h-12 opacity-30 animate-spin-slow" />
                        <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-center">Rendering Structure...</span>
                    </div>
                </div>
            </div>

            {status === 'constructed' && (
                <div className="fixed inset-0 z-[100] bg-white/95 backdrop-blur-2xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Maximize2 className="w-20 h-20 text-indigo-600 mx-auto mb-8 animate-pulse" />
                        <h2 className="text-5xl font-bold tracking-tighter text-slate-800 mb-4 uppercase italic">World Finalized</h2>
                        <p className="text-slate-500 mb-10 font-light leading-relaxed">The logic you have paved is now the foundation of a new reality. The Logician acknowledges your brilliance.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-12 py-4 bg-slate-800 rounded-2xl text-white font-bold uppercase tracking-widest hover:bg-slate-700 transition-all shadow-2xl"
                        >
                            Begin New Design
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const StatItem = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="flex flex-col">
        <div className="flex items-center gap-2 mb-1">
            {icon}
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#94a3b8]">{label}</span>
        </div>
        <span className="text-xl font-bold text-slate-800 italic tracking-tighter">{value}</span>
    </div>
);

const MetricRow = ({ label, value }: { label: string, value: string }) => (
    <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400">{label}</span>
        <span className="text-xs font-bold text-slate-700 italic underline decoration-indigo-200 underline-offset-4">{value}</span>
    </div>
);
