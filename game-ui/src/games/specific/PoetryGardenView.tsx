import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Flower2,
    Wind,
    Droplets,
    Sun,
    Leaf,
    PenTool,
    CloudRain,
    ChevronRight,
    Scroll,
    Heart,
    Palette,
    Sparkles
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const PoetryGardenView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        inspiration = 10,
        ink = 100,
        vibe = 'Zen Reflection',
        blooms = [],
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
            console.error("Lyric-Weaver communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#fcfaf2] text-[#4a4a4a] font-serif p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Soft Organic Background Elements */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-10 right-10 w-64 h-64 bg-pink-100/50 rounded-full blur-3xl" />
                <div className="absolute bottom-20 left-10 w-80 h-80 bg-green-50/50 rounded-full blur-3xl" />
            </div>

            {/* Header - Garden Status */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-black/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-green-100 rounded-full border border-green-200 shadow-sm">
                        <Flower2 className="w-6 h-6 text-green-700" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-light tracking-widest text-[#2d3a3a] uppercase">The Poetry Garden</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-green-700/60 italic">{vibe} Atmosphere</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-bold text-black/20 tracking-widest mb-1">Creative Ink</p>
                        <div className="flex items-center gap-3">
                            <div className="w-24 h-1.5 bg-black/5 rounded-full overflow-hidden">
                                <motion.div
                                    animate={{ width: `${ink}%` }}
                                    className="h-full bg-slate-800"
                                />
                            </div>
                            <span className="text-xl font-light italic text-[#2d3a3a]">{ink}ml</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Center: Scroll Narrative */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-white/40 border border-[#e2e8f0] rounded-[2rem] p-12 backdrop-blur-xl shadow-inner relative overflow-y-auto custom-scrollbar"
                    >
                        <div className="absolute top-6 right-6 opacity-10">
                            <Scroll className="w-12 h-12 rotate-12" />
                        </div>

                        <div className="prose prose-slate max-w-none text-2xl font-light leading-relaxed text-[#334155] italic selection:bg-pink-100 pb-20">
                            {scene.split('\n').map((line: string, i: number) => (
                                <p key={i} className="mb-6 last:mb-0 hover:text-[#0f172a] transition-colors">
                                    {line}
                                </p>
                            ))}
                        </div>

                        {/* Visual Inspiration Wave */}
                        <div className="absolute bottom-10 left-0 w-full px-12">
                            <div className="flex items-center gap-4">
                                <span className="text-[10px] uppercase font-black tracking-widest text-black/10">Inspiration Flow</span>
                                <div className="flex-grow flex items-center h-4 gap-0.5">
                                    {[...Array(40)].map((_, i) => (
                                        <motion.div
                                            key={i}
                                            animate={{ height: `${20 + (Math.random() * 80)}%` }}
                                            transition={{ repeat: Infinity, duration: 2, delay: i * 0.05 }}
                                            className={`flex-grow rounded-full ${i < (inspiration * 0.4) ? 'bg-pink-300/30' : 'bg-black/5'}`}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Seeds of Thought (Actions) */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-2 justify-center">
                            {available_actions.map((path: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(path)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-white/50 border border-black/5 rounded-full hover:bg-white hover:border-pink-200 transition-all text-[11px] font-bold tracking-widest text-[#64748b] hover:text-pink-600 flex items-center gap-2 shadow-sm"
                                >
                                    <Leaf className="w-3 h-3 text-green-400 group-hover:rotate-45 transition-transform" />
                                    {path}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your verse to the soil..."
                                className="w-full bg-white/60 border border-[#e2e8f0] rounded-full py-5 px-10 focus:outline-none focus:border-pink-300 transition-all text-[#1e293b] placeholder:text-slate-300 text-xl font-light italic shadow-sm"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center text-white hover:bg-slate-700 transition-all shadow-lg"
                            >
                                <PenTool className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Garden Blooms */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white/40 border border-[#e2e8f0] rounded-3xl p-8 backdrop-blur-md">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 border-b border-black/5 pb-4 mb-6 flex items-center gap-2">
                            <Palette className="w-4 h-4" /> Active Blooms
                        </h3>

                        <div className="grid grid-cols-2 gap-4">
                            {blooms.length > 0 ? blooms.map((b: string, i: number) => (
                                <motion.div
                                    initial={{ scale: 0.8, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    key={i}
                                    className="p-4 bg-white/60 border border-pink-50 rounded-2xl flex flex-col items-center gap-2 group hover:border-pink-200 transition-all cursor-default"
                                >
                                    <div className="w-10 h-10 rounded-full bg-pink-50 flex items-center justify-center text-pink-400 group-hover:scale-110 transition-transform">
                                        <Flower2 className="w-5 h-5" />
                                    </div>
                                    <span className="text-[10px] font-black uppercase tracking-tighter text-[#4a4a4a] text-center">{b}</span>
                                </motion.div>
                            )) : (
                                <p className="col-span-2 text-[10px] uppercase font-bold text-slate-300 tracking-widest text-center py-8">The garden is dormant...</p>
                            )}
                        </div>
                    </div>

                    {/* Garden Spells (Stats) */}
                    <div className="space-y-4">
                        <StatCard icon={<Sun className="w-4 h-4 text-orange-400" />} label="Inspiration" value={`${inspiration}%`} />
                        <StatCard icon={<Droplets className="w-4 h-4 text-blue-400" />} label="Garden Vibe" value={vibe} />
                        <StatCard icon={<Heart className="w-4 h-4 text-red-400" />} label="Resonance" value={inspiration > 70 ? 'High' : 'Gentle'} />
                    </div>

                    <div className="p-6 bg-green-50 rounded-2xl border border-green-100 flex items-start gap-4 mt-auto">
                        <Wind className="w-6 h-6 text-green-700 opacity-20 mt-1" />
                        <p className="text-[10px] uppercase font-bold tracking-widest leading-loose text-green-900/40">
                            Words are seeds. Water them with thought, and watch the landscape shifting under your gaze.
                        </p>
                    </div>
                </div>
            </div>

            {status === 'bloomed' && (
                <div className="fixed inset-0 z-[100] bg-white/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Sparkles className="w-20 h-20 text-pink-400 mx-auto mb-8 animate-pulse" />
                        <h2 className="text-5xl font-light italic tracking-tighter text-[#2d3a3a] mb-4">Garden Ascended</h2>
                        <p className="text-slate-500 mb-10 font-light leading-relaxed">Your verse has taken permanent root in the collective consciousness. The garden will never forget your touch.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-12 py-4 bg-slate-800 rounded-full text-white font-bold uppercase tracking-widest hover:bg-slate-700 transition-all shadow-xl"
                        >
                            Return to Soil
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const StatCard = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="bg-white/40 border border-[#e2e8f0] p-4 rounded-2xl flex items-center justify-between backdrop-blur-sm">
        <div className="flex items-center gap-3">
            {icon}
            <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400">{label}</span>
        </div>
        <span className="text-xs font-bold text-[#1e293b]">{value}</span>
    </div>
);
