import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    Thermometer,
    Zap,
    Activity,
    Box,
    Database,
    ChevronRight,
    FlaskConical,
    Microscope,
    Pipette,
    AlertCircle,
    Dna
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const MicroMysteriesView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        magnification = 'Cellular',
        clarity = 10,
        anomaly = 'None',
        stability = 100,
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
            console.error("Lens communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#022c22] text-[#6ee7b7] font-mono p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Cellular background pattern */}
            <div className="absolute inset-0 opacity-[0.05] pointer-events-none bg-[radial-gradient(#6ee7b7_1px,transparent_1px)] bg-[size:20px_20px]" />

            {/* Header - The Lens HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b-2 border-[#10b981]/20 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-[#064e3b] rounded-lg border border-[#10b981]/40 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                        <Microscope className="w-8 h-8 text-[#10b981]" />
                    </div>
                    <div>
                        <h1 className="text-xl font-black tracking-[0.2em] text-white uppercase italic">Quant-Investigation // <span className="text-[#10b981]">{magnification}</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-[#10b981]/40 italic">System Ready // Anomaly detected</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8 bg-[#064e3b]/80 px-8 py-4 rounded-xl border border-[#10b981]/10 backdrop-blur-xl">
                    <MicroStat icon={<Search className="w-4 h-4 text-[#10b981]" />} label="Clarity" value={`${clarity}%`} />
                    <div className="w-px h-8 bg-white/5" />
                    <MicroStat icon={<Activity className="w-4 h-4 text-emerald-400" />} label="Stability" value={`${stability}%`} />
                    <div className="w-px h-8 bg-white/5" />
                    <MicroStat icon={<Box className="w-4 h-4 text-cyan-400" />} label="Anomaly" value={anomaly} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Micro Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 1.02 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-[#064e3b]/40 border border-[#10b981]/10 rounded-2xl p-10 relative overflow-hidden backdrop-blur-md flex flex-col justify-center shadow-inner"
                    >
                        {/* Scanline effect */}
                        <div className="absolute inset-0 bg-[linear-gradient(rgba(110,231,183,0)_50%,rgba(110,231,183,0.02)_50%)] bg-[size:100%_4px] pointer-events-none" />

                        <div className="relative z-10">
                            <div className="flex items-center gap-2 mb-8 text-[11px] font-black text-[#10b981]/30 uppercase tracking-[0.6em]">
                                <Database className="w-4 h-4" /> Microscope_Observation_Stream
                            </div>

                            <p className="text-xl md:text-2xl font-light leading-relaxed text-emerald-50 selection:bg-[#10b981]/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-6 last:mb-0 border-l-2 border-[#10b981]/10 pl-10 hover:border-[#10b981] transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Investigation Tools */}
                    <div className="flex flex-col gap-5">
                        <div className="flex flex-wrap gap-2 justify-center">
                            {available_actions.map((tool: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(tool)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-[#065f46] border border-[#10b981]/20 rounded-md hover:bg-[#10b981] hover:text-[#022c22] transition-all text-[10px] font-black uppercase tracking-widest text-[#6ee7b7] flex items-center gap-3 group shadow-xl"
                                >
                                    <Pipette className="w-3 h-3 opacity-30 group-hover:opacity-100 transition-all" />
                                    {tool}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-[#10b981] rounded-xl blur opacity-5 group-focus-within:opacity-20 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Execute subatomic directive..."
                                className="w-full bg-black/80 border border-[#10b981]/20 rounded-xl py-6 px-10 focus:outline-none focus:border-[#10b981] transition-all text-white placeholder:text-[#064e3b] text-lg uppercase font-bold"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-14 h-14 bg-[#10b981] text-[#022c22] rounded-lg flex items-center justify-center hover:bg-white transition-all shadow-xl"
                            >
                                <Zap className={`w-7 h-7 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Lab Diagnostics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#064e3b]/30 border border-[#10b981]/10 rounded-2xl p-8 backdrop-blur-md shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-[#10b981]/30 mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                            <FlaskConical className="w-4 h-4" /> Lab_Analysis
                        </h3>

                        <div className="space-y-8">
                            <LabMeter label="Sample Integrity" value={98} color="bg-[#10b981]" />
                            <LabMeter label="Cognitive Clarity" value={clarity} color="bg-cyan-500" />
                            <LabMeter label="Quantum Distortion" value={100 - stability} color="bg-red-500" />
                        </div>

                        <div className="mt-12 p-6 bg-[#10b981]/5 border border-[#10b981]/10 rounded-xl flex items-start gap-4">
                            <Dna className="w-5 h-5 text-[#10b981] opacity-20 mt-1 animate-spin-slow" />
                            <p className="text-[9px] uppercase font-black tracking-widest leading-loose text-[#10b981]/40 italic">
                                "Observation is an act of creation. The deeper you look, the more the world pushes back."
                            </p>
                        </div>
                    </div>

                    <div className="bg-[#064e3b]/10 border border-[#10b981]/5 rounded-2xl p-8 flex flex-col items-center justify-center gap-4 text-[#10b981]/10">
                        <Search className="w-12 h-12 opacity-10 animate-pulse" />
                        <span className="text-[9px] font-black uppercase tracking-[0.5em] text-center">Spectral Signature Locked</span>
                    </div>
                </div>
            </div>

            {status === 'solved' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center border-2 border-[#10b981]/20 p-12 rounded-3xl"
                    >
                        <AlertCircle className="w-20 h-20 text-[#10b981] mx-auto mb-8 shadow-[0_0_50px_rgba(16,185,129,0.5)]" />
                        <h2 className="text-5xl font-black italic tracking-tighter text-white mb-4 uppercase">Case Solved</h2>
                        <p className="text-[#10b981]/60 mb-12 font-bold leading-relaxed tracking-widest uppercase text-sm">The subatomic truth has been synthesized. Sample archived.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-16 py-5 bg-[#10b981] rounded-xl text-[#022c22] font-black uppercase tracking-[0.3em] hover:bg-white transition-all shadow-2xl"
                        >
                            New Investigation
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const MicroStat = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="text-center">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest">{label}</span>
        </div>
        <p className="text-xl font-black italic text-white tracking-tighter">{value}</p>
    </div>
);

const LabMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-3">
        <div className="flex justify-between items-center text-[9px] font-black uppercase tracking-[0.2em] text-[#10b981]/40">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_10px_rgba(16,185,129,0.3)]`}
            />
        </div>
    </div>
);
