import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Library,
    Scroll,
    Zap,
    Sparkles,
    Moon,
    Sun,
    ChevronRight,
    Flame,
    Feather,
    Eye,
    Key,
    Compass
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const SymbolQuestView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        resonance = 10,
        alignment = 'The Seeker',
        symbol = 'Unknown',
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
            console.error("Inscriber communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#0c0908] text-[#d4af37] font-serif p-4 md:p-8 flex flex-col gap-6 overflow-hidden relative">
            {/* Parchment/Antique texture overlay */}
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/dark-wood.png')] pointer-events-none opacity-20" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,#1a1512,transparent)] pointer-events-none" />

            {/* Header - Inscriber HUD */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-[#d4af37]/20 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-[#1a1512] rounded-full border border-gold/40 shadow-[0_0_20px_rgba(212,175,55,0.2)]">
                        <Library className="w-6 h-6 text-gold" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black tracking-[0.2em] text-gold uppercase italic">The Sacred Lexicon</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-gold/50 animate-pulse" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-gold/30 italic">Current Archetype: {alignment}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8 bg-[#1a1512]/80 px-8 py-4 rounded-full border border-gold/10 backdrop-blur-md">
                    <SymbolStat icon={<Flame className="w-4 h-4 text-orange-500" />} label="Resonance" value={`${resonance}%`} />
                    <div className="w-px h-8 bg-gold/5" />
                    <SymbolStat icon={<Eye className="w-4 h-4 text-emerald-400" />} label="Active Symbol" value={symbol} />
                    <div className="w-px h-8 bg-gold/5" />
                    <SymbolStat icon={<Key className="w-4 h-4 text-purple-400" />} label="Sanctity" value="High" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Ritual Feed */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                    <motion.div
                        key={scene}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex-grow bg-[#1a1512]/40 border border-[#d4af37]/10 rounded-[2rem] p-12 backdrop-blur-sm relative overflow-hidden flex flex-col justify-center text-center shadow-inner shadow-black"
                    >
                        {/* Golden corner accents */}
                        <div className="absolute top-0 left-0 w-24 h-24 border-t-2 border-l-2 border-gold/20 rounded-tl-[2rem]" />
                        <div className="absolute bottom-0 right-0 w-24 h-24 border-b-2 border-r-2 border-gold/20 rounded-br-[2rem]" />

                        <div className="relative z-10">
                            <div className="flex items-center justify-center gap-2 mb-10 text-[11px] font-bold text-gold/20 uppercase tracking-[0.8em]">
                                <Scroll className="w-4 h-4" /> Inscription_Manifesting
                            </div>

                            <p className="text-3xl md:text-4xl font-light leading-relaxed text-gold/80 italic selection:bg-gold/30">
                                {scene.split('\n').map((line: string, i: number) => (
                                    <span key={i} className="block mb-6 last:mb-0">
                                        {line}
                                    </span>
                                ))}
                            </p>
                        </div>
                    </motion.div>

                    {/* Ritual Inputs */}
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-wrap gap-3 justify-center">
                            {available_actions.map((rune: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(rune)}
                                    disabled={loading}
                                    className="px-8 py-3 bg-[#1a1512] border border-gold/20 rounded-full hover:bg-gold/10 hover:border-gold transition-all text-[11px] font-black uppercase tracking-[0.2em] text-gold/60 hover:text-gold flex items-center gap-3 group shadow-2xl"
                                >
                                    <Sparkles className="w-3 h-3 text-gold opacity-0 group-hover:opacity-100 transition-all scale-0 group-hover:scale-100" />
                                    {rune}
                                </button>
                            ))}
                        </div>

                        <div className="relative group max-w-2xl mx-auto w-full">
                            <div className="absolute -inset-1 bg-gold/10 rounded-full blur opacity-5 group-focus-within:opacity-20 transition duration-500" />
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your intent to the lexicon..."
                                className="w-full bg-[#0c0908] border border-gold/20 rounded-full py-6 px-12 focus:outline-none focus:border-gold/50 transition-all text-gold placeholder:text-gold/10 text-xl font-light italic text-center"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-4 top-1/2 -translate-y-1/2 w-14 h-14 bg-gold rounded-full flex items-center justify-center text-black hover:bg-[#d49d37] transition-all shadow-xl"
                            >
                                <Feather className={`w-6 h-6 ${loading ? 'animate-bounce' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Cosmological Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-[#1a1512]/30 border border-gold/10 rounded-[2rem] p-8 shadow-2xl">
                        <h3 className="text-[10px] font-black uppercase tracking-[0.5em] text-gold/20 mb-8 flex items-center gap-2 border-b border-gold/5 pb-4">
                            <Compass className="w-4 h-4" /> Celestial_Alignment
                        </h3>

                        <div className="space-y-10">
                            <CosmicMeter label="Runic Convergence" value={resonance} />
                            <CosmicMeter label="Archetypal Sync" value={95} />
                            <CosmicMeter label="Void Resistance" value={15} />
                        </div>

                        <div className="mt-12 p-8 bg-gold/5 border border-gold/10 rounded-3xl flex items-start gap-4">
                            <Sun className="w-5 h-5 text-gold opacity-30 mt-1" />
                            <p className="text-[10px] uppercase font-bold tracking-[0.1em] leading-relaxed text-gold/40 italic text-center w-full">
                                "The meaning is not in the ink, but in the silence between the lines."
                            </p>
                        </div>
                    </div>

                    <div className="bg-[#1a1512]/20 border border-gold/5 rounded-[2rem] p-8 flex flex-col items-center justify-center gap-4 text-gold/10">
                        <Moon className="w-10 h-10 opacity-10 animate-pulse" />
                        <span className="text-[8px] font-black uppercase tracking-[0.6em] text-center">Ley Lines Converging</span>
                    </div>
                </div>
            </div>

            {status === 'enlightened' && (
                <div className="fixed inset-0 z-[100] bg-black/98 backdrop-blur-3xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Sun className="w-24 h-24 text-gold mx-auto mb-10 shadow-[0_0_60px_rgba(212,175,55,0.4)] animate-spin-slow" />
                        <h2 className="text-6xl font-black italic tracking-tighter text-gold mb-4 uppercase">Enlightenment</h2>
                        <p className="text-gold/40 mb-12 font-bold leading-relaxed tracking-widest uppercase text-sm">The symbols have dissolved. You no longer read the lexicon; you are the hand that writes it.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-16 py-5 bg-gold rounded-full text-black font-black uppercase tracking-[0.3em] hover:bg-white transition-all shadow-2xl"
                        >
                            Begin New Cycle
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const SymbolStat = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="text-center">
        <div className="flex items-center gap-2 mb-1 justify-center opacity-40">
            {icon}
            <span className="text-[9px] uppercase font-black tracking-widest">{label}</span>
        </div>
        <p className="text-xl font-black italic text-white tracking-tighter">{value}</p>
    </div>
);

const CosmicMeter = ({ label, value }: { label: string, value: number }) => (
    <div className="space-y-4">
        <div className="flex justify-between items-center text-[9px] font-black uppercase tracking-[0.4em] text-gold/30">
            <span>{label}</span>
            <span>{value}%</span>
        </div>
        <div className="h-0.5 bg-gold/5 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                className="h-full bg-gold shadow-[0_0_15px_rgba(212,175,55,1)]"
            />
        </div>
    </div>
);
