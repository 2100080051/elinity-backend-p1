import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Eye,
    VenetianMask,
    Zap,
    Activity,
    ShieldAlert,
    Users,
    ChevronRight,
    TrendingUp,
    Fingerprint,
    Layers,
    Sparkles,
    Search,
    Lock,
    MessageSquare,
    Wine
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const SocialLabyrinthView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        standing = 10,
        agenda = 'Observation',
        circle = 'The Outer Ring',
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
            console.error("Oracle communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#080808] text-white font-serif p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Noir shadows and light spill */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-red-900/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 right-0 w-full h-[30%] bg-gradient-to-t from-black to-transparent" />
                {/* Interconnected string visual (simulated) */}
                <div className="absolute inset-0 opacity-[0.03]">
                    <svg width="100%" height="100%">
                        <line x1="10%" y1="10%" x2="90%" y2="90%" stroke="red" strokeWidth="1" />
                        <line x1="90%" y1="10%" x2="10%" y2="90%" stroke="red" strokeWidth="1" />
                        <circle cx="50%" cy="50%" r="2" fill="red" />
                    </svg>
                </div>
            </div>

            {/* Header - Oracle HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-10">
                <div className="flex items-center gap-8">
                    <div className="p-5 bg-gradient-to-b from-neutral-800 to-black rounded-full border border-white/5 shadow-2xl">
                        <Eye className="w-8 h-8 text-red-600 animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-light tracking-tighter text-white uppercase selection:bg-red-900">Social <span className="font-black italic text-red-600">Labyrinth</span></h1>
                        <div className="flex items-center gap-3 mt-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-600 shadow-[0_0_10px_rgba(220,38,38,1)]" />
                            <span className="text-[10px] uppercase font-black tracking-[0.4em] text-white/30 italic">Observing Circle: {circle.toUpperCase()}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-12 bg-white/[0.02] px-10 py-5 rounded-full border border-white/5 backdrop-blur-xl">
                    <OracleStat label="Social Standing" value={standing.toString()} icon={<TrendingUp className="w-4 h-4 text-emerald-500" />} />
                    <div className="w-[1px] h-10 bg-white/5" />
                    <OracleStat label="Active Agenda" value={agenda} icon={<Lock className="w-4 h-4 text-red-500" />} />
                    <div className="w-[1px] h-10 bg-white/5" />
                    <OracleStat label="Influence" value="Medium" icon={<Users className="w-4 h-4 text-blue-500" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 z-10 flex-grow pt-4">
                {/* Intrigue Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-grow bg-[#0c0c0c] border border-white/5 rounded-[2.5rem] p-16 relative overflow-hidden flex flex-col justify-center shadow-inner"
                    >
                        {/* Smoke effect simulating overlay */}
                        <div className="absolute inset-0 pointer-events-none opacity-10 bg-[radial-gradient(circle_at_50%_0%,rgba(255,255,255,0.05),transparent)]" />

                        <div className="relative z-10 max-w-4xl">
                            <div className="flex items-center gap-3 mb-10 text-[11px] font-black text-white/10 uppercase tracking-[0.8em]">
                                <MessageSquare className="w-4 h-4" /> Intercepted_Dialogue_Node
                            </div>

                            <p className="text-3xl md:text-4xl font-light leading-relaxed text-neutral-300 italic selection:bg-red-900/50">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-10 last:mb-0 border-l-4 border-red-900/20 pl-12 hover:border-red-600 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Strategist Gambits */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-4 justify-center">
                            {available_actions.map((gambit: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(gambit)}
                                    disabled={loading}
                                    className="px-10 py-4 bg-white/[0.03] border border-white/10 rounded-full hover:bg-red-950 hover:border-red-600 transition-all text-[11px] font-black uppercase tracking-widest text-neutral-500 hover:text-white flex items-center gap-3 group shadow-2xl"
                                >
                                    <Wine className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-all scale-50 group-hover:scale-100" />
                                    {gambit}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-red-600/10 rounded-full blur opacity-5 group-focus-within:opacity-30 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your next move into the shadows..."
                                className="w-full bg-[#050505] border border-white/5 rounded-full py-8 px-14 focus:outline-none focus:border-red-600/40 transition-all text-neutral-200 placeholder:text-neutral-800 text-2xl font-light italic text-center shadow-2xl"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-6 top-1/2 -translate-y-1/2 w-16 h-16 bg-red-600 text-white rounded-full flex items-center justify-center hover:bg-white hover:text-black transition-all shadow-[0_0_30px_rgba(220,38,38,0.3)]"
                            >
                                <Fingerprint className={`w-8 h-8 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Dynamics Observation */}
                <div className="lg:col-span-4 flex flex-col gap-8">
                    <div className="bg-[#0c0c0c] border border-white/10 rounded-[3rem] p-10 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.6em] text-white/10 mb-12 flex items-center gap-2 border-b border-white/5 pb-6">
                            <TrendingUp className="w-4 h-4" /> Social_Vibe_Check
                        </h3>

                        <div className="space-y-14">
                            <CircleMeter label="Anonymity Index" value={100 - standing} color="bg-neutral-600" />
                            <CircleMeter label="Political Leverage" value={standing} color="bg-red-600" />
                            <CircleMeter label="Tension Coefficient" value={45} color="bg-orange-800" />
                        </div>

                        <div className="mt-16 p-10 bg-red-900/5 border border-red-900/10 rounded-[2rem] flex items-start gap-6">
                            <Search className="w-6 h-6 text-red-900 opacity-20 mt-1" />
                            <p className="text-[11px] uppercase font-bold tracking-[0.2em] leading-loose text-neutral-500 italic text-center w-full">
                                "In this room, the loudest voices are the ones not speaking at all."
                            </p>
                        </div>
                    </div>

                    <div className="bg-red-600/5 border border-red-600/10 rounded-[3rem] p-10 flex flex-col items-center justify-center gap-5 text-red-950">
                        <ShieldAlert className="w-12 h-12 opacity-20 animate-wiggle" />
                        <span className="text-[10px] font-black uppercase tracking-[0.5em] text-center">Threat: Leveraged Insight</span>
                    </div>
                </div>
            </div>

            {status === 'ascended' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Lock className="w-24 h-24 text-red-600 mx-auto mb-10 shadow-[0_0_80px_rgba(220,38,38,0.2)]" />
                        <h2 className="text-7xl font-light italic tracking-tighter text-white mb-6 uppercase">Total <span className="text-red-600">Control</span></h2>
                        <p className="text-neutral-500 mb-14 font-bold leading-relaxed tracking-widest uppercase text-sm px-6">The threads are in your hands. Everyone else is merely a puppet in your grand design.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-red-600 text-white font-black uppercase tracking-[0.4em] hover:bg-white hover:text-black transition-all shadow-2xl rounded-full"
                        >
                            Return to Shadows
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const OracleStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-[#9ca3af]">{label}</span>
        </div>
        <p className="text-3xl font-light italic text-white tracking-tighter group-hover:text-red-500 transition-colors">{value}</p>
    </div>
);

const CircleMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-5">
        <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-[0.4em] text-neutral-600">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-[2px] bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_15px_rgba(220,38,38,0.5)]`}
            />
        </div>
    </div>
);
