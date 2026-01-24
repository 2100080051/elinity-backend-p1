import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield,
    Search,
    Zap,
    Lock,
    Unlock,
    AlertCircle,
    ChevronRight,
    Terminal,
    Activity,
    DollarSign,
    Briefcase,
    Crosshair
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const AIHeistView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        heat = 0,
        integrity = 100,
        loot = 0,
        objective = 'Awaiting Briefing',
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
            console.error("Broker communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#05080a] text-[#8fa7b3] font-mono p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Cyber Gradient */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,#0a1a24,transparent)] pointer-events-none opacity-50" />
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent opacity-20" />

            {/* Header - Mission HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-cyan-500/10 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-cyan-950/40 rounded border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.1)]">
                        <Lock className="w-6 h-6 text-cyan-400" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold tracking-[0.2em] text-white uppercase italic">Operation: {gameSlug?.toUpperCase()}</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-[10px] uppercase font-bold tracking-widest text-cyan-500/50">Objectives Loaded // Encryption active</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8 bg-black/40 px-6 py-3 rounded-xl border border-white/5 backdrop-blur-md">
                    <StatItem icon={<Activity className="w-4 h-4 text-red-500" />} label="Heat" value={`${heat}%`} color={heat > 70 ? 'text-red-500' : 'text-cyan-400'} />
                    <div className="w-px h-8 bg-white/10" />
                    <StatItem icon={<Shield className="w-4 h-4 text-blue-400" />} label="Security" value={`${integrity}%`} color="text-white" />
                    <div className="w-px h-8 bg-white/10" />
                    <StatItem icon={<DollarSign className="w-4 h-4 text-emerald-400" />} label="Loot" value={`$${loot.toLocaleString()}`} color="text-emerald-400" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Tactical Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-[#0a1217]/80 border border-cyan-900/30 rounded-lg p-8 backdrop-blur-xl relative overflow-hidden group flex flex-col"
                    >
                        <div className="absolute top-0 left-0 w-full h-0.5 bg-cyan-500/20" />

                        <div className="flex items-center gap-2 mb-6 text-[10px] font-bold text-cyan-500/40 uppercase tracking-[0.5em]">
                            <Terminal className="w-4 h-4" /> Tactical_Intel_Stream
                        </div>

                        <div className="prose prose-invert max-w-none text-cyan-50/80 text-lg leading-relaxed selection:bg-cyan-500/30 font-light">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className="mb-4 last:mb-0 border-l-2 border-cyan-500/10 pl-6 hover:border-cyan-500/40 transition-colors">
                                    {line}
                                </p>
                            ))}
                        </div>

                        {status === 'breached' && (
                            <motion.div
                                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                className="mt-8 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded flex items-center gap-4 text-emerald-400"
                            >
                                <Unlock className="w-5 h-5" />
                                <span className="text-xs font-bold uppercase tracking-widest">Vault Breached // Extraction Protocol Active</span>
                            </motion.div>
                        )}
                    </motion.div>

                    {/* Controls */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2">
                            {available_actions.map((tactic: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(tactic)}
                                    disabled={loading}
                                    className="px-5 py-2 bg-cyan-950/20 border border-cyan-500/20 rounded hover:bg-cyan-500/10 hover:border-cyan-500/50 transition-all text-[10px] font-bold tracking-widest text-cyan-400/70 hover:text-white flex items-center gap-2 group italic"
                                >
                                    <Crosshair className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all" />
                                    {tactic}
                                </button>
                            ))}
                        </div>

                        <div className="relative group">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Execute command..."
                                className="w-full bg-black/60 border border-cyan-900/30 rounded py-5 px-10 focus:outline-none focus:border-cyan-500/40 transition-all text-white placeholder:text-cyan-950 font-mono italic"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-cyan-500 text-black rounded hover:bg-cyan-400 transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)]"
                            >
                                <Zap className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Tactical Status */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#0a1217]/50 border border-white/5 rounded-xl p-8 backdrop-blur-md">
                        <h3 className="text-[10px] font-bold uppercase tracking-widest text-white/20 mb-8 border-b border-white/5 pb-4">
                            Mission Parameters
                        </h3>

                        <div className="space-y-6">
                            <ParamItem label="Target Objective" value={objective} />
                            <ParamItem label="Extraction Point" value="PENDING" />
                            <ParamItem label="Comms Privacy" value="ENCRYPTED" />
                        </div>

                        <div className="mt-10 p-4 bg-cyan-500/5 border border-cyan-500/10 rounded flex items-start gap-4">
                            <Briefcase className="w-5 h-5 text-cyan-500/40" />
                            <p className="text-[9px] leading-relaxed uppercase font-bold text-cyan-500/30">
                                Maintain stealth. HEAT levels above 80% will trigger automated heavy response systems.
                            </p>
                        </div>
                    </div>

                    <div className="flex-grow bg-cyan-950/5 border border-cyan-900/20 rounded-xl relative overflow-hidden flex items-center justify-center">
                        <AnimatePresence>
                            {heat > 50 && (
                                <motion.div
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                    className="absolute inset-0 bg-red-500/5 animate-pulse"
                                />
                            )}
                        </AnimatePresence>
                        <Search className="w-12 h-12 text-cyan-500/10" />
                    </div>
                </div>
            </div>

            {status === 'busted' && (
                <div className="fixed inset-0 z-[100] bg-black/95 flex items-center justify-center p-8 backdrop-blur-xl">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <AlertCircle className="w-20 h-20 text-red-500 mx-auto mb-8 shadow-[0_0_30px_rgba(239,68,68,0.5)]" />
                        <h2 className="text-5xl font-black italic tracking-tighter text-white mb-4 uppercase">Mission Failed</h2>
                        <p className="text-red-500/60 mb-10 font-bold uppercase tracking-widest text-sm">The Broker session has been terminated by external forces.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-12 py-4 bg-red-600 rounded text-white font-black uppercase tracking-[0.2em] hover:bg-red-500 transition-all"
                        >
                            Reset Instance
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const StatItem = ({ icon, label, value, color }: { icon: React.ReactNode, label: string, value: string, color: string }) => (
    <div className="flex flex-col">
        <div className="flex items-center gap-2 mb-1">
            {icon}
            <span className="text-[10px] font-bold uppercase tracking-widest text-white/30">{label}</span>
        </div>
        <span className={`text-lg font-black italic tracking-tighter ${color}`}>{value}</span>
    </div>
);

const ParamItem = ({ label, value }: { label: string, value: string }) => (
    <div>
        <span className="text-[9px] font-bold uppercase tracking-widest text-white/10 block mb-1">{label}</span>
        <span className="text-xs font-bold text-cyan-100 uppercase italic tracking-tight">{value}</span>
    </div>
);
