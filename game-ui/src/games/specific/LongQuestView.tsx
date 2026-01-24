import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Scroll,
    Map,
    Backpack,
    Sword,
    Compass,
    HeartPulse,
    Brain,
    Users,
    MapPin,
    Search,
    Shield,
    Sparkles,
    ChevronRight,
    Database,
    Skull,
    Flame,
    Wind
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const LongQuestView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        campaign_name = 'The Azure Peaks',
        fortitude = 100,
        wisdom = 10,
        camaraderie = 50,
        quest_log = [],
        status = 'active',
        last_ai_response = {}
    } = gameState;

    const narrative = last_ai_response?.narrative || "The adventure begins. The road ahead is long, but glory awaits.";
    const options = last_ai_response?.options || [];
    const visual = last_ai_response?.visual_cue || "Uncharted Lands";

    const handleAction = async (act: string) => {
        if (!sessionId || !gameSlug || loading) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', act);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) {
            console.error("The Chronicler communication error:", e);
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-[#0c0a09] text-[#f5f5f4] font-serif p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Ancient Map Overlay */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_40%,#451a03_0%,transparent_100%)] opacity-20" />
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/old-map.png')] opacity-10" />
            </div>

            {/* Header - Quest Leader HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-amber-900/20 pb-8 bg-black/40 backdrop-blur-3xl p-8 rounded-[2.5rem] shadow-2xl relative">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-amber-500/20 to-transparent" />

                <div className="flex items-center gap-6">
                    <div className="p-4 bg-amber-900/20 rounded-2xl border border-amber-500/20 shadow-xl">
                        <Map className="w-8 h-8 text-amber-500 animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-black tracking-tighter text-white uppercase italic">The <span className="text-amber-600">Long</span> Quest</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-2 h-2 rounded-full bg-amber-600 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-[0.4em] text-amber-600/40 italic">Campaign: {campaign_name.toUpperCase()} // Difficulty: BRUTAL</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-10">
                    <QuestStat label="Fortitude" value={`${fortitude}%`} icon={<HeartPulse className="w-4 h-4 text-rose-500" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <QuestStat label="Wisdom" value={`${wisdom}%`} icon={<Brain className="text-amber-500 w-4 h-4" />} />
                    <div className="w-px h-10 bg-white/5" />
                    <QuestStat label="Camaraderie" value={`${camaraderie}%`} icon={<Users className="w-4 h-4 text-emerald-400" />} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4 overflow-hidden">
                {/* Journal Sidebar */}
                <div className="lg:col-span-3 flex flex-col gap-6 h-full overflow-hidden">
                    <div className="bg-[#1c1917] border border-amber-900/20 rounded-[3rem] flex flex-col h-full shadow-2xl relative overflow-hidden">
                        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/paper.png')] opacity-5" />

                        <div className="p-8 border-b border-amber-900/10 flex items-center justify-between bg-black/20">
                            <div className="flex items-center gap-3">
                                <Scroll className="w-5 h-5 text-amber-600" />
                                <h3 className="text-[11px] font-black uppercase tracking-[0.5em] text-amber-900">Quest_Log</h3>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar bg-amber-950/5">
                            <AnimatePresence>
                                {quest_log.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center opacity-10 gap-4">
                                        <Skull className="w-16 h-16" />
                                        <span className="text-[10px] font-black uppercase tracking-widest text-center">No Deeds Recorded</span>
                                    </div>
                                ) : (
                                    quest_log.map((log: string, i: number) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="p-4 border-l-2 border-amber-900/30 hover:border-amber-500 transition-colors bg-black/10 rounded-r-xl"
                                        >
                                            <p className="text-xs text-amber-100/60 font-serif italic leading-relaxed">
                                                {log}
                                            </p>
                                        </motion.div>
                                    ))
                                )}
                            </AnimatePresence>
                        </div>

                        <div className="p-6 bg-black/40 border-t border-amber-900/10 flex justify-around">
                            <InventoryItem icon={<Backpack size={16} />} label="Pack" count={3} />
                            <InventoryItem icon={<Sword size={16} />} label="Arms" count={1} />
                            <InventoryItem icon={<Shield size={16} />} label="Guard" count={2} />
                        </div>
                    </div>
                </div>

                {/* Narrative Engine */}
                <div className="lg:col-span-9 flex flex-col gap-6 overflow-hidden">
                    {/* Visual Cue Header */}
                    <div className="h-48 rounded-[3rem] bg-gradient-to-br from-amber-950 to-black border border-amber-900/20 relative overflow-hidden shadow-2xl group shrink-0">
                        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/dark-leather.png')] opacity-20" />
                        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />

                        <div className="absolute bottom-10 left-12 flex flex-col gap-2">
                            <div className="flex items-center gap-3 text-amber-500 text-[10px] font-black uppercase tracking-[0.5em] bg-black/60 backdrop-blur-md px-5 py-2 rounded-full border border-amber-500/20 w-fit">
                                <MapPin size={12} className="animate-bounce" /> {visual}
                            </div>
                            <h2 className="text-4xl font-serif text-white italic drop-shadow-2xl">The Path of Destiny</h2>
                        </div>

                        <div className="absolute top-10 right-12 opacity-5 scale-150 rotate-12 transition-transform group-hover:rotate-0 duration-1000">
                            <Skull size={120} />
                        </div>
                    </div>

                    {/* Narrative Display */}
                    <motion.div
                        key={narrative}
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex-grow bg-white/[0.02] border border-white/5 rounded-[3rem] p-16 relative overflow-hidden flex flex-col justify-center shadow-2xl backdrop-blur-md"
                    >
                        <div className="absolute top-0 right-0 p-10 font-serif text-[180px] text-white/[0.01] -rotate-12 pointer-events-none tracking-tighter uppercase font-black">
                            Quest
                        </div>

                        <div className="relative z-10 max-w-4xl">
                            <div className="flex items-center gap-3 mb-10 text-[11px] font-black text-amber-900 uppercase tracking-[0.8em]">
                                <Compass className="w-4 h-4" /> Chronicler_Transmission
                            </div>

                            <p className="text-2xl md:text-4xl lg:text-5xl font-light leading-snug text-slate-100 italic selection:bg-amber-600/30">
                                {narrative}
                            </p>
                        </div>
                    </motion.div>

                    {/* Choice Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 h-56">
                        {options.map((opt: string, i: number) => (
                            <motion.button
                                key={i}
                                whileHover={{ scale: 1.02, y: -4 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => handleAction(opt)}
                                disabled={loading}
                                className="group relative bg-[#1c1917] hover:bg-amber-900/10 border border-amber-900/20 rounded-[2.5rem] p-8 text-left transition-all overflow-hidden flex flex-col justify-between shadow-xl"
                            >
                                <div className="absolute top-0 right-0 p-6 opacity-[0.05] group-hover:opacity-100 transition-all">
                                    <Flame className="w-12 h-12 text-amber-600" />
                                </div>
                                <div>
                                    <span className="text-[9px] uppercase font-black tracking-[0.4em] text-amber-700/60 mb-2 block">Resolution {i + 1}</span>
                                    <h4 className="text-2xl font-serif font-black text-amber-100 group-hover:text-white transition-colors capitalize">{opt}</h4>
                                </div>
                                <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-amber-900 group-hover:text-amber-500 transition-colors">
                                    <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                                    Forge The Path
                                </div>
                            </motion.button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

const QuestStat = ({ label, value, icon }: { label: string, value: string, icon: React.ReactNode }) => (
    <div className="text-center group">
        <div className="flex items-center gap-2 mb-2 justify-center opacity-30 group-hover:opacity-100 transition-opacity">
            {icon}
            <span className="text-[10px] uppercase font-black tracking-widest text-slate-400">{label}</span>
        </div>
        <p className="text-3xl font-black italic text-white tracking-tighter group-hover:text-amber-500 transition-colors uppercase">{value}</p>
    </div>
);

const InventoryItem = ({ icon, label, count }: { icon: React.ReactNode, label: string, count: number }) => (
    <div className="flex flex-col items-center gap-1 opacity-30 hover:opacity-100 transition-opacity cursor-pointer">
        <div className="relative">
            {icon}
            <span className="absolute -top-1 -right-1 text-[8px] bg-amber-600 text-black px-1 rounded-full font-black">{count}</span>
        </div>
        <span className="text-[7px] font-black tracking-widest text-amber-600 uppercase">{label}</span>
    </div>
)
