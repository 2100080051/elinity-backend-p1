import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Flame,
    Skull,
    Activity,
    Users,
    Zap,
    AlertTriangle,
    Smile,
    Ghost,
    MessageCircle,
    ChevronRight,
    TrendingDown,
    Wind
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const RoastToastView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        char_level = 50,
        tension = 0,
        vibe = 'Snickering',
        last_burn = {},
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
            console.error("Singe-Master communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-[#d1d1d1] font-mono p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Heat Haze Effect */}
            <div className="absolute inset-0 pointer-events-none opacity-20">
                <div className="absolute inset-0 bg-gradient-to-t from-red-900/20 via-transparent to-transparent" />
            </div>

            {/* Header - Grill Status */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-red-600/10 rounded-xl border border-red-600/20 shadow-[0_0_20px_rgba(220,38,38,0.1)]">
                        <Flame className="w-6 h-6 text-red-600" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black tracking-tighter text-white uppercase italic">Singe-Master 9000</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-red-600/70 underline decoration-red-900">Grill Active // {vibe}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-bold text-white/30 tracking-widest mb-1">Tension Level</p>
                        <div className="flex items-center gap-3">
                            <div className="w-32 h-2 bg-white/5 rounded-full overflow-hidden border border-white/10 group">
                                <motion.div
                                    animate={{ width: `${tension}%`, backgroundColor: tension > 80 ? '#ef4444' : '#facc15' }}
                                    className="h-full"
                                />
                            </div>
                            <span className={`text-xl font-black italic tracking-tighter ${tension > 80 ? 'text-red-500 animate-bounce' : 'text-white'}`}>{tension}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Left: Burn Report */}
                <div className="lg:col-span-3 flex flex-col gap-6">
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Skull className="w-12 h-12" />
                        </div>
                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 mb-4 border-b border-white/5 pb-2">Last Burn Report</h3>
                        <div className="space-y-4">
                            <MetricRow label="Intensity" value={`${last_burn.intensity || 0}/10`} color="red" />
                            <MetricRow label="Damage" value={last_burn.damage || 'N/A'} color="orange" />
                            <MetricRow label="Reaction" value={last_burn.audience_reaction || 'Mixed'} color="gray" />
                        </div>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-white/40 mb-4">Char Points</h3>
                        <div className="text-4xl font-black italic tracking-tighter text-white flex items-baseline gap-2">
                            {char_level}
                            <span className="text-[10px] uppercase tracking-widest text-red-500/50 not-italic">Scorched</span>
                        </div>
                        <div className="mt-4 flex gap-1">
                            {[...Array(10)].map((_, i) => (
                                <div key={i} className={`h-1.5 flex-grow rounded-full ${i < (char_level / 10) ? 'bg-orange-500' : 'bg-white/5'}`} />
                            ))}
                        </div>
                    </div>
                </div>

                {/* center: Narrative feed */}
                <div className="lg:col-span-9 flex flex-col gap-6">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-white/[0.02] border border-white/10 rounded-[2rem] p-10 backdrop-blur-2xl relative overflow-hidden group flex flex-col justify-center"
                    >
                        <div className="absolute top-6 left-6 flex items-center gap-2">
                            <Smile className="w-4 h-4 text-red-600" />
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-red-600/50 italic">The_Hot_Seat // Uncensored_Mode</span>
                        </div>

                        <div className="prose prose-invert max-w-none text-3xl font-black leading-tight italic tracking-tighter text-white/90 uppercase text-center selection:bg-red-600/40 drop-shadow-[0_10px_20px_rgba(0,0,0,0.5)]">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className="mb-6 last:mb-0 border-l-4 border-red-600/20 pl-6 text-left">
                                    {line}
                                </p>
                            ))}
                        </div>
                    </motion.div>

                    {/* Controls */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2 justify-center">
                            {available_actions.map((act: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(act)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-red-600/20 hover:border-red-600/40 transition-all text-[10px] font-black uppercase tracking-widest text-white/60 hover:text-white flex items-center gap-2 italic"
                                >
                                    <ChevronRight className="w-3 h-3 text-red-600" />
                                    {act}
                                </button>
                            ))}
                        </div>

                        <div className="flex gap-4 items-center">
                            <div className="flex-grow relative group">
                                <div className="absolute -inset-1 bg-gradient-to-r from-red-600 to-orange-600 rounded-2xl blur opacity-10 group-focus-within:opacity-30 transition duration-500" />
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                    placeholder="Enter the roast rotation..."
                                    className="relative w-full bg-black/80 border border-white/10 rounded-2xl py-5 px-8 focus:outline-none focus:border-red-900/50 transition-all text-white placeholder:text-white/10 text-xl font-black italic uppercase italic tracking-tighter"
                                />
                            </div>
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="h-20 w-32 bg-red-600 rounded-2xl flex flex-col items-center justify-center text-white hover:bg-red-500 active:scale-95 transition-all shadow-2xl shadow-red-950/20"
                            >
                                {loading ? <Activity className="w-8 h-8 animate-spin" /> : (
                                    <>
                                        <Zap className="w-8 h-8 group-hover:scale-120 transition-transform" />
                                        <span className="text-[10px] font-black uppercase">Singe</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {status === 'meltdown' && (
                <div className="fixed inset-0 z-[100] bg-red-600 flex flex-col items-center justify-center p-10 text-white text-center">
                    <AlertTriangle className="w-32 h-32 mb-8 animate-ping" />
                    <h2 className="text-8xl font-black italic tracking-tighter uppercase mb-4">Core Meltdown</h2>
                    <p className="text-2xl font-black uppercase tracking-[0.5em] opacity-40 mb-12 border-b-4 border-white pb-4">The Grill Has Exploded</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-16 py-6 border-4 border-white text-2xl font-black uppercase hover:bg-white hover:text-red-600 transition-all font-mono"
                    >
                        Reset System
                    </button>
                </div>
            )}
        </div>
    );
};

const MetricRow = ({ label, value, color }: { label: string, value: string, color: string }) => (
    <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase font-bold tracking-widest text-white/20">{label}</span>
        <span className={`text-xs font-black uppercase italic tracking-tight text-${color}-400`}>{value}</span>
    </div>
);
