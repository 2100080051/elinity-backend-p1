import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumText } from '../../components/shared/PremiumComponents';
import {
    Zap, Sparkles, Orbit,
    Compass, Eye, Ghost,
    Feather, ScrollText, Crosshair,
    LayoutGrid, ChevronRight, Star,
    Flame, Hexagon, CircleDashed
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const MythMakerView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const narrative = gameState.narrative || "The stars are cold and waiting for your spark.";
    const belief = gameState.belief ?? 10;
    const divinity = gameState.divinity ?? 0;
    const status = gameState.constellation_status || "The Spark";
    const mythicCard = gameState.mythic_card || {};
    const options = gameState.divine_options || [];
    const starsigns = gameState.starsigns || [];

    // Favors
    const favorA = gameState.favor_architect ?? 0;
    const favorC = gameState.favor_catalyst ?? 0;
    const favorW = gameState.favor_witness ?? 0;

    const handleAction = async (actionText: string) => {
        if (!actionText.trim() || !sessionId || !gameSlug) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'action', actionText);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error("Celestial Error:", e); }
        setLoading(false);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="Myth Maker Arena"
            subtitle={`Consellation: ${status}`}
            icon={Orbit}
            backgroundVar="aurora"
            guideText="Weave your legend into the stars. Divinity grants power; Belief grants presence. Follow the star-signs to godhood."
        >
            <div className="flex flex-col h-full relative p-6 md:p-10 overflow-hidden">

                {/* --- COSMIC SIDEBARS (STATUS) --- */}
                <div className="absolute top-0 inset-x-0 p-8 flex justify-between items-start pointer-events-none z-50">

                    {/* Pantheon Favors */}
                    <div className="flex flex-col gap-3 pointer-events-auto">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-white/30 mb-2">Pantheon Resonance</h4>
                        <div className="flex flex-col gap-2">
                            {[
                                { label: 'Architect', val: favorA, color: 'text-cyan-400', bg: 'bg-cyan-500' },
                                { label: 'Catalyst', val: favorC, color: 'text-orange-500', bg: 'bg-orange-600' },
                                { label: 'Witness', val: favorW, color: 'text-purple-400', bg: 'bg-purple-500' }
                            ].map((f, i) => (
                                <div key={i} className="flex flex-col gap-1 w-32 px-3 py-1.5 bg-black/40 border border-white/5 rounded-xl backdrop-blur-md">
                                    <div className="flex justify-between items-center">
                                        <span className={`text-[8px] font-black uppercase tracking-widest ${f.color}`}>{f.label}</span>
                                        <span className="text-[8px] text-white/60">{f.val}</span>
                                    </div>
                                    <div className="h-0.5 bg-white/10 rounded-full overflow-hidden">
                                        <motion.div animate={{ width: `${Math.min(100, Math.abs(f.val))}%` }} className={`h-full ${f.bg}`} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Star Signs */}
                    <div className="flex flex-col items-end gap-2 pointer-events-auto">
                        <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-white/30 mb-2">Attained Star-Signs</h4>
                        <div className="flex flex-wrap flex-col items-end gap-2">
                            {starsigns.map((sign: string, i: number) => (
                                <motion.div
                                    initial={{ x: 20, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    key={i}
                                    className="px-4 py-1.5 bg-white/5 border border-white/10 rounded-full backdrop-blur-xl flex items-center gap-2 group"
                                >
                                    <Star className="w-3 h-3 text-yellow-400 animate-pulse" />
                                    <span className="text-[9px] font-black uppercase tracking-widest text-white/80 group-hover:text-white transition-colors">{sign}</span>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* --- MAIN DIVINE DISPLAY --- */}
                <div className="flex-1 flex flex-col items-center justify-center relative min-h-0">

                    {/* Divinity & Belief Meters (Vertical Nebula) */}
                    <div className="absolute top-1/2 left-10 -translate-y-1/2 flex flex-col items-center gap-4">
                        <span className="text-[9px] -rotate-90 uppercase tracking-[0.4em] text-white/20 font-black mb-12">Divinity</span>
                        <div className="h-64 w-3 bg-white/5 rounded-full relative overflow-hidden flex flex-col justify-end">
                            <motion.div
                                animate={{ height: `${divinity}%` }}
                                className="w-full bg-gradient-to-t from-orange-600 via-orange-400 to-white shadow-[0_0_20px_orange]"
                            />
                        </div>
                        <Zap size={16} className="text-orange-400" />
                    </div>

                    <div className="absolute top-1/2 right-10 -translate-y-1/2 flex flex-col items-center gap-4">
                        <span className="text-[9px] rotate-90 uppercase tracking-[0.4em] text-white/20 font-black mb-12">Belief</span>
                        <div className="h-64 w-3 bg-white/5 rounded-full relative overflow-hidden flex flex-col justify-end">
                            <motion.div
                                animate={{ height: `${belief}%` }}
                                className="w-full bg-gradient-to-t from-cyan-600 via-cyan-400 to-white shadow-[0_0_20px_cyan]"
                            />
                        </div>
                        <Flame size={16} className="text-cyan-400" />
                    </div>

                    {/* Central Mythic Card */}
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={narrative}
                            initial={{ opacity: 0, scale: 0.9, rotateY: 90 }}
                            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
                            exit={{ opacity: 0, scale: 1.1, rotateY: -90 }}
                            transition={{ duration: 0.8, ease: "circOut" }}
                            className="relative w-full max-w-3xl bg-black/40 border border-white/10 rounded-[3rem] p-12 backdrop-blur-3xl shadow-2xl flex flex-col items-center text-center overflow-hidden"
                        >
                            {/* Decorative Borders */}
                            <div className="absolute inset-4 border border-white/5 rounded-[2.5rem] pointer-events-none" />

                            <div className="mb-8">
                                <h3 className="text-3xl md:text-5xl font-serif font-black text-white italic tracking-tighter mb-4 selection:bg-orange-500/40">
                                    {mythicCard.title || "The Unwritten Word"}
                                </h3>
                                <div className="h-px w-32 bg-gradient-to-r from-transparent via-orange-500 to-transparent mx-auto" />
                            </div>

                            <p className="text-xl md:text-3xl text-white/80 font-serif leading-relaxed italic max-w-2xl mb-12">
                                <PremiumText text={narrative} />
                            </p>

                            <div className="bg-white/5 border border-white/5 p-8 rounded-3xl relative w-full group overflow-hidden">
                                <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-orange-500/5 to-transparent pointer-events-none" />
                                <Feather className="w-6 h-6 text-orange-500/40 mx-auto mb-4" />
                                <p className="text-sm font-serif text-white/40 italic leading-relaxed px-8">
                                    "{mythicCard.prophecy || "The future is a blank sky awaiting its first star."}"
                                </p>
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* --- DIVINE COMMAND FOOTER --- */}
                <div className="p-10 bg-gradient-to-t from-black via-black/80 to-transparent flex flex-col items-center gap-10">

                    {/* Path Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
                        {options.map((opt: any, i: number) => (
                            <button
                                key={i}
                                onClick={() => handleAction(opt.concept)}
                                disabled={loading}
                                className="group relative p-6 bg-white/5 hover:bg-white/10 border border-white/10 rounded-3xl text-left transition-all duration-500 transform hover:-translate-y-2 overflow-hidden flex flex-col justify-between h-40"
                            >
                                <div className="absolute top-4 right-4 opacity-5 group-hover:opacity-100 transition-opacity">
                                    <CircleDashed className="w-12 h-12 text-white animate-spin-slow" />
                                </div>
                                <div>
                                    <span className="text-[9px] uppercase font-black tracking-widest text-orange-500/60 mb-1 block">The Way of {opt.concept.split(' ')[2]}</span>
                                    <h4 className="text-sm font-black text-white uppercase tracking-tight">{opt.concept}</h4>
                                </div>
                                <div className="space-y-1">
                                    <span className="text-[8px] uppercase tracking-widest text-white/30 font-bold block">Cost: {opt.cost}</span>
                                    <p className="text-[10px] text-white/60 font-serif italic leading-relaxed line-clamp-2">{opt.benefit}</p>
                                </div>
                            </button>
                        ))}
                    </div>

                    <div className="w-full max-w-4xl flex gap-4">
                        <div className="flex-1 relative group">
                            <div className="absolute -inset-1 bg-gradient-to-r from-orange-500/20 to-cyan-500/20 rounded-3xl blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-700" />
                            <div className="relative flex items-center bg-black/60 border-2 border-white/10 rounded-[2.5rem] px-8 py-5">
                                <ScrollText className="w-6 h-6 text-white/20 mr-4" />
                                <input
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && handleAction(input)}
                                    placeholder="Forge an absolute command..."
                                    className="w-full bg-transparent border-none text-xl font-serif font-black text-white italic placeholder:text-white/10 focus:outline-none"
                                    disabled={loading}
                                />
                            </div>
                        </div>
                        <PremiumButton
                            onClick={() => handleAction(input)}
                            disabled={loading || !input}
                            className={`h-[72px] w-[72px] rounded-[2rem] flex items-center justify-center transition-all ${loading ? 'opacity-50' : 'bg-gradient-to-br from-orange-500 to-orange-700 shadow-2xl hover:scale-105 active:scale-95'}`}
                        >
                            {loading ? <Orbit className="animate-spin text-white" /> : <ChevronRight className="text-white" size={32} />}
                        </PremiumButton>
                    </div>

                    <button className="flex items-center gap-2 text-[10px] font-black text-white/20 hover:text-white/50 transition-colors uppercase tracking-[0.4em]">
                        <LayoutGrid size={12} /> View Previous Epochs
                    </button>
                </div>

            </div>
        </PremiumGameLayout>
    );
};
