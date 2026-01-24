import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    UserCircle,
    SwitchCamera,
    Zap,
    Activity,
    ShieldAlert,
    Users,
    ChevronRight,
    TrendingUp,
    Fingerprint,
    Layers,
    Sparkles,
    Eye,
    Heart
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const CharacterSwapView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        sync = 10,
        trait = 'Unknown',
        form = 'The Shadow',
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
            console.error("Mimic communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Mirror ripple effect */}
            <div className="absolute inset-0 opacity-[0.05] pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_40%,#3b82f6_0%,transparent_100%)] blur-[100px]" />
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/glass.png')]" />
            </div>

            {/* Header - Mimic HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/10 pb-8 bg-black/40 backdrop-blur-2xl p-6 rounded-[2rem]">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl shadow-[0_0_30px_rgba(59,130,246,0.3)]">
                        <SwitchCamera className="w-8 h-8 text-white animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tight text-white uppercase italic">Hall of <span className="text-blue-500">Reflections</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-white/30 italic">Active Mirror // Morphogenesis in progress</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <MimicStat label="Identity Sync" value={`${sync}%`} icon={<Fingerprint className="w-4 h-4 text-blue-400" />} />
                    <div className="w-px h-10 bg-white/10" />
                    <MimicStat label="Vessel Form" value={form} icon={<UserCircle className="w-4 h-4 text-purple-400" />} />
                    <div className="w-px h-10 bg-white/10" />
                    <MimicStat label="Dominant Trait" value={trait} icon={<Heart className="w-4 h-4 text-red-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Identity Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, backdropFilter: 'blur(0px)' }}
                        animate={{ opacity: 1, backdropFilter: 'blur(10px)' }}
                        className="flex-grow bg-white/5 border border-white/5 rounded-[3rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl"
                    >
                        <div className="absolute inset-0 pointer-events-none opacity-20">
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-blue-500 to-transparent animate-scan" style={{ animationDuration: '3s' }} />
                        </div>

                        <div className="relative z-10 max-w-4xl">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-white/10 uppercase tracking-[0.6em]">
                                <Eye className="w-4 h-4" /> Reflection_Data_Stream
                            </div>

                            <p className="text-2xl md:text-3xl font-light leading-relaxed text-blue-100 italic selection:bg-blue-600/50">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0 border-l-2 border-white/10 pl-10 hover:border-blue-500 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Morph Options */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((morph: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(morph)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-white/5 border border-white/10 rounded-2xl hover:bg-blue-600/20 hover:border-blue-500 transition-all text-[11px] font-black uppercase tracking-widest text-white/40 hover:text-white flex items-center gap-3 group shadow-xl"
                                >
                                    <Sparkles className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all" />
                                    {morph}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your intent to change..."
                                className="relative w-full bg-black border border-white/10 rounded-2xl py-8 px-12 focus:outline-none focus:border-blue-500 transition-all text-white placeholder:text-white/10 text-xl font-light italic text-center"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-16 h-16 bg-blue-600 text-white rounded-xl flex items-center justify-center hover:bg-white hover:text-black transition-all shadow-2xl"
                            >
                                <Zap className={`w-8 h-8 ${loading ? 'animate-pulse' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Morphological Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white/5 border border-white/5 rounded-[3.1rem] p-10 backdrop-blur-xl transition-all hover:bg-white/[0.07] group">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-white/20 mb-10 flex items-center gap-2 border-b border-white/5 pb-5">
                            <TrendingUp className="w-4 h-4" /> Genetic_Divergence
                        </h3>

                        <div className="space-y-12">
                            <MorphMeter label="Ego Dissolution" value={sync} color="bg-blue-500" />
                            <MorphMeter label="Memory Bleed" value={45} color="bg-purple-500" />
                            <MorphMeter label="Limbic Resonance" value={80} color="bg-red-500" />
                        </div>

                        <div className="mt-14 p-8 bg-blue-600/5 border border-blue-600/10 rounded-3xl flex items-start gap-5">
                            <Users className="w-6 h-6 text-blue-500 opacity-20 mt-1" />
                            <p className="text-[10px] uppercase font-black tracking-widest leading-loose text-white/20 italic text-center w-full">
                                "The self is but a costume. We wear it until it frays, then we find another."
                            </p>
                        </div>
                    </div>

                    <div className="bg-blue-600/5 border border-blue-600/10 rounded-[3rem] p-8 flex flex-col items-center justify-center gap-4 text-blue-900">
                        <ShieldAlert className="w-12 h-12 opacity-20 animate-pulse" />
                        <span className="text-[9px] font-black uppercase tracking-[0.5em] text-center">Stability Warning: Low</span>
                    </div>
                </div>
            </div>

            {status === 'merged' && (
                <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <div className="relative inline-block mb-10">
                            <UserCircle className="w-32 h-32 text-blue-600 mx-auto opacity-20" />
                            <UserCircle className="w-32 h-32 text-purple-600 absolute inset-0 animate-ping opacity-40 ml-4 mt-4" />
                        </div>
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-6 uppercase leading-none">Complete <br /><span className="text-blue-500">Unity</span></h2>
                        <p className="text-white/40 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm">The original has vanished. You are the form. The mirror reflects nothing but truth.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-white text-black font-black uppercase tracking-[0.4em] hover:bg-blue-600 hover:text-white transition-all shadow-2xl rounded-2xl"
                        >
                            Return to Hall
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const MimicStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group cursor-crosshair">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest text-white">{label}</span>
        </div>
        <p className="text-2xl font-black italic text-white tracking-tighter group-hover:text-blue-500 transition-colors">{value}</p>
    </div>
);

const MorphMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-white/20">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_20px_rgba(59,130,246,0.3)]`}
            />
        </div>
    </div>
);
