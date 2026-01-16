import { useState } from 'react';
import { useGame } from '../../context/GameContext';
import { sendAction } from '../../api/client';
import { PremiumButton, PremiumCard, PremiumInput } from '../../components/shared/PremiumComponents';
import { Hexagon, Share2, Network, GitMerge } from 'lucide-react';
import { motion } from 'framer-motion';
import { PremiumGameLayout } from '../PremiumGameLayout';

export const SerendipityStringsView = () => {
    const { gameState, sessionId, userId, updateGameState, gameSlug } = useGame();
    const [input, setInput] = useState("");

    const question = gameState.last_ai_response?.question || "What connects us across the digital void?";
    const connections = gameState.last_ai_response?.connections || [];
    const insight = gameState.last_ai_response?.serendipity_insight || "";

    const handleSubmit = async () => {
        const resp = await sendAction(gameSlug!, sessionId!, userId, 'answer', input);
        if (resp.ok) updateGameState(resp.state);
        setInput("");
    };

    return (
        <PremiumGameLayout
            title="Serendipity Strings"
            subtitle="Invisible Threads"
            icon={Hexagon}
            backgroundVar="starfield"
            guideText="1. Pull on the invisible threads that connect the group.\n2. Answer introspective questions to reveal hidden commonalities.\n3. The AI map visualizes your shared strings of serendipity.\n4. Discover deep connections with other participants."
        >
            <div className="h-full flex flex-col items-center justify-center relative">

                {/* Background Network Animation */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20">
                    <defs>
                        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    <motion.circle
                        cx="50%" cy="50%" r="100"
                        fill="none" stroke="#FFD700" strokeWidth="1"
                        animate={{ r: [100, 120, 100], opacity: [0.2, 0.5, 0.2] }}
                        transition={{ duration: 4, repeat: Infinity }}
                    />
                </svg>

                <div className="z-10 w-full max-w-3xl space-y-12">
                    {/* Main Question Card */}
                    <div className="text-center relative">
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="inline-block mb-6 p-4 rounded-full bg-white/5 border border-white/10"
                        >
                            <Hexagon className="text-gold animate-[spin_10s_linear_infinite]" size={48} />
                        </motion.div>

                        <h2 className="text-3xl md:text-5xl font-light text-white mb-6 leading-tight font-premium">
                            {question}
                        </h2>

                        {insight && (
                            <motion.div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                className="bg-gradient-to-r from-transparent via-gold/10 to-transparent p-4 border-y border-gold/20"
                            >
                                <p className="text-gold text-lg italic serif">"{insight}"</p>
                            </motion.div>
                        )}
                    </div>

                    {/* Connections Grid */}
                    {connections.length > 0 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {connections.map((conn: string, i: number) => (
                                <motion.div
                                    key={i}
                                    initial={{ x: -20, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="bg-white/5 hover:bg-white/10 border border-white/10 p-4 rounded-xl flex items-center gap-4 transition-colors group"
                                >
                                    <div className="p-2 bg-black/40 rounded-lg text-purple-400 group-hover:text-gold transition-colors">
                                        <GitMerge size={20} />
                                    </div>
                                    <span className="text-sm text-gray-200 font-medium">{conn}</span>
                                </motion.div>
                            ))}
                        </div>
                    )}

                    {/* Input */}
                    <div className="bg-black/40 p-1.5 rounded-2xl border border-white/10 flex gap-2">
                        <PremiumInput
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            placeholder="Add your thread to the web..."
                            className="bg-transparent border-none text-lg h-12"
                            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                        />
                        <PremiumButton onClick={handleSubmit} className="px-8 shadow-lg shadow-purple-500/20">
                            <Network size={18} className="mr-2" /> Connect
                        </PremiumButton>
                    </div>
                </div>
            </div>
        </PremiumGameLayout>
    );
};
