import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Cloud,
    Wind,
    Zap,
    Activity,
    ShieldAlert,
    Compass,
    ChevronRight,
    TrendingUp,
    Brain,
    Layers,
    Sparkles,
    Eye,
    Heart,
    Sun,
    Moon,
    Mountain
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const InnerWorldQuestView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        clarity = 20,
        emotion = 'Curiosity',
        terrain = 'The Void',
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
            console.error("Psyche communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-[#0f172a] to-[#1e1b4b] text-[#fde68a] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Ethereal light rays and floating particles */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-1/4 w-[1px] h-full bg-gradient-to-b from-transparent via-white/10 to-transparent" />
                <div className="absolute top-0 left-1/2 w-[1px] h-full bg-gradient-to-b from-transparent via-white/10 to-transparent" />
                <div className="absolute top-0 left-3/4 w-[1px] h-full bg-gradient-to-b from-transparent via-white/10 to-transparent" />
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(253,230,138,0.05)_0%,transparent_100%)] opacity-40" />
            </div>

            {/* Header - Psyche HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-8 bg-black/20 backdrop-blur-2xl p-8 rounded-[3rem]">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-gradient-to-br from-indigo-900 to-purple-900 rounded-full border border-indigo-400/30 shadow-[0_0_40px_rgba(129,140,248,0.2)]">
                        <Brain className="w-8 h-8 text-indigo-400 animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tight text-white uppercase italic">Internal <span className="text-indigo-400">Horizon</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-white animate-ping" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.4em] text-white/30 italic">Observing Subconscious // State: Ethereal</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-12">
                    <PsycheStat label="Clarity" value={`${clarity}%`} icon={<Sun className="w-4 h-4 text-amber-400" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <PsycheStat label="Resonance" value={emotion} icon={<Heart className="text-rose-400 w-4 h-4" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <PsycheStat label="Terrain" value={terrain} icon={<Mountain className="w-4 h-4 text-indigo-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Introspection Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-white/5 border border-white/5 rounded-[3.5rem] p-16 relative overflow-hidden flex flex-col justify-center shadow-2xl backdrop-blur-sm"
                    >
                        <div className="absolute top-0 left-0 w-full h-full pointer-events-none opacity-5">
                            <Cloud className="absolute top-10 right-20 w-64 h-64 animate-drift" />
                            <Cloud className="absolute bottom-20 left-10 w-48 h-48 animate-drift-slow" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-white/10 uppercase tracking-[0.8em]">
                                <Wind className="w-4 h-4" /> Cognitive_Drift_Feed
                            </div>

                            <p className="text-2xl md:text-4xl font-light leading-relaxed text-indigo-100 italic selection:bg-indigo-500/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-10 last:mb-0 border-l-2 border-white/10 pl-12 hover:border-indigo-400 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Seeker Actions */}
                    <div className="flex flex-col gap-6">
                        <div className="flex flex-wrap gap-4 justify-center">
                            {available_actions.map((move: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(move)}
                                    disabled={loading}
                                    className="px-10 py-4 bg-white/5 border border-white/10 rounded-full hover:bg-white hover:text-indigo-900 transition-all text-[11px] font-black uppercase tracking-widest text-indigo-200/50 flex items-center gap-3 group shadow-xl"
                                >
                                    <Sparkles className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all scale-50 group-hover:scale-100" />
                                    {move}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-3xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full blur opacity-10 group-focus-within:opacity-30 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your intent to the horizon..."
                                className="w-full bg-black/40 border border-white/5 rounded-full py-8 px-14 focus:outline-none focus:border-indigo-400/50 transition-all text-white placeholder:text-white/10 text-2xl font-light italic text-center shadow-inner"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-6 top-1/2 -translate-y-1/2 w-16 h-16 bg-white text-indigo-900 rounded-full flex items-center justify-center hover:bg-indigo-400 hover:text-white transition-all shadow-2xl"
                            >
                                <Compass className={`w-8 h-8 ${loading ? 'animate-spin-slow' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Subconscious Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-8">
                    <div className="bg-white/5 border border-white/5 rounded-[3.5rem] p-10 shadow-2xl backdrop-blur-xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.6em] text-white/20 mb-12 flex items-center gap-2 border-b border-white/5 pb-6">
                            <TrendingUp className="w-4 h-4" /> Psyche_Harmonics
                        </h3>

                        <div className="space-y-14">
                            <HarmonicMeter label="Clarity Index" value={clarity} color="bg-amber-400" />
                            <HarmonicMeter label="Emotional Balance" value={70} color="bg-rose-400" />
                            <HarmonicMeter label="Metaphor Strength" value={85} color="bg-indigo-400" />
                        </div>

                        <div className="mt-16 p-10 bg-indigo-500/5 border border-indigo-500/10 rounded-[2.5rem] flex items-start gap-6">
                            <Eye className="w-6 h-6 text-indigo-400 opacity-20 mt-1" />
                            <p className="text-[11px] uppercase font-bold tracking-[0.3em] leading-loose text-white/20 italic text-center w-full">
                                "The map is not the territory, but the territory is all you have."
                            </p>
                        </div>
                    </div>

                    <div className="bg-indigo-500/5 border border-indigo-500/10 rounded-[3rem] p-10 flex flex-col items-center justify-center gap-5 text-indigo-900">
                        <Moon className="w-12 h-12 opacity-20 animate-pulse" />
                        <span className="text-[10px] font-black uppercase tracking-[0.5em] text-center">Reflecting...</span>
                    </div>
                </div>
            </div>

            {status === 'awakened' && (
                <div className="fixed inset-0 z-[100] bg-[#1e1b4b]/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Sun className="w-24 h-24 text-amber-400 mx-auto mb-10 shadow-[0_0_80px_rgba(251,191,36,0.3)] animate-spin-slow" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-6 uppercase leading-none">Inner <br /><span className="text-indigo-400">Awakening</span></h2>
                        <p className="text-white/40 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">The horizon has opened. You are the architect of your own peace.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-white text-indigo-900 font-black uppercase tracking-[0.4em] hover:bg-indigo-400 hover:text-white transition-all shadow-2xl rounded-full"
                        >
                            Rest in Clarity
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const PsycheStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group cursor-crosshair">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-[#94a3b8]">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-indigo-400 transition-colors uppercase">{value}</p>
    </div>
);

const HarmonicMeter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-5">
        <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-[0.4em] text-white/10">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-[2px] bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full ${color} shadow-[0_0_20px_rgba(129,140,248,0.5)]`}
            />
        </div>
    </div>
);
