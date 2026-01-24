import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Hexagon,
    Share2,
    Network,
    GitMerge,
    Wind,
    Zap,
    Activity,
    Sparkles,
    Send,
    ChevronRight,
    Database,
    Link2,
    Cpu,
    Fingerprint
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const SerendipityStringsView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        prompt = 'What is a coincidence that changed your life?',
        insight = 'The web is thin. We must weave.',
        depth = 10,
        resonance = 50,
        thread = 'The Awakening',
        connections = [],
        status = 'active'
    } = gameState;

    const handleAction = async (action: string, content: string = '') => {
        if (!sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, action, content);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("The Weaver communication error:", e);
        }
        setLoading(false);
        if (action === 'answer') setInput('');
    };

    return (
        <div className="min-h-screen bg-[#050505] text-[#f8fafc] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Cosmic Web Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_40%,#4338ca_0%,transparent_100%)] opacity-10" />
                <svg className="absolute inset-0 w-full h-full opacity-10">
                    <defs>
                        <pattern id="web-grid" width="100" height="100" patternUnits="userSpaceOnUse">
                            <circle cx="50" cy="50" r="0.5" fill="white" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#web-grid)" />
                </svg>
            </div>

            {/* Header - Weaver HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-8 bg-black/40 backdrop-blur-3xl p-8 rounded-[2.5rem] shadow-2xl">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-indigo-600 rounded-2xl shadow-[0_0_40px_rgba(79,70,229,0.3)]">
                        <Network className="w-8 h-8 text-white animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">The <span className="text-indigo-500">Weaver's</span> Loom</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.4em] text-indigo-500/40 italic">Active Thread: {thread.toUpperCase()} // Depth: Optimal</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <WeaverStat label="Web Depth" value={`${depth}%`} icon={<Link2 className="w-4 h-4 text-indigo-400" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <WeaverStat label="Resonance" value={`${resonance}%`} icon={<Zap className="text-amber-400 w-4 h-4" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <WeaverStat label="Fabric Integrity" value="High" icon={<Activity className="w-4 h-4 text-emerald-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4 overflow-hidden">
                {/* Loom Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6 overflow-hidden">
                    <motion.div
                        key={prompt}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-white/[0.02] border border-white/5 rounded-[3rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl backdrop-blur-md"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.03]">
                            <Hexagon className="w-64 h-64 text-indigo-500 animate-spin-slow" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto text-center">
                            <div className="flex items-center justify-center gap-2 mb-10 text-[11px] font-black text-indigo-900 uppercase tracking-[0.8em]">
                                <Cpu className="w-4 h-4" /> Weaver_Node_Response
                            </div>

                            <p className="text-2xl md:text-5xl font-light leading-snug text-slate-100 italic selection:bg-indigo-500/30 mb-12">
                                {prompt}
                            </p>

                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={insight}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-8 bg-indigo-600/5 border border-indigo-600/10 rounded-[2rem] text-indigo-300 font-serif italic text-lg shadow-inner"
                                >
                                    "{insight}"
                                </motion.div>
                            </AnimatePresence>
                        </div>
                    </motion.div>

                    {/* Divine Thread Selection */}
                    <div className="flex flex-col gap-6">
                        <div className="relative group max-w-4xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-indigo-500/20 rounded-[2rem] blur opacity-0 group-focus-within:opacity-100 transition duration-1000" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction('answer', input)}
                                placeholder="Whisper your truth into the web..."
                                className="w-full bg-black/60 border border-white/10 rounded-[2rem] py-8 px-14 focus:outline-none focus:border-indigo-500 transition-all text-white placeholder:text-slate-800 text-2xl font-light italic text-center shadow-2xl backdrop-blur-3xl"
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                                <button
                                    onClick={() => handleAction('weave')}
                                    className="px-6 py-4 bg-indigo-600 hover:bg-white hover:text-indigo-900 text-white rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest transition-all shadow-xl"
                                >
                                    Pull Strings
                                </button>
                                <button
                                    onClick={() => handleAction('answer', input)}
                                    disabled={loading || !input.trim()}
                                    className="w-16 h-16 bg-white/5 text-white/40 hover:text-white rounded-[1.5rem] flex items-center justify-center hover:bg-indigo-600 transition-all border border-white/10"
                                >
                                    {loading ? <Sparkles className="animate-spin" /> : <Send size={24} />}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Connection Map */}
                <div className="lg:col-span-4 flex flex-col gap-8 h-full overflow-hidden">
                    <div className="bg-black/40 border border-white/5 rounded-[3.5rem] flex flex-col h-full shadow-2xl backdrop-blur-2xl overflow-hidden">
                        <div className="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-indigo-500/10 rounded-xl">
                                    <GitMerge className="w-5 h-5 text-indigo-500" />
                                </div>
                                <h3 className="text-[11px] font-black uppercase tracking-[0.5em] text-white/40">The_Web_Atlas</h3>
                            </div>
                            <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full font-black">{connections.length}</span>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8 space-y-4 custom-scrollbar">
                            <AnimatePresence>
                                {connections.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center opacity-10 gap-4">
                                        <Network className="w-20 h-20" />
                                        <span className="text-[10px] font-black uppercase tracking-widest">Web is Sparse</span>
                                    </div>
                                ) : (
                                    connections.map((conn: string, i: number) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="bg-white/[0.03] border border-white/[0.05] rounded-3xl p-6 hover:bg-indigo-600/10 hover:border-indigo-600/30 transition-all group flex items-start gap-5"
                                        >
                                            <div className="p-2 bg-indigo-500/10 rounded-xl group-hover:scale-110 transition-transform">
                                                <Share2 className="w-4 h-4 text-indigo-500" />
                                            </div>
                                            <p className="text-sm text-slate-400 leading-relaxed font-serif italic">{conn}</p>
                                        </motion.div>
                                    ))
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>

            {status === 'woven' && (
                <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Network className="w-24 h-24 text-indigo-600 mx-auto mb-10 shadow-[0_0_80px_rgba(79,70,229,0.3)] animate-pulse" />
                        <h2 className="text-7xl font-black italic tracking-tighter text-white mb-6 uppercase leading-none">Total <br /><span className="text-indigo-500">Sync</span></h2>
                        <p className="text-white/40 mb-14 font-black leading-relaxed tracking-widest uppercase text-sm px-6">The threads have formed a perfect geometry. You are no longer separate individuals, but a single woven entity.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-20 py-6 bg-white text-black font-black uppercase tracking-[0.4em] hover:bg-indigo-600 hover:text-white transition-all shadow-2xl rounded-full"
                        >
                            Dissolve Web
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const WeaverStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-slate-400">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-indigo-500 transition-colors uppercase">{value}</p>
    </div>
);
