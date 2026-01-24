import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Swords,
    Trophy,
    Zap,
    Flame,
    Activity,
    Shield,
    ChevronRight,
    TrendingUp,
    Skull,
    Star,
    Award,
    Skull as SkullIcon,
    Crown
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const CreativeDuelView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        style = 0,
        hype = 50,
        health = 100,
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
            console.error("Arbiter communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#050505] text-[#facc15] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Dynamic Arena Pulse */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_0%,#450a0a_0%,transparent_70%)] opacity-30" />
                <div className="absolute top-0 left-0 w-full h-full bg-[linear-gradient(to_bottom,transparent_0%,#000_100%)]" />
            </div>

            {/* Header - Arbiter HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/10 pb-6 bg-black/40 backdrop-blur-xl p-6 rounded-3xl">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-red-600 rounded-2xl shadow-[0_0_30px_rgba(220,38,38,0.4)] animate-pulse">
                        <Swords className="w-8 h-8 text-black" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">The Creative Pit</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-red-500" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-red-500/60 italic">LIVE COMBAT ENGINE // STATUS: {status.toUpperCase()}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <CombatStat label="Style" value={style.toString()} icon={<Star className="w-4 h-4 text-yellow-400" />} />
                    <div className="w-px h-10 bg-white/10" />
                    <CombatStat label="Hype" value={`${hype}%`} icon={<Flame className="w-4 h-4 text-orange-500" />} />
                    <div className="w-px h-10 bg-white/10" />
                    <HealthBar current={health} max={100} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Combat Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, x: -50 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-grow bg-white/5 border border-white/10 rounded-[2.5rem] p-12 backdrop-blur-md relative overflow-hidden flex flex-col shadow-[0_0_50px_rgba(220,38,38,0.05)]"
                    >
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-red-600/50 to-transparent" />

                        <div className="relative z-10">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-white/20 uppercase tracking-[0.6em]">
                                <Activity className="w-4 h-4" /> Live_Commentary_Link
                            </div>

                            <p className="text-2xl md:text-3xl font-black leading-tight text-white uppercase italic selection:bg-red-600/50">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0 border-l-4 border-red-600/20 pl-10 hover:border-red-600 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>

                        {/* Crowd visual placeholder */}
                        <div className="mt-auto h-20 flex items-end gap-1 opacity-[0.03]">
                            {[...Array(60)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    animate={{ height: `${10 + (Math.random() * 90)}%` }}
                                    transition={{ repeat: Infinity, duration: 0.8, delay: i * 0.02 }}
                                    className="flex-1 bg-white"
                                />
                            ))}
                        </div>
                    </motion.div>

                    {/* Gladiator Moves */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((move: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(move)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-red-600 text-black rounded-xl hover:bg-red-500 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-3 group shadow-[0_0_20px_rgba(220,38,38,0.2)]"
                                >
                                    <Zap className="w-4 h-4 group-hover:scale-125 transition-transform" />
                                    {move}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-red-600 rounded-2xl blur opacity-20 group-focus-within:opacity-50 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="EXECUTE YOUR CREATIVE STRIKE..."
                                className="relative w-full bg-black border-2 border-red-600/20 rounded-2xl py-8 px-12 focus:outline-none focus:border-red-600 transition-all text-white placeholder:text-white/10 text-xl font-black uppercase italic tracking-tighter"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-white text-black rounded-xl flex items-center justify-center hover:bg-yellow-400 transition-all shadow-2xl"
                            >
                                <TrendingUp className={`w-8 h-8 ${loading ? 'animate-bounce' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Performance Analytics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white/5 border border-white/10 rounded-[2.5rem] p-8 backdrop-blur-md">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-white/20 mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                            <TrendingUp className="w-4 h-4" /> Combat_Analytics
                        </h3>

                        <div className="space-y-10">
                            <DuelMeter label="Originality Index" value={Math.min(100, style / 10)} color="bg-yellow-400" />
                            <DuelMeter label="Crowd Saturation" value={hype} color="bg-orange-500" />
                            <DuelMeter label="Meta-Humor Levels" value={65} color="bg-red-600" />
                        </div>

                        <div className="mt-12 p-8 bg-red-600/5 border border-red-600/10 rounded-3xl flex items-start gap-5">
                            <Award className="w-6 h-6 text-red-500 opacity-30 mt-1" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-red-500/40 italic text-center w-full">
                                "THE ARBITER OBSERVES ALL. SURVIVAL IS SECONDARY TO SPECTACLE."
                            </p>
                        </div>
                    </div>

                    <div className="bg-red-600/5 border border-red-600/10 rounded-[2.5rem] p-8 flex flex-col items-center justify-center gap-4 text-red-900">
                        <Skull className="w-12 h-12 opacity-20 animate-wiggle" />
                        <span className="text-[9px] font-black uppercase tracking-[0.5em] text-center">Threat Level: Extreme</span>
                    </div>
                </div>
            </div>

            {status === 'eliminated' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <SkullIcon className="w-24 h-24 text-red-600 mx-auto mb-10 shadow-[0_0_80px_rgba(220,38,38,0.5)]" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-6 uppercase">Wasted</h2>
                        <p className="text-red-600 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm">Your creative spark was extinguished in the pit. The audience has already forgotten your name.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-red-600 rounded-2xl text-black font-black uppercase tracking-[0.4em] hover:bg-white transition-all shadow-2xl"
                        >
                            Return to Pit
                        </button>
                    </motion.div>
                </div>
            )}

            {status === 'legendary' && (
                <div className="fixed inset-0 z-[100] bg-yellow-400 flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Crown className="w-32 h-32 text-black mx-auto mb-10 animate-bounce" />
                        <h2 className="text-8xl font-black italic tracking-tighter text-black mb-6 uppercase">Legend</h2>
                        <p className="text-black mb-14 font-black leading-relaxed tracking-[0.3em] uppercase text-sm">The Arena is yours. The Arbiter bows.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-black rounded-2xl text-white font-black uppercase tracking-[0.4em] hover:bg-red-600 transition-all shadow-2xl"
                        >
                            Reign Again
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const CombatStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-white">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter">{value}</p>
    </div>
);

const HealthBar = ({ current, max }: { current: number, max: number }) => (
    <div className="w-48">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-red-600 mb-2">
            <span>Critical Integrity</span>
            <span>{current}%</span>
        </div>
        <div className="h-4 bg-white/5 rounded-lg border border-white/10 overflow-hidden p-1">
            <motion.div
                initial={{ width: '100%' }}
                animate={{ width: `${(current / max) * 100}%` }}
                className="h-full bg-red-600 rounded-sm shadow-[0_0_15px_rgba(220,38,38,0.5)]"
            />
        </div>
    </div>
);

const DuelMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-white/20">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_20px_rgba(255,255,255,0.1)]`}
            />
        </div>
    </div>
);
