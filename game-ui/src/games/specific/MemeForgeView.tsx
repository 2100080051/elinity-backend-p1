import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Dices,
    TrendingUp,
    Share2,
    MessageSquare,
    Zap,
    Flame,
    Ghost,
    ChevronRight,
    Monitor,
    Trophy,
    Skull,
    MousePointer2
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const MemeForgeView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        virality = 10,
        dankness = 0,
        format = 'Expanding Brain',
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
            console.error("Trend-Oracle communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#050505] text-[#e0e0e0] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Scanline Effect */}
            <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%] z-50 opacity-20" />

            {/* Header - Algorithm Status */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/10 pb-6 bg-black/40 backdrop-blur-md px-4 py-2 rounded-2xl">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-purple-600/20 rounded-xl border border-purple-500/40 shadow-[0_0_20px_rgba(168,85,247,0.2)]">
                        <TrendingUp className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black italic tracking-tighter text-white uppercase">Meme Forge // <span className="text-purple-500">v0.69-Dank</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-green-500 animate-ping" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-green-500/70 underline decoration-green-900">Algorithm: Feeding</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-bold text-white/30 tracking-widest mb-1">Virality Potential</p>
                        <div className="flex items-center gap-4">
                            <div className="w-48 h-2 bg-white/5 rounded-full overflow-hidden border border-white/10">
                                <motion.div
                                    animate={{ width: `${virality}%` }}
                                    className="h-full bg-gradient-to-r from-purple-600 to-pink-500 shadow-[0_0_15px_rgba(168,85,247,0.5)]"
                                />
                            </div>
                            <span className="text-2xl font-black text-purple-400 italic">{virality}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Center: The Forge */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-zinc-900 border-4 border-zinc-800 rounded-[2.5rem] p-12 relative overflow-hidden group shadow-2xl flex flex-col justify-center text-center"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-transparent to-transparent opacity-50" />

                        <div className="absolute top-6 left-1/2 -translate-x-1/2 px-4 py-1 bg-zinc-800 rounded-full text-[10px] font-black uppercase tracking-widest text-zinc-500 border border-zinc-700">
                            Current Selection: {format}
                        </div>

                        <div className="relative z-10">
                            <h2 className="text-4xl md:text-5xl font-black italic tracking-tighter text-white uppercase leading-tight selection:bg-purple-500 shadow-purple-900/20 drop-shadow-2xl">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-4 last:mb-0">
                                        {line}
                                    </span>
                                ))}
                            </h2>
                        </div>

                        <div className="absolute bottom-6 left-6 flex items-center gap-4 text-zinc-600">
                            <Monitor className="w-5 h-5" />
                            <span className="text-[10px] font-bold uppercase tracking-[0.2em]">Render_Output // Dank_Scale_100</span>
                        </div>
                    </motion.div>

                    {/* Inputs */}
                    <div className="flex flex-col gap-4 bg-zinc-900/20 p-6 rounded-3xl border border-white/5">
                        <div className="flex flex-wrap gap-2 justify-center mb-2">
                            {available_actions.map((act: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(act)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-zinc-800/50 border border-zinc-700 rounded-xl hover:bg-purple-600/20 hover:border-purple-500/40 transition-all text-[11px] font-black uppercase tracking-widest text-zinc-400 hover:text-white flex items-center gap-2 group italic shadow-lg shadow-black/40"
                                >
                                    <Share2 className="w-3 h-3 text-purple-500 group-hover:rotate-12 transition-transform" />
                                    {act}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Caption this for maximum engagement..."
                                className="relative w-full bg-black border border-zinc-800 rounded-2xl py-6 px-10 focus:outline-none focus:border-purple-500/50 transition-all text-white placeholder:text-zinc-800 text-xl font-black italic uppercase tracking-tighter"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-14 h-14 bg-purple-600 rounded-xl flex items-center justify-center text-white hover:bg-purple-500 active:scale-95 transition-all shadow-xl shadow-purple-950/40"
                            >
                                <Zap className="w-7 h-7" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Analytics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 backdrop-blur-md">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500 mb-8 flex items-center gap-2 border-b border-zinc-800 pb-4">
                            <Dices className="w-4 h-4" /> Dank Analytics
                        </h3>

                        <div className="space-y-6">
                            <ValueRow icon={<Trophy className="w-4 h-4 text-yellow-500" />} label="Dankness Score" value={dankness.toString()} />
                            <ValueRow icon={<MessageSquare className="w-4 h-4 text-blue-400" />} label="Engagement" value={virality > 80 ? 'CRITICAL' : virality > 30 ? 'TRENDING' : 'LOW'} />
                            <ValueRow icon={<Skull className="w-4 h-4 text-red-500" />} label="Cringe Level" value={dankness < 100 ? 'Warning' : 'Minimal'} />
                        </div>

                        <div className="mt-10 p-4 bg-purple-500/5 border border-purple-500/10 rounded-2xl">
                            <div className="flex items-center gap-2 mb-2 text-purple-400">
                                <Flame className="w-4 h-4" />
                                <span className="text-[10px] font-black uppercase tracking-widest">Oracle Memo</span>
                            </div>
                            <p className="text-[10px] uppercase font-bold tracking-widest leading-loose text-zinc-500 italic">
                                The Algorithm demands fresh perspective. Avoid repetition or face shadow-ban.
                            </p>
                        </div>
                    </div>

                    <div className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 flex flex-col items-center justify-center gap-4 text-zinc-700">
                        <MousePointer2 className="w-12 h-12 opacity-20 animate-bounce" />
                        <span className="text-[10px] font-black uppercase tracking-widest">Manifesting Virality...</span>
                    </div>
                </div>
            </div>

            {status === 'viral' && (
                <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Ghost className="w-24 h-24 text-purple-500 mx-auto mb-8 shadow-[0_0_50px_rgba(168,85,247,0.5)]" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-4 uppercase">Viral Ascent</h2>
                        <p className="text-zinc-500 mb-10 font-bold leading-relaxed tracking-wider">The Internet has spoken. Your meme is now the only truth. The Algorithm bows to you.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-12 py-5 bg-purple-600 rounded-full text-white font-black uppercase tracking-[0.2em] hover:bg-purple-500 transition-all shadow-2xl shadow-purple-900/20"
                        >
                            Forge Again
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const ValueRow = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
            <div className="opacity-50">{icon}</div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-[#666]">{label}</span>
        </div>
        <span className="text-sm font-black text-white italic tracking-tighter">{value}</span>
    </div>
);
