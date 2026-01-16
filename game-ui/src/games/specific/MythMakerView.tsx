import { useState, useEffect } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumText } from '../../components/shared/PremiumComponents';
import { Sword, Shield, Scroll, Send, Flame, Sparkles, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const MythMakerView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    if (!gameState) return <div className="text-white text-center mt-20">Initializing Mythos...</div>;

    const mythNarrative = gameState.last_ai_response?.narrative || "The Hero's Journey begins... Awaiting the Oracle's voice.";
    const mythPanel = gameState.last_ai_response?.myth_panel || {};
    const stage = gameState.stage || 'Origin';
    const turn = gameState.turn || 1;

    // Safety check for panel in case it is just a string (fallback)
    const panelTitle = typeof mythPanel === 'object' ? mythPanel.title : "Mythic Vision";
    const panelPoem = typeof mythPanel === 'object' ? mythPanel.poem : (typeof mythPanel === 'string' ? mythPanel : "");
    const panelVisual = typeof mythPanel === 'object' ? mythPanel.visual_description : "";

    const handleAction = async () => {
        if (!input.trim() || !sessionId) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug || 'myth-maker', sessionId, userId, 'action', input);
            if (resp.ok) {
                updateGameState(resp.state);
                setInput("");
            }
        } catch (e) {
            console.error(e);
        }
        setLoading(false);
    };

    return (
        <PremiumGameLayout
            title="Myth Maker Arena"
            subtitle={`Epoch: ${stage}`}
            icon={Sword}
            backgroundVar="nebula"
            guideText="1. Shape your legend through mythic actions.\n2. In each epoch, describe how your hero reacts to the Oracle's prophecy.\n3. The chronicler weaves your words into an immortal saga.\n4. Complete the hero's journey with other participants."
        >
            <div className="flex flex-col h-full gap-6 relative min-h-[70vh]">

                {/* Heroic Header / Status Bar */}
                <div className="flex items-center justify-between bg-white/5 px-6 py-3 rounded-2xl border border-white/10 backdrop-blur-md shadow-lg">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-full bg-gold/20 text-gold border border-gold/30 shadow-[0_0_15px_rgba(251,191,36,0.3)]">
                            <Flame size={18} className="animate-pulse" />
                        </div>
                        <span className="text-sm font-premium font-bold text-white tracking-widest uppercase">Hero's Spirit</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="h-1 w-24 bg-white/10 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: "10%" }}
                                animate={{ width: `${Math.min(100, turn * 10)}%` }}
                                className="h-full bg-gradient-to-r from-gold to-orange-500"
                            />
                        </div>
                        <span className="text-xs text-gold font-mono tracking-tighter">Turn {turn}</span>
                    </div>
                </div>

                <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Narrative - The Chronicler's Voice */}
                    <div className="lg:col-span-2 flex flex-col gap-6">
                        <div className="flex-1 bg-black/40 rounded-3xl relative overflow-hidden group border border-white/10 shadow-2xl transition-all duration-500 hover:border-gold/20 flex flex-col">
                            {/* Background Atmosphere */}
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/10 via-transparent to-red-900/10 pointer-events-none" />
                            <div className="absolute top-0 right-0 p-12 opacity-[0.03] group-hover:opacity-[0.07] transition-opacity duration-1000">
                                <Shield size={300} />
                            </div>

                            <div className="relative z-10 flex-1 flex flex-col p-10 md:p-14">
                                <div className="flex items-center gap-2 mb-8 text-gold/40 text-[10px] uppercase tracking-[0.4em] font-bold">
                                    <Sparkles size={12} />
                                    <span>The Oracle's Proclamation</span>
                                </div>

                                <div className="flex-1 flex flex-col justify-center">
                                    <AnimatePresence mode="wait">
                                        <motion.div
                                            key={mythNarrative}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, scale: 0.98 }}
                                            transition={{ duration: 0.8, ease: "easeOut" }}
                                            className="text-2xl md:text-3xl lg:text-4xl font-premium font-bold text-white leading-[1.3] text-shadow-xl"
                                        >
                                            <PremiumText text={mythNarrative} />
                                        </motion.div>
                                    </AnimatePresence>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Prophecy & Visions */}
                    <div className="lg:col-span-1 flex flex-col gap-6">
                        {/* Prophecy Card */}
                        <div className="bg-gradient-to-br from-gold/10 to-transparent p-[1px] rounded-3xl shadow-xl">
                            <div className="bg-[#120f1a] rounded-[1.7rem] p-6 h-full border border-white/5 backdrop-blur-sm">
                                <div className="flex items-center gap-2 mb-4 text-gold border-b border-gold/10 pb-3">
                                    <BookOpen size={16} />
                                    <span className="text-xs font-bold uppercase tracking-widest">{panelTitle || "Unknown Prophecy"}</span>
                                </div>
                                <p className="text-gray-300 italic font-serif leading-relaxed text-lg whitespace-pre-wrap">
                                    {panelPoem || "The ink of destiny is still wet, awaiting the hero's next stride."}
                                </p>
                            </div>
                        </div>

                        {/* Vision Card */}
                        <div className="bg-white/5 rounded-3xl p-6 flex-1 border border-white/10 relative overflow-hidden group">
                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                            <div className="relative z-10 h-full flex flex-col">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="px-3 py-1 bg-white/5 rounded-full border border-white/10 text-[10px] text-gray-400 font-bold uppercase tracking-widest">
                                        Vision Cue
                                    </div>
                                </div>
                                <div className="flex-1 flex flex-col justify-end">
                                    <p className="text-sm text-gray-400 font-medium group-hover:text-white transition-colors duration-500 line-clamp-4">
                                        {panelVisual || "A hazy mist obscures the paths ahead, where shadows dance with starlight."}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bard Input - Immortal Command */}
                <div className="relative mt-2">
                    <div className="absolute -inset-1 bg-gradient-to-r from-gold/20 via-orange-500/20 to-gold/20 rounded-3xl blur opacity-30 group-focus-within:opacity-100 transition duration-1000" />
                    <div className="relative bg-[#0d0b14] rounded-2xl border border-white/10 p-2 flex items-center gap-3 shadow-2xl focus-within:border-gold/50 transition-all">
                        <div className="pl-4 text-gold/40">
                            <Scroll size={28} />
                        </div>
                        <input
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleAction()}
                            placeholder="Forge your next legend together..."
                            className="flex-1 bg-transparent border-none text-white placeholder:text-gray-600 py-5 px-3 focus:outline-none font-serif text-xl tracking-wide"
                            disabled={loading}
                        />
                        <PremiumButton
                            onClick={handleAction}
                            disabled={!input || loading}
                            className="px-8 py-4 rounded-xl text-lg group overflow-hidden relative"
                        >
                            <span className="relative z-10 flex items-center gap-2">
                                {loading ? <Flame size={20} className="animate-spin" /> : <>Command <Send size={20} /></>}
                            </span>
                            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                        </PremiumButton>
                    </div>
                </div>
            </div>
        </PremiumGameLayout>
    );
};
