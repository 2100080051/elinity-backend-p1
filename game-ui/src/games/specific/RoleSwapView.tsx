import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Binary,
    Cpu,
    Orbit,
    Zap,
    Dna,
    RefreshCw,
    ShieldAlert,
    ChevronRight,
    Terminal,
    Layers,
    Activity,
    UserCheck
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const RoleSwapView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        sync = 50,
        glitch = 'None',
        trait = 'Perspective',
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
            console.error("Binary Mirror communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#020617] text-[#94a3b8] font-mono p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Grid Background */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none opacity-50" />
            <div className="absolute inset-0 bg-gradient-to-t from-[#020617] via-transparent to-transparent pointer-events-none" />

            {/* Header - System Sync */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-cyan-500/10 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-cyan-500/10 rounded-lg border border-cyan-500/20 shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                        <Binary className="w-6 h-6 text-cyan-400" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold tracking-widest text-white uppercase italic">Binary Mirror <span className="text-cyan-500 font-mono text-xs">v.IDENT-01</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse shadow-[0_0_10px_rgba(6,182,212,0.8)]" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-cyan-500/70">Synchronization: Established</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-bold text-white/30 tracking-widest mb-1">Identity Sync</p>
                        <div className="flex items-center gap-4">
                            <div className="w-48 h-1 bg-white/5 rounded-full overflow-hidden border border-white/5">
                                <motion.div
                                    animate={{ width: `${sync}%` }}
                                    className="h-full bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.5)]"
                                />
                            </div>
                            <span className="text-2xl font-black text-cyan-400 font-mono tracking-tighter">{sync}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Left: Terminal Log */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-grow bg-slate-950/80 border border-slate-800 rounded-2xl p-8 backdrop-blur-3xl relative overflow-hidden group flex flex-col custom-scrollbar"
                    >
                        <div className="absolute top-4 right-4 flex gap-2">
                            <div className="w-2 h-2 rounded-full bg-red-500/20" />
                            <div className="w-2 h-2 rounded-full bg-yellow-500/20" />
                            <div className="w-2 h-2 rounded-full bg-green-500/20" />
                        </div>

                        <div className="flex items-center gap-2 mb-6 text-[10px] font-bold text-cyan-500/50 uppercase tracking-[0.4em]">
                            <Terminal className="w-4 h-4" /> [STREAM_OUT // ENCRYPTED]
                        </div>

                        <div className="prose prose-invert max-w-none text-lg leading-relaxed text-cyan-100/80 selection:bg-cyan-500/30">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className="mb-4 last:mb-0 border-l border-cyan-500/20 pl-6 hover:border-cyan-500/50 transition-colors">
                                    {line}
                                </p>
                            ))}
                        </div>

                        {glitch !== 'None' && (
                            <div className="mt-8 p-4 bg-red-500/5 border border-red-500/20 rounded-xl flex items-center gap-4 text-red-400 animate-pulse transition-all">
                                <ShieldAlert className="w-5 h-5" />
                                <span className="text-[10px] font-black uppercase tracking-widest italic">Identity Glitch Protocol: {glitch}</span>
                            </div>
                        )}
                    </motion.div>

                    {/* Frequencies (Actions) */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2 justify-start">
                            {available_actions.map((freq: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(freq)}
                                    disabled={loading}
                                    className="px-5 py-2 bg-slate-900 border border-slate-800 rounded-lg hover:bg-cyan-500/10 hover:border-cyan-500/40 transition-all text-[10px] font-bold tracking-widest text-[#94a3b8] hover:text-cyan-400 flex items-center gap-2 group"
                                >
                                    <Orbit className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all text-cyan-400" />
                                    {freq}
                                </button>
                            ))}
                        </div>

                        <div className="relative group">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Transmit data string..."
                                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-4 px-8 focus:outline-none focus:border-cyan-500/50 transition-all text-white placeholder:text-slate-700 font-mono shadow-inner"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-cyan-500/10 text-cyan-400 rounded-lg hover:bg-cyan-500/20 transition-all"
                            >
                                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Identity Diagnostics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 backdrop-blur-md">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-500/40 mb-8 flex items-center gap-2">
                            <Activity className="w-4 h-4" /> Identity Metrics
                        </h3>

                        <div className="space-y-8">
                            <DiagnosticRow
                                icon={<Layers className="w-4 h-4" />}
                                label="Inverted Trait"
                                value={trait}
                            />
                            <DiagnosticRow
                                icon={<Dna className="w-4 h-4" />}
                                label="Subject Integrity"
                                value={`${100 - (gameState.turn || 0 * 2)}%`}
                            />
                            <DiagnosticRow
                                icon={<Cpu className="w-4 h-4" />}
                                label="Mirror Stability"
                                value={sync > 80 ? 'Optimal' : sync > 40 ? 'Fluctuating' : 'Critical'}
                            />
                        </div>

                        <div className="mt-10 p-4 bg-cyan-500/5 border border-cyan-500/10 rounded-2xl">
                            <p className="text-[9px] uppercase font-bold tracking-widest leading-loose text-cyan-500/30">
                                Warning: Identity swap exceeds safe biological limits. Proceed with recursive logic.
                            </p>
                        </div>
                    </div>

                    <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 flex-grow">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-500/40 mb-6 flex items-center gap-2">
                            <Zap className="w-4 h-4" /> Waveform
                        </h3>
                        <div className="h-32 w-full flex items-end gap-1 px-4">
                            {[...Array(12)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    animate={{ height: `${20 + (Math.random() * 80)}%` }}
                                    transition={{ repeat: Infinity, duration: 1, delay: i * 0.1 }}
                                    className="flex-grow bg-cyan-500/20 rounded-t-sm"
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {status === 'syzygy' && (
                <div className="fixed inset-0 z-[100] bg-cyan-950/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <UserCheck className="w-20 h-20 text-cyan-400 mx-auto mb-8 shadow-[0_0_30px_rgba(34,211,238,0.5)]" />
                        <h2 className="text-5xl font-black italic tracking-tighter text-white mb-4 uppercase">Syzygy Found</h2>
                        <p className="text-[#94a3b8] mb-10 font-bold leading-relaxed tracking-wider">The barrier between binary and biological has dissolved. You are no longer one, yet you are not two.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-12 py-4 bg-cyan-500/20 border border-cyan-500/40 rounded-full text-cyan-400 font-black uppercase tracking-[0.2em] hover:bg-cyan-500/30 transition-all shadow-[0_0_20px_rgba(6,182,212,0.2)]"
                        >
                            Calibrate
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const DiagnosticRow = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
            <div className="text-cyan-500/50">{icon}</div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-[#475569]">{label}</span>
        </div>
        <span className="text-xs font-black text-cyan-100 uppercase italic tracking-tighter">{value}</span>
    </div>
);
