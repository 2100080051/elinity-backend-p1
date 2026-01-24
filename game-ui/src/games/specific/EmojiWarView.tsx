import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Zap,
    Shield,
    Target,
    Swords,
    Activity,
    Cpu,
    Terminal,
    Crosshair,
    Flame,
    Bomb,
    Wind,
    Skull
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const EmojiWarView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        hp = 100,
        glitch_percent = 0,
        round = 1,
        entities = [],
        available_moves = [],
        faction = 'None',
        status = 'active'
    } = gameState;

    const handleAction = async (action: string) => {
        if (!action.trim() || !sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', action);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("Overseer communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    const quickEmojis = ["⚔️", "🛡️", "🔥", "⚡", "🌀", "💀", "🧬", "🧪"];

    return (
        <div className="min-h-screen bg-[#050505] text-[#e0e0e0] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Background Glitch Effects */}
            <div className="absolute inset-0 opacity-10 pointer-events-none overflow-hidden">
                <div className="absolute top-1/4 -left-20 w-96 h-96 bg-magenta-500 rounded-full blur-[100px] animate-pulse" />
                <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-blue-500 rounded-full blur-[100px] animate-pulse delay-1000" />
            </div>

            {/* Header - Arena Status */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-magenta-500/20 rounded-2xl border border-magenta-500/30 shadow-[0_0_20px_rgba(236,72,153,0.2)]">
                        <Swords className="w-6 h-6 text-magenta-500" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black italic tracking-tighter text-white uppercase flex items-center gap-2">
                            Emoji War <span className="text-xs px-2 py-0.5 bg-white/10 rounded-full font-bold not-italic">R{round}</span>
                        </h1>
                        <p className="text-[10px] uppercase font-bold tracking-widest text-magenta-500/70">Cyber-Glyph Arena 01</p>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-black text-white/30 tracking-widest mb-1">Reality Glitch</p>
                        <div className="w-48 h-2 bg-white/5 rounded-full overflow-hidden border border-white/10">
                            <motion.div
                                animate={{ width: `${glitch_percent}%` }}
                                className="h-full bg-gradient-to-r from-magenta-500 via-white to-blue-500 shadow-[0_0_10px_rgba(255,255,255,0.5)]"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow h-0">
                {/* Left: Opponents & Stats */}
                <div className="lg:col-span-4 flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar">
                    {/* Player Card */}
                    <div className="bg-white/5 border border-white/10 rounded-[2rem] p-6 backdrop-blur-xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Target className="w-12 h-12" />
                        </div>
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-xs font-black uppercase tracking-[0.2em] text-white/40">Gladiator Profile</span>
                            <span className="text-[10px] px-2 py-1 bg-blue-500/20 text-blue-400 rounded-lg font-bold border border-blue-500/20 uppercase tracking-widest">
                                {faction}
                            </span>
                        </div>
                        <div className="flex flex-col gap-2">
                            <div className="flex justify-between items-end">
                                <span className="text-3xl font-black text-white tracking-tighter italic">Vessel HP</span>
                                <span className={`text-2xl font-black ${hp < 30 ? 'text-red-500 animate-bounce' : 'text-white'}`}>{hp}</span>
                            </div>
                            <div className="h-4 w-full bg-black/40 rounded-lg p-1 border border-white/5">
                                <motion.div
                                    animate={{ width: `${hp}%` }}
                                    className={`h-full rounded-sm ${hp < 30 ? 'bg-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'bg-green-500 shadow-[0_0_15px_rgba(34,197,94,0.3)]'}`}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Opponents List */}
                    <div className="flex flex-col gap-3">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-white/20 pl-4">Detected Threats</h3>
                        {entities.map((enemy: any, idx: number) => (
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                key={idx}
                                className="bg-white/[0.03] border border-white/5 rounded-2xl p-4 flex items-center justify-between group hover:bg-red-500/5 hover:border-red-500/20 transition-all"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-xl shadow-inner">
                                        {enemy.name.includes('👑') ? '👑' : '👾'}
                                    </div>
                                    <div>
                                        <p className="text-sm font-black text-white/90 tracking-tight uppercase italic">{enemy.name}</p>
                                        <div className="flex items-center gap-2">
                                            <div className="w-24 h-1.5 bg-black/40 rounded-full overflow-hidden">
                                                <div className="h-full bg-red-500" style={{ width: `${enemy.hp}%` }} />
                                            </div>
                                            <span className="text-[10px] font-bold text-red-400">{enemy.hp}%</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-[10px] font-bold uppercase tracking-widest text-white/20 group-hover:text-red-400 transition-colors">
                                    {enemy.status}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* center: Arena Narrative & Controls */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    {/* Combat Narrative */}
                    <div className="flex-grow bg-white/[0.02] border border-white/10 rounded-[2.5rem] p-10 overflow-y-auto backdrop-blur-3xl relative group custom-scrollbar">
                        <div className="absolute top-6 left-6 flex items-center gap-2">
                            <Terminal className="w-4 h-4 text-magenta-500" />
                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-magenta-500/50">Tactical Feed // Subnet_881</span>
                        </div>

                        <div className="prose prose-invert max-w-none prose-p:text-xl prose-p:leading-relaxed prose-p:italic prose-p:font-medium prose-p:text-white/90">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className="mb-6 last:mb-0 drop-shadow-[0_2px_10px_rgba(0,0,0,0.5)]">
                                    {line}
                                </p>
                            ))}
                        </div>
                    </div>

                    {/* Combat Interface */}
                    <div className="flex flex-col gap-6 pt-4">
                        {/* Quick Moves */}
                        <div className="flex flex-wrap gap-3">
                            {available_moves.map((move: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(move)}
                                    disabled={loading}
                                    className="px-6 py-3 bg-white/5 border border-white/10 rounded-2xl hover:bg-magenta-500/20 hover:border-magenta-500/50 hover:text-magenta-400 transition-all font-black text-sm uppercase tracking-tighter italic shadow-xl group flex items-center gap-3"
                                >
                                    <Zap className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-all -ml-1" />
                                    {move}
                                </button>
                            ))}
                        </div>

                        {/* Input Area */}
                        <div className="flex gap-4 items-center">
                            <div className="flex-grow relative group">
                                <div className="absolute -inset-1 bg-gradient-to-r from-magenta-600 to-blue-600 rounded-[2rem] blur opacity-20 group-focus-within:opacity-50 transition duration-500" />
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                    placeholder="Input Combat Glyphs..."
                                    className="relative w-full bg-black/80 border border-white/10 rounded-[2rem] py-5 px-8 focus:outline-none focus:border-magenta-500/50 transition-all text-white placeholder:text-white/10 text-lg font-bold italic"
                                />
                                <div className="absolute right-4 top-1/2 -translate-y-1/2 flex gap-2">
                                    {quickEmojis.map((e, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setInput(prev => prev + e)}
                                            className="w-8 h-8 flex items-center justify-center bg-white/5 rounded-lg hover:bg-white/10 transition-all border border-white/5 text-lg"
                                        >
                                            {e}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="h-16 w-16 bg-magenta-500 rounded-[1.5rem] flex items-center justify-center text-white hover:bg-magenta-600 active:scale-95 transition-all shadow-[0_0_20px_rgba(236,72,153,0.4)] disabled:opacity-50 disabled:grayscale"
                            >
                                {loading ? <Activity className="w-6 h-6 animate-spin" /> : <Crosshair className="w-8 h-8" />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Damage Overlay */}
            <AnimatePresence>
                {hp < 30 && status !== 'defeated' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 pointer-events-none border-[20px] border-red-500/20 shadow-[inset_0_0_100px_rgba(239,68,68,0.2)] z-50 animate-pulse"
                    />
                )}
            </AnimatePresence>
        </div>
    );
};
