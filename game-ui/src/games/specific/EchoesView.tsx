import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Waves,
    Mic2,
    Activity,
    Volume2,
    Radio,
    Zap,
    Sparkles,
    Send,
    ChevronRight,
    Database,
    Music,
    Wind,
    Layers,
    Fingerprint
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const EchoesView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        creative_prompt = 'The silence waits for your frequency.',
        resonance = 10,
        clarity = 50,
        gallery = [],
        status = 'active',
        last_ai_response = {}
    } = gameState;

    const echo = last_ai_response?.echo_synthesis || '';

    const handleAction = async (action: string, content: string = '') => {
        if (!sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, action, content);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("The Architect communication error:", e);
        }
        setLoading(false);
        if (action === 'express') setInput('');
    };

    return (
        <div className="min-h-screen bg-[#020617] text-[#f8fafc] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Sonic Wave Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_40%,#0ea5e9_0%,transparent_100%)] opacity-10" />
                <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-sky-950/20 to-transparent" />

                {/* Visualizer Simulation */}
                <div className="absolute bottom-0 left-0 right-0 h-32 flex items-end justify-center gap-1 opacity-20">
                    {[...Array(60)].map((_, i) => (
                        <motion.div
                            key={i}
                            animate={{
                                height: [20, Math.random() * 80 + 20, 20],
                                opacity: [0.1, 0.4, 0.1]
                            }}
                            transition={{
                                duration: 1 + Math.random(),
                                repeat: Infinity,
                                ease: "easeInOut"
                            }}
                            className="w-1 bg-sky-500 rounded-t-full"
                        />
                    ))}
                </div>
            </div>

            {/* Header - Sound Architect HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-8 bg-black/40 backdrop-blur-3xl p-8 rounded-[2.5rem] shadow-2xl">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-sky-600 rounded-2xl shadow-[0_0_40px_rgba(14,165,233,0.3)]">
                        <Waves className="w-8 h-8 text-white animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">Echoes <span className="text-sky-500">&</span> Expressions</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.4em] text-sky-500/40 italic">Chamber: ACTIVE // Frequency: STABLE</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <ArchitectStat label="Resonance" value={`${resonance}%`} icon={<Activity className="w-4 h-4 text-sky-400" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <ArchitectStat label="Clarity" value={`${clarity}%`} icon={<Zap className="text-amber-400 w-4 h-4" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <ArchitectStat label="Acoustics" value="Premium" icon={<Music className="w-4 h-4 text-emerald-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4 overflow-hidden">
                {/* Expression Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6 overflow-hidden">
                    <motion.div
                        key={creative_prompt}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-white/[0.02] border border-white/5 rounded-[3rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl backdrop-blur-md"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.03]">
                            <Volume2 className="w-64 h-64 text-sky-500" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto text-center">
                            <div className="flex items-center justify-center gap-2 mb-10 text-[11px] font-black text-sky-900 uppercase tracking-[0.8em]">
                                <Radio className="w-4 h-4" /> Sound_Architect_Prompt
                            </div>

                            <p className="text-2xl md:text-5xl font-light leading-snug text-slate-100 italic selection:bg-sky-500/30 mb-12">
                                {creative_prompt}
                            </p>

                            <AnimatePresence mode="wait">
                                {echo && (
                                    <motion.div
                                        key={echo}
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="p-10 bg-sky-600/5 border border-sky-600/10 rounded-[2.5rem] text-sky-300 font-serif italic text-2xl shadow-inner relative overflow-hidden"
                                    >
                                        <div className="absolute top-0 left-0 w-full h-[1px] bg-sky-500/20" />
                                        "{echo}"
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </motion.div>

                    {/* Vocalist Input */}
                    <div className="flex flex-col gap-6">
                        <div className="relative group max-w-4xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-sky-500/20 rounded-[2rem] blur opacity-0 group-focus-within:opacity-100 transition duration-1000" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction('express', input)}
                                placeholder="Express your current frequency..."
                                className="w-full bg-black/60 border border-white/10 rounded-[2rem] py-8 px-14 focus:outline-none focus:border-sky-500 transition-all text-white placeholder:text-slate-800 text-2xl font-light italic text-center shadow-2xl backdrop-blur-3xl"
                            />
                            <div className="absolute right-6 top-1/2 -translate-y-1/2 flex items-center gap-3">
                                <button
                                    onClick={() => handleAction('express', input)}
                                    disabled={loading || !input.trim()}
                                    className="w-16 h-16 bg-sky-600 text-white rounded-[1.5rem] flex items-center justify-center hover:bg-white hover:text-sky-900 transition-all shadow-xl"
                                >
                                    {loading ? <Sparkles className="animate-spin" /> : <Mic2 size={24} />}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Resonance Gallery */}
                <div className="lg:col-span-4 flex flex-col gap-8 h-full overflow-hidden">
                    <div className="bg-black/40 border border-white/5 rounded-[3.5rem] flex flex-col h-full shadow-2xl backdrop-blur-2xl overflow-hidden">
                        <div className="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-sky-500/10 rounded-xl">
                                    <Layers className="w-5 h-5 text-sky-500" />
                                </div>
                                <h3 className="text-[11px] font-black uppercase tracking-[0.5em] text-white/40">The_Gallery</h3>
                            </div>
                            <span className="text-[10px] bg-sky-500/20 text-sky-400 px-3 py-1 rounded-full font-black">{gallery.length}</span>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8 space-y-4 custom-scrollbar">
                            <AnimatePresence>
                                {gallery.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center opacity-10 gap-4">
                                        <Waves className="w-20 h-20" />
                                        <span className="text-[10px] font-black uppercase tracking-widest">Total Silence</span>
                                    </div>
                                ) : (
                                    gallery.map((item: any, i: number) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="bg-white/[0.03] border border-white/[0.05] rounded-3xl p-6 hover:bg-sky-600/10 hover:border-sky-600/30 transition-all group"
                                        >
                                            <div className="flex items-center gap-3 mb-4 opacity-40 group-hover:opacity-100 transition-opacity">
                                                <Fingerprint className="w-4 h-4 text-sky-500" />
                                                <span className="text-[9px] font-black uppercase tracking-widest text-sky-400">Vocalist_Exp</span>
                                            </div>
                                            <p className="text-sm text-slate-400 leading-relaxed font-serif italic">"{item.expression}"</p>
                                        </motion.div>
                                    ))
                                )}
                            </AnimatePresence>
                        </div>

                        <div className="p-8 bg-black/60 border-t border-white/5">
                            <div className="flex items-center gap-3 text-[10px] font-black uppercase tracking-widest text-white/20">
                                <Wind className="w-4 h-4 animate-bounce" />
                                <span>Ambience: OPTIMAL</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const ArchitectStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-slate-400">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-sky-500 transition-colors uppercase">{value}</p>
    </div>
);
