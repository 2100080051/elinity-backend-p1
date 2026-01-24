import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Globe,
    Map,
    Users,
    History,
    User,
    Zap,
    Activity,
    Sparkles,
    Send,
    ChevronRight,
    Database,
    Flame,
    Wind,
    Waves,
    Mountain
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const WorldBuildersView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        round = 'Geography',
        mana = 100,
        population = 0,
        stability = 100,
        world_codex = [],
        last_ai_response = {},
        status = 'active'
    } = gameState;

    const narrative = last_ai_response?.narrative || "At first, there was only the void...";
    const nextPrompt = last_ai_response?.next_prompt || "Describe the first landmass.";

    const handleAction = async (action: string, content: string = '') => {
        if (!sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, action, content);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("World Builder communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#020617] text-[#f8fafc] font-sans p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Cosmic Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,#1e293b_0%,transparent_100%)] opacity-20" />
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-30" />
            </div>

            {/* Header - Architect HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-8 bg-black/40 backdrop-blur-3xl p-8 rounded-[2.5rem] shadow-2xl">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-blue-600 rounded-2xl shadow-[0_0_40px_rgba(37,99,235,0.3)]">
                        <Globe className="w-8 h-8 text-white animate-spin-slow" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">Genesis <span className="text-blue-500">Architect</span></h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.4em] text-blue-500/40 italic">Epoch: {round.toUpperCase()} // Reality: Stable</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <ArchitectStat label="Aether Mana" value={mana.toString()} icon={<Zap className="w-4 h-4 text-blue-400" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <ArchitectStat label="Civilization" value={population.toLocaleString()} icon={<Users className="text-emerald-400 w-4 h-4" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <ArchitectStat label="Stability" value={`${stability}%`} icon={<Activity className="w-4 h-4 text-rose-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4 overflow-hidden">
                {/* Creation Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6 overflow-hidden">
                    <motion.div
                        key={narrative}
                        initial={{ opacity: 0, scale: 1.05 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-white/[0.02] border border-white/5 rounded-[3rem] p-12 relative overflow-hidden flex flex-col justify-center shadow-2xl backdrop-blur-md"
                    >
                        <div className="absolute top-10 right-10 opacity-[0.03]">
                            <Mountain className="w-64 h-64 text-blue-500" />
                        </div>

                        <div className="relative z-10 max-w-4xl mx-auto">
                            <div className="flex items-center gap-2 mb-10 text-[11px] font-black text-blue-900 uppercase tracking-[0.8em]">
                                <Database className="w-4 h-4" /> Genesis_Log_Primary
                            </div>

                            <p className="text-2xl md:text-5xl font-light leading-snug text-slate-100 italic selection:bg-blue-500/30">
                                {narrative.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-8 last:mb-0 border-l-2 border-blue-500/20 pl-12 hover:border-blue-500 transition-all duration-500">
                                        {line}
                                    </span>
                                ))}
                            </p>

                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 0.6 }}
                                className="mt-16 text-lg text-blue-400 font-bold tracking-[0.2em] flex items-center gap-4"
                            >
                                <ChevronRight size={24} className="animate-pulse" />
                                {nextPrompt}
                            </motion.div>
                        </div>
                    </motion.div>

                    {/* Divine Interventions */}
                    <div className="flex flex-col gap-6">
                        <div className="relative group max-w-4xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-blue-500/20 rounded-[2rem] blur opacity-0 group-focus-within:opacity-100 transition duration-1000" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction('create', input)}
                                placeholder="Speak your decree into the void..."
                                className="w-full bg-black/60 border border-white/10 rounded-[2rem] py-8 px-14 focus:outline-none focus:border-blue-500 transition-all text-white placeholder:text-slate-800 text-2xl font-light italic text-center shadow-2xl backdrop-blur-3xl"
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                                <button
                                    onClick={() => handleAction('advance_round', 'skip')}
                                    className="px-6 py-4 bg-white/5 hover:bg-white/10 text-white/40 hover:text-white rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest transition-all"
                                >
                                    End Age
                                </button>
                                <button
                                    onClick={() => handleAction('create', input)}
                                    disabled={loading || !input.trim()}
                                    className="w-16 h-16 bg-blue-600 text-white rounded-[1.5rem] flex items-center justify-center hover:bg-white hover:text-blue-900 transition-all shadow-xl"
                                >
                                    {loading ? <Sparkles className="animate-spin" /> : <Send size={24} />}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* World Codex */}
                <div className="lg:col-span-4 flex flex-col gap-8 h-full overflow-hidden">
                    <div className="bg-black/40 border border-white/5 rounded-[3.5rem] flex flex-col h-full shadow-2xl backdrop-blur-2xl overflow-hidden">
                        <div className="p-10 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-blue-500/10 rounded-xl">
                                    <Database className="w-5 h-5 text-blue-500" />
                                </div>
                                <h3 className="text-[11px] font-black uppercase tracking-[0.5em] text-white/40">The_Codex</h3>
                            </div>
                            <span className="text-[10px] bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-black">{world_codex.length}</span>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8 space-y-6 custom-scrollbar">
                            <AnimatePresence>
                                {world_codex.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center opacity-10 gap-4">
                                        <Globe className="w-20 h-20" />
                                        <span className="text-[10px] font-black uppercase tracking-widest">Awaiting Creation</span>
                                    </div>
                                ) : (
                                    world_codex.map((entry: any, i: number) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="bg-white/[0.03] border border-white/[0.05] rounded-3xl p-6 hover:bg-white/[0.08] transition-all group"
                                        >
                                            <div className="flex items-center gap-3 mb-4 opacity-40 group-hover:opacity-100 transition-opacity">
                                                <CodexIcon type={entry.type} />
                                                <span className="text-[9px] font-black uppercase tracking-widest text-blue-400">{entry.type}</span>
                                            </div>
                                            <h4 className="text-lg font-bold text-white mb-2 leading-tight">{entry.title}</h4>
                                            <p className="text-sm text-slate-400 leading-relaxed font-serif italic">{entry.description}</p>
                                        </motion.div>
                                    ))
                                )}
                            </AnimatePresence>
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
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-blue-500 transition-colors uppercase">{value}</p>
    </div>
);

const CodexIcon = ({ type }: { type: string }) => {
    switch (type?.toLowerCase()) {
        case 'geography': return <Mountain size={14} />;
        case 'culture': return <Users size={14} />;
        case 'history': return <History size={14} />;
        case 'characters': return <User size={14} />;
        default: return <Sparkles size={14} />;
    }
}
