import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumInput } from '../../components/shared/PremiumComponents';
import { Image, Sparkles, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const MemoryMosaicView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const theme = gameState.theme || "Collective Memories";
    const memories = gameState.memories || [];
    const narrative = gameState.last_ai_narrative || "Share a memory to begin the mosaic.";

    const handleShare = async () => {
        if (!sessionId || !gameSlug || !input) return;
        setLoading(true);
        try {
            const resp = await sendAction(gameSlug, sessionId, userId, 'share_memory', input);
            if (resp.ok) updateGameState(resp.state);
        } catch (e) { console.error(e); }
        setLoading(false);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="Memory Mosaic"
            subtitle="Weave the Past"
            icon={Image}
            backgroundVar="void"
            guideText="1. Share a personal or fictional memory to add a tile to the collective mosaic.\n2. The AI will weave these memories into a unified narrative theme.\n3. Explore tiles added by other participants to see the world you've built together."
        >
            <div className="flex flex-col h-full gap-6">

                {/* Theme & Prompt */}
                <div className="text-center mb-4">
                    <h3 className="text-2xl text-gold font-serif italic mb-2">"{theme}"</h3>
                    <p className="text-white/60 text-sm">{narrative}</p>
                </div>

                {/* Mosaic Grid */}
                <div className="flex-1 rounded-2xl bg-black/20 border border-white/5 p-4 overflow-y-auto custom-scrollbar">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <AnimatePresence>
                            {memories.length === 0 && (
                                <motion.div
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                    className="col-span-full h-40 flex flex-col items-center justify-center text-white/20"
                                >
                                    <Sparkles size={32} className="mb-2 opacity-50" />
                                    <p>The canvas is empty.</p>
                                </motion.div>
                            )}
                            {memories.map((mem: any, i: number) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    layout
                                    className="bg-white/5 hover:bg-white/10 p-6 rounded-xl border border-white/5 relative group cursor-default transition-colors aspect-video flex flex-col justify-center text-center"
                                >
                                    <div className="absolute top-2 right-2 text-gold opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Sparkles size={14} />
                                    </div>
                                    <p className="text-gray-200 italic font-serif leading-relaxed text-sm">"{mem.text}"</p>
                                    <div className="mt-4 flex justify-between items-center text-[10px] text-gray-500 uppercase tracking-wider">
                                        <span>User {mem.user?.slice(-4)}</span>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Input Area */}
                <div className="bg-white/5 p-2 rounded-xl border border-white/10 flex items-center gap-2">
                    <div className="pl-3 text-gold/50">
                        <Plus size={20} />
                    </div>
                    <input
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="Add a tile to the mosaic..."
                        className="flex-1 bg-transparent border-none text-white placeholder:text-gray-500 py-3 px-2 focus:outline-none font-serif text-lg"
                        onKeyDown={e => e.key === 'Enter' && handleShare()}
                    />
                    <PremiumButton onClick={handleShare} disabled={loading || !input} className="px-6">
                        Add Memory
                    </PremiumButton>
                </div>
            </div>
        </PremiumGameLayout>
    );
};
