import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles,
    Moon,
    Sun,
    Eye,
    Wind,
    Zap,
    Layers,
    Heart,
    Star,
    Compass,
    Scroll,
    History,
    Ghost
} from 'lucide-react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';

export const FortuneTellerView = () => {
    const { gameState, sessionId, userId, gameSlug, updateGameState } = useGame();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    if (!gameState) return null;

    const {
        scene = '',
        ether = 100,
        current_vision = {},
        alignment = 'Unknown',
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
            console.error("Oracle communication error:", e);
        }
        setLoading(false);
        setInput('');
    };

    return (
        <div className="min-h-screen bg-[#080315] text-[#d4d4d8] font-serif p-4 md:p-8 flex flex-col gap-6 relative overflow-hidden">
            {/* Celestial Background Effect */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-purple-900/10 rounded-full blur-[120px] animate-pulse" />
                <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-blue-900/10 rounded-full blur-[100px]" />
                <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-indigo-900/10 rounded-full blur-[100px]" />
            </div>

            {/* Header - Oracle Status */}
            <div className="flex flex-wrap items-center justify-between gap-4 z-10 border-b border-white/5 pb-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 bg-purple-500/10 rounded-full border border-purple-500/20 shadow-[0_0_30px_rgba(168,85,247,0.1)]">
                        <Sparkles className="w-6 h-6 text-purple-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-light tracking-[0.2em] text-white uppercase italic">Oracle of Aethelgard</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-ping" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-purple-400/70">{alignment} Alignment Active</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-8">
                    <div className="text-right">
                        <p className="text-[10px] uppercase font-bold text-white/30 tracking-widest mb-1">Ether Resonance</p>
                        <div className="flex items-center gap-3">
                            <div className="flex -space-x-1">
                                {[...Array(5)].map((_, i) => (
                                    <div key={i} className={`w-3 h-3 rounded-full border border-white/10 ${i < (ether / 20) ? 'bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.5)]' : 'bg-white/5'}`} />
                                ))}
                            </div>
                            <span className="text-xl font-light text-white italic tracking-tighter">{ether}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 flex-grow pt-4">
                {/* Center: The Vision Artifact */}
                <div className="lg:col-span-8 flex flex-col gap-8">
                    <div className="flex flex-col items-center justify-center flex-grow relative">
                        {/* Artifact Card/Orb */}
                        <motion.div
                            key={current_vision.artifact}
                            initial={{ scale: 0.9, opacity: 0, rotateY: 180 }}
                            animate={{ scale: 1, opacity: 1, rotateY: 0 }}
                            transition={{ duration: 1, ease: "circOut" }}
                            className="relative group cursor-pointer"
                        >
                            <div className="absolute -inset-4 bg-gradient-to-t from-purple-500/20 to-blue-500/20 rounded-[3rem] blur-2xl opacity-50 transition duration-1000 group-hover:opacity-100" />
                            <div className="relative w-72 h-[450px] bg-[#120b25] border border-white/10 rounded-[2.5rem] flex flex-col items-center p-8 backdrop-blur-xl shadow-2xl overflow-hidden">
                                <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-30" />

                                <div className="mt-4 p-4 rounded-full bg-purple-500/5 border border-purple-500/10">
                                    <Eye className="w-10 h-10 text-purple-400/50" />
                                </div>

                                <h3 className="mt-8 text-xl font-light text-purple-200 tracking-[0.2em] text-center uppercase">
                                    {current_vision.artifact || 'Drawing...'}
                                </h3>

                                <div className="mt-auto text-center">
                                    <p className="text-[10px] text-white/40 uppercase tracking-widest mb-4">Vision Flash</p>
                                    <p className="text-sm italic leading-relaxed text-gray-400 border-t border-white/5 pt-4">
                                        "{current_vision.flash || 'Concentrate on your inquiry...'}"
                                    </p>
                                </div>

                                {/* Floral Pattern Overlays */}
                                <div className="absolute -bottom-10 -right-10 opacity-5 pointer-events-none">
                                    <Star className="w-32 h-32" />
                                </div>
                            </div>
                        </motion.div>

                        {/* Main Narrative */}
                        <motion.div
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            className="w-full max-w-2xl mt-8 text-center"
                        >
                            <p className="text-2xl font-light text-white leading-relaxed italic drop-shadow-lg">
                                {scene}
                            </p>
                        </motion.div>
                    </div>

                    {/* Pathways (Actions) */}
                    <div className="flex flex-col gap-6 pb-8">
                        <div className="flex flex-wrap justify-center gap-3">
                            {available_actions.map((path: string, idx: number) => (
                                <button
                                    key={idx}
                                    onClick={() => handleAction(path)}
                                    disabled={loading}
                                    className="px-6 py-2 bg-purple-500/5 border border-purple-500/20 rounded-full hover:bg-purple-500/20 hover:border-purple-500/40 transition-all text-xs font-bold tracking-[0.1em] text-purple-300 uppercase italic shadow-xl flex items-center gap-2 group"
                                >
                                    <Wind className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-all" />
                                    {path}
                                </button>
                            ))}
                        </div>

                        <div className="max-w-xl mx-auto w-full relative group">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAction(input)}
                                placeholder="Whisper your inquiry to the ether..."
                                className="w-full bg-white/5 border border-white/10 rounded-full py-5 px-10 focus:outline-none focus:border-purple-500/30 transition-all text-white placeholder:text-white/20 italic text-lg shadow-2xl"
                            />
                            <button
                                onClick={() => handleAction(input)}
                                disabled={loading || !input.trim()}
                                className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white hover:bg-purple-500 transition-all shadow-xl shadow-purple-900/20"
                            >
                                <Eye className="w-6 h-6" />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Celestial Metrics */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 backdrop-blur-md shadow-inner">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 border-b border-white/5 pb-4 mb-6 flex items-center gap-2">
                            <Compass className="w-4 h-4 text-purple-500" /> Celestial State
                        </h3>

                        <div className="space-y-8">
                            <InfoCard
                                icon={<Moon className="w-5 h-5" />}
                                label="Alignment"
                                value={alignment}
                            />
                            <InfoCard
                                icon={<Heart className="w-5 h-5" />}
                                label="Resonance"
                                value={ether > 50 ? 'Strong' : 'Fading'}
                            />
                            <InfoCard
                                icon={<Ghost className="w-5 h-5" />}
                                label="Entities"
                                value="1 Observer"
                            />
                        </div>

                        <div className="mt-10 p-6 bg-purple-500/5 border border-purple-500/10 rounded-2xl flex items-center gap-4">
                            <Scroll className="w-8 h-8 text-purple-400 opacity-30" />
                            <p className="text-[10px] uppercase font-bold tracking-widest leading-loose text-white/30">
                                Predictions made within the Aethelgard realm are subject to the shifting tides of the Void. Seek clarity with caution.
                            </p>
                        </div>
                    </div>

                    {/* Quick Charms */}
                    <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-white/40 mb-6 flex items-center gap-2">
                            <Zap className="w-4 h-4 text-purple-500" /> Astral Charms
                        </h3>
                        <div className="grid grid-cols-2 gap-3">
                            <CharmButton label="Deep Sight" cost={30} onClick={() => handleAction("Initiate Deep Sight reading")} />
                            <CharmButton label="Heal Ether" cost={0} onClick={() => handleAction("Offer gratitude to the Oracle")} />
                        </div>
                    </div>
                </div>
            </div>

            {status === 'faded' && (
                <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-2xl flex items-center justify-center p-8">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="max-w-md w-full text-center"
                    >
                        <Ghost className="w-20 h-20 text-white/10 mx-auto mb-8" />
                        <h2 className="text-5xl font-light italic tracking-tighter text-white mb-4">The Veil Closes</h2>
                        <p className="text-gray-400 mb-10 font-light leading-relaxed">The connection to the Oracle has dissolved into the silent Void. Your fate remains yours to shape.</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-12 py-4 bg-white/5 border border-white/10 rounded-full text-white font-bold uppercase tracking-widest hover:bg-white/10 transition-all shadow-2xl"
                        >
                            Reconnect
                        </button>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

const InfoCard = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
    <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
            <div className="text-purple-400/50">{icon}</div>
            <span className="text-xs uppercase font-bold tracking-widest text-white/20">{label}</span>
        </div>
        <span className="text-sm font-light text-white italic tracking-tight">{value}</span>
    </div>
);

const CharmButton = ({ label, cost, onClick }: { label: string, cost: number, onClick: () => void }) => (
    <button
        onClick={onClick}
        className="p-3 border border-white/5 rounded-xl bg-white/[0.02] hover:bg-purple-500/10 hover:border-purple-500/20 transition-all flex flex-col items-center gap-1 group"
    >
        <span className="text-[10px] font-bold uppercase tracking-tighter text-white/60 group-hover:text-purple-300">{label}</span>
        <span className="text-[8px] font-black uppercase text-purple-500/50">{cost} ETHER</span>
    </button>
);
