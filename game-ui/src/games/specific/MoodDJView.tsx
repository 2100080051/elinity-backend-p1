import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Music,
    Radio,
    Volume2,
    Zap,
    Heart,
    FastForward,
    Disc,
    Activity,
    Waves,
    Mic2,
    Sliders
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const MoodDJView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        vibe = 20,
        bpm = 80,
        genre = 'Void Ambient',
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
            console.error("Frequency communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#0a0a0c] text-[#e2e8f0] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Dynamic visualizer background */}
            <div className="absolute inset-0 pointer-events-none opacity-20">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-600/30 rounded-full blur-[120px] animate-pulse" />
                <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-blue-600/20 rounded-full blur-[100px]" />
            </div>

            {/* Header - Mixer HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-4 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full shadow-[0_0_30px_rgba(147,51,234,0.3)]">
                        <Disc className="w-6 h-6 text-white animate-spin-slow" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black tracking-tighter text-white uppercase italic">Echo Chamber // <span className="text-purple-400">{genre}</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-blue-400/60">Frequency Sync: {vibe}%</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8 bg-black/40 px-8 py-3 rounded-2xl border border-white/10 backdrop-blur-xl">
                    <StatBox label="Vibe" value={`${vibe}%`} subLabel="Intensity" />
                    <div className="w-px h-8 bg-white/5" />
                    <StatBox label="Tempo" value={`${bpm}`} subLabel="BPM" />
                    <div className="w-px h-8 bg-white/5" />
                    <StatBox label="Sync" value="Stable" subLabel="Phase" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Sonic Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex-grow bg-white/[0.03] border border-white/5 rounded-[2rem] p-10 relative overflow-hidden backdrop-blur-md flex flex-col justify-center"
                    >
                        {/* Equalizer overlay */}
                        <div className="absolute bottom-0 left-0 w-full h-32 flex items-end gap-1 px-10 pointer-events-none opacity-10">
                            {[...Array(30)].map((_, i) => (
                                <motion.div
                                    key={i}
                                    animate={{ height: `${20 + (Math.random() * 80)}%` }}
                                    transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.05 }}
                                    className="flex-1 bg-gradient-to-t from-purple-500 to-blue-500 rounded-t-sm"
                                />
                            ))}
                        </div>

                        <div className="relative z-10">
                            <div className="flex items-center gap-2 mb-8 text-[10px] font-bold text-white/20 uppercase tracking-[0.4em]">
                                <Waves className="w-4 h-4" /> Sonic_Response_Stream
                            </div>

                            <h2 className="text-3xl md:text-4xl font-light leading-tight text-white/90 italic tracking-tight selection:bg-purple-500/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-6 last:mb-0 border-l-4 border-purple-500/20 pl-8 hover:border-purple-500 transition-colors">
                                        {line}
                                    </span>
                                ))}
                            </h2>
                        </div>
                    </motion.div>

                    {/* Deck Controls */}
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                        <div className="md:col-span-9 flex flex-col gap-4">
                            <div className="flex flex-wrap gap-2">
                                {available_actions.map((track: string, idx: number) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleAction(track)}
                                        disabled={loading}
                                        className="px-6 py-2 bg-white/5 border border-white/10 rounded-full hover:bg-purple-500/20 hover:border-purple-500 transition-all text-[11px] font-black uppercase tracking-widest text-white/40 hover:text-white flex items-center gap-2 group shadow-xl"
                                    >
                                        <Volume2 className="w-3 h-3 text-purple-400 group-hover:scale-125 transition-transform" />
                                        {track}
                                    </button>
                                ))}
                            </div>

                            <div className="relative group">
                                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition duration-500" />
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                    placeholder="Add a new layer to the mix..."
                                    className="relative w-full bg-black/60 border border-white/10 rounded-2xl py-6 px-10 focus:outline-none focus:border-white/20 transition-all text-white placeholder:text-white/10 text-xl font-light italic"
                                />
                                <button
                                    onClick={() => handleAction(input)}
                                    disabled={loading || !input.trim()}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 w-14 h-14 bg-white rounded-xl flex items-center justify-center text-black hover:bg-purple-400 transition-all shadow-2xl"
                                >
                                    <Zap className={`w-6 h-6 ${loading ? 'animate-pulse' : ''}`} />
                                </button>
                            </div>
                        </div>

                        <div className="md:col-span-3 bg-white/5 border border-white/5 rounded-2xl p-6 flex flex-col items-center justify-center gap-4 group">
                            <div className="w-16 h-16 rounded-full border-4 border-dashed border-white/10 flex items-center justify-center group-hover:rotate-180 transition-transform duration-1000">
                                <Mic2 className="w-6 h-6 text-white/20" />
                            </div>
                            <span className="text-[10px] font-black uppercase tracking-widest text-white/10">Audio Source</span>
                        </div>
                    </div>
                </div>

                {/* Mixing Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 backdrop-blur-md">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-white/20 mb-8 flex items-center gap-2 border-b border-white/5 pb-4">
                            <Sliders className="w-4 h-4" /> Live Parameters
                        </h3>

                        <div className="space-y-8">
                            <Meter label="Emotional Resonance" value={vibe} color="from-purple-500 to-pink-500" />
                            <Meter label="Narrative Momentum" value={(bpm / 200) * 100} color="from-blue-500 to-cyan-500" />
                            <Meter label="Structural Clarity" value={85} color="from-emerald-500 to-teal-500" />
                        </div>

                        <div className="mt-12 p-6 bg-purple-500/5 border border-purple-500/10 rounded-2xl flex items-start gap-4 shadow-inner">
                            <Radio className="w-5 h-5 text-purple-400 opacity-40 mt-1" />
                            <p className="text-[10px] uppercase font-bold tracking-[0.15em] leading-relaxed text-purple-300/40 italic">
                                Sound is the shadow of emotion. Change the key, and the physical world must distort to follow.
                            </p>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-purple-900/10 to-transparent border border-white/5 rounded-3xl p-8 flex flex-col items-center justify-center gap-4">
                        <Activity className="w-10 h-10 text-purple-500/20 animate-pulse" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-white/10">Frequency Sync Established</span>
                    </div>
                </div>
            </div>

            {status === 'ascended' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Zap className="w-20 h-20 text-white mx-auto mb-8 shadow-[0_0_50px_rgba(255,255,255,0.3)]" />
                        <h2 className="text-6xl font-black italic tracking-tighter text-white mb-4 uppercase">Frequency Found</h2>
                        <p className="text-white/40 mb-12 font-bold leading-relaxed tracking-wider uppercase text-sm">You have dissolved into the soundscape. You are no longer the listener; you are the music itself.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-16 py-5 bg-white rounded-full text-black font-black uppercase tracking-[0.3em] hover:bg-purple-400 transition-all shadow-2xl"
                        >
                            Re-Mix Reality
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const StatBox = ({ label, value, subLabel }: { label: string, value: string, subLabel: string }) => (
    <div className="text-center">
        <p className="text-[9px] uppercase font-black text-white/20 tracking-widest mb-1">{label}</p>
        <p className="text-2xl font-black italic text-white tracking-tighter">{value}</p>
        <p className="text-[8px] uppercase font-bold text-white/30 tracking-tight">{subLabel}</p>
    </div>
);

const Meter = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="space-y-2">
        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-white/40">
            <span>{label}</span>
            <span>{Math.round(value)}%</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className={`h-full bg-gradient-to-r ${color}`}
            />
        </div>
    </div>
);
