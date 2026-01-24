import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumText } from '../../components/shared/PremiumComponents';
import {
    Sword, Shield, Heart, Zap,
    Coins, Map as MapIcon, Box,
    Flame, Skull, ChevronRight,
    Trophy, Sparkles, Wand2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const AdventureDungeonView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const narrative = gameState.scene || "The dungeon waits...";
    const hp = gameState.hp ?? 100;
    const ap = gameState.ap ?? 100;
    const xp = gameState.xp ?? 0;
    const level = gameState.level ?? 1;
    const gold = gameState.gold ?? 0;
    const inventory = gameState.inventory || [];
    const atmosphere = gameState.atmosphere || "Damp & Dark";
    const roomData = gameState.room_data || {};
    const actions = gameState.available_actions || [];

    const handleAction = async (actionText: string) => {
        if (!sessionId || !gameSlug) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', actionText);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error("Dungeon Error", e); }
        setLoading(false);
    };

    return (
        <PremiumGameLayout
            title="AI Adventure Dungeon"
            subtitle={`Floor ${gameState.floor || 1} • Level ${level}`}
            icon={Sword}
            backgroundVar="void"
            guideText="Survive the procedurally generated depths. Use AP for skills. HP is life. XP evolves your power."
        >
            <div className="flex flex-col h-full gap-6 p-4 md:p-8 relative overflow-hidden">

                {/* --- STATS HUD --- */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 z-20">
                    {/* HP Bar */}
                    <div className="bg-black/40 border border-white/5 p-4 rounded-2xl backdrop-blur-xl">
                        <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2 text-red-500">
                                <Heart size={14} fill="currentColor" />
                                <span className="text-[10px] font-black uppercase tracking-widest">Vitality</span>
                            </div>
                            <span className="text-xs font-bold text-white">{hp}/100</span>
                        </div>
                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{ width: `${hp}%` }} className="h-full bg-red-600 shadow-[0_0_10px_rgba(220,38,38,0.5)]" />
                        </div>
                    </div>

                    {/* AP Bar */}
                    <div className="bg-black/40 border border-white/5 p-4 rounded-2xl backdrop-blur-xl">
                        <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2 text-cyan-500">
                                <Zap size={14} fill="currentColor" />
                                <span className="text-[10px] font-black uppercase tracking-widest">Energy</span>
                            </div>
                            <span className="text-xs font-bold text-white">{ap}/100</span>
                        </div>
                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{ width: `${ap}%` }} className="h-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]" />
                        </div>
                    </div>

                    {/* XP / Level Bar */}
                    <div className="bg-black/40 border border-white/5 p-4 rounded-2xl backdrop-blur-xl">
                        <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2 text-yellow-500">
                                <Trophy size={14} />
                                <span className="text-[10px] font-black uppercase tracking-widest">Mastery</span>
                            </div>
                            <span className="text-[8px] bg-yellow-500/20 text-yellow-500 px-2 py-0.5 rounded-md font-bold">LVL {level}</span>
                        </div>
                        <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                            <motion.div animate={{ width: `${xp}%` }} className="h-full bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]" />
                        </div>
                    </div>

                    {/* Gold Count */}
                    <div className="bg-black/40 border border-white/5 p-4 rounded-2xl backdrop-blur-xl flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-orange-500/10 rounded-lg">
                                <Coins className="text-orange-500 w-5 h-5" />
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[10px] text-white/40 uppercase font-black">Treasure</span>
                                <span className="text-lg font-black text-white">{gold}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* --- MAIN GAMEPLAY AREA --- */}
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">

                    {/* Character & Room Info (3 cols) */}
                    <div className="lg:col-span-3 flex flex-col gap-6">
                        {/* Room Card */}
                        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 backdrop-blur-md">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 bg-purple-500/10 rounded-xl">
                                    <MapIcon className="text-purple-400 w-5 h-5" />
                                </div>
                                <h3 className="text-xs font-black uppercase tracking-widest text-white/60">Location Intelligence</h3>
                            </div>
                            <div className="space-y-4">
                                <div className="flex justify-between text-[11px]">
                                    <span className="text-white/30 uppercase font-bold tracking-tight">Anomalous State</span>
                                    <span className="text-white font-medium">{atmosphere}</span>
                                </div>
                                <div className="flex justify-between text-[11px]">
                                    <span className="text-white/30 uppercase font-bold tracking-tight">Zone Type</span>
                                    <span className="text-cyan-400 font-bold">{roomData.type || "Threshold"}</span>
                                </div>
                                <div className="flex justify-between text-[11px]">
                                    <span className="text-white/30 uppercase font-bold tracking-tight">Threat Density</span>
                                    <div className="flex gap-1">
                                        {[...Array(5)].map((_, i) => (
                                            <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < (roomData.threat_level || 1) / 2 ? 'bg-red-500 shadow-[0_0_5px_red]' : 'bg-white/10'}`} />
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Inventory Grid */}
                        <div className="flex-1 bg-black/40 border border-white/5 rounded-3xl p-6 backdrop-blur-xl overflow-hidden flex flex-col">
                            <div className="flex items-center gap-3 mb-4">
                                <Box className="text-gray-500 w-4 h-4" />
                                <span className="text-[10px] uppercase font-black tracking-widest text-white/30">Satchel Contents</span>
                            </div>
                            <div className="grid grid-cols-3 gap-2 overflow-y-auto custom-scrollbar pr-2">
                                {inventory.map((item: string, i: number) => (
                                    <motion.div
                                        initial={{ scale: 0.8, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        key={i}
                                        className="aspect-square bg-white/5 border border-white/10 rounded-xl flex items-center justify-center group relative cursor-help"
                                        title={item}
                                    >
                                        <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl" />
                                        <span className="text-[8px] text-center p-1 leading-tight text-white/60 font-medium line-clamp-2">{item}</span>
                                    </motion.div>
                                ))}
                                {[...Array(Math.max(0, 9 - inventory.length))].map((_, i) => (
                                    <div key={`empty-${i}`} className="aspect-square bg-white/[0.02] border border-dashed border-white/5 rounded-xl" />
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Encounter Narrative (9 cols) */}
                    <div className="lg:col-span-9 flex flex-col gap-6 min-h-0">
                        <div className="flex-1 bg-gradient-to-br from-white/[0.02] to-transparent border border-white/10 rounded-[2.5rem] p-10 flex flex-col overflow-hidden relative">
                            {/* Ambient Effect */}
                            <div className="absolute top-0 right-0 p-8 opacity-5">
                                {roomData.type === 'Combat' ? <Skull size={200} /> : <Flame size={200} />}
                            </div>

                            <div className="relative z-10 flex-1 overflow-y-auto custom-scrollbar pr-6">
                                <div className="flex items-center gap-2 mb-6 text-red-500/60 text-[10px] font-black uppercase tracking-[0.3em]">
                                    <ChevronRight size={14} /> The Chronicle Updates
                                </div>
                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={narrative}
                                        initial={{ opacity: 0, scale: 0.98 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="text-xl md:text-2xl lg:text-3xl text-gray-100 font-serif leading-relaxed italic"
                                    >
                                        <PremiumText text={narrative} />
                                    </motion.div>
                                </AnimatePresence>
                            </div>

                            {/* Action Floating Buttons */}
                            <div className="relative z-10 mt-8 flex flex-wrap gap-4">
                                {actions.map((act: string, i: number) => (
                                    <motion.button
                                        whileHover={{ scale: 1.05, y: -2 }}
                                        whileTap={{ scale: 0.95 }}
                                        key={i}
                                        onClick={() => handleAction(act)}
                                        disabled={loading}
                                        className="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl flex items-center gap-3 transition-all"
                                    >
                                        <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_cyan]" />
                                        <span className="text-xs font-bold text-white/80">{act}</span>
                                    </motion.button>
                                ))}
                            </div>
                        </div>

                        {/* Custom Interaction Bar */}
                        <div className="h-24 flex gap-4">
                            <div className="flex-1 bg-black/60 border-2 border-white/5 rounded-3xl backdrop-blur-2xl flex items-center px-8 group focus-within:border-white/20 transition-all">
                                <Wand2 className="text-white/20 mr-4 group-focus-within:text-cyan-400 group-focus-within:animate-pulse transition-colors" />
                                <input
                                    className="bg-transparent border-none w-full text-white placeholder:text-white/10 focus:outline-none font-serif text-lg italic"
                                    placeholder="Dictate your next move to the Architect..."
                                    onKeyDown={e => {
                                        if (e.key === 'Enter') {
                                            handleAction((e.target as HTMLInputElement).value);
                                            (e.target as HTMLInputElement).value = "";
                                        }
                                    }}
                                />
                            </div>
                            <PremiumButton
                                className="w-24 h-full rounded-3xl"
                                onClick={() => { }}
                            >
                                <ChevronRight size={32} />
                            </PremiumButton>
                        </div>
                    </div>
                </div>

                {/* Level Up Flash Overlay */}
                <AnimatePresence>
                    {xp >= 100 && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-yellow-500/10 backdrop-blur-sm z-[100] flex items-center justify-center"
                        >
                            <motion.div
                                initial={{ scale: 0.5 }}
                                animate={{ scale: 1 }}
                                className="flex flex-col items-center gap-4"
                            >
                                <Sparkles className="w-20 h-20 text-yellow-500 animate-spin" />
                                <h2 className="text-6xl font-black text-white italic tracking-tighter">LEVEL ASCENDED</h2>
                                <span className="text-xs uppercase tracking-[1em] text-yellow-500/60 font-black">Neural Reconfiguration Complete</span>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>

            </div>
        </PremiumGameLayout>
    );
};
